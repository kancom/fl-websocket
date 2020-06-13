import base64

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA


class CypherRSA(object):
    def __init__(self):
        self.pubkey = None
        self.recp_key = None
        self.cipher_rsa = None

    def set_pubkey(self, pubkey: str):
        assert isinstance(pubkey, str)
        self.pubkey = base64.b64decode(pubkey.encode("utf8"))
        self.recp_key = RSA.import_key(self.pubkey)
        self.cipher_rsa = PKCS1_v1_5.new(self.recp_key)

    def encrypt(self, msg):
        msg_bytes = msg.encode("utf8")
        enc_session_key = self.cipher_rsa.encrypt(msg_bytes)
        return base64.b64encode(enc_session_key).decode()
