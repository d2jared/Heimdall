import os
import socket
from cryptography.fernet import Fernet

def start_receiver(client_socket, client_address, config):
    """
    Handles the reception of files from a peer.

    Args:
        client_socket (socket.socket): The socket connection to the client.
        client_address (tuple): The address of the client.
        config (dict): Configuration dictionary loaded from config.json.
    """
    try:
        # Load encryption key
        encryption_key = config["encryption_key"].encode()
        cipher = Fernet(encryption_key)

        # Receive file metadata (name and size)
        file_metadata = client_socket.recv(1024).decode().strip()
        file_name, file_size = file_metadata.split("|")
        file_size = int(file_size)

        print(f"Receiving file: {file_name} ({file_size} bytes) from {client_address[0]}")

        # Receive the file data
        received_data = b""
        while len(received_data) < file_size:
            packet = client_socket.recv(4096)
            if not packet:
                break
            received_data += packet

        # Decrypt the file data
        decrypted_data = cipher.decrypt(received_data)

        # Save the file to the sync folder
        file_path = os.path.join(config["sync_folder"], file_name)
        with open(file_path, "wb") as file:
            file.write(decrypted_data)

        print(f"File {file_name} received and saved to {file_path}")

    except Exception as e:
        print(f"Error receiving file from {client_address[0]}: {e}")

    finally:
        client_socket.close()
