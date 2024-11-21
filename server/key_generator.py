from Crypto.PublicKey import RSA
import json
import os


def generate_server_keys():
    """Generate public/private key pair for the server"""
    # Generate 2048-bit RSA key pair
    key = RSA.generate(2048)

    # Export private key
    private_key = key.export_key()
    with open("server_private.pem", "wb") as f:
        f.write(private_key)

    # Export public key
    public_key = key.publickey().export_key()
    with open("server_public.pem", "wb") as f:
        f.write(public_key)


def initialize_server():
    """Initialize server directory with necessary files and structure"""
    print("Initializing server...")

    # Generate server keys
    print("Generating server keys...")
    generate_server_keys()

    # Create empty user_pass.json if it doesn't exist
    if not os.path.exists("user_pass.json"):
        print("Creating empty user_pass.json...")
        with open("user_pass.json", "w") as f:
            json.dump({}, f)

    print("\nServer initialization complete!")
    print("Created the following files:")
    print("- server_private.pem")
    print("- server_public.pem")
    print("- user_pass.json")


if __name__ == "__main__":
    initialize_server()
