/**
 * Phylogenle - Dual-Layer Storage Module
 * LocalStorage offline-first with real-time Firestore synchronization.
 */
import { initFirebase } from './firebase-config.js';
import { onAuthChange, getCurrentUser } from './auth.js';

let firestoreDb = null;
let firestoreFns = null;

// Initialize Firestore on http/https
(async () => {
    try {
        const fb = await initFirebase();
        if (fb && fb.db) {
            firestoreDb = fb.db;
            firestoreFns = await import("https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore.js");
        }
    } catch (e) {
        console.warn("Firestore unavailable, running in local-storage mode:", e);
    }
})();

const STATS_KEY = 'phylogenle_stats_v1';
const HISTORY_KEY = 'phylogenle_history_v1';
const ACTIVE_PREFIX = 'phylogenle_active_state_v1_';
const HINTS_PREFIX = 'phylogenle_active_hints_v1_';

const DEFAULT_STATS = {
    played: 0,
    won: 0,
    currentStreak: 0,
    maxStreak: 0,
    lastPlayedDate: null,
    distribution: {
        '1-3': 0,
        '4-6': 0,
        '7-9': 0,
        '10-12': 0,
        '13-15': 0,
        '16+': 0
    }
};

/**
 * Get distribution bucket key for guess count
 */
function getBucketKey(count) {
    if (count <= 3) return '1-3';
    if (count <= 6) return '4-6';
    if (count <= 9) return '7-9';
    if (count <= 12) return '10-12';
    if (count <= 15) return '13-15';
    return '16+';
}

/**
 * Compute current and max streaks from sorted history ledger
 */
function computeStreaksFromHistory(history) {
    const dates = Object.keys(history || {}).sort();
    if (dates.length === 0) return { currentStreak: 0, maxStreak: 0 };

    let maxStreak = 0;
    let tempStreak = 0;
    let prevDate = null;

    for (const d of dates) {
        const record = history[d];
        if (!record || !record.solved) {
            tempStreak = 0;
            prevDate = d;
            continue;
        }

        if (!prevDate) {
            tempStreak = 1;
        } else {
            const p = new Date(prevDate + 'T00:00:00Z');
            const c = new Date(d + 'T00:00:00Z');
            const diffDays = Math.round((c - p) / (1000 * 60 * 60 * 24));
            if (diffDays === 1) {
                tempStreak++;
            } else if (diffDays > 1) {
                tempStreak = 1;
            }
        }
        if (tempStreak > maxStreak) maxStreak = tempStreak;
        prevDate = d;
    }

    const todayStr = new Date().toISOString().slice(0, 10);
    const lastWonDate = [...dates].reverse().find(d => history[d] && history[d].solved);
    let currentStreak = 0;
    if (lastWonDate) {
        const p = new Date(lastWonDate + 'T00:00:00Z');
        const t = new Date(todayStr + 'T00:00:00Z');
        const diffFromToday = Math.round((t - p) / (1000 * 60 * 60 * 24));
        currentStreak = (diffFromToday <= 1) ? tempStreak : 0;
    }

    return { currentStreak, maxStreak };
}

/**
 * Sanitize and heal stats against history records
 */
function sanitizeStats(stats, history) {
    const cleanStats = { ...DEFAULT_STATS, ...(stats || {}) };
    cleanStats.distribution = { ...DEFAULT_STATS.distribution, ...(cleanStats.distribution || {}) };

    const historyEntries = Object.values(history || {});
    if (historyEntries.length > 0) {
        const histDist = {
            '1-3': 0,
            '4-6': 0,
            '7-9': 0,
            '10-12': 0,
            '13-15': 0,
            '16+': 0
        };
        let histWon = 0;

        for (const rec of historyEntries) {
            if (!rec || !rec.completed) continue;
            if (rec.solved) {
                histWon++;
                const bucket = getBucketKey(rec.guessCount || 1);
                histDist[bucket] = (histDist[bucket] || 0) + 1;
            }
        }

        const distSum = Object.values(cleanStats.distribution).reduce((a, b) => a + (Number(b) || 0), 0);
        const isCorrupt = distSum > historyEntries.length || distSum !== histWon;

        if (isCorrupt) {
            cleanStats.distribution = histDist;
            cleanStats.played = historyEntries.length;
            cleanStats.won = histWon;
            const { currentStreak, maxStreak } = computeStreaksFromHistory(history);
            cleanStats.currentStreak = currentStreak;
            cleanStats.maxStreak = Math.max(cleanStats.maxStreak || 0, maxStreak);
        }
    }
    return cleanStats;
}

let memoryHistory = loadLocalHistory();
let memoryStats = sanitizeStats(loadLocalStats(), memoryHistory);
try {
    localStorage.setItem(STATS_KEY, JSON.stringify(memoryStats));
} catch (e) { }

let firestoreUnsubscribe = null;
const storageChangeListeners = new Set();

