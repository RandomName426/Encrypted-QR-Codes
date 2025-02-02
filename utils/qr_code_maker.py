import qrcode

def create_qr_code(data):
    qr = qrcode.QRCode()
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.show()
    img.save("qrcode.png")