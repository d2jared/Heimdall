import os
import json
import socket
import threading
from sync.watcher import FileWatcher
from sync.sender import send_file
from sync.receiver import start_receiver
from network.blacklist import is_ip_allowed, log_blacklisted_ip

# Load configuration
def load_config():
    try:
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
        return config
    except FileNotFoundError:
        print("Error: config.json not found. Please create the configuration file.")
        exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON in config.json.")
        exit(1)

from network.blacklist import is_ip_allowed, log_blacklisted_ip

# Main server loop (modifié)
def server_loop(config):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", config["port"]))
    server_socket.listen(5)
    print(f"Server started on port {config['port']}. Waiting for connections...")

    while True:
        client_socket, client_address = server_socket.accept()
        client_ip = client_address[0]
        print(f"Connection attempt from {client_ip}")

        # Vérification de l'IP autorisée
        if not is_ip_allowed(client_ip, config["whitelist_file"]):
            print(f"Connection from {client_ip} rejected (not in whitelist).")
            log_blacklisted_ip(client_ip)
            client_socket.close()
            continue

        # Lancer le gestionnaire de réception
        threading.Thread(target=start_receiver, args=(client_socket, client_address, config)).start()

# Main function
def main():
    # Load configuration
    config = load_config()

    # Ensure sync folder exists
    if not os.path.exists(config["sync_folder"]):
        os.makedirs(config["sync_folder"])

    # Start file watcher
    file_watcher = FileWatcher(config["sync_folder"], config)
    watcher_thread = threading.Thread(target=file_watcher.start)
    watcher_thread.daemon = True
    watcher_thread.start()

    # Start server loop
    server_thread = threading.Thread(target=server_loop, args=(config,))
    server_thread.daemon = True
    server_thread.start()

    print("File synchronization service is running. Press Ctrl+C to stop.")

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Shutting down...")
        file_watcher.stop()
        print("Service stopped.")

if __name__ == "__main__":
    main()