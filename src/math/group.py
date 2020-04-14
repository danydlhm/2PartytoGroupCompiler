from random import SystemRandom


class ZqMultiplicativeGroup:
    def __init__(self, q, a=1):
        self.q = q
        self.a = a % self.q

    def __mul__(self, other):
        """ Return self*value. """
        if type(self) == type(other) and self.q == other.q:
            return ZqMultiplicativeGroup(a=self.a * other.a, q=self.q)
        else:
            RuntimeError("Can't multiply two elements of distinct groups")

    def __pow__(self, power):
        """ Return pow(self, value). """
        power = power % (self.q - 1)
        if power == 0:
            return ZqMultiplicativeGroup(q=self.q, a=1)
        if power == 1:
            return self
        else:
            power_1 = power // 2
            power_2 = power - power_1
            return self ** power_1 * self ** power_2

    def __truediv__(self, other):
        """ Return self/value. """
        if type(self) == type(other) and self.q == other.q:
            return ZqMultiplicativeGroup(a=self.a * other.a ** -1, q=self.q)
        else:
            RuntimeError("Can't divide two elements of distinct groups")

    def __str__(self):
        return f"{self.a} mod {self.q}"

    def __repr__(self):
        return str(self)

    def __random__(self):
        return ZqMultiplicativeGroup(q=self.q, a=SystemRandom().randrange(1, self.q))

    @classmethod
    def random(cls, q):
        return ZqMultiplicativeGroup(q=q, a=SystemRandom().randrange(1, q))


class ZqQuadraticResidues(ZqMultiplicativeGroup):
    def __init__(self, q, a=1):
        super().__init__(q=q, a=a ** 2)

    def __random__(self):
        return ZqQuadraticResidues(q=self.q, a=SystemRandom().randrange(1, self.q))

    @classmethod
    def random(cls, q):
        return ZqQuadraticResidues(q=q, a=SystemRandom().randrange(1, q))