function loadLocalStats() {
    try {
        const raw = localStorage.getItem(STATS_KEY);
        if (raw) return { ...DEFAULT_STATS, ...JSON.parse(raw) };
    } catch (e) {
        console.error("Failed to parse local stats:", e);
    }
    return { ...DEFAULT_STATS };
}

function loadLocalHistory() {
    try {
        const raw = localStorage.getItem(HISTORY_KEY);
        if (raw) return JSON.parse(raw);
    } catch (e) {
        console.error("Failed to parse local history:", e);
    }
    return {};
}

export function saveLocalStats(stats) {
    memoryStats = sanitizeStats(stats, memoryHistory);
    try {
        localStorage.setItem(STATS_KEY, JSON.stringify(memoryStats));
    } catch (e) {
        console.error("Failed to save local stats:", e);
    }
    syncToCloud();
    notifyListeners();
}

/**
 * Record puzzle completion (win or give up)
 */
export function recordDailyCompletion(dateStr, puzzleNum, solved, guessCount, guesses, targetSpecies) {
    const record = {
        dateStr,
        puzzleNum,
        solved: Boolean(solved),
        guessCount: Number(guessCount) || (guesses ? guesses.length : 1),
        targetSpecies,
        guesses: Array.isArray(guesses) ? [...guesses] : [],
        completed: true,
        timestamp: Date.now()
    };

    memoryHistory[dateStr] = record;
    try {
        localStorage.setItem(HISTORY_KEY, JSON.stringify(memoryHistory));
    } catch (e) {
        console.error("Failed to save history locally:", e);
    }

    const stats = sanitizeStats(memoryStats, memoryHistory);
    stats.played = Object.keys(memoryHistory).length;
    stats.lastPlayedDate = dateStr;
    if (solved) {
        stats.won = Object.values(memoryHistory).filter(r => r.solved).length;
        const bucket = getBucketKey(record.guessCount);
        stats.distribution[bucket] = (stats.distribution[bucket] || 0) + 1;
    }
    const { currentStreak, maxStreak } = computeStreaksFromHistory(memoryHistory);
    stats.currentStreak = currentStreak;
    stats.maxStreak = Math.max(stats.maxStreak || 0, maxStreak);

    saveLocalStats(stats);
    clearActiveGuesses(dateStr);
}

/**
 * Save in-progress guesses
 */
export function saveActiveGuesses(dateStr, guesses) {
    try {
        localStorage.setItem(ACTIVE_PREFIX + dateStr, JSON.stringify(guesses));
    } catch (e) { }
}

export function loadActiveGuesses(dateStr) {
    try {
        const raw = localStorage.getItem(ACTIVE_PREFIX + dateStr);
        if (raw) return JSON.parse(raw);
    } catch (e) { }
    return null;
}

export function clearActiveGuesses(dateStr) {
    try {
        localStorage.removeItem(ACTIVE_PREFIX + dateStr);
        localStorage.removeItem(HINTS_PREFIX + dateStr);
    } catch (e) { }
}

/**
 * Save in-progress hints
 */
export function saveActiveHints(dateStr, hints) {
    try {
        localStorage.setItem(HINTS_PREFIX + dateStr, JSON.stringify(hints));
    } catch (e) { }
}

export function loadActiveHints(dateStr) {
    try {
        const raw = localStorage.getItem(HINTS_PREFIX + dateStr);
        if (raw) return JSON.parse(raw);
    } catch (e) { }
    return [];
}

export function clearActiveHints(dateStr) {
    try {
        localStorage.removeItem(HINTS_PREFIX + dateStr);
    } catch (e) { }
}


/**
 * Reset / clear record and in-progress guesses for a specific date
 */
export function resetDateRecord(dateStr) {
    if (memoryHistory[dateStr]) {
        delete memoryHistory[dateStr];
    }
    try {
        localStorage.setItem(HISTORY_KEY, JSON.stringify(memoryHistory));
    } catch (e) {
        console.error("Failed to update history locally:", e);
    }
    clearActiveGuesses(dateStr);

    const stats = sanitizeStats({ ...DEFAULT_STATS }, memoryHistory);
    stats.played = Object.keys(memoryHistory).length;
    stats.won = Object.values(memoryHistory).filter(r => r && r.solved).length;
    const { currentStreak, maxStreak } = computeStreaksFromHistory(memoryHistory);
    stats.currentStreak = currentStreak;
    stats.maxStreak = maxStreak;

    saveLocalStats(stats);
    notifyListeners();
}

/**
 * Reset all puzzle history and active guesses across the archive
 */
export function resetAllHistory() {
    memoryHistory = {};
    try {
        localStorage.removeItem(HISTORY_KEY);
    } catch (e) { }

    try {
        const keysToRemove = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith(ACTIVE_PREFIX)) {
                keysToRemove.push(key);
            }
        }
        keysToRemove.forEach(k => localStorage.removeItem(k));
    } catch (e) { }

    const freshStats = { ...DEFAULT_STATS };
    saveLocalStats(freshStats);
    notifyListeners();
}

