import os
import socket
from cryptography.fernet import Fernet

def send_file(file_path, config):
    """
    Encrypts and sends a file to the peers defined in the whitelist.

    Args:
        file_path (str): Path to the file to send.
        config (dict): Configuration dictionary loaded from config.json.
    """
    # Load encryption key
    encryption_key = config["encryption_key"].encode()
    cipher = Fernet(encryption_key)

    # Encrypt the file
    try:
        with open(file_path, "rb") as file:
            file_data = file.read()
        encrypted_data = cipher.encrypt(file_data)
    except Exception as e:
        print(f"Error encrypting file {file_path}: {e}")
        return

    # Load the whitelist
    try:
        with open(config["whitelist_file"], "r") as whitelist_file:
            whitelist = whitelist_file.read().splitlines()
    except FileNotFoundError:
        print("Whitelist file not found. Ensure whitelist.txt exists.")
        return

    # Send the file to each IP in the whitelist
    for ip in whitelist:
        try:
            send_to_peer(ip, config["port"], os.path.basename(file_path), encrypted_data)
        except Exception as e:
            print(f"Error sending file to {ip}: {e}")

def send_to_peer(ip, port, file_name, data):
    """
    Sends encrypted data to a peer over a socket connection.

    Args:
        ip (str): IP address of the peer.
        port (int): Port number to connect to.
        file_name (str): Name of the file being sent.
        data (bytes): Encrypted file data.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((ip, port))
        print(f"Connected to {ip}:{port}")

        # Send file name and size
        file_metadata = f"{file_name}|{len(data)}"
        client_socket.sendall(file_metadata.encode() + b"\n")

        # Send file data
        client_socket.sendall(data)
        print(f"File {file_name} sent to {ip}:{port}")
