##################################################################
# THIS MAKEFILE IS AI-GENERATED, INTENDED FOR TESTING PURPOSES!! #
##################################################################

# Directories
SERVER_DIR := server
CLIENT_DIRS := client1 client2 client3 client4 client5
CLIENT_FILES_DIR := client_files

# Default target
.PHONY: all
all:
	@echo "Available commands:"
	@echo "  make client <clientname>  - Create/populate client directory"
	@echo "  make pubkey <clientname>  - Copy server's public key to client directory"
	@echo "  make clean                - Clean all test files"
	@echo "  make cleanall             - Remove all client directories and their server inboxes"

# Target to create/populate client directory
.PHONY: client
client:
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "Usage: make client <clientname>"; \
		exit 1; \
	fi
	$(eval CLIENT_NAME := $(filter-out $@,$(MAKECMDGOALS)))
	@if [ ! -d "$(CLIENT_NAME)" ]; then \
		echo "Creating new client directory: $(CLIENT_NAME)"; \
		mkdir -p $(CLIENT_NAME)/files; \
		cp $(CLIENT_FILES_DIR)/client.py $(CLIENT_NAME)/; \
		cp $(CLIENT_FILES_DIR)/key_generator.py $(CLIENT_NAME)/; \
		cp $(SERVER_DIR)/server_public.pem $(CLIENT_NAME)/; \
	else \
		echo "Populating existing client directory: $(CLIENT_NAME)"; \
		mkdir -p $(CLIENT_NAME)/files; \
		cp -f $(CLIENT_FILES_DIR)/client.py $(CLIENT_NAME)/; \
		cp -f $(CLIENT_FILES_DIR)/key_generator.py $(CLIENT_NAME)/; \
		cp -f $(SERVER_DIR)/server_public.pem $(CLIENT_NAME)/; \
	fi
	@echo "Done setting up $(CLIENT_NAME)"

# Target to copy server's public key to client directory
.PHONY: pubkey
pubkey:
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "Usage: make pubkey <clientname>"; \
		exit 1; \
	fi
	$(eval CLIENT_NAME := $(filter-out $@,$(MAKECMDGOALS)))
	@if [ ! -d "$(CLIENT_NAME)" ]; then \
		echo "Error: Client directory $(CLIENT_NAME) does not exist"; \
		exit 1; \
	fi
	@echo "Copying server's public key to $(CLIENT_NAME)"
	@cp -f $(SERVER_DIR)/server_public.pem $(CLIENT_NAME)/
	@echo "Done"

# Clean test files but keep directories
.PHONY: clean
clean:
	@echo "Cleaning test files..."
	@for dir in $(CLIENT_DIRS); do \
		if [ -d "$$dir" ]; then \
			echo "Cleaning $$dir files directory..."; \
			rm -f $$dir/files/*; \
			echo "Removing $$dir keys..."; \
			rm -f $$dir/*_private.pem $$dir/*_public.pem; \
			echo "Cleaning server inbox for $$dir..."; \
			rm -f $(SERVER_DIR)/$$dir/inbox/*; \
		fi \
	done
	@echo "Clean complete"

# Remove all client directories and their server inboxes
.PHONY: cleanall
cleanall:
	@echo "Removing all client directories and server inboxes..."
	@for dir in $(CLIENT_DIRS); do \
		if [ -d "$$dir" ]; then \
			echo "Removing $$dir..."; \
			rm -rf $$dir; \
			echo "Removing server inbox for $$dir..."; \
			rm -rf $(SERVER_DIR)/$$dir; \
		fi \
	done
	@echo "Clean complete"

# Handle unknown arguments
%:
	@:
