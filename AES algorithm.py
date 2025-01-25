import KeyExpansion as KE

def subBytes(message):
    pass



oringinalKey, roundKeys, S_box = KE.main()
message = input("message: ")
messageBytes = b""
chunks = []
for i in message:
    messageBytes += (ord(i)).to_bytes(1,"big")  
paddingamount = 16 - len(message)%16
if paddingamount < 16:
    messageBytes += bytes([paddingamount]*paddingamount)

