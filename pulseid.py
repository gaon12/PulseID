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

_BASE58_LENGTH = 21
_ZERO_BASE58 = _ALPHABET[0] * _BASE58_LENGTH
_BASE58_CHUNK_SIZE = 3
_BASE58_CHUNK_BASE = 58 ** _BASE58_CHUNK_SIZE
_BASE58_CHUNKS = (_BASE58_LENGTH + _BASE58_CHUNK_SIZE - 1) // _BASE58_CHUNK_SIZE


def _build_chunk_lookup() -> tuple[str, ...]:
    alphabet = _ALPHABET
    base = 58
    chunk_size = _BASE58_CHUNK_SIZE
    lookup = [None] * _BASE58_CHUNK_BASE
    for value in range(_BASE58_CHUNK_BASE):
        v = value
        chars = [''] * chunk_size
        for i in range(chunk_size - 1, -1, -1):
            v, rem = divmod(v, base)
            chars[i] = alphabet[rem]
        lookup[value] = ''.join(chars)
    return tuple(lookup)


_BASE58_CHUNK_LOOKUP = _build_chunk_lookup()
_TIMESTAMP_MASK = (1 << 42) - 1
_SEQUENCE_MASK = (1 << 20) - 1
_RANDOM_BITS = 41
_RANDOM_MASK = (1 << _RANDOM_BITS) - 1
_VERSION_INSTANCE = ((_VERSION & 0xF) << 16) | _INSTANCE_ID
_TIMESTAMP_SHIFT = 4 + 16

_RAND_BITS = random.getrandbits
_TIME_NS = time.time_ns


def _encode_base58(num: int) -> str:
    """
    Encodes an integer into a fixed-length Base58 string.
    """
    if num == 0:
        return _ZERO_BASE58

    chunk_base = _BASE58_CHUNK_BASE
    lookup = _BASE58_CHUNK_LOOKUP
    chunks = [''] * _BASE58_CHUNKS
    for i in range(_BASE58_CHUNKS - 1, -1, -1):
        num, rem = divmod(num, chunk_base)
        chunks[i] = lookup[rem]
    return ''.join(chunks)


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

    rnd = _RAND_BITS(_RANDOM_BITS) & _RANDOM_MASK
    with _lock:
        ms = (_TIME_NS() // 1_000_000) & _TIMESTAMP_MASK
        _sequence = (_sequence + 1) & _SEQUENCE_MASK
        seq = _sequence

    raw = (ms << _TIMESTAMP_SHIFT) | _VERSION_INSTANCE
    raw = (raw << 20) | seq
    raw = (raw << _RANDOM_BITS) | rnd

    # Encode to Base58 (21 characters)
    return _encode_base58(raw)


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