export function getStats() {
    return sanitizeStats(memoryStats, memoryHistory);
}

export function getHistory() {
    return { ...memoryHistory };
}

export function getRecordForDate(dateStr) {
    return memoryHistory[dateStr] || null;
}

export function onStorageChange(callback) {
    storageChangeListeners.add(callback);
    return () => storageChangeListeners.delete(callback);
}

function notifyListeners() {
    storageChangeListeners.forEach(cb => {
        try { cb({ stats: memoryStats, history: memoryHistory }); } catch (e) { }
    });
}

/**
 * Sync local state to Firestore
 */
async function syncToCloud() {
    const user = getCurrentUser();
    if (!user || !firestoreDb || !firestoreFns) return;

    try {
        const userRef = firestoreFns.doc(firestoreDb, 'users', user.uid);
        const cleanStats = sanitizeStats(memoryStats, memoryHistory);
        await firestoreFns.setDoc(userRef, {
            phylogenle_stats: cleanStats,
            phylogenle_history: memoryHistory,
            lastUpdated: Date.now()
        }, { merge: true });
    } catch (e) {
        console.warn("Could not sync Phylogenle data to Firestore:", e);
    }
}

/**
 * Listen for auth change to load / merge cloud profile
 */
onAuthChange(async (user) => {
    if (firestoreUnsubscribe) {
        firestoreUnsubscribe();
        firestoreUnsubscribe = null;
    }

    if (!user || !firestoreDb || !firestoreFns) return;

    try {
        const userRef = firestoreFns.doc(firestoreDb, 'users', user.uid);
        const snap = await firestoreFns.getDoc(userRef);

        if (snap.exists()) {
            const cloudData = snap.data();
            const cloudStats = cloudData.phylogenle_stats || {};
            const cloudHistory = cloudData.phylogenle_history || {};

            // Merge history: union of dates, prefer solved and lower guess count
            const mergedHistory = { ...memoryHistory };
            for (const [date, rec] of Object.entries(cloudHistory)) {
                if (!mergedHistory[date]) {
                    mergedHistory[date] = rec;
                } else if (rec.solved && !mergedHistory[date].solved) {
                    mergedHistory[date] = rec;
                } else if (rec.solved && mergedHistory[date].solved && (rec.guessCount < mergedHistory[date].guessCount)) {
                    mergedHistory[date] = rec;
                }
            }

            // Merge stats
            const mergedStats = {
                ...DEFAULT_STATS,
                ...cloudStats,
                played: Math.max(memoryStats.played || 0, cloudStats.played || 0),
                won: Math.max(memoryStats.won || 0, cloudStats.won || 0),
                currentStreak: Math.max(memoryStats.currentStreak || 0, cloudStats.currentStreak || 0),
                maxStreak: Math.max(memoryStats.maxStreak || 0, cloudStats.maxStreak || 0),
                distribution: {
                    '1-3': Math.max(memoryStats.distribution?.['1-3'] || 0, cloudStats.distribution?.['1-3'] || 0),
                    '4-6': Math.max(memoryStats.distribution?.['4-6'] || 0, cloudStats.distribution?.['4-6'] || 0),
                    '7-9': Math.max(memoryStats.distribution?.['7-9'] || 0, cloudStats.distribution?.['7-9'] || 0),
                    '10-12': Math.max(memoryStats.distribution?.['10-12'] || 0, cloudStats.distribution?.['10-12'] || 0),
                    '13-15': Math.max(memoryStats.distribution?.['13-15'] || 0, cloudStats.distribution?.['13-15'] || 0),
                    '16+': Math.max(memoryStats.distribution?.['16+'] || 0, cloudStats.distribution?.['16+'] || 0)
                }
            };

            memoryHistory = mergedHistory;
            memoryStats = sanitizeStats(mergedStats, memoryHistory);

            localStorage.setItem(STATS_KEY, JSON.stringify(memoryStats));
            localStorage.setItem(HISTORY_KEY, JSON.stringify(memoryHistory));
            notifyListeners();

            await syncToCloud();
        } else {
            // First time login
            await syncToCloud();
        }

        // Listen for remote updates
        firestoreUnsubscribe = firestoreFns.onSnapshot(userRef, (docSnap) => {
            if (docSnap.exists()) {
                const updated = docSnap.data();
                if (updated.phylogenle_history) memoryHistory = { ...memoryHistory, ...updated.phylogenle_history };
                if (updated.phylogenle_stats) {
                    memoryStats = sanitizeStats({ ...DEFAULT_STATS, ...updated.phylogenle_stats }, memoryHistory);
                }
                localStorage.setItem(STATS_KEY, JSON.stringify(memoryStats));
                localStorage.setItem(HISTORY_KEY, JSON.stringify(memoryHistory));
                notifyListeners();
            }
        });
    } catch (e) {
        console.warn("Error setting up Firestore storage sync:", e);
    }
});
