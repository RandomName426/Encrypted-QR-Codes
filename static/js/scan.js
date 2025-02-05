document.getElementById('qr-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const fileInput = document.getElementById('qr-file');
    const file = fileInput.files[0];
    const keySelection = document.getElementById('key_selection').value;

    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            console.log("FileReader onload triggered");  // Debug statement
            const image = new Image();
            image.onload = function() {
                console.log("Image onload triggered");  // Debug statement
                const canvas = document.createElement('canvas');
                canvas.width = image.width;
                canvas.height = image.height;
                console.log(`Image dimensions: ${image.width}x${image.height}`);  // Log image dimensions
                const context = canvas.getContext('2d');
                context.drawImage(image, 0, 0);
                const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
                console.log(`Image data: width=${imageData.width}, height=${imageData.height}`);  // Debug statement

                const code = jsQR(imageData.data, canvas.width, canvas.height);
                if (code) {
                    const qrData = code.binaryData;  // Use binaryData to get raw bytes
                    console.log("Extracted QR Data (raw bytes):", qrData);  // Debug statement

                    // Construct form data to mimic form submission
                    const formData = new FormData();
                    formData.append('qr_code', new Blob([new Uint8Array(qrData)], { type: 'application/octet-stream' }));
                    formData.append('key_selection', keySelection);

                    fetch('/decode_qr', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.decryptedData) {
                            document.getElementById('qr-result').textContent = `Decoded Data: ${data.decryptedData}`;
                        } else {
                            document.getElementById('qr-result').textContent = `Error: ${data.error}`;
                        }
                    })
                    .catch(error => {
                        console.error('Error decoding QR code:', error);
                        document.getElementById('qr-result').textContent = 'Error decoding QR code.';
                    });
                } else {
                    document.getElementById('qr-result').textContent = 'No QR code found.';
                }
            };
            image.src = e.target.result;
        };
        reader.readAsDataURL(file);
    } else {
        document.getElementById('qr-result').textContent = 'No file selected.';
    }
});

document.getElementById('start-webcam').addEventListener('click', function() {
    const video = document.getElementById('webcam');
    video.style.display = 'block';

    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
        .then(function(stream) {
            video.srcObject = stream;
            video.setAttribute('playsinline', true);
            video.play();
            requestAnimationFrame(tick);
        });

    function tick() {
        if (video.readyState === video.HAVE_ENOUGH_DATA) {
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const context = canvas.getContext('2d');
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
            const code = jsQR(imageData.data, canvas.width, canvas.height);
            if (code) {
                const qrData = code.binaryData;  // Use binaryData to get raw bytes
                console.log("Extracted QR Data (raw bytes):", qrData);  // Debug statement

                // Construct form data to mimic form submission
                const formData = new FormData();
                formData.append('qr_code', new Blob([new Uint8Array(qrData)], { type: 'application/octet-stream' }));
                formData.append('key_selection', document.getElementById('key_selection').value);

                fetch('/decode_qr', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.decryptedData) {
                        document.getElementById('qr-result').textContent = `Decoded Data: ${data.decryptedData}`;
                    } else {
                        document.getElementById('qr-result').textContent = `Error: ${data.error}`;
                    }
                })
                .catch(error => {
                    console.error('Error decoding QR code:', error);
                    document.getElementById('qr-result').textContent = 'Error decoding QR code.';
                });
                return;
            }
        }
        requestAnimationFrame(tick);
    }
});