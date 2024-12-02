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
23/11/2024

TO-DO:
    - Maybe create a property for socket number like in server
"""

import socket
import sys
import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES

class EmailClient:
    def __init__(self):
        """
        Initialize EmailClient object.

        Properties:
            self.server_host (str): Hostname/IP of server to connect to
            self.username (str): Client's username for authentication
            self.password (str): Client's password for authentication
            self.private_cipher: PKCS1_OAEP cipher using client's private key
            self.public_key_data (bytes): Client's public key data
            self.server_cipher: PKCS1_OAEP cipher using server's public key

        Raises:
            SystemExit: Key file(s) not found in client directory
        """

        self.server_host = input("Enter the server IP or name: ")
        self.username = input("Enter your username: ")
        self.password = input("Enter your password: ")

        try:
            # Load client's private key
            with open(f"{self.username}_private.pem", "rb") as f:
                private_key = RSA.import_key(f.read())
                self.private_cipher = PKCS1_OAEP.new(private_key)

            # Load client's public key
            with open(f"{self.username}_public.pem", "rb") as f:
                self.public_key_data = f.read()

            # Load server's public key
            with open("server_public.pem", "rb") as f:
                server_key = RSA.import_key(f.read())
                self.server_cipher = PKCS1_OAEP.new(server_key)

        except FileNotFoundError:
            print("Missing certain PEM files.")
            print("Terminating.")
            sys.exit(1)

    def connect(self):
        """
        Establish connection to email server.

        Creates a TCP socket connection to the server using the stored
        server hostname and port 13000.

        Raises:
            SystemExit: If connection fails
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, 13000))
        except Exception:
            print("Failed to connect to server.")
            print("Terminating.")
            sys.exit(1)

    def authenticate(self):
        """
        Perform authentication with the server.

        Sends encrypted credentials to server and handles the authentication
        protocol including key exchange for first-time connections.

        Returns:
            bool: True if authentication successful, False otherwise

        Sets:
            self.sym_key: Symmetric key for session encryption
            self.cipher: AES cipher using symmetric key
        """
        try:
            # Encrypt credentials with server's public key and send
            credentials = f"{self.username}:{self.password}"
            encrypted_credentials = self.server_cipher.encrypt(
                credentials.encode())
            self.socket.send(encrypted_credentials)

            # Get server response
            response = self.socket.recv(1024)

            # Handle server response
            if response == b"NEW_CLIENT":
                self.socket.send(self.public_key_data)
                # Receive symmetric key
                response = self.socket.recv(1024)
            elif response == b"Invalid username or password":
                print("Invalid username or password.")
                print("Terminating.")
                return False

            try:
                # Decrypt symmetric key and create cipher
                self.sym_key = self.private_cipher.decrypt(response)
                self.cipher = AES.new(self.sym_key, AES.MODE_ECB)

                # Send acknowledgment
                encrypted_ack = self.cipher.encrypt(b"OK".ljust(16))
                self.socket.send(encrypted_ack)
                return True
                

            except Exception as _:
                print("Decryption of symmetric key failed.")
                print("Terminating.")
                return False

        except Exception as _:
            print("Error validating credentials.")
            print("Terminating.")
            return False

    def create_email(self):
        """
        Create and send an email message.

        Prompts user for email details including recipients, title, and content.
        Content can be loaded from a file or entered directly.
        Validates message lengths and sends encrypted email to server.

        Message format:
            From: [username]
            To: [recipients]
            Title: [title]
            Content Length: [length]
            Content:
            [content]
        """
        # Wait for server prompt
        # encrypted_prompt = self.socket.recv(1024)
        # self.cipher.decrypt(encrypted_prompt)
        self.recv_with_challenge()

        # Get email details
        recipients = input("Enter destinations (separated by ;): ")
        title = input("Enter title: ")

        # Validate title length
        if len(title) > 100:
            print("Error: Title exceeds maximum length of 100 characters")
            return

        # Get content choice
        content_choice = input(
            "Would you like to load contents from a file?(Y/N) ")

        if content_choice.upper() == 'Y':
            filename = input("Enter filename: ")
            filepath = os.path.join("files", filename)
            try:
                with open(filepath, "r") as f:
                    content = f.read()
            except FileNotFoundError:
                print(f"Error: File {filename} not found in files directory")
                return
        else:
            content = input("Enter message contents: ")

        # Validate content length
        if len(content) > 1000000:
            print("Error: Content exceeds maximum length of 1,000,000 characters")
            return

        # Construct email
        email = (
            f"From: {self.username}\n"
            f"To: {recipients}\n"
            f"Title: {title}\n"
            f"Content Length: {len(content)}\n"
            f"Content:\n"
            f"{content}"
        )

        # Encrypt and send
        self.send_with_challenge(email)
        print("The message is sent to the server.")

    def view_inbox(self):
        """
        Display list of emails in inbox.

        Receives encrypted inbox listing from server, decrypts and displays it.
        Sends acknowledgment back to server after displaying.
        """
        inbox_list = self.recv_with_challenge()
        print(inbox_list)

        # Send acknowledgment
        self.send_with_challenge("OK")

    def view_email(self):
        """
        Display contents of a specific email.

        Prompts user for email index, sends request to server,
        receives and displays the decrypted email contents.
        """
        # Receive server request
        # encrypted_request = self.socket.recv(1024)
        # self.cipher.decrypt(encrypted_request)
        self.recv_with_challenge()

        # Send email index
        index = input("Enter the email index you wish to view: ")
        self.send_with_challenge(index)

        # Receive and display email
        email = self.recv_with_challenge()
        if not email.startswith("Invalid"):
            print(email)
        else:
            print(f"\nError: {email}")

    def recv_with_challenge(self):
        encrypted_msg = self.socket.recv(2048)
        decrypted_msg = self.cipher.decrypt(encrypted_msg).strip().decode()
        self.next_ans = int(decrypted_msg[:6].replace(".","")) + \
                int(decrypted_msg[6:12].replace(".",""))
        self.next_ans = f"{self.next_ans:}"
       
        return decrypted_msg[12:]
        
    def send_with_challenge(self, message):
        message = self.next_ans.rjust(6,".") + message
        padded_message = message.encode().ljust((len(message) // 16 + 1) * 16)
        self.socket.send(self.cipher.encrypt(padded_message))
    def run(self):
        """
        Main client operation loop.

        Establishes connection, performs authentication, and enters
        main command loop for email operations. Handles:
            1. Creating/sending emails
            2. Viewing inbox
            3. Viewing specific emails
            4. Terminating connection

        Ensures proper cleanup of resources on exit.
        """
        try:
            self.connect()
            if not self.authenticate():
                return

            # Get first challenge
            self.recv_with_challenge()
            
            while True:
                # Receive and decrypt menu
                menu = self.recv_with_challenge()
                print(menu, end='')

                # Get user choice
                choice = input().strip()

                # Encrypt and send choice
                self.send_with_challenge(choice)

                # Handle user choice
                if choice == '1':
                    self.create_email()
                elif choice == '2':
                    self.view_inbox()
                elif choice == '3':
                    self.view_email()
                elif choice == '4':
                    print("The connection is terminated with the server.")
                    break

        except KeyboardInterrupt:
            print("\nClient terminated by user.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.socket.close()


def main():
    """
    Entry point for the email client application.

    Creates and runs an EmailClient instance, handling any
    keyboard interrupts for graceful shutdown.
    """
    try:
        client = EmailClient()
        client.run()
    except KeyboardInterrupt:
        print("\nClient terminated by user.")


if __name__ == "__main__":
    main()
