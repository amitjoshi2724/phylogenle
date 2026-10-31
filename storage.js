/**
 * Phylogenle - Dual-Layer Storage Module
 * LocalStorage offline-first with real-time Firestore synchronization.
 * Persists and syncs all completed Daily/Archive games, Practice games, and Unfinished games
 * to each user's account so they can review their complete game history across devices.
 */
import { initFirebase } from './firebase-config.js';
import { onAuthChange, getCurrentUser } from './auth.js';
import { getPuzzleNumber } from './prng.js';

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
const PRACTICE_HISTORY_KEY = 'phylogenle_practice_history_v1';
const ACTIVE_GAMES_KEY = 'phylogenle_active_games_v1';
const ACTIVE_PREFIX = 'phylogenle_active_state_v1_';
const HINTS_PREFIX = 'phylogenle_active_hints_v1_';

const DEFAULT_STATS = {
    played: 0,
    won: 0,
    currentStreak: 0,
    maxStreak: 0,
    meanGuesses: 0,
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
 * Compute current and max streaks from sorted daily history ledger
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
 * Sanitize and heal stats against daily + practice history records
 */
function sanitizeStats(stats, history, practiceHistory = {}) {
    const cleanStats = { ...DEFAULT_STATS, ...(stats || {}) };
    cleanStats.distribution = { ...DEFAULT_STATS.distribution, ...(cleanStats.distribution || {}) };

    const dailyEntries = Object.values(history || {}).filter(r => r && r.completed);
    const practiceEntries = Object.values(practiceHistory || {}).filter(r => r && r.completed);
    const allCompleted = [...dailyEntries, ...practiceEntries];

    if (allCompleted.length > 0) {
        const histDist = {
            '1-3': 0,
            '4-6': 0,
            '7-9': 0,
            '10-12': 0,
            '13-15': 0,
            '16+': 0
        };
        let histWon = 0;
        let totalGuessCountAll = 0;

        for (const rec of allCompleted) {
            const gc = Number(rec.guessCount) || (Array.isArray(rec.guesses) ? rec.guesses.length : 1);
            totalGuessCountAll += gc;
            if (rec.solved) {
                histWon++;
                const bucket = getBucketKey(gc);
                histDist[bucket] = (histDist[bucket] || 0) + 1;
            }
        }

        cleanStats.meanGuesses = Number((totalGuessCountAll / allCompleted.length).toFixed(1));

        const distSum = Object.values(cleanStats.distribution).reduce((a, b) => a + (Number(b) || 0), 0);
        const isCorrupt = distSum > allCompleted.length || distSum !== histWon || cleanStats.played < allCompleted.length;

        if (isCorrupt) {
            cleanStats.distribution = histDist;
            cleanStats.played = allCompleted.length;
            cleanStats.won = histWon;
        }
        const { currentStreak, maxStreak } = computeStreaksFromHistory(history);
        cleanStats.currentStreak = currentStreak;
        cleanStats.maxStreak = Math.max(cleanStats.maxStreak || 0, maxStreak);
    } else {
        cleanStats.meanGuesses = 0;
    }
    return cleanStats;
}

let memoryHistory = loadLocalHistory();
let memoryPracticeHistory = loadLocalPracticeHistory();
let memoryActiveGames = loadLocalActiveGames();
let memoryStats = sanitizeStats(loadLocalStats(), memoryHistory, memoryPracticeHistory);
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

function loadLocalPracticeHistory() {
    try {
        const raw = localStorage.getItem(PRACTICE_HISTORY_KEY);
        if (raw) return JSON.parse(raw);
    } catch (e) {
        console.error("Failed to parse local practice history:", e);
    }
    return {};
}

function loadLocalActiveGames() {
    const activeMap = {};
    try {
        const raw = localStorage.getItem(ACTIVE_GAMES_KEY);
        if (raw) {
            Object.assign(activeMap, JSON.parse(raw));
        }
        // Also scan legacy per-date active keys in localStorage
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith(ACTIVE_PREFIX)) {
                const dateStr = key.slice(ACTIVE_PREFIX.length);
                const rawState = localStorage.getItem(key);
                if (!rawState) continue;
                const parsed = JSON.parse(rawState);
                const guesses = Array.isArray(parsed) ? parsed : (parsed.guesses || []);
                const targetSpecies = Array.isArray(parsed) ? null : (parsed.targetSpecies || null);
                const hintsRaw = localStorage.getItem(HINTS_PREFIX + dateStr);
                const hints = hintsRaw ? JSON.parse(hintsRaw) : [];
                if (guesses.length > 0 || hints.length > 0) {
                    activeMap[dateStr] = {
                        id: `active_${dateStr}`,
                        mode: 'daily',
                        dateStr,
                        puzzleNum: getPuzzleNumber(dateStr),
                        targetSpecies,
                        guesses,
                        hints,
                        guessCount: guesses.length,
                        solved: false,
                        completed: false,
                        timestamp: activeMap[dateStr]?.timestamp || Date.now()
                    };
                }
            }
        }
    } catch (e) { }
    return activeMap;
}

