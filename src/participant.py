from random import getrandbits
from functools import reduce


class Participant:
    def __init__(self, uid, k1: int, k2: int) -> None:
        self.uid = uid
        self.i = None
        self.pid_i = []
        self.key_next = k1
        self.key_before = k2
        self.x_i = None
        self.x_list = []
        self.k_list = []
        self.r_i = None
        self.K = None

    def round_0(self, uids: list):
        self.pid_i = uids
        self.i = self.pid_i.index(self.uid)
        self.k_list = [None] * len(self.pid_i)

    def round_1(self) -> tuple:
        self.x_i = self.key_next ^ self.key_before
        # TODO: Generate Commitment
        self.r_i = getrandbits(1024)
        commitment = getrandbits(1024)
        # TODO: Broadcast M1
        return self.uid, commitment

    def round_2_1(self) -> tuple:
        return self.uid, self.x_i, self.r_i

    def round_2_2(self, x_list: list) -> None:
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
