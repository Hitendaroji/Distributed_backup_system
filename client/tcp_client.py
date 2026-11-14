
import socket
import struct
import hashlib
import time
from common.chunker import split_file
from common.checksum import calculate_checksum

HOST = "127.0.0.1"
PORTS = [5000, 5001, 5002]
FILENAME = "large_sample.bin"

def receive_exact(connection, size):
    data = b""
    while len(data) < size:
        part = connection.recv(size - len(data))
        if not part:
            raise ConnectionError("Server disconnected")
        data += part
    return data

chunks = split_file(FILENAME)

with open(FILENAME, "rb") as file:
    file_data = file.read()
    file_id = hashlib.sha256(file_data).hexdigest()
    file_size = len(file_data)

for port in PORTS:
    print(f"\nConnecting to server on port {port}...")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        start_time = time.perf_counter()
        client.connect((HOST, port))
        client.sendall(file_id.encode())
        client.sendall(struct.pack("!I", len(chunks)))

        missing_count = struct.unpack(
            "!I", receive_exact(client, 4)
        )[0]

        missing = []
        for _ in range(missing_count):
            chunk_id = struct.unpack(
                "!I", receive_exact(client, 4)
            )[0]
            missing.append(chunk_id)

        transferred_bytes = 0

        for chunk_id in missing:
            data = chunks[chunk_id][1]
            checksum = calculate_checksum(data)

            client.sendall(struct.pack("!II", chunk_id, len(data)))
            client.sendall(checksum.encode())
            client.sendall(data)

            transferred_bytes += len(data)

            acknowledgement = receive_exact(client, 1)

            if acknowledgement == b"1":
                print("Chunk", chunk_id, "saved")

        response = client.recv(1024)
        end_time = time.perf_counter()

        elapsed = end_time - start_time
        throughput = (
            transferred_bytes * 8 / elapsed / 1_000_000
            if elapsed > 0 else 0
        )

        print("Server response:", response.decode())
        print("Transfer time:", round(elapsed, 4), "seconds")
        print("Data transferred:", transferred_bytes, "bytes")
        print("Throughput:", round(throughput, 4), "Mbps")

    except (ConnectionError, OSError) as error:
        print("Server", port, "failed:", error)

    finally:
        client.close()
