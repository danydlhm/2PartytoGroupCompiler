from random import SystemRandom


class ZqMultiplicativeGroup:
    def __init__(self, q, a=1):
        self.q = q
        self.a = a % self.q

    def __mul__(self, other):
        """ Return self*value. """
        if type(self) == type(other) and self.q == other.q:
            return self.__class__(a=self.a * other.a, q=self.q)
        else:
            RuntimeError("Can't multiply two elements of distinct groups")

    def __pow__(self, power):
        """ Return pow(self, value). """
        if isinstance(power, int):
            aux_power = power
        elif isinstance(power, ZqMultiplicativeGroup):
            aux_power = power.a
        else:
            raise RuntimeError(f"Can't use {type(power)} class as power value")
        aux_power = aux_power % (self.q - 1)
        if aux_power == 0:
            return self.__class__(q=self.q, a=1)
        elif aux_power == 1:
            return self
        else:
            power_1 = aux_power // 2
            power_2 = aux_power - power_1
            return self ** power_1 * self ** power_2

    def __truediv__(self, other):
        """ Return self/value. """
        if type(self) == type(other) and self.q == other.q:
            return self.__class__(a=self.a * other.a ** -1, q=self.q)
        else:
            RuntimeError("Can't divide two elements of distinct groups")

    def __eq__(self, other):
       return type(self) == type(other) and self.q == other.q and self.a == other.a

    def __str__(self):
        return f"{self.a} mod {self.q}"

    def __repr__(self):
        return str(self)

    def __random__(self):
        return ZqMultiplicativeGroup(q=self.q, a=SystemRandom().randrange(1, self.q))

    @classmethod
    def random(cls, q):
        return ZqMultiplicativeGroup(q=q, a=SystemRandom().randrange(1, q))

    @classmethod
    def from_bytes(cls, a, q, *args, **kwargs):
        int_aux = int.from_bytes(a, *args, **kwargs)
        if int_aux == 0:
            element = cls(q=q)
        else:
            element = cls(q=q, a=int_aux)
        return element

    def to_bytes(self, *args, **kwargs):
        return self.a.to_bytes(*args, **kwargs)

    def bit_length(self):
        return self.a.bit_length()


class ZqQuadraticResidues(ZqMultiplicativeGroup):
    def __init__(self, q, a=1):
        super().__init__(q=q, a=a ** 2)

    def __random__(self):
        return ZqQuadraticResidues(q=self.q, a=SystemRandom().randrange(1, self.q))

    @classmethod
    def random(cls, q):
        return ZqQuadraticResidues(q=q, a=SystemRandom().randrange(1, q))
