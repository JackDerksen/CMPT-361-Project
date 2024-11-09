from Crypto.PublicKey import RSA
import json
import os


def generate_key_pair(username):
    """ Generate public/private key pair for a given username """

    # Generate 2048-bit RSA key pair
    key = RSA.generate(2048)

    # Export private key
    private_key = key.export_key()
    with open(f"{username}_private.pem", "wb") as f:
        f.write(private_key)

    # Export public key
    public_key = key.publickey().export_key()
    with open(f"{username}_public.pem", "wb") as f:
        f.write(public_key)


def main():
    """ Main function to generate keys for server and known clients """

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
