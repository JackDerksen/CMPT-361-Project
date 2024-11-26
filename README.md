# MacEwan CMPT-361 Final Project: A Python secure mail transfer protocol application

This is a **reasonably secure** SMTP application that works between 5 clients and a single central server over a TCP connection. Utilizes AES message encryption.


## Developed by

- Jack Derksen
- Nolan Schlacht
- De Xie


## How to use the program

1. First, ensure that the user_pass.json file (located in the server directory) is populated with usernames and passwords. It should look something like:

```json
{
    "client1": "password1",
    "client2": "password2",
    "client3": "password3",
    "client4": "password4",
    "client5": "password5"
}
```

2. Next, ensure the server directory contains a public/private key pair. If not, generate keys for the server by running the `key_generator.py` script from within the server directory.

3. Ensure an up-to-date copy of the server's public key exists in the directory of the client you wish to use. Also, generate a public/private client key pair if they do not exist already. Just like with the server, run the `key_generator.py` script from within that client's directory.

4. Navigate to the server directory and start the server program with `$ python3 server.py`

5. On a separate machine or a separate terminal instance, navigate to the directory of the client you would like to use. Start their client program with`$ python3 client.py`. Follow the prompts to connect to the server. If it is the first time that client has connected to the server, they will automatically exchange their public keys with each other for the purposes of encrypting/decrypting messages.

6. If you wish to send a message from one client to another, ensure that recipient client's directory is also properly populated (ie. that it also contains an up-to-date copy of the server's public key, and that their own client public/private key pair has been generated).


## How to use the makefile

The makefile in this project only exists for the purposes of testing and debugging, so we don't have to manually add and move all of this stuff around. Its use-cases obviously wouldn't make sense the way the application would be used in real life, with each client having a completely isolated machine with no view of the overall file structure.

### Available commands
* `make client <client name>` - Create/populate a client directory
* `make pubkey <target client name>` - Copy server's public key to a client directory
* `make clean` - Clean test files while preserving directory structure
* `make cleanall` - Remove all client directories and their server inboxes

### Make a new client directory
The makefile can be used to auto-generate a new client directory. Run `$ make client <client name>` from the root project directory. For example, running `$ make client client2` will create a new client directory for 'client2,' populated with the following:

  - client.py (the client program)
  - key_generator.py script
  - files/ directory (for storing files to be sent in messages)
  - server_public.pem (copy of server's current public key)

And will automatically run the key_generator script to create:
  - client2_private.pem
  - client2_public.pem

### Copy over the server's public key
The makefile can copy over the server's current public key to a client directory of your choosing. Run `$make pubkey <target client name>` to copy it over. For example, `$ make pubkey client1` will copy the server's public key into client1's directory. This is useful when the server's keys have been regenerated and clients need the updated public key.

### Clean test files but keep directories
To clean out test files while preserving the directory structure, run `$ make clean`. This will:

- Remove all files from each client's files/ directory
- Remove all client key files (*_private.pem, *_public.pem)
- Clean out server-side client inbox directories
- Preserve the basic directory structure and program files

### Complete cleanup
This one is a pretty intensive cleanup, use at your own risk. To remove all client directories and their corresponding server inboxes, run `make cleanall`. This will:
- Remove all client directories completely (won't touch 'client_files/')
- Remove their corresponding server-side inbox directories
- Leave only the server directory and template files

### A common usage example of the makefile:
1. Set up a new client using `$ make client client1`
2. Update the client with the server's public key using `$ make pubkey client1`
3. Clean out their files for a fresh start with `$ make clean`
4. If needed, completely reset the system with `$ make cleanall`
