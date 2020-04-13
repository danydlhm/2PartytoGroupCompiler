from random import getrandbits
from functools import reduce
from .commitment import Commitment


class Participant:
    def __init__(self, uid, k1: int, k2: int, commitment: Commitment) -> None:
        self.uid = uid
        self.i = None
        self.pid_i = []
        self.key_next = k1
        self.key_before = k2
        self.x_i = None
        self.x_list = []
        self.k_list = []
        self.r_i = None
        self.pk_i = None
        self.commitment_i = None
        self.K = None
        self.commitment = commitment

    def round_0(self, uids: list) -> None:
        self.pid_i = uids
        self.i = self.pid_i.index(self.uid)
        self.k_list = [None] * len(self.pid_i)

    def round_1(self) -> tuple:
        self.x_i = self.key_next ^ self.key_before
        self.r_i = self.commitment.generate_random()
        self.pk_i = self.commitment.generate_parameters()
        # TODO: Check if algorithm does not need the i parameter
        self.commitment_i = self.commitment.generate_commitment(pk=self.pk_i, random=self.r_i, m=self.x_i)
        # TODO: Broadcast M1
        return self.uid, self.commitment_i, self.pk_i

    def round_2_1(self) -> tuple:
        return self.uid, self.x_i, self.r_i

    def round_2_2(self, x_list: list) -> bool:
        # TODO: Broadcast acc_i and check correctness
        acc_i = False
        self.x_list = x_list
        self.k_list[self.i] = self.key_before
        for j in range(1, len(self.pid_i) + 1):
            aux_index = self.i - j
            if aux_index >= 0:
                x_list_aux = self.x_list[aux_index:self.i]
            else:
                x_list_aux = self.x_list[:self.i] + self.x_list[aux_index:]
            x_list_aux = [self.key_before] + x_list_aux
            k_i_j = reduce(lambda x, y: x ^ y, x_list_aux)
            self.k_list[aux_index] = k_i_j
        self.K = tuple(self.k_list + self.pid_i)
        acc_i = True
        return acc_i
