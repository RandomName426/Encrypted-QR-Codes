document.getElementById('qr-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const fileInput = document.getElementById('qr-file');
    const file = fileInput.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const image = new Image();
            image.onload = function() {
                const canvas = document.createElement('canvas');
                canvas.width = image.width;
                canvas.height = image.height;
                const context = canvas.getContext('2d');
                context.drawImage(image, 0, 0);
                const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
                const code = jsQR(imageData.data, canvas.width, canvas.height);
                if (code) {
                    const qrData = code.data;
                    fetch('/decode_qr', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ qrData: qrData })
                    })
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('qr-result').textContent = `Decoded Data: ${data.decryptedData}`;
                    })
                    .catch(error => {
                        document.getElementById('qr-result').textContent = 'Error decoding QR code.';
                    });
                } else {
                    document.getElementById('qr-result').textContent = 'No QR code found.';
                }
            };
            image.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
});