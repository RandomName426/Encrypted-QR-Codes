from secrets import randbelow
import KeyExpansion as KE
import RSAalgorithm as RSA

def subBytes(sBox, message, encryption):
    if encryption:
        subbedMessage = [sBox[byte] for byte in message]
    else:
        subbedMessage = [sBox[byte] for byte in message]
    return subbedMessage

def chunking(message):
    chunks = []
    for i in range(0, len(message), 16):
        chunks.append(message[i:i+16])
    return chunks

def addRoundKey(message, roundKey):
    return [message[i] ^ roundKey[i] for i in range(16)]

def shiftRows(state, encryption):
    shifted = []
    if encryption:
        shifted = [state[i] for i in (0, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12, 1, 6, 11)]
    else:
        shifted = [state[i] for i in (0, 13, 10, 7, 4, 1, 14, 11, 8, 5, 2, 15, 12, 9, 6, 3)]
    return shifted

def galois_multiplication(a, b):
    p = 0
    for i in range(8):
        if b & 1:
            p ^= a
        hi_bit_set = a & 0x80
        a <<= 1
        if hi_bit_set:
            a ^= 0x1b  # x^8 + x^4 + x^3 + x + 1
        b >>= 1
    return p & 0xFF

def mixColumns(state, encryption):
    newState = [0] * 16
    if encryption:
        for col in range(4):
            start = col * 4
            a = state[start:start + 4]
            newState[start + 0] = (galois_multiplication(2, a[0]) ^
                                   galois_multiplication(3, a[1]) ^
                                   a[2] ^
                                   a[3])
            newState[start + 1] = (a[0] ^
                                   galois_multiplication(2, a[1]) ^
                                   galois_multiplication(3, a[2]) ^
                                   a[3])
            newState[start + 2] = (a[0] ^
                                   a[1] ^
                                   galois_multiplication(2, a[2]) ^
                                   galois_multiplication(3, a[3]))
            newState[start + 3] = (galois_multiplication(3, a[0]) ^
                                   a[1] ^
                                   a[2] ^
                                   galois_multiplication(2, a[3]))
    else:
        for col in range(4):
            start = col * 4
            a = state[start:start + 4]
            newState[start + 0] = (galois_multiplication(0x0e, a[0]) ^
                                   galois_multiplication(0x0b, a[1]) ^
                                   galois_multiplication(0x0d, a[2]) ^
                                   galois_multiplication(0x09, a[3]))
            newState[start + 1] = (galois_multiplication(0x09, a[0]) ^
                                   galois_multiplication(0x0e, a[1]) ^
                                   galois_multiplication(0x0b, a[2]) ^
                                   galois_multiplication(0x0d, a[3]))
            newState[start + 2] = (galois_multiplication(0x0d, a[0]) ^
                                   galois_multiplication(0x09, a[1]) ^
                                   galois_multiplication(0x0e, a[2]) ^
                                   galois_multiplication(0x0b, a[3]))
            newState[start + 3] = (galois_multiplication(0x0b, a[0]) ^
                                   galois_multiplication(0x0d, a[1]) ^
                                   galois_multiplication(0x09, a[2]) ^
                                   galois_multiplication(0x0e, a[3]))
    return newState

def encrypt_aes(data, key):
    originalKey = key
    roundKeys, sBox = KE.main(True, originalKey)
    messageBytes = data.encode('utf-8')
    paddingamount = 16 - len(messageBytes) % 16
    if paddingamount < 16:
        messageBytes += bytes([paddingamount] * paddingamount)
    chunks = chunking(messageBytes)
    encrypted = []
    for chunk in chunks:
        state = addRoundKey(chunk, roundKeys[0])
        for i in range(9):
            state = subBytes(sBox, state, True)
            state = shiftRows(state, True)
            state = mixColumns(state, True)
            state = addRoundKey(state, roundKeys[i+1])
        state = subBytes(sBox, state, True)
        state = shiftRows(state, True)
        state = addRoundKey(state, roundKeys[10])
        encrypted.append(state)
    encryptedHex = "".join("".join(f"{byte:02x}" for byte in block) for block in encrypted)
    return originalKey, encryptedHex

def decrypt_aes(message, key):
    originalKey = key
    roundKeys, sBox = KE.main(False, originalKey)
    roundKeys = roundKeys[::-1]
    chunks = chunking(bytes.fromhex(message))
    decrypted = []
    for chunk in chunks:
        state = addRoundKey(chunk, roundKeys[0])
        for i in range(9):
            state = shiftRows(state, False)
            state = subBytes(sBox, state, False)
            state = addRoundKey(state, roundKeys[i + 1])
            state = mixColumns(state, False)
        state = shiftRows(state, False)
        state = subBytes(sBox, state, False)
        state = addRoundKey(state, roundKeys[10])
        decrypted.append(state)
    paddedHex = "".join("".join(f"{byte:02x}" for byte in block) for block in decrypted)
    paddingLength = int(paddedHex[-2:], 16)
    decryptedData = paddedHex[:-paddingLength*2]
    decryptedData = bytes.fromhex(decryptedData).decode('utf-8')
    return decryptedData

# Functions to combine AES and RSA encryptions
def Encryption(message, pubKey):
    aes_key = randbelow(2**128 - 2**127) + 2**127
    print(f"Original AES Key: {aes_key}")
    originalKey, encrypted_message = encrypt_aes(message, aes_key)
    print(f"Encrypted Message: {encrypted_message}")
    encryptedKey = RSA.main(originalKey, True, pubKey)
    print(f"Encrypted AES Key: {encryptedKey.hex()}")
    print(f"Encrypted Data: {(encryptedKey + encrypted_message.encode('utf-8')).hex()}")
    return encryptedKey + encrypted_message.encode('utf-8')

def Decryption(encrypted_data, privateKey):
    print(f"Encrypted Data (key part): {encrypted_data[:2048]}")
    print(f"Encrypted Data (message part): {encrypted_data[2048:]}")
    decrytedKey = RSA.main(encrypted_data[:2048], False, privateKey)
    print(f"Decrypted AES Key: {decrytedKey}")
    encrypted_message = encrypted_data[2048:].decode('utf-8')
    print(f"Encrypted Message: {encrypted_message}")
    decrypted_message = decrypt_aes(encrypted_message, decrytedKey)
    print(f"Decrypted Message: {decrypted_message}")
    return decrypted_message