/**
 * Phylogenle - Deterministic PRNG & Date Arithmetic Module
 * Uses Mulberry32 algorithm seeded by daily date hash.
 */

// Epoch for Puzzle #1: Jan 1, 2024
export const EPOCH_DATE_STR = '2024-01-01';

/**
 * 32-bit integer string hash (MurmurHash-inspired)
 */
export function hashString(str) {
    let h = 2166136261 >>> 0;
    for (let i = 0; i < str.length; i++) {
        h ^= str.charCodeAt(i);
        h = Math.imul(h, 16777619);
    }
    return h >>> 0;
}

/**
 * Mulberry32 PRNG generator
 * Returns a function that produces deterministic pseudo-random floats in [0, 1).
 */
export function createMulberry32(seed) {
    let s = seed >>> 0;
    return function() {
        s = (s + 0x6D2B79F5) >>> 0;
        let t = Math.imul(s ^ (s >>> 15), 1 | s);
        t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
}

/**
 * Format Date object to YYYY-MM-DD
 */
export function formatDate(date) {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
}

/**
 * Parse YYYY-MM-DD to Date object at local midnight
 */
export function parseDate(dateStr) {
    const [y, m, d] = dateStr.split('-').map(Number);
    return new Date(y, m - 1, d, 0, 0, 0, 0);
}

/**
 * Get Puzzle Number from date string (1-indexed from epoch)
 */
export function getPuzzleNumber(dateStr, epochStr = EPOCH_DATE_STR) {
    const [y1, m1, d1] = dateStr.split('-').map(Number);
    const [y2, m2, d2] = epochStr.split('-').map(Number);
    const utc1 = Date.UTC(y1, m1 - 1, d1);
    const utc2 = Date.UTC(y2, m2 - 1, d2);
    return Math.max(1, Math.round((utc1 - utc2) / (1000 * 60 * 60 * 24)) + 1);
}

/**
 * Get date string for a given Puzzle Number
 */
export function getDateForPuzzleNumber(puzzleNum, epochStr = EPOCH_DATE_STR) {
    const [y2, m2, d2] = epochStr.split('-').map(Number);
    const d = new Date(Date.UTC(y2, m2 - 1, d2 + (puzzleNum - 1)));
    const y = d.getUTCFullYear();
    const m = String(d.getUTCMonth() + 1).padStart(2, '0');
    const day = String(d.getUTCDate()).padStart(2, '0');
    return `${y}-${m}-${day}`;
}

/**
 * Get Today's YYYY-MM-DD string
 */
export function getTodayDateStr() {
    return formatDate(new Date());
}

/**
 * Pick a deterministic target species for a specific date
 */
export function getDailyTargetSpecies(allSpecies, dateStr) {
    if (!allSpecies || allSpecies.length === 0) return null;
    // Pinned target for daily puzzle continuity
    if (dateStr === '2026-10-23') {
        const pinned = allSpecies.find(s => s.toLowerCase() === 'california ground squirrel (otospermophilus beecheyi)');
        if (pinned) return pinned;
    }
    if (dateStr === '2026-10-26') {
        const pinned = allSpecies.find(s => s.toLowerCase() === 'orangespine unicornfish (naso lituratus)');
        if (pinned) return pinned;
    }
    const seedVal = hashString(`phylogenle-daily-${dateStr}`);
    const rng = createMulberry32(seedVal);
    const index = Math.floor(rng() * allSpecies.length);
    return allSpecies[index];
}

/**
 * Extract all clean, human-readable aliases for a canonical species.
 * E.g., for "Puma (Puma concolor)", returns ["Catamount", "Cougar", "Florida Panther", "Mountain Lion", "Panther"].
 */
export function getAliasesForSpecies(canonicalSpecies, aliasesDict) {
    if (!aliasesDict || !canonicalSpecies) return [];
    const targetLower = canonicalSpecies.toLowerCase();
    const latinMatch = canonicalSpecies.match(/\((.*?)\)/);
    const targetLatin = latinMatch ? latinMatch[1].toLowerCase() : "";
    const primaryCommon = canonicalSpecies.split(" (")[0].trim().toLowerCase();

    const matches = new Set();
    for (const [alias, canonical] of Object.entries(aliasesDict)) {
        if (alias.includes("(") || alias.includes(")")) continue;
        const canLower = canonical.toLowerCase();
        const canLatinMatch = canonical.match(/\((.*?)\)/);
        const canLatin = canLatinMatch ? canLatinMatch[1].toLowerCase() : "";
        
        if (canLower === targetLower || (targetLatin && canLatin === targetLatin)) {
            const aliasClean = alias.trim();
            if (aliasClean.toLowerCase() !== primaryCommon && aliasClean.toLowerCase() !== targetLatin) {
                const titleCased = aliasClean.split(" ")
                    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
                    .join(" ");
                matches.add(titleCased);
            }
        }
    }
    return Array.from(matches).sort();
}

/**
 * Deterministically select a presentation name (either the canonical common name or one of its recognized aliases)
 * for a daily or practice round.
 * Guarantees 100% multiplayer parity worldwide on any given puzzle date while adding rich variety.
 */
export function getTargetPresentationName(canonicalSpecies, aliasesDict, seedKey) {
    if (!canonicalSpecies) return "";
    const primaryCommon = canonicalSpecies.split(" (")[0].trim();
    const aliases = getAliasesForSpecies(canonicalSpecies, aliasesDict);
    if (!aliases || aliases.length === 0) return primaryCommon;

    const availableNames = [primaryCommon, ...aliases];
    const seedVal = hashString(`phylogenle-alias-${seedKey}-${canonicalSpecies}`);
    const rng = createMulberry32(seedVal);
    const index = Math.floor(rng() * availableNames.length);
    return availableNames[index];
}

