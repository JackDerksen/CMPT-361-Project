# Variables
PYTHON = python3
PEM_FILES = $(wildcard *.pem)
CLIENT_DIRS = $(wildcard client*/)

# Default target
all: clean setup

# Create user_pass.json file
user_pass.json:
	@echo "Creating user_pass.json..."
	@echo '{\n    "client1": "password1",\n    "client2": "password2",\n    "client3": "password3",\n    "client4": "password4",\n    "client5": "password5"\n}' > user_pass.json

# Set up the system by running key generator
setup: user_pass.json
	$(PYTHON) key_generator.py

# Clean up all generated files
clean:
	rm -f *.pem
	rm -rf client*/
	rm -rf __pycache__/
	rm -f user_pass.json

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

.PHONY: all clean setup run-server run-client status
