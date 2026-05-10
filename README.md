<div align="center">

```
╔══════════════════════════════════════════════════════════╗
║              NetFix - Network Troubleshooter             ║
║    Cross-platform (Windows & Linux) v1.0 by KronosA9     ║
╚══════════════════════════════════════════════════════════╝
```

**A powerful, interactive, cross-platform network diagnostic tool built in pure Python.**

[![Python](https://img.shields.io/badge/Python-3.6%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey?logo=windows&logoColor=white)](https://github.com/KronosA9/netfix)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0-orange)](https://github.com/KronosA9/netfix/releases)
[![Dependencies](https://img.shields.io/badge/Dependencies-None-brightgreen)](https://github.com/KronosA9/netfix)

[Features](#-features) · [Quick Start](#-quick-start) · [Usage](#-usage) · [Checks](#-diagnostic-checks) · [Output](#-sample-output) · [Contributing](#-contributing)

</div>

---

## 📖 Overview

**NetFix** is a lightweight, zero-dependency Python script designed to diagnose and resolve common network issues on both **Windows** and **Linux** systems. It runs through a structured set of checks — interfaces, gateways, DNS, connectivity, ports, firewall rules, traceroutes, and latency — and for every problem it finds, it tells you exactly how to fix it.

No external libraries. No installation headaches. Just Python 3 and a terminal.

---

## ✨ Features

- 🖥️ **Cross-platform** — works natively on Windows and Linux with no code changes
- 🔍 **8 diagnostic modules** — covering every layer of a typical network stack
- 🛠️ **Actionable fix suggestions** — every failure prints the exact CLI commands to resolve it
- 🎨 **Color-coded output** — instant visual feedback with ✔ / ⚠ / ✘ indicators
- 📋 **Session summary** — aggregated pass/warn/fail report at the end
- 💾 **Report export** — saves a timestamped `.txt` report to your home directory
- ⚡ **Interactive menu** — run all checks at once or pick individual diagnostics
- 📦 **Zero dependencies** — uses only the Python standard library

---

## ⚡ Quick Start

```bash
# Clone the repository
git clone https://github.com/KronosA9/netfix.git
cd netfix

# Run the script
python3 netfix.py          # Linux / macOS
python netfix.py           # Windows

# For full firewall and interface checks on Linux (recommended)
sudo python3 netfix.py
```

> **Requirements:** Python 3.6 or higher. No `pip install` needed.

---

## 🖥️ Compatibility

| Feature | Windows | Linux |
|---------|:-------:|:-----:|
| Interface / IP info | ✅ `ipconfig` | ✅ `ip` / `ifconfig` |
| Gateway ping | ✅ | ✅ |
| DNS resolution | ✅ | ✅ |
| Internet ping | ✅ | ✅ |
| Port reachability | ✅ | ✅ |
| Traceroute | ✅ `tracert` | ✅ `traceroute` |
| Firewall check | ✅ `netsh advfirewall` | ✅ `ufw` / `firewalld` / `iptables` |
| Latency benchmark | ✅ | ✅ |

---

## 🔍 Diagnostic Checks

### 1 · Network Interface Status
Inspects all network adapters for:
- Disconnected or `DOWN` interfaces
- APIPA addresses (`169.254.x.x`) indicating DHCP failure
- Missing or invalid IP configurations

**Example fix suggestions:**
```
➜  FIX: Run: ipconfig /release && ipconfig /renew          (Windows)
➜  FIX: sudo ip link set <interface> up                    (Linux)
➜  FIX: sudo dhclient -r && sudo dhclient <interface>      (Linux)
```

---

### 2 · Default Gateway Reachability
Automatically detects the default gateway from your routing table and pings it to verify L3 connectivity.

**Example fix suggestions:**
```
➜  FIX: Check the physical/Wi-Fi connection
➜  FIX: Reboot the router/modem
➜  FIX: sudo systemctl restart NetworkManager              (Linux)
➜  FIX: netsh winsock reset  (then reboot)                 (Windows)
```

---

### 3 · DNS Resolution
Tests name resolution for multiple well-known hosts and displays your current DNS server configuration if resolution fails.

**Example fix suggestions:**
```
➜  FIX: Set a public DNS server:
        • Google     : 8.8.8.8  /  8.8.4.4
        • Cloudflare : 1.1.1.1  /  1.0.0.1
➜  FIX: Linux : edit /etc/resolv.conf → nameserver 8.8.8.8
➜  FIX: Windows: netsh interface ip set dns <adapter> static 8.8.8.8
```

---

### 4 · Internet Connectivity
Pings an external IP (default: `8.8.8.8`) and measures packet loss to classify the connection as stable, intermittent, or down.

---

### 5 · Port / Service Reachability
Attempts a TCP connection to any host and port combination you specify. Distinguishes between:
- **OPEN** — connection succeeded
- **REFUSED** — host is up but service is not running
- **TIMEOUT** — port is filtered by a firewall

---

### 6 · Traceroute (Path Analysis)
Traces the full network path to a target, highlighting hops where packets are dropped (`* * *`) and flagging paths with excessive timeouts.

---

### 7 · Firewall Status
Detects and inspects firewall state across all supported managers:

| Manager | Platform | Detection |
|---------|----------|-----------|
| `Windows Firewall` | Windows | `netsh advfirewall show allprofiles state` |
| `UFW` | Linux (Debian/Ubuntu) | `ufw status` |
| `firewalld` | Linux (RHEL/Fedora) | `firewall-cmd --state` |
| `iptables` | Linux (any) | Scans for `DROP` / `REJECT` rules |

---

### 8 · Latency Benchmark
Pings three public DNS servers 10 times each and rates the round-trip time:

| RTT | Rating |
|-----|--------|
| < 30 ms | ✦ Excellent |
| 30 – 80 ms | ✦ Good |
| 80 – 150 ms | ✦ Fair |
| > 150 ms | ✦ Poor |

---

## 🖼️ Sample Output

```
╔══════════════════════════════════════════════════════════╗
║              NetFix - Network Troubleshooter             ║
║    Cross-platform (Windows & Linux) v1.0 by KronosA9     ║
╚══════════════════════════════════════════════════════════╝
  OS detected : Linux 6.8.0
  Started at  : 2025-08-14  09:32:11

┌────────────────────────────────────────────────────────────┐
│  1 · Network Interface Status                              │
└────────────────────────────────────────────────────────────┘
  ✔  All interfaces appear UP with valid addresses.

┌────────────────────────────────────────────────────────────┐
│  2 · Default Gateway Reachability                          │
└────────────────────────────────────────────────────────────┘
  ℹ  Default gateway: 192.168.1.1
  ✔  Gateway is reachable. RTT ≈ 3 ms

┌────────────────────────────────────────────────────────────┐
│  3 · DNS Resolution                                        │
└────────────────────────────────────────────────────────────┘
  ✔  google.com       →  142.250.185.14
  ✔  cloudflare.com   →  104.16.133.229
  ✔  github.com       →  140.82.114.4
  ✔  DNS resolution is working correctly.

┌────────────────────────────────────────────────────────────┐
│  8 · Latency Benchmark                                     │
└────────────────────────────────────────────────────────────┘
  ✔  Google DNS (8.8.8.8)          →   4.2 ms  ✦ Excellent
  ✔  Cloudflare (1.1.1.1)          →   5.1 ms  ✦ Excellent
  ✔  OpenDNS (208.67.222.222)      →  11.8 ms  ✦ Excellent

📋 Session Summary
  Passed   : 12
  Warnings : 0
  Failures : 0

  🎉  No issues found! Your network looks healthy.
```

---

## 📁 Repository Structure

```
netfix/
│
├── netfix.py          # Main script — single-file, self-contained
├── README.md          # This file
├── LICENSE            # MIT License
└── CONTRIBUTING.md    # Contribution guidelines
```

---

## 🔧 Advanced Usage

### Run with elevated privileges (Linux)
Some checks (firewall inspection, raw socket operations) require root access:
```bash
sudo python3 netfix.py
```

### Redirect output to a log file
```bash
python3 netfix.py 2>&1 | tee netfix_session.log
```

### Run non-interactively (future CLI flag — see roadmap)
```bash
# Planned for v1.1
python3 netfix.py --full-scan --save-report
```

---

## 🗺️ Roadmap

- [ ] CLI argument mode (`--check dns`, `--check gateway`, `--full-scan`)
- [ ] JSON/HTML report export
- [ ] macOS support (currently untested)
- [ ] Bandwidth speed test integration
- [ ] Scheduled / daemon mode (run checks every N minutes)
- [ ] Wi-Fi signal strength check (Linux `iwconfig`, Windows `netsh wlan`)
- [ ] IPv6 support
- [ ] ARP table inspection

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** this repository
2. **Create** a feature branch: `git checkout -b feature/my-improvement`
3. **Commit** your changes: `git commit -m "Add: my improvement description"`
4. **Push** to your fork: `git push origin feature/my-improvement`
5. **Open** a Pull Request with a clear description of what you changed and why

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines on code style, testing, and PR expectations.

### Bug Reports

Found a bug? [Open an issue](https://github.com/KronosA9/netfix/issues) and include:
- Your OS and Python version (`python3 --version`)
- The exact menu option and input that triggered the issue
- The full terminal output (paste or screenshot)

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**KronosA9**

> *"Simple tools, powerful results."*

---

<div align="center">

If NetFix helped you, consider giving the repo a ⭐ — it helps others discover the project!

</div>
