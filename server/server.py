"""
Program:
server.py

Purpose:
Perform all server-side operations for email server

Authors:
Jack Derksen
Nolan Schlacht
De Xie

Last Updated:
19/11/2024

TO-DO:
    - 
"""

import json
import socket
import os
import glob
import datetime
import sys
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes


class EmailServer:
    def __init__(self, port=13000):
        """
        Initialize EmailServer object.

        Parameters:
            port (int): Port number for server to listen on, defaults to 13000

        Properties:
            self.port: Server port number
            self.private_key: Server's RSA private key
            self.private_cipher: PKCS1_OAEP cipher using server's private key
            self.user_credentials: Dictionary of valid username/password pairs
            self.client_public_keys: Dictionary of client public key ciphers
        """
        self.port = port
        self.load_server_keys()
        self.load_user_credentials()
        self.client_public_keys = {}

    def load_server_keys(self):
        """
        Load the server's private key from PEM file.

        Loads server_private.pem and initializes the PKCS1_OAEP cipher
        for decryption of client messages.

        Raises:
            SystemExit: If key files not found or invalid
        """

        # Server private key file exist
        try:
            with open("server_private.pem", "rb") as f:
                self.private_key = RSA.import_key(f.read())
                self.private_cipher = PKCS1_OAEP.new(self.private_key)

        # Server private key file does not exist or cannot be found
        except FileNotFoundError:
            print("Error: Server keys not found. Please run key_generator.py first.")
            sys.exit(1)

    def load_user_credentials(self):
        """
        Load user credentials from JSON file.

        Reads user_pass.json containing valid username/password pairs.

        Raises:
            SystemExit: If credentials file not found
        """

        # JSON file for user credentials exists
        try:
            with open("user_pass.json", "r") as f:
                self.user_credentials = json.load(f)
        # JSON file for user credentials does not exist or cannot be found
        except FileNotFoundError:
            print("Error: user_pass.json not found.")
            sys.exit(1)

    def setup_client_directory(self, username):
        """
        Create directory structure for a client.

        Parameters:
            username (str): Client's username

        Returns:
            str: Path to client's directory

        Creates:
            - Client directory named after username
            - inbox/ subdirectory for storing emails
        """

        client_dir = os.path.join(username)
        inbox_dir = os.path.join(client_dir, "inbox")
        os.makedirs(inbox_dir, exist_ok=True)
        return client_dir

    def store_client_public_key(self, username, public_key_data):
        """
        Store client's public key and load it into memory.

        Parameters:
            username (str): Client's username
            public_key_data (bytes): Client's public key data

        Stores key in client's directory and initializes PKCS1_OAEP cipher
        for encryption of messages to this client.
        """
        client_dir = self.setup_client_directory(username)
        key_path = os.path.join(client_dir, f"{username}_public.pem")

        # Write client public key data to to new client public key PEM file
        with open(key_path, "wb") as f:
            f.write(public_key_data)

        key = RSA.import_key(public_key_data)
        self.client_public_keys[username] = PKCS1_OAEP.new(key)

    def load_client_public_key(self, username):
        """
        Load a client's public key from their directory.

        Parameters:
            username (str): Client's username

        Returns:
            PKCS1_OAEP cipher or None if key not found

        Loads existing client public key and initializes cipher for encryption.
        """
        if username not in self.client_public_keys:
            key_path = os.path.join(username, f"{username}_public.pem")

            if not os.path.exists(key_path) or os.path.getsize(key_path) == 0:
                return None

            try:
                with open(key_path, "rb") as f:
                    key_data = f.read()
                    key = RSA.import_key(key_data)
                    self.client_public_keys[username] = PKCS1_OAEP.new(key)
            except Exception:
                return None

        return self.client_public_keys.get(username)

    def handle_client(self, client_socket, client_address):
        """
        Handle individual client connection and operations.

        Parameters:
            client_socket: Socket connection to client
            client_address: Client's address information

        Handles:
            - Client authentication
            - Public key exchange for first connections
            - Symmetric key generation
            - Main service loop for email operations
        """
        try:
            # Get and decrypt credentials
            encrypted_creds = client_socket.recv(1024)

            decrypted_creds = self.private_cipher.decrypt(encrypted_creds)
            username, password = decrypted_creds.decode().split(':')

            # Verify credentials
            if not self.verify_credentials(username, password):
                #print("DEBUG: Verification failed")
                client_socket.send(b"Invalid username or password")
                print(f"The received client information: {
                      username} is invalid (Connection Terminated).")
                return

            # Check if we have the client's public key
            client_cipher = self.load_client_public_key(username)
            if not client_cipher:
                # First time connection - receive client's public key
                client_socket.send(b"NEW_CLIENT")
                public_key_data = client_socket.recv(2048)
                self.store_client_public_key(username, public_key_data)
                client_cipher = self.client_public_keys[username]

            # Generate and send symmetric key
            sym_key = get_random_bytes(32)  # 256-bit key
            encrypted_sym_key = self.client_public_keys[username].encrypt(
                sym_key)
            client_socket.send(encrypted_sym_key)

            # Create cipher for this session
            cipher = AES.new(sym_key, AES.MODE_ECB)

            # Wait for client's acknowledgment
            encrypted_ack = client_socket.recv(1024)
            decrypted_ack = cipher.decrypt(encrypted_ack).strip()

            
            if decrypted_ack != b"OK":
                return

            # Main service loop
            while True:
                menu = (
                    "\n\nSelect the operation:\n"
                    "1) Create and send an email\n"
                    "2) Display the inbox list\n"
                    "3) Display the email contents\n"
                    "4) Terminate the connection\n"
                    "choice: "
                )
                encrypted_menu = cipher.encrypt(
                    menu.encode().ljust((len(menu) // 16 + 1) * 16))
                client_socket.send(encrypted_menu)

                # Get client's choice
                encrypted_choice = client_socket.recv(1024)
                choice = cipher.decrypt(encrypted_choice).strip().decode()

                if choice == "1":
                    self.handle_send_email(client_socket, cipher, username)
                elif choice == "2":
                    self.handle_view_inbox(client_socket, cipher, username)
                elif choice == "3":
                    self.handle_view_email(client_socket, cipher, username)
                else:
                    print(f"Terminating connection with {username}")
                    break

        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
        finally:
            client_socket.close()

    def verify_credentials(self, username, password):
        """
        Verify client credentials against stored values.

        Parameters:
            username (str): Client's username
            password (str): Client's password

        Returns:
            bool: True if credentials are valid, False otherwise
        """
        return (username in self.user_credentials and
                self.user_credentials[username] == password)

    def handle_send_email(self, client_socket, cipher, sender):
        """
        Handle email sending protocol with client.

        Parameters:
            client_socket: Socket connection to client
            cipher: AES cipher for this session
            sender (str): Username of sending client

        Receives encrypted email from client, adds timestamp,
        and saves to each recipient's inbox directory.
        """
        encrypted_msg = cipher.encrypt(b"Send the email".ljust(16))
        client_socket.send(encrypted_msg)

        # Receive and process email
        encrypted_email = client_socket.recv(4096)
        email_content = cipher.decrypt(encrypted_email).strip().decode()

        # Parse email content
        lines = email_content.split('\n')
        recipients = lines[1].split(': ')[1].split(';')
        content_length = int(lines[3].split(': ')[1])

        # Add timestamp
        timestamp = datetime.datetime.now()
        email_with_time = (
            f"{lines[0]}\n"  # From
            f"{lines[1]}\n"  # To
            f"Time and Date: {timestamp}\n"
            f"{lines[2]}\n"  # Title
            f"{lines[3]}\n"  # Content Length
            f"{lines[4]}\n"  # Content marker
            f"{lines[5]}"    # Content
        )

        # Save for each recipient
        title = lines[2].split(': ')[1]
        for recipient in recipients:
            recipient = recipient.strip()
            inbox_path = os.path.join(
                recipient, "inbox", f"{sender}_{title}.txt")
            with open(inbox_path, "w") as f:
                f.write(email_with_time)

        print(f"An email from {sender} is sent to {
              ';'.join(recipients)} has a content length of {content_length}")

    def handle_view_inbox(self, client_socket, cipher, username):
        """
        Handle inbox viewing protocol with client.

        Parameters:
            client_socket: Socket connection to client
            cipher: AES cipher for this session
            username (str): Client's username

        Retrieves list of emails in client's inbox,
        sorts by timestamp, and sends encrypted list to client.
        """
        inbox_path = os.path.join(username, "inbox")
        emails = []

        for filepath in glob.glob(os.path.join(inbox_path, "*.txt")):
            with open(filepath, "r") as f:
                content = f.read()
                lines = content.split('\n')
                sender = lines[0].split(': ')[1]
                timestamp = lines[2].split(': ')[1]
                title = lines[3].split(': ')[1]
                emails.append((sender, timestamp, title))

        # Sort by timestamp
        emails.sort(key=lambda x: x[1], reverse=True)

        # Format inbox list
        inbox_list = "Index From DateTime Title\n"
        inbox_list += "\n".join(
            f"{i+1} {sender} {timestamp} {title}"
            for i, (sender, timestamp, title) in enumerate(emails)
        )

        # Send to client
        encrypted_list = cipher.encrypt(
            inbox_list.encode().ljust((len(inbox_list) // 16 + 1) * 16))
        client_socket.send(encrypted_list)

        # Wait for acknowledgment
        client_socket.recv(1024)

    def handle_view_email(self, client_socket, cipher, username):
        """
        Handle email viewing protocol with client.

        Parameters:
            client_socket: Socket connection to client
            cipher: AES cipher for this session
            username (str): Client's username

        Receives email index from client, retrieves corresponding
        email from inbox, and sends encrypted content to client.
        """
        # Request email index
        request = cipher.encrypt(b"the server request email index".ljust(32))
        client_socket.send(request)

        # Get email index
        encrypted_index = client_socket.recv(1024)
        index = int(cipher.decrypt(encrypted_index).strip())

        # Get email content
        inbox_path = os.path.join(username, "inbox")
        emails = sorted(
            glob.glob(os.path.join(inbox_path, "*.txt")),
            key=lambda x: os.path.getmtime(x),
            reverse=True
        )

        if 0 <= index - 1 < len(emails):
            with open(emails[index-1], "r") as f:
                content = f.read()
                encrypted_content = cipher.encrypt(
                    content.encode().ljust((len(content) // 16 + 1) * 16))
                client_socket.send(encrypted_content)
        else:
            error_msg = "Invalid email index"
            client_socket.send(cipher.encrypt(error_msg.encode().ljust(16)))

    def start(self):
        """
        Start the email server.

        Creates socket, binds to port, and enters main server loop.
        Uses fork() to handle multiple clients concurrently.
        Handles graceful shutdown on keyboard interrupt.
        """

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('', self.port))
        server_socket.listen(5)
        print("The server is ready to accept connections")

        while True:
            try:
                client_socket, client_address = server_socket.accept()

                # Fork for each client connection
                pid = os.fork()
                if pid == 0:  # Child process
                    # Close server socket to accept new connections
                    server_socket.close()
                    # Perform client operations
                    self.handle_client(client_socket, client_address)
                    sys.exit(0)
                else:  # Parent process
                    client_socket.close()
            except KeyboardInterrupt:
                print("\nServer shutting down...")
                break
            except Exception as e:
                print(f"Error accepting connection: {e}")


if __name__ == "__main__":
    server = EmailServer()
    server.start()
