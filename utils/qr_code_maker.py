import qrcode
import zlib

def create_qr_code(data, filename="qrcode.png"):
    # Compress the data
    compressed_data = zlib.compress(data.encode('utf-8'))
    
    qr = qrcode.QRCode(
        version=1,  # Controls the size of the QR code; larger version = more data
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Lower error correction level
        box_size=10,
        border=4,
    )
    qr.add_data(compressed_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    img.save(filename)