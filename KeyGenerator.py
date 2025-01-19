import MillerRobinPrimalityChecker
from math import lcm
class key_generator:
    def __init__(self, first_prime,second_prime):
        self.p = first_prime - 1
        self.q = second_prime - 1
        self.n = first_prime * second_prime
        self.carmichael_lambda_function = self.lcm(self.p,self.q)
        self.e = 65537
    
    def lcm(self,a,b):
        from math import gcd
        return abs(a * b)// gcd(a,b)

    def extended_euclidean_algorithm(self,a,b):
        x0,x1 = 1, 0 
        y0,y1 = 0, 1  
        while b != 0:
            q,r = divmod(a, b)
            x0,x1 = x1, x0 - q * x1
            y0,y1 = y1, y0 - q * y1
            a,b = b, r
        return a,x0,y0
    
    def modular_inverse(self, a, m):
        g,x,y = self.extended_euclidean_algorithm(a, m)
        if g != 1:
            raise ValueError(f"{a} has no modular inverse modulo {m}")
        else:
            return x % m  
    
    def generate_key(self):
        d = self.modular_inverse(self.e,self.carmichael_lambda_function)
        public_key = (self.e,self.n)
        private_key = (d,self.n)
        return public_key,private_key        

def main():
    prime_1,prime_2 = MillerRobinPrimalityChecker.main()
    y = key_generator(prime_1,prime_2)
    return key_generator.generate_key(y)
     
