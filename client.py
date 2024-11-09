"""
import socket
import sys
import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
"""


class EmailClient:
    def __init__(self, server_host, username):
        self.server_host = server_host
        self.username = username
        self.load_keys()

    def load_keys(self):
        pass


def main():
    pass


if __name__ == "__main__":
    main()
