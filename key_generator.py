"""
Program: 
key_generator.py

Purpose: 
Generate public/private key pairs for the server and all clients

Authors: 
Jack Derksen
Nolan Schlacht
De Xie

Last Updated: 
18/11/2024

Comments: 
Can be ran in directory using 'make keys' in CLI

"""

from Crypto.PublicKey import RSA
import json
import os


def generate_key_pair(username):
    """ 
    Generate public/private key pairs and export to PEM files 

    Input:
    username (str): Name of public/private key owner

    Return:
    None
    """

    # Generate 2048-bit RSA key pair
    key = RSA.generate(2048)

    # Export private key to PEM file
    private_key = key.export_key()
    with open(f"{username}_private.pem", "wb") as f:
        f.write(private_key)

    # Export public key to PEM file
    public_key = key.publickey().export_key()
    with open(f"{username}_public.pem", "wb") as f:
        f.write(public_key)


def main():
    """
    Call key generation function for server and client. Display generation status.
    """
    # Generate keys for server
    print("Generating server keys...")
    generate_key_pair("server")

    # Read user credentials from JSON
    with open("user_pass.json", "r") as f:
        user_pass = json.load(f)

    # Generate keys for each user
    print("Generating client keys...")
    for username in user_pass.keys():
        generate_key_pair(username)

        # Create user directory on server side
        if not os.path.exists(username):
            os.makedirs(username)
    
    # Display generated files and directories
    print("Key generation complete!")
    print("Created the following files:")
    print("- server_private.pem")
    print("- server_public.pem")
    for username in user_pass.keys():
        print(f"- {username}_private.pem")
        print(f"- {username}_public.pem")
        print(f"- {username}/ (directory)")


if __name__ == "__main__":
    main()
