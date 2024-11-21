from Crypto.PublicKey import RSA
import os


def get_client_username():
    """Get client username from directory name"""
    # Get the current directory name
    current_dir = os.path.basename(os.getcwd())
    return current_dir


def generate_client_keys(username):
    """Generate public/private key pair for a client"""
    print(f"Generating keys for client: {username}")

    # Generate 2048-bit RSA key pair
    key = RSA.generate(2048)

    # Export private key
    private_key = key.export_key()
    private_key_file = f"{username}_private.pem"
    with open(private_key_file, "wb") as f:
        f.write(private_key)

    # Export public key
    public_key = key.publickey().export_key()
    public_key_file = f"{username}_public.pem"
    with open(public_key_file, "wb") as f:
        f.write(public_key)


def initialize_client():
    """Initialize client directory with necessary files and structure"""
    print("Initializing client...")

    # Get username from directory name
    username = get_client_username()

    # Generate client keys
    generate_client_keys(username)

    # Create files directory if it doesn't exist
    if not os.path.exists("files"):
        print("Creating files directory...")
        os.makedirs("files")

    print("\nClient initialization complete!")
    print("Created the following files and directories:")
    print(f"- {username}_private.pem")
    print(f"- {username}_public.pem")
    print("- files/ (directory)")


if __name__ == "__main__":
    initialize_client()
