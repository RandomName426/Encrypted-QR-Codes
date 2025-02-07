import MillerRabinPrimalityChecker

# Dictionary to store keys
key_store = {}

def generate_keys(username):
    prime1 = MillerRabinPrimalityChecker.generate_prime()
    prime2 = MillerRabinPrimalityChecker.generate_prime()
    public_key, private_key = create_rsa_keys(prime1, prime2)
    key_store[username] = {'public_key': public_key, 'private_key': private_key}
    return public_key, private_key

def create_rsa_keys(prime1, prime2):
    n = prime1 * prime2
    phi = (prime1 - 1) * (prime2 - 1)
    e = 65537  # Commonly used prime exponent
    d = modinv(e, phi)
    public_key = (e, n)
    private_key = (d, n)
    return public_key, private_key

def modinv(a, m):
    # Extended Euclidean Algorithm
    m0, x0, x1 = m, 0, 1
    if m == 1:
        return 0
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    if x1 < 0:
        x1 += m0
    return x1

def get_private_key(username):
    # Storing the private keys of the user
    return key_store.get(username, {}).get('private_key')

def get_public_key(username):
    # Storing the public keys of the user
    return key_store.get(username, {}).get('public_key')


