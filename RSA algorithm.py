import KeyGenerator

message = input("Imput Message\n>>> ")
dataArr = []
for char in message:
    dataArr.append(str(ord(char)))
    
def RSAEncoding(plaintxt_arr, publickey):
    encryptedtxt_data = []
    for data in plaintxt_arr:
        encryptedtxt_data.append(str(pow(int(data), publickey[0], publickey[1])))
    return " ".join(encryptedtxt_data)

def RSADecoding(encryptedtxt_arr, privatekey):
    plaintxt_data = []
    for data in encryptedtxt_arr:
        plaintxt_data.append(str(pow(int(data), privatekey[0], privatekey[1])))
    return " ".join(plaintxt_data)
publicKey,privateKey = KeyGenerator.main()


x= RSAEncoding(dataArr,publicKey)
y= RSADecoding(x.split(),privateKey)
initalData = " ".join(dataArr)
print(f"Initial Data: {initalData}")
print(f"\n\nPublic Key: {publicKey}\n\nEncrypted Data: {x}\n\nPrivate Key: {privateKey}\n\nDecrypted Data (should be identical to initial data): {y}")