function persistActiveGamesMap() {
    try {
        localStorage.setItem(ACTIVE_GAMES_KEY, JSON.stringify(memoryActiveGames));
    } catch (e) { }
}

export function saveLocalStats(stats) {
    memoryStats = sanitizeStats(stats, memoryHistory, memoryPracticeHistory);
    try {
        localStorage.setItem(STATS_KEY, JSON.stringify(memoryStats));
    } catch (e) {
        console.error("Failed to save local stats:", e);
    }
    syncToCloud();
    notifyListeners();
}

/**
 * Record Daily / Archive puzzle completion (win or give up)
 */
export function recordDailyCompletion(dateStr, puzzleNum, solved, guessCount, guesses, targetSpecies, hints = []) {
    const record = {
        id: `daily_${dateStr}`,
        mode: 'daily',
        dateStr,
        playedDateStr: new Date().toISOString().slice(0, 10),
        puzzleNum: puzzleNum || getPuzzleNumber(dateStr),
        solved: Boolean(solved),
        guessCount: Number(guessCount) || (guesses ? guesses.length : 1),
        targetSpecies,
        guesses: Array.isArray(guesses) ? [...guesses] : [],
        hints: Array.isArray(hints) ? [...hints] : [],
        completed: true,
        timestamp: Date.now()
    };

    memoryHistory[dateStr] = record;
    try {
        localStorage.setItem(HISTORY_KEY, JSON.stringify(memoryHistory));
    } catch (e) {
        console.error("Failed to save history locally:", e);
    }

    clearActiveGuesses(dateStr);
    const stats = sanitizeStats(memoryStats, memoryHistory, memoryPracticeHistory);
    stats.lastPlayedDate = dateStr;
    saveLocalStats(stats);
}

/**
 * Record Practice / Unlimited game completion so every game is remembered in the user's account
 */
export function recordPracticeCompletion(solved, guessCount, guesses, targetSpecies, hints = []) {
    const now = Date.now();
    const todayStr = new Date(now).toISOString().slice(0, 10);
    const id = `practice_${now}`;
    const record = {
        id,
        mode: 'practice',
        dateStr: todayStr,
        playedDateStr: todayStr,
        puzzleNum: null,
        solved: Boolean(solved),
        guessCount: Number(guessCount) || (guesses ? guesses.length : 1),
        targetSpecies,
        guesses: Array.isArray(guesses) ? [...guesses] : [],
        hints: Array.isArray(hints) ? [...hints] : [],
        completed: true,
        timestamp: now
    };

    memoryPracticeHistory[id] = record;
    try {
        localStorage.setItem(PRACTICE_HISTORY_KEY, JSON.stringify(memoryPracticeHistory));
    } catch (e) {
        console.error("Failed to save practice history locally:", e);
    }

    const stats = sanitizeStats(memoryStats, memoryHistory, memoryPracticeHistory);
    saveLocalStats(stats);
}

/**
 * Save in-progress guesses and lock round's target species (also synced to account)
 */
