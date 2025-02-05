document.getElementById('qr-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const fileInput = document.getElementById('qr-file');
    const file = fileInput.files[0];
    const keySelection = document.getElementById('key_selection').value;

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
                    const qrData = code.binaryData;

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

    console.log('Requesting webcam access...');
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function(stream) {
            console.log('Webcam stream received');
            video.srcObject = stream;
            video.onloadedmetadata = function() {
                video.play();
                console.log('Webcam video playing');
                requestAnimationFrame(tick);
            };
        })
        .catch(function(err) {
            console.error('Error accessing webcam: ', err);
            document.getElementById('qr-result').textContent = `Error accessing webcam: ${err.name} - ${err.message}`;
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
                const qrData = code.binaryData;

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
                    stopWebcam();
                })
                .catch(error => {
                    console.error('Error decoding QR code:', error);
                    document.getElementById('qr-result').textContent = 'Error decoding QR code.';
                    stopWebcam();
                });
                return;
            }
        }
        requestAnimationFrame(tick);
    }

    function stopWebcam() {
        const stream = video.srcObject;
        const tracks = stream.getTracks();
        tracks.forEach(function(track) {
            track.stop();
        });
        video.style.display = 'none';
    }
});