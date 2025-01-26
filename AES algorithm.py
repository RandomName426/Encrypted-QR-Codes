import KeyExpansion as KE

def subBytes(sBox,message):
    return [sBox[byte] for byte in message]
        
def chunking(message):
    chunks = []
    for i in range(0, len(message), 16):
        chunk = message[i:i+16]
        flattened = [chunk[j + 4 * k] for j in range(4) for k in range(4)]
        chunks.append(flattened)
    return chunks
        
def addRoundKey(message, roundKey):
    return [message[i] ^ roundKey[i] for i in range(16)]
          
def shiftRows(state):
    return [
        state[0], state[5], state[10], state[15],
        state[4], state[9], state[14], state[3],
        state[8], state[13], state[2], state[7],
        state[12], state[1], state[6], state[11]
    ]

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
    for i in range(4):
        col = state[i::4]
        state[i*4+0] = galois_multiplication(col[0], 2) ^ galois_multiplication(col[1], 3) ^ col[2] ^ col[3]
        state[i*4+1] = col[0] ^ galois_multiplication(col[1], 2) ^ galois_multiplication(col[2], 3) ^ col[3]
        state[i*4+2] = col[0] ^ col[1] ^ galois_multiplication(col[2], 2) ^ galois_multiplication(col[3], 3)
        state[i*4+3] = galois_multiplication(col[0], 3) ^ col[1] ^ col[2] ^ galois_multiplication(col[3], 2)
    return state

def main():
    originalKey, roundKeys, sBox = KE.main()
    print("Original Key:", originalKey.hex())
    print("Round Keys:", [bytes(roundKey).hex() for roundKey in roundKeys])
    message = input("message: ")
    messageBytes = b""
    messageBytes = message.encode('utf-8')  
    paddingamount = 16 - len(message)%16
    if paddingamount < 16:
        messageBytes += bytes([paddingamount]*paddingamount)
    chunks = chunking(messageBytes)
    print(chunks)
    encrypted = []
    for chunk in chunks:
        state = addRoundKey(chunk,roundKeys[0])
        for i in range(0,8):
            state = subBytes(sBox,state)
            state = shiftRows(state)
            state = mixColumns(state)
            state = addRoundKey(state,roundKeys[i+1])
        state = subBytes(sBox, state)
        state = shiftRows(state)
        state = addRoundKey(state, roundKeys[10])
        encrypted.append(state)
    print(encrypted)
    print("Encrypted:", "".join(f"{byte:02x}" for byte in encrypted[0])) 



main()