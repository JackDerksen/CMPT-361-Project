# MacEwan CMPT-361 Final Project


## Python secure mail transfer protocol application

A **reasonably secure** SMTP application that works between n clients and a
server over a TCP connection.


## Developed by

- Jack Derksen
- Nolan Schlacht
- De Xie


## How to use the program

1. First, ensure that the user_pass.json file is populated with usernames and passwords.It should look something like:

```json
{
    "client1": "password1",
    "client2": "password2",
    "client3": "password3",
    "client4": "password4",
    "client5": "password5"
}
```

2. Next, run the key_generator.py script with `$ python3 key_generator.py`. This script will generate a public/private key pair for the server, generate public/private key pairs for each client listed in the JSON file, and create directories for each client to store their emails.

3. Start the server with `$ python3 server.py`

4. In a separate terminal, start a client session with `$ python3 client.py <server_host> <username>`


## How to utilize the Makefile functionality

- Clean everything: `$ make clean`
- Generate new keys and setup: `$ make setup`
- Do both (clean and setup): `$ make all`
- Run the server: `$ make run-server`
- Run a client session: `$ make run-client SERVER=localhost USERNAME=client1`
- Check what files currently exist: `$ make status`
