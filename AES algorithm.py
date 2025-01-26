import KeyExpansion as KE

def subBytes(sBox,message):
    return [sBox[byte] for byte in message]
        
def chunking(message):
    chunks = []
    for i in range(0, len(message), 16):
        chunks.append(message[i:i+16])
    return chunks
        
def addRoundKey(message, roundKey):
    return [message[i] ^ roundKey[i] for i in range(16)]
          
def shiftRows(state):
    return [state[i] for i in (0, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12, 1, 6, 11)]

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

def mixColumns(state):
    newState = [0] * 16
    for col in range(4):
        start = col * 4
        a = state[start:start + 4]
        newState[start + 0] = galois_multiplication(2, a[0]) ^ galois_multiplication(3, a[1]) ^ a[2] ^ a[3]
        newState[start + 1] = a[0] ^ galois_multiplication(2, a[1]) ^ galois_multiplication(3, a[2]) ^ a[3]
        newState[start + 2] = a[0] ^ a[1] ^ galois_multiplication(2, a[2]) ^ galois_multiplication(3, a[3])
        newState[start + 3] = galois_multiplication(3, a[0]) ^ a[1] ^ a[2] ^ galois_multiplication(2, a[3])
    return newState

def main():
    originalKey, roundKeys, sBox = KE.main()
    print("Original Key:", originalKey.hex())
    print("Round Keys:", [bytes(roundKey).hex() for roundKey in roundKeys])
    message = input("message: ")
    messageBytes = message.encode('utf-8')  
    paddingamount = 16 - len(message)%16
    if paddingamount < 16:
        messageBytes += bytes([paddingamount]*paddingamount)
    chunks = chunking(messageBytes)
    print("Input Chunks:", [bytes(chunk).hex() for chunk in chunks])
    encrypted = []
    for chunk in chunks:
        state = addRoundKey(chunk,roundKeys[0])
        print("Input state:", bytes(state).hex())
        for i in range(9):
            state = subBytes(sBox,state)
            print("Input state:", [bytes(state).hex() for byte in state])
            state = shiftRows(state)
            print("Input state:", [bytes(state).hex() for byte in state])
            state = mixColumns(state)
            print("Input state:", [bytes(state).hex() for byte in state])
            state = addRoundKey(state,roundKeys[i+1])
            print("Input state:", [bytes(state).hex() for byte in state])
        state = subBytes(sBox, state)
        print("Input state:", [bytes(state).hex() for byte in state])
        state = shiftRows(state)
        print("Input state:", [bytes(state).hex() for byte in state])
        state = addRoundKey(state, roundKeys[10])
        print("Input state:", [bytes(state).hex() for byte in state])
        encrypted.append(state)
    encryptedHex = "".join("".join(f"{byte:02x}" for byte in block) for block in encrypted)
    print("Encrypted:", encryptedHex)


main()