import KeyGenerator as KG
from hashlib import sha256 as sha256_hash
import secrets

def sha256(data):
    return sha256_hash(data).digest()

def mgf1(seed, mask_len):
    mask = b""
    hash_len = 32  
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

def rsaDecrypytion(cipherInt, privateKey):
    d, n = privateKey
    return pow(cipherInt, d, n)

def rsaEncryptWithIntegrity(plainTxtArr, publicKey):

    messageBytes = bytes(plainTxtArr)
    messageInt = int.from_bytes(messageBytes, byteorder="big")
    encryptedMessage = rsaEncoding(messageInt, publicKey)

    keySize = (publicKey[1].bit_length() + 7) // 8
    hashSize = 32 

    try:
        integrityPadding = oaepPadding(messageBytes, hashSize, keySize)
        print(f"Debug - Padding created: {integrityPadding.hex()}")
        paddingInt = int.from_bytes(integrityPadding, byteorder="big")
        encryptedPadding = rsaEncoding(paddingInt, publicKey)
        return (encryptedMessage, encryptedPadding)
    except Exception as e:
        print(f"Debug - Padding error: {e}")
        return None

def rsaDecryptWithIntegrity(encryptedData, privateKey):
    try:
        encryptedMessage, encryptedPadding = encryptedData
        keySize = (privateKey[1].bit_length() + 7) // 8
        hashSize = 32

        decryptedMessage = rsaDecrypytion(encryptedMessage, privateKey)
        messageBytes = decryptedMessage.to_bytes((decryptedMessage.bit_length() + 7) // 8, byteorder="big")
        print(f"Debug - Decrypted message: {messageBytes.hex()}")

        decryptedPadding = rsaDecrypytion(encryptedPadding, privateKey)
        paddingBytes = decryptedPadding.to_bytes(keySize, byteorder="big")
        print(f"Debug - Decrypted padding: {paddingBytes.hex()}")

        decryptedOAEP = oaepUnpadding(paddingBytes, hashSize, keySize)
        if decryptedOAEP == messageBytes:
            print("Data integrity verified!")
            return [i for i in messageBytes]
            
        print("Warning: Integrity verification failed!")
        return None
    except Exception as e:
        print(f"Debug - Decryption error: {e}")
        return None

def main():
    message = input("Input Message\n>>> ")
    dataArr = [ord(i) for i in list(message)]
    publicKey, privateKey = KG.main()
    
    encrypted_data = rsaEncryptWithIntegrity(dataArr, publicKey)
    if encrypted_data:
        print(f"Encrypted Data: {encrypted_data}")
        
        decrypted_data = rsaDecryptWithIntegrity(encrypted_data, privateKey)
        if decrypted_data:
            message = ''.join([chr(i) for i in decrypted_data])
            print(f"Decrypted message: {message}")
        else:
            print("Decryption failed - integrity check failed")
    else:
        print("Encryption failed")

if __name__ == "__main__":
    main()