/**
 * Phylogenle - Real-Time Cooperative Multiplayer Module (Redactle-Style Co-Op)
 * Enables multiple players to guess together in real-time via shared room links (?room=XYZ-123).
 * Syncs guesses, hints, cladogram visualization, and updates all players' stats upon completion.
 */
import { initFirebase } from './firebase-config.js';
import { getCurrentUser, onAuthChange } from './auth.js';

let firestoreDb = null;
let firestoreFns = null;

// Available animal / nature avatars for players
export const AVATAR_PALETTE = [
    '🦁', '🦊', '🐺', '🐻', '🐼', '🐨',
    '🦅', '🦉', '🐸', '🐢', '🐙', '🐬',
    '🦈', '🦋', '🐝', '🌿', '🍄', '🌵'
];

const DEFAULT_ANIMAL_NAMES = [
    'Clever Fox', 'Curious Otter', 'Wise Owl', 'Brave Lion',
    'Swift Falcon', 'Gentle Panda', 'Mighty Wolf', 'Playful Dolphin',
    'Keen Eagle', 'Silent Leopard', 'Noble Stag', 'Calm Turtle'
];

const PROFILE_KEY = 'phylogenle_coop_profile_v1';
const ACTIVE_ROOM_KEY = 'phylogenle_active_coop_room_v1';

// In-memory state
let currentProfile = loadOrInitProfile();
let activeRoom = null;
let roomUnsubscribe = null;
const eventListeners = new Set();

/**
 * Initialize Firestore connection on http/https
 */
async function ensureFirestore() {
    if (firestoreDb && firestoreFns) return { db: firestoreDb, fns: firestoreFns };
    try {
        const fb = await initFirebase();
        if (fb && fb.db) {
            firestoreDb = fb.db;
            firestoreFns = await import("https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore.js");
            return { db: firestoreDb, fns: firestoreFns };
        }
    } catch (e) {
        console.warn("Firestore not available for co-op mode:", e);
    }
    return null;
}

/**
 * Load or initialize local player profile
 */
function loadOrInitProfile() {
    try {
        const raw = localStorage.getItem(PROFILE_KEY);
        if (raw) {
            const parsed = JSON.parse(raw);
            if (parsed && parsed.id && parsed.name) {
                return parsed;
            }
        }
    } catch (e) {}

    const randomId = 'p_' + Math.random().toString(36).substring(2, 10);
    const randomAvatar = AVATAR_PALETTE[Math.floor(Math.random() * AVATAR_PALETTE.length)];
    const randomName = DEFAULT_ANIMAL_NAMES[Math.floor(Math.random() * DEFAULT_ANIMAL_NAMES.length)];

    const newProfile = {
        id: randomId,
        uid: null,
        name: randomName,
        avatarEmoji: randomAvatar,
        photoUrl: null
    };

    saveProfile(newProfile);
    return newProfile;
}

/**
 * Save profile to localStorage and sync with auth if signed in
 */
export function saveProfile(profile) {
    currentProfile = { ...currentProfile, ...profile };
    try {
        localStorage.setItem(PROFILE_KEY, JSON.stringify(currentProfile));
    } catch (e) {}
    notifySubscribers('PROFILE_CHANGED', currentProfile);
    return currentProfile;
}

export function getMyPlayerProfile() {
    return { ...currentProfile };
}

// Automatically sync profile with Google Auth if user signs in
onAuthChange((user) => {
    if (user) {
        saveProfile({
            uid: user.uid,
            name: user.displayName || currentProfile.name,
            photoUrl: user.photoURL || null
        });
    } else {
        saveProfile({
            uid: null,
            photoUrl: null
        });
    }
});

/**
 * Generate a short, readable 6-character room code (e.g., 'FOX-742' or 'K7M9PQ')
 */