export function saveActiveGuesses(dateStr, guesses, targetSpecies) {
    try {
        const cleanGuesses = Array.isArray(guesses) ? guesses : [];
        const payload = {
            targetSpecies: targetSpecies || null,
            guesses: cleanGuesses
        };
        localStorage.setItem(ACTIVE_PREFIX + dateStr, JSON.stringify(payload));

        if (!memoryHistory[dateStr] && cleanGuesses.length > 0) {
            const existing = memoryActiveGames[dateStr] || {};
            memoryActiveGames[dateStr] = {
                id: `active_${dateStr}`,
                mode: 'daily',
                dateStr,
                puzzleNum: getPuzzleNumber(dateStr),
                targetSpecies: targetSpecies || existing.targetSpecies || null,
                guesses: cleanGuesses,
                hints: existing.hints || loadActiveHints(dateStr) || [],
                guessCount: cleanGuesses.length,
                solved: false,
                completed: false,
                timestamp: Date.now()
            };
            persistActiveGamesMap();
            syncToCloud();
            notifyListeners();
        }
    } catch (e) { }
}

export function loadActiveGuesses(dateStr) {
    try {
        const raw = localStorage.getItem(ACTIVE_PREFIX + dateStr);
        if (raw) {
            const parsed = JSON.parse(raw);
            if (Array.isArray(parsed)) {
                return { targetSpecies: null, guesses: parsed };
            }
            return parsed;
        }
        if (memoryActiveGames[dateStr] && Array.isArray(memoryActiveGames[dateStr].guesses)) {
            return {
                targetSpecies: memoryActiveGames[dateStr].targetSpecies || null,
                guesses: memoryActiveGames[dateStr].guesses
            };
        }
    } catch (e) { }
    return null;
}

export function clearActiveGuesses(dateStr) {
    try {
        localStorage.removeItem(ACTIVE_PREFIX + dateStr);
        localStorage.removeItem(HINTS_PREFIX + dateStr);
        if (memoryActiveGames[dateStr]) {
            delete memoryActiveGames[dateStr];
            persistActiveGamesMap();
        }
    } catch (e) { }
}

/**
 * Save in-progress hints
 */
export function saveActiveHints(dateStr, hints) {
    try {
        const cleanHints = Array.isArray(hints) ? hints : [];
        localStorage.setItem(HINTS_PREFIX + dateStr, JSON.stringify(cleanHints));
        if (!memoryHistory[dateStr] && (cleanHints.length > 0 || memoryActiveGames[dateStr])) {
            const existing = memoryActiveGames[dateStr] || {};
            const activeGuessesObj = loadActiveGuesses(dateStr);
            const guesses = existing.guesses || (activeGuessesObj ? activeGuessesObj.guesses : []);
            memoryActiveGames[dateStr] = {
                id: `active_${dateStr}`,
                mode: 'daily',
                dateStr,
                puzzleNum: getPuzzleNumber(dateStr),
                targetSpecies: existing.targetSpecies || (activeGuessesObj ? activeGuessesObj.targetSpecies : null),
                guesses,
                hints: cleanHints,
                guessCount: guesses.length,
                solved: false,
                completed: false,
                timestamp: Date.now()
            };
            persistActiveGamesMap();
            syncToCloud();
            notifyListeners();
        }
    } catch (e) { }
}

