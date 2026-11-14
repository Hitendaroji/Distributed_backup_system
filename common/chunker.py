
CHUNK_SIZE = 1024

def split_file(filename):
    chunks = []

    with open(filename, "rb") as file:
        chunk_id = 0

        while True:
            data = file.read(CHUNK_SIZE)

            if not data:
                break

            chunks.append((chunk_id, data))
            chunk_id += 1

    return chunks
