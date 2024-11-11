import json
import socket
import os
import datetime
import sys
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
import glob


class EmailServer:
    def __init__(self, port=13000):
        self.port = port
        self.load_server_keys()
        self.load_user_credentials()
        self.load_client_public_keys()

    def load_server_keys(self):
        """ Load server's public and private keys """

        with open("server_private.pem", "rb") as f:
            self.private_key = RSA.import_key(f.read())
        self.private_cipher = PKCS1_OAEP.new(self.private_key)

    def load_user_credentials(self):
        """ Load client credentials from JSON file """

        with open("user_pass.json", "r") as f:
            self.user_credentials = json.load(f)

    def load_client_public_keys(self):
        """ Load public keys for all known clients """

        self.client_public_keys = {}
        for username in self.user_credentials.keys():
            with open(f"{username}_public.pem", "rb") as f:
                key = RSA.import_key(f.read())
                # Create a OKCS1_OAEP cipher object for the imported key
                self.client_public_keys[username] = PKCS1_OAEP.new(key)

    def handle_client(self, client_socket, client_address):
        """ Handle individual client connection """

        try:
            # Authentication
            encrypted_creds = client_socket.recv(1024)
            decrypted_creds = self.private_cipher.decrypt(encrypted_creds)
            username, password = decrypted_creds.decode().split(':')

            # Verify credentials
            if not self.verify_credentials(username, password):
                client_socket.send("Invalid username or password".encode())
                print(f"The received client information: {
                      username} is invalid (Connection Terminated).")
                return

            # Generate and send a symmetric key
            sym_key = get_random_bytes(32)  # 256-bit key
            encrypted_sym_key = self.client_public_keys[username].encrypt(
                sym_key)
            client_socket.send(encrypted_sym_key)
            print(
                f"Connection accepted, symmetric key generated for client: {username}")

            # Wait for client's acknowledgement
            cipher = AES.new(sym_key, AES.MODE_ECB)
            encrypted_ack = client_socket.recv(1024)
            decrypted_ack = cipher.decrypt(encrypted_ack).strip()
            if decrypted_ack != b"OK":
                return

            # Main client service loop
            while True:
                menu = '''
\nSelect the operation:
 1) Create and send an email
 2) Display the inbox list
 3) Display the email contents
 4) Terminate the connection
Choice:
'''

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
                    print(f"Invalid choice, terminating connection with {
                        username}.")
                    break

        finally:
            client_socket.close()

    def verify_credentials(self, username, password):
        """ Verify client credentials, obviously """

        return (username in self.user_credentials and
                self.user_credentials[username] == password)

    def handle_send_email(self, client_socket, cipher, sender):
        """ Handle email sending protocol for client """

        # Send request for email
        encrypted_msg = cipher.encrypt(b"Send the email".ljust(16))
        client_socket.send(encrypted_msg)

        # Receive and process email
        encrypted_email = client_socket.recv(4096)  # Might need to adjust size
        email_content = cipher.decrypt(encrypted_email).strip().decode()

        # Parse email content
        lines = email_content.split('\n')
        recipients = lines[1].split(': ')[1].split(';')
        content_length = int(lines[3].split(': ')[1])

        # Add timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
            filename = f"{recipient}/{sender}_{title}.txt"
            with open(filename, "w") as f:
                f.write(email_with_time)

        print(f"An email from {sender} is sent to {', '.join(
            recipients)} has a content length of {content_length}")

    def handle_view_inbox(self, client_socket, cipher, username):
        """ Handle inbox viewing protocol for client """

        # Get all emails in the user's directory
        emails = []
        for filepath in glob.glob(f"{username}/*_*.txt"):
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
        inbox_list = "\n".join(f"{i+1}. From: {sender}, Time: {timestamp}, Title: {title}"
                               for i, (sender, timestamp, title) in enumerate(emails))

        # Send to client
        encrypted_list = cipher.encrypt(
            inbox_list.encode().ljust((len(inbox_list)//16 + 1) * 16))
        client_socket.send(encrypted_list)

        # Wait for acknowledgment
        client_socket.recv(1024)

    def handle_view_email(self, client_socket, cipher, username):
        """ Handle email viewing protocol for client """

        # Request email index
        request = cipher.encrypt(b"the server request email index".ljust(32))
        client_socket.send(request)

        # Get email index
        encrypted_index = client_socket.recv(1024)
        index = int(cipher.decrypt(encrypted_index).strip())

        # Get email content
        emails = sorted(glob.glob(f"{username}/*_*.txt"),
                        key=lambda x: os.path.getmtime(x), reverse=True)

        if 0 <= index - 1 < len(emails):
            with open(emails[index-1], "r") as f:
                content = f.read()
                encrypted_content = cipher.encrypt(
                    content.encode().ljust((len(content)//16 + 1) * 16))
                client_socket.send(encrypted_content)
        else:
            error_msg = "Invalid email index"
            client_socket.send(cipher.encrypt(error_msg.encode().ljust(16)))

    def start(self):
        """ Start up the server """

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('', self.port))
        server_socket.listen(5)
        print(f"Server listening on port {self.port}")

        while True:
            client_socket, client_address = server_socket.accept()

            # Fork for each client connection
            pid = os.fork()
            if pid == 0:  # Child process
                server_socket.close()
                self.handle_client(client_socket, client_address)
                sys.exit(0)
            else:  # Parent process
                client_socket.close()


if __name__ == "__main__":
    server = EmailServer()
    server.start()
