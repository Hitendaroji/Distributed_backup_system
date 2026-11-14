
import hashlib

def calculate_checksum(data):
    return hashlib.sha256(data).hexdigest()

def verify_checksum(data, expected_checksum):
    actual_checksum = calculate_checksum(data)

    return actual_checksum == expected_checksum
