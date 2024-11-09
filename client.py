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
        """ Load necessary keys """

        pass

    def connect(self):
        """ Connect to email server """

        pass

    def authenticate(self):
        """ Perform server authentication """

        pass

    def create_email(self):
        """ Create and send an email """

        pass

    def view_inbox(self):
        """ View inbox contents """

        pass

    def view_email(self):
        """ View content of specific email """

        pass

    def terminate_connection(self):
        """ Helper function to handle connection termination """

        self.socket.close()
        print("Connection with server terminated.")

    def run(self):
        """ Main client loop """

        pass


def main():
    """ Start client """

    pass


if __name__ == "__main__":
    main()
