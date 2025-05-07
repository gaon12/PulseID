"""
pulseid.py

PulseID: Distributed unique identifier generator with UUID-level uniqueness
Encoded as a 21-character Base58 string.
"""
import time
import threading
import random
import secrets

# Thread-safe lock for sequence generation\ n_lock = threading.Lock()
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
    s = []
    for _ in range(length):
        num, rem = divmod(num, 58)
        s.append(_ALPHABET[rem])
    return ''.join(reversed(s))


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
