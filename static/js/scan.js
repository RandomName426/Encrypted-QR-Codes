document.getElementById('qr-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const fileInput = document.getElementById('qr-file');
    const file = fileInput.files[0];

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

                // Log image data to ensure it is being created correctly
                console.log(`Image data: width=${imageData.width}, height=${imageData.height}`);

                Quagga.decodeSingle({
                    src: e.target.result,
                    numOfWorkers: 0,  // Needs to be 0 when used within node
                    inputStream: {
                        size: 800  // restrict input-size to be 800px in width (long-side)
                    },
                    decoder: {
                        readers: ["qr_reader"]  // List of active readers
                    },
                }, function(result) {
                    if (result && result.codeResult) {
                        const qrData = result.codeResult.code;
                        console.log("Extracted QR Data:", qrData);  // Debug statement

                        if (qrData) {
                            // Convert the QR data to a Uint8Array to handle raw bytes
                            const qrBytes = new TextEncoder().encode(qrData);
                            console.log("QR Data as bytes:", qrBytes);  // Debug statement

                            // Send the raw bytes to the server for decryption
                            fetch('/decode_qr', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/octet-stream'
                                },
                                body: qrBytes
                            })
                            .then(response => response.json())
                            .then(data => {
                                document.getElementById('qr-result').textContent = `Decoded Data: ${data.decryptedData}`;
                            })
                            .catch(error => {
                                console.error('Error decoding QR code:', error);  // Debug statement
                                document.getElementById('qr-result').textContent = 'Error decoding QR code.';
                            });
                        } else {
                            console.error("QR Data is empty!");  // Debug statement
                            document.getElementById('qr-result').textContent = 'QR Data is empty!';
                        }
                    } else {
                        console.error("No QR code found or error in decoding.");  // Debug statement
                        document.getElementById('qr-result').textContent = 'No QR code found.';
                    }
                });
            };

            image.src = e.target.result;
        };

        reader.readAsDataURL(file);
    } else {
        console.error("No file selected.");  // Debug statement
        document.getElementById('qr-result').textContent = 'No file selected.';
    }
});