from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


class AKE:
    def __init__(self):
        self.pk = None
        self.sk = None

    def get_public_key(self):
        raise NotImplementedError

    def common_secret(self, pk_peer):
        raise NotImplementedError


class DHAKE(AKE):
    parameters = None

    @classmethod
    def init_parameters(cls, g=2, k_size=2048):
        cls.parameters = dh.generate_parameters(generator=g, key_size=k_size, backend=default_backend())

    def __init__(self) -> None:
        super().__init__()
        if self.parameters is None:
            self.init_parameters()

    def get_public_key(self):
        self.sk = self.parameters.generate_private_key()
        self.pk = self.sk.public_key()
        return self.pk

    def common_secret(self, pk_peer):
        shared_key = self.sk.exchange(pk_peer)
        super().__init__()
        return shared_key