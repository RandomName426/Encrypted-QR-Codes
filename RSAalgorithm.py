import KeyGenerator as KG 
import secrets
from hashlib import sha256 as sha256_hash

def sha256(data):
    return sha256_hash(data).digest()

def mgf1(seed, mask_len):
    mask = b""
    counter = 0
    while len(mask) < mask_len:
        counter_bytes = counter.to_bytes(4, byteorder="big")
        mask += sha256(seed + counter_bytes)
        counter += 1
    return mask[:mask_len]

def oaepPadding(message, hashSize, keySize):
    label_hash = sha256(b"")
    PS = b"\x00" * (keySize - len(message) - 2*hashSize - 2)
    DB = label_hash + PS + b"\x01" + message
    seed = secrets.token_bytes(hashSize)
    dbMask = mgf1(seed, len(DB))
    maskedDB = bytes(a ^ b for a, b in zip(DB, dbMask))
    seedMask = mgf1(maskedDB, hashSize)
    maskedSeed = bytes(a ^ b for a, b in zip(seed, seedMask))
    return b"\x00" + maskedSeed + maskedDB

def oaepUnpadding(paddedMessage, hashSize, keySize):
    maskedSeed = paddedMessage[1:hashSize+1]
    maskedDB = paddedMessage[hashSize+1:]

    seedMask = mgf1(maskedDB, hashSize)
    seed = bytes(a ^ b for a, b in zip(maskedSeed, seedMask))

    dbMask = mgf1(seed, len(maskedDB))
    DB = bytes(a ^ b for a, b in zip(maskedDB, dbMask))
    
    label_hash = sha256(b"")
    if DB[:hashSize] != label_hash:
        raise ValueError("Invalid label hash")

    i = hashSize
    while i < len(DB) and DB[i] == 0:
        i += 1
    if i == len(DB) or DB[i] != 1:
        raise ValueError("Invalid padding")
    
    return DB[i+1:]

def rsaEncoding(messageInt, publicKey):
    e, n = publicKey
    return pow(messageInt, e, n)

def rsaDecryption(cipherInt, privateKey):
def rsaDecryption(cipherInt, privateKey):
    d, n = privateKey
    return pow(cipherInt, d, n)

def rsaEncryptWithIntegrity(plainTxtArr, publicKey):
    messageBytes = bytes(plainTxtArr)
    keySize = (publicKey[1].bit_length() + 7) // 8
    hashSize = 32 

    try:
        integrityPadding = oaepPadding(messageBytes, hashSize, keySize)
        paddingInt = int.from_bytes(integrityPadding, byteorder="big")
        encryptedPadding = rsaEncoding(paddingInt, publicKey)
        
        encryptedMessage = rsaEncoding(int.from_bytes(messageBytes, byteorder="big"), publicKey)
        
        return encryptedMessage.to_bytes(keySize, byteorder="big") + encryptedPadding.to_bytes(keySize, byteorder="big")
        
        encryptedMessage = rsaEncoding(int.from_bytes(messageBytes, byteorder="big"), publicKey)
        
        return encryptedMessage.to_bytes(keySize, byteorder="big") + encryptedPadding.to_bytes(keySize, byteorder="big")
    except Exception as e:
        print(f"Debug - Padding error: {e}")
        return None


def rsaDecryptWithIntegrity(encryptedData, privateKey):
    try:
        keySize = (privateKey[1].bit_length() + 7) // 8
        hashSize = 32

        encryptedMessage = encryptedData[:keySize]
        encryptedPadding = encryptedData[keySize:]
        print(f"\n\nEncrypted Message: {encryptedMessage.hex()}\n")
        print(f"\n\nEncrypted Padding: {encryptedPadding.hex()}\n")
        decryptedMessage = rsaDecryption(int.from_bytes(encryptedMessage, byteorder="big"), privateKey)
        encryptedMessage = encryptedData[:keySize]
        encryptedPadding = encryptedData[keySize:]
        print(f"\n\nEncrypted Message: {encryptedMessage.hex()}\n")
        print(f"\n\nEncrypted Padding: {encryptedPadding.hex()}\n")
        decryptedMessage = rsaDecryption(int.from_bytes(encryptedMessage, byteorder="big"), privateKey)
        messageBytes = decryptedMessage.to_bytes((decryptedMessage.bit_length() + 7) // 8, byteorder="big")

        decryptedPadding = rsaDecryption(int.from_bytes(encryptedPadding, byteorder="big"), privateKey)
        decryptedPadding = rsaDecryption(int.from_bytes(encryptedPadding, byteorder="big"), privateKey)
        paddingBytes = decryptedPadding.to_bytes(keySize, byteorder="big")

        decryptedOAEP = oaepUnpadding(paddingBytes, hashSize, keySize)
        decryptedOAEP = oaepUnpadding(paddingBytes, hashSize, keySize)
        if decryptedOAEP == messageBytes:
            print("Data integrity verified!")
            return messageBytes
            
        print("Warning: Integrity verification failed!")
        return None
    except Exception as e:
        print(f"Debug - Decryption error: {e}")
        return None

def Encryption(message, publicKey):
    messageBytes = message.to_bytes(16, byteorder="big")
    dataArr = [int(byte) for byte in messageBytes]
def Encryption(message, publicKey):
    messageBytes = message.to_bytes(16, byteorder="big")
    dataArr = [int(byte) for byte in messageBytes]
    encrypted_data = rsaEncryptWithIntegrity(dataArr, publicKey)
    print(f"Encrypted Data: {encrypted_data.hex()}")
    print(f"Encrypted Data: {encrypted_data.hex()}")
    return encrypted_data

def Decryption(encrypted_data, privateKey):    

def Decryption(encrypted_data, privateKey):    
    decrypted_data = rsaDecryptWithIntegrity(encrypted_data, privateKey)
    if decrypted_data:
        message = int.from_bytes(decrypted_data, byteorder="big")
        print(f"Decrypted message: {message}")
        return message
        message = int.from_bytes(decrypted_data, byteorder="big")
        print(f"Decrypted message: {message}")
        return message
    else:
        print("Decryption failed - integrity check failed")
        return None
        return None

def main(message, encryption, key):
    if encryption == True:
        encrypted_data = Encryption(message, key)
        return encrypted_data
    else:
        decrypted_data = Decryption(message, key)
        return decrypted_data