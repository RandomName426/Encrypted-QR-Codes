import KeyGenerator
import secrets
import hashlib

message = input("Imput Message\n>>> ")
dataArr = []
for i in list(message):
    dataArr.append(ord(i))

def seedGen(size):
    return secrets.token_bytes(size)

def sha256(dataForHashing):
    return hashlib.sha256(dataForHashing).digest()

def split_to_chunks(plainTextArr, maxChunkSize):
    for i in range(0,len(plainTextArr),maxChunkSize):
        yield plainTextArr[i:i+maxChunkSize]
 
def oaepPadding(message, hashSize, keySize):
    seed = seedGen(hashSize)
    label = b""
    hashLabel = sha256(label)
    hashMessage = sha256(message)
    seedXor = bytes([seed[i] ^ hashLabel[i % len(hashLabel)] for i in range (hashSize)])
    maskedMessage = bytes([hashMessage[i] ^ seedXor[i % len(seedXor)] for i in range (hashSize)])
    paddedMessage = seed + maskedMessage
    paddedMessageInt = int.from_bytes(paddedMessage)
    if paddedMessageInt.bit_length() > keySize*8:
        raise ValueError("Message is too long for OAEP padding with the key size used")
    return paddedMessageInt

def rsaEncoding(message,publicKey):
    return pow(message,publicKey[0],publicKey[1])

def rsaDecrypytion(message,privateKey):
    return pow(message,privateKey[0],privateKey[1])

def rsaOaepEncryption(plainTxtArr, publicKey):
    rsaKeySize = publicKey[1].bit_length() // 8
    sha256HashSize = 32
    maxChunkSize = rsaKeySize - (2 * sha256HashSize) - 2
    messageChunks = list(split_to_chunks(plainTxtArr,maxChunkSize))
    encryptedTxtData = []
    for chunk in messageChunks:
        chunkBytes = bytes(chunk)
        messageInt = oaepPadding(chunkBytes,sha256HashSize,rsaKeySize)
        encryptedChunk = rsaEncoding(messageInt,publicKey)
        encryptedTxtData.append(encryptedChunk)
    return encryptedChunk

def rsaOaepDecryption(encryptedTxt,privateKey,hashSize,label=b""):
    decryptedMessage = rsaDecrypytion(int(encryptedTxt),privateKey)
    paddedMessage = decryptedMessage.to_bytes((decryptedMessage.bit_length() +7) // 8,"big")
    seed = paddedMessage[len(paddedMessage) - (2*hashSize):len(paddedMessage) - hashSize]
    maskedMessage = paddedMessage[len(paddedMessage) - hashSize:]
    hashLabel = sha256(label)
    recoverdSeed = bytes(seed[i] ^ hashLabel[i % len(hashLabel)] for i in range(hashSize))
    recoverdMessage = bytes([maskedMessage[i] ^ recoverdSeed[i % len(recoverdSeed)] for i in range(hashSize)])
    ''.join([chr(byte) for byte in recoverdMessage if byte != 0])

publicKey,privateKey = KeyGenerator.main()
x= rsaOaepEncryption(dataArr,publicKey)
y= rsaOaepDecryption(int(x),privateKey,32)
initalData = " ".join(str(dataArr))
print(f"Initial Data: {initalData}")
print(f"\n\nPublic Key: {publicKey}\n\nEncrypted Data: {x}\n\nPrivate Key: {privateKey}\n\nDecrypted Data (should be identical to initial data): {y}")
