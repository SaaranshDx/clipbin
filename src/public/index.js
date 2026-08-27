const API = "https://clipbin.github.io/";
let encryptionKey = null;
let encryptionKeyResolver = null;

function showToast(message, isError) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = isError ? 'show error' : 'show';
    setTimeout(() => { toast.className = ''; }, 2500);
}

function copyLink() {
    const url = document.getElementById('paste-url').value;
    navigator.clipboard.writeText(url).then(() => {
        showToast('link copied');
    }).catch(() => {
        showToast('failed to copy', true);
    });
}

function comingSoon() {
    showToast('coming soon');
}

function toggleApiModal() {
    document.getElementById('api-modal').classList.toggle('open');
}

function toggleEncryption(toggle) {
    if (toggle.checked) {
        encryptionKey = null;
        openEncryptionModal();
    } else {
        encryptionKey = null;
    }
}

function openEncryptionModal() {
    const modal = document.getElementById('encryption-modal');
    const input = document.getElementById('encryption-key');
    input.value = '';
    modal.classList.add('open');
    setTimeout(() => input.focus(), 0);
    return new Promise((resolve) => { encryptionKeyResolver = resolve; });
}

function closeEncryptionModal() {
    document.getElementById('encryption-modal').classList.remove('open');
    encryptionKeyResolver = null;
}

function confirmEncryption() {
    const key = document.getElementById('encryption-key').value;
    if (!key) {
        showToast('encryption key is required', true);
        return;
    }
    encryptionKey = key;
    if (encryptionKeyResolver) encryptionKeyResolver(key);
    closeEncryptionModal();
}

function cancelEncryption() {
    document.getElementById('encryption-toggle').checked = false;
    encryptionKey = null;
    if (encryptionKeyResolver) encryptionKeyResolver(null);
    closeEncryptionModal();
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.getElementById('api-modal').classList.remove('open');
    }
});

async function uploadPaste() {
    const data = document.getElementById('data-feild').value.trim();
    const duration = document.getElementById('duration').value;

    if (!data) {
        showToast('nothing to paste', true);
        return;
    }

    try {
        let pasteData = data;
        if (document.getElementById('encryption-toggle').checked) {
            if (!encryptionKey) {
                encryptionKey = await openEncryptionModal();
            }
            if (!encryptionKey) return;
            pasteData = await encryptPaste(data, encryptionKey);
        }
        const response = await fetch(`/pastes`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ data: pasteData, duration: Number(duration) })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'unknown error');
        }

        const result = await response.json();
        const url = `${API}${result.id}`;
        document.getElementById('paste-url').value = url;
        document.getElementById('result').hidden = false;
        showToast('paste created');
    } catch (error) {
        showToast(error.message || 'failed to create paste', true);
    }
}
