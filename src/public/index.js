const API = 'http://127.0.0.1:8000';

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

    try {
        const response = await fetch(`${API}/pastes`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ data, duration: Number(duration) })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'unknown error');
        }

        const result = await response.json();
        const url = `${API}/${result.id}`;
        document.getElementById('paste-url').value = url;
        document.getElementById('result').hidden = false;
        showToast('paste created');
    } catch (error) {
        showToast(error.message || 'failed to create paste', true);
    }
}
