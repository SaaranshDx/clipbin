const ENCRYPTION_VERSION = 1;
const PBKDF2_ITERATIONS = 250000;

function isEncryptedPaste(payload) {
    try {
        const encrypted = JSON.parse(payload);
        return encrypted.version === ENCRYPTION_VERSION &&
            encrypted.algorithm === 'AES-GCM' &&
            encrypted.kdf === 'PBKDF2-SHA-256';
    } catch {
        return false;
    }
}

function bytesToBase64(bytes) {
    let binary = '';
    bytes.forEach((byte) => { binary += String.fromCharCode(byte); });
    return btoa(binary);
}

function base64ToBytes(value) {
    const binary = atob(value);
    return Uint8Array.from(binary, (character) => character.charCodeAt(0));
}

async function deriveEncryptionKey(passphrase, salt) {
    const passphraseKey = await crypto.subtle.importKey(
        'raw',
        new TextEncoder().encode(passphrase),
        'PBKDF2',
        false,
        ['deriveKey']
    );

    return crypto.subtle.deriveKey(
        {
            name: 'PBKDF2',
            salt,
            iterations: PBKDF2_ITERATIONS,
            hash: 'SHA-256'
        },
        passphraseKey,
        { name: 'AES-GCM', length: 256 },
        false,
        ['encrypt', 'decrypt']
    );
}

async function encryptPaste(plaintext, passphrase) {
    const salt = crypto.getRandomValues(new Uint8Array(16));
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const key = await deriveEncryptionKey(passphrase, salt);
    const ciphertext = await crypto.subtle.encrypt(
        { name: 'AES-GCM', iv },
        key,
        new TextEncoder().encode(plaintext)
    );

    return JSON.stringify({
        version: ENCRYPTION_VERSION,
        algorithm: 'AES-GCM',
        kdf: 'PBKDF2-SHA-256',
        iterations: PBKDF2_ITERATIONS,
        salt: bytesToBase64(salt),
        iv: bytesToBase64(iv),
        ciphertext: bytesToBase64(new Uint8Array(ciphertext))
    });
}

async function decryptPaste(payload, passphrase) {
    const encrypted = JSON.parse(payload);
    if (
        encrypted.version !== ENCRYPTION_VERSION ||
        encrypted.algorithm !== 'AES-GCM' ||
        encrypted.kdf !== 'PBKDF2-SHA-256' ||
        encrypted.iterations !== PBKDF2_ITERATIONS
    ) {
        throw new Error('unsupported encrypted paste');
    }

    const salt = base64ToBytes(encrypted.salt);
    const iv = base64ToBytes(encrypted.iv);
    const key = await deriveEncryptionKey(passphrase, salt);
    const plaintext = await crypto.subtle.decrypt(
        { name: 'AES-GCM', iv },
        key,
        base64ToBytes(encrypted.ciphertext)
    );
    return new TextDecoder().decode(plaintext);
}
