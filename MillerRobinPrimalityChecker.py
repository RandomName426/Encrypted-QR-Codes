from secrets import randbelow

def trial_division(n):
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101,
                     103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199]
    for prime in small_primes:
        if n % prime == 0:
            return False
    return True

def MillerRobinPrimalityChecker(num):
    s, d = 0, num - 1
    while d % 2 == 1:
        d //= 2
        s += 1
    for i in range(40):
        a = randbelow(num - 3) + 2
        x = pow(a, d, num)
        if x == 1 or x == num - 1:
            continue
        for i in range(s - 1):
            x = pow(a, 2, num)
            if x == num - 1:
                break
        else:
            return False
    return True

def generate_prime():
    while True:
        candidate_for_prime = randbelow(2**2048 - 2**2047) + 2**2047
        if candidate_for_prime % 2 == 0:
            candidate_for_prime += 1
        if trial_division(candidate_for_prime):
            if MillerRobinPrimalityChecker(candidate_for_prime):
                return candidate_for_prime
