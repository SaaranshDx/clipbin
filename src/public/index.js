const API = "https://api.ghostdrop.qzz.io/";

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

    const key = window.prompt('Enter an encryption key for this paste:');
    if (key === null) {
        return;
    }
    if (!key) {
        showToast('encryption key is required', true);
        return;
    }

    try {
        const encryptedData = await encryptPaste(data, key);
        const response = await fetch(`/pastes`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ data: encryptedData, duration: Number(duration) })
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
