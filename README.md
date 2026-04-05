# PortScout

**PortScout** is a fast, multi‑threaded TCP port scanner with optional banner grabbing, file input support, and a beautiful terminal interface.

## Features

- Scan single IP, domain, or list from `.txt` file
- Port specification: single, comma‑separated, or range (e.g., `1-1000`)
- Configurable threads and timeout
- Optional **banner grabbing** (`--grab`)
- Verbose mode (`-v`)
- Rich CLI output (progress bar, colored tables) – falls back gracefully if `rich` not installed
- Save results as JSON or plain text

## Installation

```bash
git clone https://github.com/arthenox/portscout.git
cd portscout
pip install -r requirements.txt   # optional, for rich output
```

## Usage

```bash
# Basic scan on common ports
python portscout.py scanme.nmap.org

# Scan specific ports
python portscout.py example.com -p 80,443,8080

# Range of ports with more threads
python portscout.py 192.168.1.1 -p 1-1000 -t 200

# Enable banner grabbing (slower but more info)
python portscout.py example.com -p 22,80,443 --grab -v

# Scan targets from a file (one per line)
python portscout.py targets.txt --top -o results.txt
```

## Example output

```
$ python portscout.py scanme.nmap.org -p 22,80,443

▶ Target: scanme.nmap.org (45.33.32.156)

┏━━━━━━┳━━━━━━━━━┓
┃ Port ┃ Service ┃
┡━━━━━━╇━━━━━━━━━┩
│   22 │ ssh     │
│   80 │ http    │
└──────┴─────────┘
```

## Requirements

- Python 3.6+
- `rich` (optional, for enhanced UI)

## License

MIT © arthenox

## Disclaimer

Use this tool only on systems you own or have explicit permission to test.
EOF
```
