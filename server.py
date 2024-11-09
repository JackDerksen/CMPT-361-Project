"""
import json
import socket
import os
import datetime
import sys
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
import glob
"""


class EmailServer:
    def __init__(self, port=1300):
        self.port = port
        self.load_server_keys()
        self.load_user_credentials()
        self.load_client_public_keys()

    def load_server_keys(self):
        pass

    def load_user_credentials(self):
        pass

    def load_client_public_keys(self):
        pass


def main():
    pass


if __name__ == "__main__":
    main()
