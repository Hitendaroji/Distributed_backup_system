
from common.chunker import split_file
from common.checksum import calculate_checksum, verify_checksum

filename = "large_sample.bin"

chunks = split_file(filename)

print("Total chunks:", len(chunks))

for chunk_id, data in chunks:
    checksum = calculate_checksum(data)

    print("Chunk ID:", chunk_id)
    print("Chunk size:", len(data))
    print("Checksum:", checksum)
    print("Verified:", verify_checksum(data, checksum))
