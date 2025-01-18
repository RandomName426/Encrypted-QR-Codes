import qrcode
import qrcode.constants
data = "Integral maths is the best"
myQr = qrcode.QRCode(
    version= 5,
    error_correction= qrcode.constants.ERROR_CORRECT_M,
    box_size= 100,
    border= 30
)
myQr.add_data(data)
myQr.make(fit=True)
image = myQr.make_image(fill_color="black",back_color="white")
image.save("qrcode.png")
