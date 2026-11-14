	
import socket
import struct
import hashlib
import os
import sys

HOST = "0.0.0.0"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
SERVER_NAME = sys.argv[2] if len(sys.argv) > 2 else "backup1"

CHUNK_DIR = f"server/storage/{SERVER_NAME}/chunks"
OUTPUT_DIR = f"server/received_files/{SERVER_NAME}"

def receive_exact(connection, size):
    data = b""
    while len(data) < size:
        part = connection.recv(size - len(data))
        if not part:
            raise ConnectionError("Connection interrupted")
        data += part
    return data

os.makedirs(CHUNK_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(5)

print(f"{SERVER_NAME} running on port {PORT}...")

while True:
    connection, address = server.accept()
    print("\nClient connected:", address)

    try:
        file_id = receive_exact(connection, 64).decode()

        if any(c not in "0123456789abcdef" for c in file_id):
            raise ValueError("Invalid file ID")

        total_chunks = struct.unpack("!I", receive_exact(connection, 4))[0]

        file_directory = os.path.join(CHUNK_DIR, file_id)
        os.makedirs(file_directory, exist_ok=True)

        missing = []

        for chunk_id in range(total_chunks):
            path = os.path.join(file_directory, f"chunk_{chunk_id}.bin")
            if not os.path.exists(path):
                missing.append(chunk_id)

        connection.sendall(struct.pack("!I", len(missing)))

        for chunk_id in missing:
            connection.sendall(struct.pack("!I", chunk_id))

        print("File ID:", file_id)
        print("Missing chunks:", missing)

        for _ in missing:
            header = receive_exact(connection, 8)
            chunk_id, chunk_size = struct.unpack("!II", header)

            if chunk_id not in missing:
                raise ValueError("Unexpected chunk ID")
            if chunk_size > 1024:
                raise ValueError("Invalid chunk size")

            expected_hash = receive_exact(connection, 64).decode()
            chunk_data = receive_exact(connection, chunk_size)

            actual_hash = hashlib.sha256(chunk_data).hexdigest()
            if actual_hash != expected_hash:
                raise ValueError("Checksum verification failed")

            path = os.path.join(file_directory, f"chunk_{chunk_id}.bin")
            with open(path, "wb") as file:
                file.write(chunk_data)

            connection.sendall(b"1")
            print("Chunk", chunk_id, "verified and saved")

        all_present = all(
            os.path.exists(os.path.join(file_directory, f"chunk_{i}.bin"))
            for i in range(total_chunks)
        )

        if all_present:
            output_path = os.path.join(OUTPUT_DIR, f"{file_id}.bin")

            with open(output_path, "wb") as output:
                for chunk_id in range(total_chunks):
                    path = os.path.join(file_directory, f"chunk_{chunk_id}.bin")
                    with open(path, "rb") as part:
                        output.write(part.read())

            connection.sendall(b"Backup completed successfully!")
            print("File reconstructed:", output_path)
        else:
            connection.sendall(b"Some chunks are still missing.")

    except (ConnectionError, ValueError, OSError) as error:
        print("Transfer failed:", error)
    finally:
        connection.close()

