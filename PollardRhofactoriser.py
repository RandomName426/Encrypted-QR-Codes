from random import randint
from math import gcd
class PollardRhoFactorisor:
    def __init__(self, number):
        self.number = number
        
    def modularExpo(self, base, exponent, divisor):
        result = 1
        while exponent > 0:
            if (exponent & 1):
                result = (result * base) % divisor
            base = (base * base) % divisor
            exponent //= 2
        return result
    
    def main(self):
        if (self.number) == 1:
            return self.number
        elif (self.number % 2) == 0:
            return 2
        d = 1
        x = randint(2, self.number - 1)
        y = x
        c = randint(1, self.number - 1)
        while (d == 1):
            x = (self.modularExpo(self, x, 2, self.number) + c + self.number) % self.number
            
            y = (self.modularExpo(self, y, 2, self.number) + c + self.number) % self.number
            y = (self.modularExpo(self, y, 2, self.number) + c + self.number) % self.number
            
            d= gcd(abs(x - y), self.number)
            
            if (d == self.number):
                return self.main(self)
        return d