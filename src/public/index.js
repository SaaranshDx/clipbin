async function uploadPaste() {
    try {
        const data = document.getElementById("data-feild").value
        const payload = {
            duration: 168,
            data: data
        }
        const response = await fetch('http://127.0.0.1:8000/pastes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })

        if (!response.ok) {
            throw new Error('HTTP error!');
        }

        const result = await response.json();
        console.log('Success:', result);
    } catch(error) {
        console.error('Failed to upload paste:', error);
    }
}