from random import randint
from math import gcd

def modularExpo(base, exponent, divisor):
    result = 1
    while exponent > 0:
        if (exponent & 1):
            result = (result * base) % divisor
        base = (base * base) % divisor
        exponent //= 2
    return result

def main(number):
    if (number) == 1:
        return number
    elif (number % 2) == 0:
        return 2
    d = 1
    x = randint(2,number - 1)
    y = x
    c = randint(1,number - 1)
    while (d == 1):
        x = (modularExpo(x,2,number) + c + number) % number
        y = (modularExpo(y,2,number) + c + number) % number
        y = (modularExpo(y,2,number) + c + number) % number
        d= gcd(abs(x - y),number)
        if (d == number):
            return main(number)
    return d