from sympy.ntheory.generate import randprime
from hashlib import sha3_512
from .math.group import ZqQuadraticResidues


class Commitment:
    """Commitment Class Interface"""
    def generate_parameters(cls, *args, **kwargs):
        raise NotImplementedError

    def generate_commitment(self, pk, random, m):
        raise NotImplementedError

    def check_correctness(self, c, pk, random, m):
        raise NotImplementedError

    def generate_random(self):
        raise NotImplementedError


class CramerShoup(Commitment):
    """ Commitment implementation using CramerShoup"""
    def __init__(self):
        self.q = randprime(2**10, 2**11)

    def generate_parameters(self):
        """Generate parameter of CramerShoup algorithm"""
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
        """Generate commitment using a pk, random and m parameter"""
        g_1, g_2, c, d, h, H = pk
        m_aux = ZqQuadraticResidues(self.q, a=m)
        u_1 = g_1 ** random
        u_2 = g_2 ** random
        e = h ** random * m_aux
        alpha = H(u_1, u_2, e)
        v = c**random * d**(random*alpha)
        return u_1, u_2, e, v

    def generate_random(self):
        """Generate an aleatory integer"""
        return ZqQuadraticResidues.random(self.q)

    def check_correctness(self, c, pk, random, m):
        """Check if the commitment c is generated by pk, random and m parameters"""
        try:
            u_1, u_2, e, v = c
            u_1_, u_2_, e_, v_ = self.generate_commitment(pk=pk, random=random, m=m)
            verification = u_1 == u_1_ and u_2 == u_2_ and e == e_ and v == v_
        except Exception as e:
            verification = False
        return verification