from . import log
import traceback
from functools import reduce
from .commitment import Commitment
from .ake import DHAKE, AKE
from hashlib import sha3_512, sha3_224


class Participant:

    def __k_to_hash(self, hash):
        if self.K is None:
            raise AttributeError("Not generate K yet")
        else:
            h = hash()
            for i in self.K:
                h.update(i.to_bytes((i.bit_length() + 7) // 8, byteorder='big'))
            return format(int.from_bytes(h.digest(), byteorder='big'), 'b')

    def __init__(self, uid, commitment: Commitment, ake: AKE) -> None:
        self.uid = uid
        self.i = None
        self.pid_i = None
        self.x_i = None
        self.x_list = None
        self.k_list = None
        self.r_i = None
        self.pk_i = None
        self.commitment_i = None
        self.K = None
        self.sid = None
        self.sk = None
        self.commitment = commitment
        if ake is None:
            self.ake = DHAKE()
        else:
            self.ake = ake
        self.pk_ake = self.ake.get_public_key()

    def round_0(self, uids: list, pk_1: int, pk_2: int) -> None:
        """Execute algorithm's Round 0"""
        self.pid_i = uids
        self.i = self.pid_i.index(self.uid)
        self.k_list = [None] * len(self.pid_i)
        self.key_next, self.key_before = self.ake.common_secret(pk_peer_1=pk_1, pk_peer_2=pk_2)

    def round_1(self, pk_i) -> tuple:
        """Execute algorithm's Round 1"""
        self.x_i = self.key_next ^ self.key_before
        self.r_i = self.commitment.generate_random()
        self.pk_i = pk_i
        self.commitment_i = self.commitment.generate_commitment(pk=self.pk_i, random=self.r_i, m=self.x_i)
        return self.uid, self.commitment_i

    def round_2_1(self) -> tuple:
        """Send parameters for commitment validation. Round 2 Broadcast"""
        return self.uid, self.x_i, self.r_i

    def round_2_2(self, m_1: list, m_2: list) -> tuple:
        """Execute algorithm's Round 2"""
        acc_i = False
        try:
            x_list = list()
            for i in range(len(m_1)):
                uid_1, c_i = m_1[i]
                uid_2, x_i, r_i = m_2[i]
                if uid_1 == uid_2 and self.commitment.check_correctness(c_i, self.pk_i, r_i, x_i):
                    x_list.append(x_i)
            if len(x_list) == len(self.pid_i) and reduce(lambda x,y: x^y, x_list) == 0:
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
                self.sk = self.__k_to_hash(sha3_512)
                self.sid = self.__k_to_hash(sha3_224)
                acc_i = True
        except Exception as e:
            log.error(traceback.format_exc())
            log.error(e)
        return acc_i, self.K, self.sk, self.sid


class ParticipantCommunication:
    def __init__(self):
        pass