export function loadActiveHints(dateStr) {
    try {
        const raw = localStorage.getItem(HINTS_PREFIX + dateStr);
        if (raw) return JSON.parse(raw);
        if (memoryActiveGames[dateStr] && Array.isArray(memoryActiveGames[dateStr].hints)) {
            return memoryActiveGames[dateStr].hints;
        }
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

    const stats = sanitizeStats({ ...DEFAULT_STATS }, memoryHistory, memoryPracticeHistory);
    saveLocalStats(stats);
    notifyListeners();
}

/**
 * Reset all puzzle history and active guesses across the archive
 */
export function resetAllHistory() {
    memoryHistory = {};
    memoryPracticeHistory = {};
    memoryActiveGames = {};
    try {
        localStorage.removeItem(HISTORY_KEY);
        localStorage.removeItem(PRACTICE_HISTORY_KEY);
        localStorage.removeItem(ACTIVE_GAMES_KEY);
    } catch (e) { }

    try {
        const keysToRemove = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && (key.startsWith(ACTIVE_PREFIX) || key.startsWith(HINTS_PREFIX))) {
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
    return sanitizeStats(memoryStats, memoryHistory, memoryPracticeHistory);
}

export function getHistory() {
    return { ...memoryHistory };
}

export function getPracticeHistory() {
    return { ...memoryPracticeHistory };
}

export function getActiveGames() {
    return { ...memoryActiveGames };
}

/**
 * Return a unified, chronological array of all games played by the user
 * (Daily/Archive completed games, Practice completed games, and optionally Unfinished games).
 */
export function getAllGamesLedger({ includeUnfinished = false } = {}) {
    const entries = [];

    for (const [dateStr, rec] of Object.entries(memoryHistory || {})) {
        if (!rec) continue;
        entries.push({
            ...rec,
            id: rec.id || `daily_${dateStr}`,
            mode: rec.mode || 'daily',
            dateStr: rec.dateStr || dateStr,
            puzzleNum: rec.puzzleNum || getPuzzleNumber(dateStr),
            completed: true
        });
    }

    for (const [id, rec] of Object.entries(memoryPracticeHistory || {})) {
        if (!rec) continue;
        entries.push({
            ...rec,
            id: rec.id || id,
            mode: 'practice',
            completed: true
        });
    }

    if (includeUnfinished) {
        const latestActive = loadLocalActiveGames();
        Object.assign(memoryActiveGames, latestActive);
        for (const [dateStr, rec] of Object.entries(memoryActiveGames || {})) {
            if (!rec || memoryHistory[dateStr]) continue;
            const gCount = Array.isArray(rec.guesses) ? rec.guesses.length : (rec.guessCount || 0);
            const hCount = Array.isArray(rec.hints) ? rec.hints.length : 0;
            if (gCount === 0 && hCount === 0) continue;
            entries.push({
                ...rec,
                id: rec.id || `active_${dateStr}`,
                mode: 'daily',
                dateStr,
                puzzleNum: rec.puzzleNum || getPuzzleNumber(dateStr),
                guessCount: gCount,
                solved: false,
                completed: false
            });
        }
    }

    // Sort most recent first (by timestamp if available, then by dateStr descending)
    entries.sort((a, b) => {
        const dA = a.dateStr || '';
        const dB = b.dateStr || '';
        if (dA !== dB) return dB.localeCompare(dA);
        return (b.timestamp || 0) - (a.timestamp || 0);
    });

    return entries;
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
        try {
            cb({
                stats: memoryStats,
                history: memoryHistory,
                practiceHistory: memoryPracticeHistory,
                activeGames: memoryActiveGames
            });
        } catch (e) { }
    });
}

/**
 * Sync local state (stats, daily history, practice history, and unfinished games) to Firestore
 */
