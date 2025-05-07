# PulseID

PulseID is a lightweight, high-performance distributed unique identifier generator designed to provide UUID-equivalent uniqueness in a compact, human-friendly format. It combines a timestamp, version field, instance identifier, sequence counter, and large random suffix, encoding the result into a 21-character Base58 string.

## Features

* **Distributed Operation**: Generate IDs independently in each process without a central server or external dependencies.
* **Ultra-Fast Throughput**: Up to 2<sup>20</sup> (≈1,048,576) sequential IDs per millisecond, plus large random suffix.
* **Five-Layer Collision Protection**: Timestamp, version, instance ID, sequence counter, and random suffix.
* **Compact & Readable**: 21-character Base58 string, omitting ambiguous characters (`0`, `O`, `I`, `l`).
* **Versioned Format**: 4-bit version field for backward compatibility and future extensions.
* **Customizable Bit Allocation**: Easily adjust timestamp, sequence, and random suffix lengths to suit your needs.

## Bit Structure (123 bits total)

| Field           | Bits | Description                                           |
| --------------- | ---- | ----------------------------------------------------- |
| **Version**     | 4    | Format version (e.g., `0b0010` for v2)                |
| **Timestamp**   | 42   | Millisecond-precision Unix epoch (covers \~139 years) |
| **Instance ID** | 16   | Process-level random identifier (`randbits(16)`)      |
| **Sequence**    | 20   | Counter within the same millisecond (0–2^20−1)        |
| **Random**      | 41   | Large random suffix for extra collision safety        |

Total combinations: 2<sup>123</sup> ≈ 58<sup>21</sup> (≈10<sup>23</sup>), approaching UUID’s 2<sup>128</sup> space.

## Encoding

PulseID encodes the 123-bit value into a 21-character Base58 string:

```
123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz
```

### Example

```
4L7Pv9sG3kQmJZ2Rt8xYb
```

## Installation
1. Copy `pulseid.py` into your project.
2. Add `import generate_pulse_id`.

## Usage

```python
from pulseid import generate_pulse_id

for _ in range(5):
    print(generate_pulse_id())
```

## Configuration & Customization

You can adjust the bit allocation or behavior by editing the constants in `pulseid.py`:

* **Timestamp Bits**: Increase to 44 bits for \~557-year range.
* **Sequence vs Random**: Swap bits (e.g., 18-bit sequence + 43-bit random).
* **Version Field**: Expand to 8 bits for more format versions.
* **Instance ID Persistence**: Store in an environment variable or file to survive restarts.
* **Clock Rollback Handling**: Implement wait or sequence reset logic to guard against backward time shifts.
* **Alternate Encodings**: Use Base32 Crockford for 26-character human-friendly IDs.

## Compare to UUID(V4)
### Compare PC Spec(s):
* CPU: Intel Core i5-6500
* RAM: 8GB

### **Comparison of PulseID and UUID (V4) Generation**
| Metric                       | PulseID | UUID (V4) |
| ---------------------------- | ------- | --------- |
| **Generation Time (1M IDs)** | 5.62s   | 3.61s     |
| **Collision Rate**           | 0%      | 0%        |

## Contributing

Contributions, issues, and feature requests are welcome! Please check the [CONTRIBUTING.md](CONTRIBUTING.md) and adhere to the coding standards.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
