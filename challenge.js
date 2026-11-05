/**
 * Phylogenle - Custom Puzzle Generator ("Challenge a Friend") Module
 * Enables players to select any organism from the master catalog (or paste a Wikipedia URL)
 * and generate an encrypted, shareable challenge link (?challenge=c1_...).
 */

const SECRET_KEY_HASH = 0x85ebca6b; // Keystream mixing constant

/**
 * Convert string to UTF-8 Uint8Array
 */
function strToUtf8Bytes(str) {
    if (typeof TextEncoder !== 'undefined') {
        return new TextEncoder().encode(str);
    }
    const unescaped = unescape(encodeURIComponent(str));
    const bytes = new Uint8Array(unescaped.length);
    for (let i = 0; i < unescaped.length; i++) {
        bytes[i] = unescaped.charCodeAt(i);
    }
    return bytes;
}

/**
 * Convert UTF-8 Uint8Array to string
 */
function utf8BytesToStr(bytes) {
    if (typeof TextDecoder !== 'undefined') {
        return new TextDecoder().decode(bytes);
    }
    let binary = '';
    for (let i = 0; i < bytes.length; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return decodeURIComponent(escape(binary));
}

/**
 * Deterministic PRNG keystream generator from 32-bit salt
 */
function createKeystream(salt, length) {
    let s = ((salt ^ SECRET_KEY_HASH) >>> 0);
    const stream = new Uint8Array(length);
    for (let i = 0; i < length; i++) {
        s = (s + 0x6D2B79F5) >>> 0;
        let t = Math.imul(s ^ (s >>> 15), 1 | s);
        t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
        stream[i] = ((t ^ (t >>> 14)) >>> 0) & 0xFF;
    }
    return stream;
}

/**
 * Convert bytes to URL-safe Base64 string
 */
function bytesToBase64Url(bytes) {
    let binary = '';
    for (let i = 0; i < bytes.length; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    const base64 = btoa(binary);
    return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

/**
 * Convert URL-safe Base64 string to bytes
 */
function base64UrlToBytes(str) {
    let base64 = str.replace(/-/g, '+').replace(/_/g, '/');
    while (base64.length % 4) {
        base64 += '=';
    }
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }
    return bytes;
}

/**
 * Encode challenge payload into an obfuscated, URL-safe token.
 * A 4-byte random salt is prepended so identical organisms produce completely distinct links.
 */
export function encodeChallengePayload({ target, creator = '', message = '' }) {
    if (!target) throw new Error("Target organism is required.");

    const payload = {
        t: target.trim(),
        c: (creator || '').trim().slice(0, 50),
        m: (message || '').trim().slice(0, 150),
        v: 1
    };

    const payloadBytes = strToUtf8Bytes(JSON.stringify(payload));
    const salt = (Math.floor(Math.random() * 0xFFFFFFFF) >>> 0);

    const encrypted = new Uint8Array(4 + payloadBytes.length);
    encrypted[0] = (salt >>> 24) & 0xFF;
    encrypted[1] = (salt >>> 16) & 0xFF;
    encrypted[2] = (salt >>> 8) & 0xFF;
    encrypted[3] = salt & 0xFF;

    const keystream = createKeystream(salt, payloadBytes.length);
    for (let i = 0; i < payloadBytes.length; i++) {
        encrypted[4 + i] = payloadBytes[i] ^ keystream[i];
    }

    return 'c1_' + bytesToBase64Url(encrypted);
}

/**
 * Decode challenge payload from URL token.
 * Returns { target, creator, message, isValid: true } or { isValid: false, error: '...' }
 */
export function decodeChallengePayload(encodedToken) {
    if (!encodedToken || typeof encodedToken !== 'string') {
        return { isValid: false, error: "Empty challenge token." };
    }

    const token = encodedToken.trim();
    if (!token.startsWith('c1_')) {
        return { isValid: false, error: "Invalid challenge version." };
    }

    try {
        const rawBase64 = token.slice(3);
        const bytes = base64UrlToBytes(rawBase64);
        if (bytes.length < 5) {
            return { isValid: false, error: "Malformed challenge data." };
        }

        const salt = ((bytes[0] << 24) | (bytes[1] << 16) | (bytes[2] << 8) | bytes[3]) >>> 0;
        const cipherLen = bytes.length - 4;
        const keystream = createKeystream(salt, cipherLen);

        const decrypted = new Uint8Array(cipherLen);
        for (let i = 0; i < cipherLen; i++) {
            decrypted[i] = bytes[4 + i] ^ keystream[i];
        }

        const jsonStr = utf8BytesToStr(decrypted);
        const parsed = JSON.parse(jsonStr);

        if (!parsed || !parsed.t) {
            return { isValid: false, error: "Missing challenge target." };
        }

        return {
            target: parsed.t,
            creator: parsed.c || '',
            message: parsed.m || '',
            version: parsed.v || 1,
            isValid: true
        };
    } catch (err) {
        return { isValid: false, error: "Could not decrypt challenge: " + err.message };
    }
}

/**
 * Extract an organism name from a Wikipedia URL or raw search query,
 * and match it against the catalog or aliases.
 */
export function resolveWikipediaUrlOrQuery(input, allSpecies = [], speciesAliases = {}, phylogenyTree = null) {
    if (!input || typeof input !== 'string') return null;
    let query = input.trim();

    // 1. Detect Wikipedia URLs (desktop or mobile)
    if (query.includes('wikipedia.org/wiki/')) {
        try {
            const parts = query.split('/wiki/');
            if (parts.length > 1) {
                query = parts[1].split('?')[0].split('#')[0];
                query = decodeURIComponent(query).replace(/_/g, ' ').trim();
            }
        } catch (e) {}
    } else if (query.startsWith('http://') || query.startsWith('https://')) {
        try {
            const parsedUrl = new URL(query);
            const pathParts = parsedUrl.pathname.split('/').filter(Boolean);
            if (pathParts.length > 0) {
                query = decodeURIComponent(pathParts[pathParts.length - 1]).replace(/_/g, ' ').trim();
            }
        } catch (e) {}
    }

    if (!query) return null;
    const cleanLower = query.toLowerCase();

    // 2. Exact match in allSpecies
    const exact = allSpecies.find(s => s.toLowerCase() === cleanLower);
    if (exact) return exact;

    // 3. Match common name or scientific name in allSpecies
    const byName = allSpecies.find(s => {
        const common = s.split(' (')[0].toLowerCase();
        const latinMatch = s.match(/\((.*?)\)/);
        const latin = latinMatch ? latinMatch[1].toLowerCase() : '';
        return common === cleanLower || latin === cleanLower;
    });
    if (byName) return byName;

    // 4. Match in speciesAliases
    if (speciesAliases && speciesAliases[cleanLower]) {
        const canonical = speciesAliases[cleanLower];
        const canonicalMatch = allSpecies.find(s => s.toLowerCase() === canonical.toLowerCase());
        if (canonicalMatch) return canonicalMatch;
    }

    // 5. Match against phylogenyTree node wiki_title or node name
    if (phylogenyTree && phylogenyTree.nodes) {
        for (const node of Object.values(phylogenyTree.nodes)) {
            if (!node || !node.name) continue;
            const nodeName = node.name.toLowerCase();
            const nodeWiki = (node.wiki_title || '').toLowerCase();
            if (nodeName === cleanLower || (nodeWiki && nodeWiki === cleanLower.replace(/ /g, '_'))) {
                // Find first representative species under this clade/genus
                const cladeMatch = allSpecies.find(s => s.toLowerCase().includes(`(${node.name.toLowerCase()}`));
                if (cladeMatch) return cladeMatch;
            }
        }
    }

    // 6. Substring prefix fallback in allSpecies
    const prefixMatch = allSpecies.find(s => {
        const common = s.split(' (')[0].toLowerCase();
        return common.startsWith(cleanLower) || s.toLowerCase().startsWith(cleanLower);
    });
    if (prefixMatch) return prefixMatch;

    return null;
}

/**
 * Format shareable challenge link URL
 */
export function getChallengeShareUrl(encodedCode) {
    if (typeof window === 'undefined') return `?challenge=${encodedCode}`;
    const url = new URL(window.location.origin + window.location.pathname);
    url.searchParams.set('challenge', encodedCode);
    return url.toString();
}

/**
 * Copy challenge link to clipboard
 */
export async function copyChallengeLink(url) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        try {
            await navigator.clipboard.writeText(url);
            return true;
        } catch (e) {}
    }
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
