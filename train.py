import concurrent.futures
import math
import time 
PRIMES = [
    112272535095293,
    112582705942171,
    112272535095293,
    115280095190773,
    115797848077099,
    1099726899285419]

def is_prime(n):
    if n % 2 == 0:
        return False

    sqrt_n = int(math.floor(math.sqrt(n)))
    for i in range(3, sqrt_n + 1, 2):
        if n % i == 0:
            return False
    return True

def main():
    with concurrent.futures.ProcessPoolExecutor() as executor:
        while True:
           print(executor.map(is_prime, PRIMES))
           print(next(executor.map(is_prime, PRIMES)))
           time.sleep(3)

if __name__ == '__main__':
    main()