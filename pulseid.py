"""
pulseid.py

PulseID: Distributed unique identifier generator with UUID-level uniqueness
Encoded as a 21-character Base58 string.
"""
import time
import threading
import random
import secrets

# Thread-safe lock for sequence generation
_lock = threading.Lock()
_sequence = 0

# 16-bit process-specific random instance ID (0–65535)
_INSTANCE_ID = secrets.randbits(16)
# 4-bit version field (e.g., 0b0001 for v1)
_VERSION = 0b0001

# Base58 alphabet (omits 0, O, I, l for readability)
_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def _base58_encode(num: int, length: int) -> str:
    """
    Encodes an integer into a fixed-length Base58 string.
    """
    if num == 0:
        return _ALPHABET[0] * length

    s = [''] * length  # Pre-allocate list of the correct size
    for i in range(length - 1, -1, -1): # Iterate from right to left
        num, rem = divmod(num, 58)
        s[i] = _ALPHABET[rem]
        if num == 0 and i > 0: # Optimization: if num becomes 0, fill rest with ALPHABET[0]
            for k in range(i -1, -1, -1):
                s[k] = _ALPHABET[0]
            break
    return "".join(s)


def generate_pulse_id() -> str:
    """
    Generates a 123-bit PulseID and encodes it as a 21-character Base58 string.

    Structure (123 bits total):
        - 42 bits: Timestamp (ms since Unix epoch)
        - 4 bits : Version
        - 16 bits: Instance ID
        - 20 bits: Sequence counter
        - 41 bits: Random suffix
    """
    global _sequence
    with _lock:
        # 1) Timestamp (42 bits)
        ms = int(time.time() * 1000) & ((1 << 42) - 1)
        # 2) Sequence (20 bits)
        _sequence = (_sequence + 1) & ((1 << 20) - 1)
        # 3) Random suffix (41 bits)
        rnd = random.getrandbits(41)
        # 4) Bitwise composition (big-endian)
        raw = ms
        raw = (raw << 4) | (_VERSION & 0xF)
        raw = (raw << 16) | _INSTANCE_ID
        raw = (raw << 20) | _sequence
        raw = (raw << 41) | rnd

    # Encode to Base58 (21 characters)
    return _base58_encode(raw, 21)


if __name__ == "__main__":
    # Example usage: print five generated IDs
    for _ in range(5):
        print(generate_pulse_id())

    # Benchmark PulseID generation
    def benchmark_pulse_id(num_ids_to_generate: int):
        """
        Benchmarks the PulseID generation process.
        """
        print(f"\nBenchmarking PulseID generation for {num_ids_to_generate} IDs...")
        start_time = time.time()

        for _ in range(num_ids_to_generate):
            generate_pulse_id()

        end_time = time.time()
        total_time = end_time - start_time
        average_time_per_id = total_time / num_ids_to_generate if num_ids_to_generate > 0 else 0

        print(f"Total time taken: {total_time:.4f} seconds")
        print(f"Average time per ID: {average_time_per_id * 1e6:.2f} microseconds") # Convert to microseconds for readability

    benchmark_pulse_id(100000)
