from secrets import randbelow

def trial_division(n):
    # List of small primes up to 1000 (or some small set you want to use)
    possiblePrime = True
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]
    for prime in small_primes:
        if n % prime == 0:
            possiblePrime = False  # Found a divisor, not a prime
    return possiblePrime

def MillerRobinPrimalityChecker(num):
    s,d = 0,(num-1)
    while d%2 == 1:
        d //= 2
        s += 1
    for i in range(40):
        a= randbelow(num-3) + 2
        
        x = pow(a,d,num)
        if x == 1 or x== -1:
            continue
        
        for i in range (s-1):
            x = pow(a,2,num)
            if x == (num - 1):
                break
        else:
            return False
    return True

def main():
    primesList = []
    while len(primesList) < 2: 
        candidate_for_prime = randbelow(2**2048 - 2**2047) + 2**2047  
        if candidate_for_prime % 2 == 0:
            candidate_for_prime += 1
        if trial_division(candidate_for_prime):
            if MillerRobinPrimalityChecker(candidate_for_prime):
                primesList.append(candidate_for_prime)  
                
    return primesList[0], primesList[1]

