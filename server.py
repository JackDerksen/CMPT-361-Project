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
        """ Load server's public and private keys """

        pass

    def load_user_credentials(self):
        """ Load client credentials from JSON file """

        pass

    def load_client_public_keys(self):
        """ Load public keys for all known clients """

        pass

    def handle_client(self, client_socket, client_address):
        """ Handle individual client connection """

        pass

    def verify_credentials(self, username, password):
        """ Verify client credentials, obviously """

        pass

    def send_email(self, client_socket, cipher, sender):
        """ Handle email sending protocol """

        pass

    def view_inbox(self, client_socket, cipher, username):
        """ Handle inbox viewing protocol """

        pass

    def view_email(self, client_socket, cipher, username):
        """ Handle email viewing protocol """

        pass

    def start(self):
        """ Start up the server """

        pass


if __name__ == "__main__":
    server = EmailServer()
    server.start()