export function generateRoomId() {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    let code = '';
    for (let i = 0; i < 6; i++) {
        code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return code;
}

/**
 * Format shareable invite URL
 */
export function getRoomShareUrl(roomId) {
    if (typeof window === 'undefined') return '';
    const url = new URL(window.location.origin + window.location.pathname);
    url.searchParams.set('room', roomId);
    return url.toString();
}

/**
 * Copy room link to clipboard with multi-fallback
 */
export async function copyRoomLink(roomId) {
    const url = getRoomShareUrl(roomId);
    if (navigator.clipboard && navigator.clipboard.writeText) {
        try {
            await navigator.clipboard.writeText(url);
            return true;
        } catch (e) {}
    }
    // Fallback: create temporary textarea
    try {
        const textArea = document.createElement("textarea");
        textArea.value = url;
        textArea.style.position = "fixed";
        textArea.style.left = "-999999px";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        const success = document.execCommand('copy');
        document.body.removeChild(textArea);
        return success;
    } catch (err) {
        return false;
    }
}

/**
 * Subscribe to co-op state and room events
 */
export function onCoopEvent(callback) {
    eventListeners.add(callback);
    return () => eventListeners.delete(callback);
}

function notifySubscribers(event, data) {
    for (const listener of eventListeners) {
        try {
            listener(event, data);
        } catch (e) {
            console.error("Error in co-op event listener:", e);
        }
    }
}

export function getActiveRoom() {
    return activeRoom;
}

export function isCoopActive() {
    return Boolean(activeRoom && activeRoom.roomId);
}

/**
 * Clean player profile map for Firestore rules conformance
 */
function sanitizePlayerMap(player) {
    if (!player) return null;
    const res = {};
    if (player.uid) res.uid = String(player.uid);
    if (player.name) res.name = String(player.name).slice(0, 100);
    if (player.avatarEmoji) res.avatarEmoji = String(player.avatarEmoji).slice(0, 32);
    if (player.photoUrl) res.photoUrl = String(player.photoUrl).slice(0, 2048);
    return res;
}

/**
 * Create a new Co-op Room (seamlessly promoting the current solo game)
 */
export async function createCoopRoom({ targetSpecies, isUnlimited, dateStr, puzzleNum, existingGuesses = [], existingHints = [] }) {
    const fs = await ensureFirestore();
    if (!fs) {
        throw new Error("Multiplayer requires an active internet connection to connect with Firebase.");
    }

    const { db, fns } = fs;
    const roomId = generateRoomId();
    const myProfile = getMyPlayerProfile();
    const now = Date.now();

    // Map existing guesses and hints to credit the creator
    const formattedGuesses = (existingGuesses || []).map(g => ({
        ...g,
        player: g.player || {
            id: myProfile.id,
            name: myProfile.name,
            avatarEmoji: myProfile.avatarEmoji,
            photoUrl: myProfile.photoUrl || null
        }
    }));

    const formattedHints = (existingHints || []).map(h => ({
        ...h,
        player: h.player || {
            id: myProfile.id,
            name: myProfile.name,
            avatarEmoji: myProfile.avatarEmoji,
            photoUrl: myProfile.photoUrl || null
        }
    }));

    const participantEntry = {
        id: myProfile.id,
        name: myProfile.name,
        avatarEmoji: myProfile.avatarEmoji,
        photoUrl: myProfile.photoUrl || null,
        joinedAt: now,
        lastActive: now
    };

    const roomData = {
        roomId,
        targetSpecies,
        gameMode: isUnlimited ? 'practice' : 'daily',
        createdAt: now,
        updatedAt: now,
        createdBy: sanitizePlayerMap(myProfile),
        status: 'active',
        solved: false,
        guesses: formattedGuesses,
        hints: formattedHints,
        participants: {
            [myProfile.id]: participantEntry
        }
    };

    if (!isUnlimited && dateStr) {
        roomData.dateStr = dateStr;
    }

    const roomRef = fns.doc(db, 'coop_rooms', roomId);
    await fns.setDoc(roomRef, roomData);

    // Save active room locally and set up real-time listener
    activeRoom = roomData;
    try {
        localStorage.setItem(ACTIVE_ROOM_KEY, roomId);
    } catch (e) {}

    // Update URL to include ?room=XYZ without reloading
    updateUrlWithRoom(roomId);

    listenToRoom(roomId);
    notifySubscribers('ROOM_CREATED', roomData);
    return roomData;
}

/**
 * Join an existing Co-op Room
 */
export async function joinCoopRoom(roomId) {
    if (!roomId) throw new Error("Invalid room code");
    roomId = roomId.trim().toUpperCase();

    const fs = await ensureFirestore();
    if (!fs) {
        throw new Error("Multiplayer requires an active internet connection to connect with Firebase.");
    }

    const { db, fns } = fs;
    const roomRef = fns.doc(db, 'coop_rooms', roomId);
    const snap = await fns.getDoc(roomRef);

    if (!snap.exists()) {
        throw new Error(`Room "${roomId}" was not found. Please verify the code or link.`);
    }

    const roomData = snap.data();
    const myProfile = getMyPlayerProfile();
    const now = Date.now();

    // Register current participant
    const updatedParticipants = {
        ...(roomData.participants || {}),
        [myProfile.id]: {
            id: myProfile.id,
            name: myProfile.name,
            avatarEmoji: myProfile.avatarEmoji,
            photoUrl: myProfile.photoUrl || null,
            joinedAt: now,
            lastActive: now
        }
    };

    await fns.updateDoc(roomRef, {
        participants: updatedParticipants,
        updatedAt: now
    });

    roomData.participants = updatedParticipants;
    activeRoom = roomData;
    try {
        localStorage.setItem(ACTIVE_ROOM_KEY, roomId);
    } catch (e) {}

    updateUrlWithRoom(roomId);
    listenToRoom(roomId);
    notifySubscribers('ROOM_JOINED', roomData);
    return roomData;
}

/**
 * Listen to real-time changes on active room
 */
function listenToRoom(roomId) {
    if (roomUnsubscribe) {
        roomUnsubscribe();
        roomUnsubscribe = null;
    }

    ensureFirestore().then(fs => {
        if (!fs) return;
        const { db, fns } = fs;
        const roomRef = fns.doc(db, 'coop_rooms', roomId);

        roomUnsubscribe = fns.onSnapshot(roomRef, (snap) => {
            if (!snap.exists()) {
                leaveCoopRoom({ reason: 'Room closed or deleted' });
                return;
            }
            const incoming = snap.data();
            activeRoom = incoming;
            notifySubscribers('ROOM_UPDATE', incoming);

            if (incoming.solved && incoming.status === 'solved') {
                notifySubscribers('ROOM_SOLVED', incoming);
            }
        }, (err) => {
            console.error("Co-op snapshot error:", err);
        });
    });
}

/**
 * Submit a guess in Co-op mode
 */
export async function submitCoopGuess(guessObj) {
    if (!activeRoom || !activeRoom.roomId) return false;
    const fs = await ensureFirestore();
    if (!fs) return false;

    const { db, fns } = fs;
    const myProfile = getMyPlayerProfile();
    const now = Date.now();

    const taggedGuess = {
        ...guessObj,
        timestamp: now,
        player: {
            id: myProfile.id,
            name: myProfile.name,
            avatarEmoji: myProfile.avatarEmoji,
            photoUrl: myProfile.photoUrl || null
        }
    };

    const roomRef = fns.doc(db, 'coop_rooms', activeRoom.roomId);

    // Fetch latest room doc to prevent race condition when appending
    const snap = await fns.getDoc(roomRef);
    if (!snap.exists()) return false;

    const currentRoom = snap.data();
    const updatedGuesses = [...(currentRoom.guesses || []), taggedGuess];

    const updates = {
        guesses: updatedGuesses,
        updatedAt: now
    };

    if (guessObj.isMatch) {
        updates.status = 'solved';
        updates.solved = true;
        updates.winner = sanitizePlayerMap(myProfile);
    }

    await fns.updateDoc(roomRef, updates);
    return taggedGuess;
}

/**
 * Submit a hint in Co-op mode
 */
export async function submitCoopHint(hintObj) {
    if (!activeRoom || !activeRoom.roomId) return false;
    const fs = await ensureFirestore();
    if (!fs) return false;

    const { db, fns } = fs;
    const myProfile = getMyPlayerProfile();
    const now = Date.now();

    const taggedHint = {
        ...hintObj,
        timestamp: now,
        player: {
            id: myProfile.id,
            name: myProfile.name,
            avatarEmoji: myProfile.avatarEmoji,
            photoUrl: myProfile.photoUrl || null
        }
    };

    const roomRef = fns.doc(db, 'coop_rooms', activeRoom.roomId);
    const snap = await fns.getDoc(roomRef);
    if (!snap.exists()) return false;

    const currentRoom = snap.data();
    const updatedHints = [...(currentRoom.hints || []), taggedHint];

    await fns.updateDoc(roomRef, {
        hints: updatedHints,
        updatedAt: now
    });

    return taggedHint;
}

/**
 * Leave the current Co-op room and return to solo mode
 */
export function leaveCoopRoom({ reason = null } = {}) {
    if (roomUnsubscribe) {
        roomUnsubscribe();
        roomUnsubscribe = null;
    }

    const previousRoom = activeRoom;
    activeRoom = null;
    try {
        localStorage.removeItem(ACTIVE_ROOM_KEY);
    } catch (e) {}

    // Remove room param from URL
    if (typeof window !== 'undefined' && window.location) {
        const url = new URL(window.location);
        url.searchParams.delete('room');
        url.searchParams.delete('coop');
        window.history.replaceState(null, '', url.pathname + (url.search ? url.search : ''));
    }

    notifySubscribers('ROOM_LEFT', { previousRoom, reason });
}

function updateUrlWithRoom(roomId) {
    if (typeof window !== 'undefined' && window.location) {
        const url = new URL(window.location);
        url.searchParams.set('room', roomId);
        window.history.replaceState(null, '', url.pathname + url.search);
    }
}

