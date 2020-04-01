from cca2python.ccapke import readparams, cskeygen
from sympy.ntheory.generate import randprime, isprime
from hashlib import sha3_512
from random import SystemRandom
import yaml


class Commitment:
    @classmethod
    def generate_parameters(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def generate_commitment(cls, pk, random, m):
        raise NotImplementedError


class CramerShoup(Commitment):
    @classmethod
    def generate_parameters(cls):
        params = readparams("cca2python\\ddh-prg-params.1024")
        kp = cskeygen(params)
        pkfile = open('test_pk.txt', 'w')
        yaml.safe_dump(kp[0], pkfile)
        pkfile.close()

        skfile = open('test_sk.txt', 'w')
        yaml.safe_dump(kp[1], skfile)
        skfile.close()
        raise NotImplementedError

    @classmethod
    def generate_commitment(cls, pk, random, m):
        raise NotImplementedError


class CramerShoupCustom:

    def __init__(self):
        self.q = randprime(0, 30)

    def generate_parameters(self):
        g_1 = SystemRandom().randrange(0, self.q)
        g_2 = SystemRandom().randrange(0, self.q)
        x_1 = SystemRandom().randrange(0, self.q)
        x_2 = SystemRandom().randrange(0, self.q)
        y_1 = SystemRandom().randrange(0, self.q)
        y_2 = SystemRandom().randrange(0, self.q)
        z = SystemRandom().randrange(0, self.q)

        c = (g_1 ** x_1 * g_2 ** x_2) % self.q
        d = (g_1 ** y_1 * g_2 ** y_2) % self.q
        h = (g_1 ** z) % self.q

        def hash_q(u_1,u_2,e):
            h = sha3_512()
            h.update(u_1.to_bytes((u_1.bit_length() + 7) // 8, byteorder='big'))
            h.update(u_2.to_bytes((u_2.bit_length() + 7) // 8, byteorder='big'))
            h.update(e.to_bytes((e.bit_length() + 7) // 8, byteorder='big'))
            return int.from_bytes(h.digest(), byteorder='big') % self.q
        H = hash_q
        return g_1, g_2, c, d, h, H

    def generate_commitment(self, pk, random, m):
        g_1, g_2, c, d, h, H = pk
        u_1 = (g_1 ** random) % self.q
        u_2 = (g_2 ** random) % self.q
        e = (h ** random * m) % self.q
        alpha = (H(u_1, u_2, e)) % self.q
        v = (c**random * d**(random*alpha)) % self.q
        return u_1, u_2, e, v

    def generate_random(self):
        return SystemRandom().randrange(0, self.q)
