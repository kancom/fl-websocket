import base64

from auth import CypherRSA
from main import AUTH_DATA

rcvd_key = """MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCrrihYXpWq9/FDV5J5c7uOCgxw2wMARLWlN+jJuE6XV4PX6OZt9fWJNitJg89pXhaHyA5ehYuV9anhp7o/PQYwW4esTVMwAQ7WtQPgZ2lHOgy8w2yxRhfxSLx7K2C3n0McmExa9pr7Py/CfrebEgCzLlHv88dH34XFjSK3mYnR0wIDAQAB"""

encrypted_pass = """MlPoCzhTpnYrwxf626k+yqrd0T/RJlkDQ/B6EnS8E/IU95tlFRBPB3P2/fgldMuWfgQhG7yrbKuLfMnqnAnPuKN/RGC42/e/tpmE2BOKdE9WZqMBLFTAf6TY44Rn1JDBlu1D85qncEomDfuLTbVOpffqlaUnA8Qg+Ua+y8n1esw="""

password = "Trellus1"


def test_encrypt():
    cypher_obj = CypherRSA()
    cypher_obj.set_pubkey(pubkey=rcvd_key)
    enc_pass = cypher_obj.encrypt(password)
    assert enc_pass == encrypted_pass
