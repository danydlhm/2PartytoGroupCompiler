from sympy.ntheory.generate import randprime
from hashlib import sha3_512
from random import SystemRandom
from .math.group import ZqQuadraticResidues


class Commitment:
    def generate_parameters(cls, *args, **kwargs):
        raise NotImplementedError

    def generate_commitment(self, pk, random, m):
        raise NotImplementedError

    def check_correctness(self, c, pk, random, m):
        raise NotImplementedError

    def generate_random(self):
        raise NotImplementedError


class CramerShoup(Commitment):

    def __init__(self):
        self.q = randprime(0, 30)

    def generate_parameters(self):
        g_1 = ZqQuadraticResidues.random(self.q)
        g_2 = ZqQuadraticResidues.random(self.q)
        x_1 = ZqQuadraticResidues.random(self.q)
        x_2 = ZqQuadraticResidues.random(self.q)
        y_1 = ZqQuadraticResidues.random(self.q)
        y_2 = ZqQuadraticResidues.random(self.q)
        z = ZqQuadraticResidues.random(self.q)

        c = g_1 ** x_1 * g_2 ** x_2
        d = g_1 ** y_1 * g_2 ** y_2
        h = g_1 ** z

        def hash_q(u_1,u_2,e):
            h = sha3_512()
            h.update(u_1.to_bytes((u_1.bit_length() + 7) // 8, byteorder='big'))
            h.update(u_2.to_bytes((u_2.bit_length() + 7) // 8, byteorder='big'))
            h.update(e.to_bytes((e.bit_length() + 7) // 8, byteorder='big'))
            return ZqQuadraticResidues.from_bytes(h.digest(), q=self.q, byteorder='big')
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

    def check_correctness(self, c, pk, random, m):
        try:
            u_1, u_2, e, v = c
            u_1_, u_2_, e_, v_ = self.generate_commitment(pk=pk, random=random, m=m)
            verification = u_1 == u_1_ and u_2 == u_2_ and e == e_ and v == v_
        except Exception as e:
            verification = False
        return verification