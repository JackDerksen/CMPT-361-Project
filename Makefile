# Variables
PYTHON = python3
PEM_FILES = $(wildcard *.pem)
CLIENT_DIRS = $(wildcard client*/)

# Default target
all: clean json keys

# Create only the json file
json:
	@echo "Creating user_pass.json..."
	@echo '{"client1": "password1", "client2": "password2", "client3": "password3", "client4": "password4", "client5": "password5"}' > user_pass.json
	@echo "Created user_pass.json with default credentials"
	@echo "You can modify the passwords in user_pass.json before running 'make setup'"

# Set up the system by running key generator
keys: user_pass.json
	@echo "Generating keys based on user_pass.json..."
	$(PYTHON) key_generator.py

# Clean up all generated files
clean:
	rm -f *.pem
	rm -rf client*/
	rm -rf __pycache__/
	rm -f user_pass.json
	@echo "Cleaned all generated files"

# Run the server
run-server:
	$(PYTHON) server.py

# Run a client (usage: make run-client SERVER=localhost USERNAME=client1)
run-client:
	$(PYTHON) client.py $(SERVER) $(USERNAME)

# Show current .pem files and client directories
status:
	@echo "Configuration Files:"
	@ls -l user_pass.json 2>/dev/null || echo "No user_pass.json found"
	@echo "\nPEM Files:"
	@ls -l *.pem 2>/dev/null || echo "No .pem files found"
	@echo "\nClient Directories:"
	@ls -d client*/ 2>/dev/null || echo "No client directories found"

.PHONY: all clean json keys run-server run-client status
