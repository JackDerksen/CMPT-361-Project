"""
Program:
client.py

Purpose:
Perform all client-side operations for email server

Authors:
Jack Derksen
Nolan Schlacht
De Xie

Last Updated:
19/11/2024

TO-DO:
    - Maybe create a property for socket number like in server
"""

import socket
import sys
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES

class EmailClient:
    """
    Class for email client containing methods to perform client actions
    """

    def __init__(self, server_host, username):
        """
        Initialize EmailClient object

        Properties:
        self.server_host - Name of server client is connecting to
        self.username - Client username
        self.load_keys() - Acquire client private key and server public key 
        """
        self.server_host = server_host
        self.username = username
        self.load_keys()

    def load_keys(self):
        """ 
        Load client private key and server public key
        """

        # Load client's private key and assign to property
        with open(f"{self.username}_private.pem", "rb") as f:
            private_key = RSA.import_key(f.read())
            self.private_cipher = PKCS1_OAEP.new(private_key)

        # Load server's public key and assign to property
        with open("server_public.pem", "rb") as f:
            server_key = RSA.import_key(f.read())
            self.server_cipher = PKCS1_OAEP.new(server_key)

    def connect(self):
        """ Connect to email server """

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_host, 13000))

    def authenticate(self):
        """ Perform server authentication """

        # Get credentials from user (password)
        password = input("Enter password: ")

        # Encrypt credentials and send to server
        credentials = f"{self.username}:{password}"
        encrypted_credentials = self.server_cipher.encrypt(
            credentials.encode())
        self.socket.send(encrypted_credentials)

        # Receive encrypted symmetric key from server
        response = self.socket.recv(1024)

        try:
            # Try to decrypt as symmetric key
            self.sym_key = self.private_cipher.decrypt(response)
            self.cipher = AES.new(self.sym_key, AES.MODE_ECB)

            # Send acknowledgment
            encrypted_ack = self.cipher.encrypt(b"OK".ljust(16))
            self.socket.send(encrypted_ack)
            return True

        except ValueError as e:
            # If decryption fails, it's an error message
            print(f"{response.decode()}\nTerminating. Error: {e}")
            return False

    def create_email(self):
        """ Create and send an email """

        # Wait for server prompt
        encrypted_prompt = self.socket.recv(1024)
        self.cipher.decrypt(encrypted_prompt)

        # Store email recipients
        to = input("Enter recipient usernames (separated by ';'): ")
        # Store email title
        title = input("Enter email title (max 100 chars): ")

        # Validate title length
        if len(title) > 100:
            print("Title too long. Maximum length is 100 characters.")
            return

        # Get content
        content_choice = input(
            "Enter '1' to type content or '2' to read from file: ")
        if content_choice == "1":
            content = input("Enter email content (max 1000000 chars): ")
        else:
            filename = input("Enter filename: ")
            try:
                with open(filename, "r") as f:
                    content = f.read()
            except FileNotFoundError:
                print(f"Error: File {filename} not found.")
                return

        # Validate content length
        if len(content) > 1000000:
            print("Content too long. Maximum length is 1000000 characters.")
            return

        # Construct email
        email = (f"From: {self.username}\n"
                 f"To: {to}\n"
                 f"Title: {title}\n"
                 f"Content Length: {len(content)}\n"
                 f"Content:\n"
                 f"{content}")

        # Encrypt and send
        encrypted_email = self.cipher.encrypt(
            email.encode().ljust((len(email)//16 + 1) * 16))
        self.socket.send(encrypted_email)
        print("The message is sent to the server.")

    def view_inbox(self):
        """ View inbox contents """

        # Decrypt inbox contents from server and display to client
        encrypted_list = self.socket.recv(4096)
        inbox_list = self.cipher.decrypt(encrypted_list).strip().decode()
        print("\nInbox contents:")
        print(inbox_list)

        # Send acknowledgment
        self.socket.send(self.cipher.encrypt(b"OK".ljust(16)))

    def view_email(self):
        """ View content of specific email """

        # Receive server request
        encrypted_request = self.socket.recv(1024)
        self.cipher.decrypt(encrypted_request)

        # Send email index
        index = input("Enter the email index to view: ")
        encrypted_index = self.cipher.encrypt(index.encode().ljust(16))
        self.socket.send(encrypted_index)

        # Receive and display email
        encrypted_email = self.socket.recv(4096)
        email = self.cipher.decrypt(encrypted_email).strip().decode()
        print("\nEmail content:")
        print(email)

    def terminate_connection(self):
        """ Helper function to handle connection termination """

        self.socket.close()
        print("Connection with server terminated.")

    def run(self):
        """ Main client loop """

        try:
            self.connect()
            # Password was invalid or could not decrypt symmetric key
            if not self.authenticate():
                return

            while True:
                # Receive and decrypt menu
                encrypted_menu = self.socket.recv(4096)
                menu = self.cipher.decrypt(encrypted_menu).strip().decode()
                print(menu)

                # Get user choice
                choice = input()
                # Repeats request until valid input is provided
                while choice not in ['1', '2', '3', '4']:
                    print("Invalid choice. Please enter 1, 2, 3, or 4.")
                    choice = input()

                # Encrypt and send choice
                encrypted_choice = self.cipher.encrypt(
                    choice.encode().ljust(16))
                self.socket.send(encrypted_choice)

                # Client creates and email
                if choice == '1':
                    self.create_email()
                # Client views inbox
                elif choice == '2':
                    self.view_inbox()
                # Client opens and email
                elif choice == '3':
                    self.view_email()
                # Client terminates connection
                elif choice == '4':
                    self.terminate_connection()
                    break

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.socket.close()


def main():
    """ Start client """

    # Invalid number of command line arguments
    if len(sys.argv) != 3:
        print("Usage: python client.py <server_host> <username>")
        sys.exit(1)

    # Extracts server name and username from command line arguments
    server_host = sys.argv[1]
    username = sys.argv[2]

    try:
        # Create client object and run
        client = EmailClient(server_host, username)
        client.run()
    except KeyboardInterrupt:
        print("\nClient terminated by user.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