async function syncToCloud() {
    const user = getCurrentUser();
    if (!user || !firestoreDb || !firestoreFns) return;

    try {
        const userRef = firestoreFns.doc(firestoreDb, 'users', user.uid);
        const cleanStats = sanitizeStats(memoryStats, memoryHistory, memoryPracticeHistory);
        await firestoreFns.setDoc(userRef, {
            phylogenle_stats: cleanStats,
            phylogenle_history: memoryHistory,
            phylogenle_practice_history: memoryPracticeHistory,
            phylogenle_active_games: memoryActiveGames,
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
            const cloudPractice = cloudData.phylogenle_practice_history || {};
            const cloudActive = cloudData.phylogenle_active_games || {};

            // 1. Merge daily history: union of dates, prefer solved and lower guess count, preserve guesses/hints
            const mergedHistory = { ...memoryHistory };
            for (const [date, rec] of Object.entries(cloudHistory)) {
                if (!mergedHistory[date]) {
                    mergedHistory[date] = rec;
                } else {
                    const local = mergedHistory[date];
                    if (rec.solved && !local.solved) {
                        mergedHistory[date] = rec;
                    } else if (rec.solved && local.solved && (rec.guessCount < local.guessCount)) {
                        mergedHistory[date] = rec;
                    } else if ((!local.guesses || local.guesses.length === 0) && Array.isArray(rec.guesses) && rec.guesses.length > 0) {
                        mergedHistory[date] = { ...local, guesses: rec.guesses, hints: rec.hints || local.hints || [] };
                    }
                }
            }

            // 2. Merge practice history: union by practice game ID
            const mergedPractice = { ...memoryPracticeHistory, ...cloudPractice };

            // 3. Merge active (unfinished) games: exclude any date already completed in mergedHistory
            const mergedActive = { ...memoryActiveGames };
            for (const [date, rec] of Object.entries(cloudActive)) {
                if (mergedHistory[date]) continue;
                const localAct = mergedActive[date];
                const cloudG = Array.isArray(rec?.guesses) ? rec.guesses.length : 0;
                const localG = Array.isArray(localAct?.guesses) ? localAct.guesses.length : 0;
                if (!localAct || cloudG > localG) {
                    mergedActive[date] = rec;
                    if (Array.isArray(rec.guesses) && rec.guesses.length > 0) {
                        localStorage.setItem(ACTIVE_PREFIX + date, JSON.stringify({
                            targetSpecies: rec.targetSpecies || null,
                            guesses: rec.guesses
                        }));
                    }
                    if (Array.isArray(rec.hints) && rec.hints.length > 0) {
                        localStorage.setItem(HINTS_PREFIX + date, JSON.stringify(rec.hints));
                    }
                }
            }
            for (const date of Object.keys(mergedActive)) {
                if (mergedHistory[date]) {
                    delete mergedActive[date];
                }
            }

            memoryHistory = mergedHistory;
            memoryPracticeHistory = mergedPractice;
            memoryActiveGames = mergedActive;
            memoryStats = sanitizeStats({ ...DEFAULT_STATS, ...cloudStats }, memoryHistory, memoryPracticeHistory);

            localStorage.setItem(STATS_KEY, JSON.stringify(memoryStats));
            localStorage.setItem(HISTORY_KEY, JSON.stringify(memoryHistory));
            localStorage.setItem(PRACTICE_HISTORY_KEY, JSON.stringify(memoryPracticeHistory));
            persistActiveGamesMap();
            notifyListeners();

            await syncToCloud();
        } else {
            await syncToCloud();
        }

        // Listen for real-time remote updates across tabs/devices
        firestoreUnsubscribe = firestoreFns.onSnapshot(userRef, (docSnap) => {
            if (docSnap.exists()) {
                const updated = docSnap.data();
                if (updated.phylogenle_history) {
                    memoryHistory = { ...memoryHistory, ...updated.phylogenle_history };
                }
                if (updated.phylogenle_practice_history) {
                    memoryPracticeHistory = { ...memoryPracticeHistory, ...updated.phylogenle_practice_history };
                }
                if (updated.phylogenle_active_games) {
                    for (const [d, rec] of Object.entries(updated.phylogenle_active_games)) {
                        if (!memoryHistory[d]) {
                            memoryActiveGames[d] = rec;
                        }
                    }
                }
                memoryStats = sanitizeStats(
                    { ...DEFAULT_STATS, ...(updated.phylogenle_stats || {}) },
                    memoryHistory,
                    memoryPracticeHistory
                );
                localStorage.setItem(STATS_KEY, JSON.stringify(memoryStats));
                localStorage.setItem(HISTORY_KEY, JSON.stringify(memoryHistory));
                localStorage.setItem(PRACTICE_HISTORY_KEY, JSON.stringify(memoryPracticeHistory));
                persistActiveGamesMap();
                notifyListeners();
            }
        });
    } catch (e) {
        console.warn("Error setting up Firestore storage sync:", e);
    }
});
