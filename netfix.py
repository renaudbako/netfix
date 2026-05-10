#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║              NetFix - Network Troubleshooter             ║
║    Cross-platform (Windows & Linux) v1.0 by KronosA9     ║
╚══════════════════════════════════════════════════════════╝
"""

import subprocess
import platform
import socket
import sys
import os
import re
import shutil
from datetime import datetime

# ─── Color codes (disabled on Windows cmd if no ANSI support) ───────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    WHITE  = "\033[97m"
    DIM    = "\033[2m"

# Enable ANSI on Windows 10+
if platform.system() == "Windows":
    os.system("color")

IS_WINDOWS = platform.system() == "Windows"
IS_LINUX   = platform.system() == "Linux"

REPORT_LINES = []   # collects findings for the final report


# ─── Helpers ─────────────────────────────────────────────────────────────────

def banner():
    print(f"""
{C.CYAN}{C.BOLD}╔══════════════════════════════════════════════════════════╗
║              NetFix - Network Troubleshooter             ║
║    Cross-platform (Windows & Linux) v1.0 by KronosA9     ║
╚══════════════════════════════════════════════════════════╝{C.RESET}
  {C.DIM}OS detected : {platform.system()} {platform.release()}
  Started at  : {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}{C.RESET}
""")


def section(title):
    width = 60
    bar = "─" * width
    print(f"\n{C.BLUE}{C.BOLD}┌{bar}┐")
    print(f"│  {title:<{width - 2}}│")
    print(f"└{bar}┘{C.RESET}")


def ok(msg):
    print(f"  {C.GREEN}✔  {msg}{C.RESET}")
    REPORT_LINES.append(f"[OK]    {msg}")


def warn(msg):
    print(f"  {C.YELLOW}⚠  {msg}{C.RESET}")
    REPORT_LINES.append(f"[WARN]  {msg}")


def fail(msg):
    print(f"  {C.RED}✘  {msg}{C.RESET}")
    REPORT_LINES.append(f"[FAIL]  {msg}")


def info(msg):
    print(f"  {C.CYAN}ℹ  {msg}{C.RESET}")
    REPORT_LINES.append(f"[INFO]  {msg}")


def fix(msg):
    print(f"  {C.YELLOW}➜  FIX: {msg}{C.RESET}")
    REPORT_LINES.append(f"[FIX]   {msg}")


def run_cmd(cmd, timeout=15):
    """Run a shell command and return (stdout, stderr, returncode)."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1
    except Exception as e:
        return "", str(e), 1


def ask(prompt, choices=None):
    """Prompt the user and return their input."""
    if choices:
        choice_str = "/".join(choices)
        while True:
            val = input(f"\n{C.WHITE}{C.BOLD}  ▶  {prompt} [{choice_str}]: {C.RESET}").strip().lower()
            if val in [c.lower() for c in choices]:
                return val
            print(f"  {C.RED}Invalid choice. Enter one of: {choice_str}{C.RESET}")
    else:
        return input(f"\n{C.WHITE}{C.BOLD}  ▶  {prompt}: {C.RESET}").strip()


def menu(title, options):
    """Numbered menu. Returns the chosen index (0-based)."""
    print(f"\n{C.BOLD}{C.WHITE}  {title}{C.RESET}")
    for i, opt in enumerate(options, 1):
        print(f"  {C.CYAN}[{i}]{C.RESET} {opt}")
    while True:
        choice = input(f"\n{C.WHITE}{C.BOLD}  ▶  Select (1-{len(options)}): {C.RESET}").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return int(choice) - 1
        print(f"  {C.RED}Please enter a number between 1 and {len(options)}.{C.RESET}")


# ─── Diagnostic modules ───────────────────────────────────────────────────────

def check_interface():
    section("1 · Network Interface Status")

    if IS_WINDOWS:
        out, _, _ = run_cmd("ipconfig /all")
        if out:
            # Show trimmed summary
            lines = [l for l in out.splitlines() if any(k in l for k in
                     ["Adapter", "IPv4", "IPv6", "Default Gateway",
                      "DNS Servers", "Physical Address", "Media State"])]
            for l in lines:
                print(f"  {C.DIM}{l}{C.RESET}")

            if "Media disconnected" in out:
                fail("One or more adapters report 'Media disconnected'.")
                fix("Check the physical cable or toggle Wi-Fi / Ethernet in Settings.")
            elif "169.254." in out:
                fail("APIPA address detected (169.254.x.x). DHCP failed.")
                fix("Run: ipconfig /release && ipconfig /renew")
                fix("Check that your router / DHCP server is running.")
            else:
                ok("All detected adapters have valid IP addresses.")
        else:
            fail("Could not retrieve network interface info.")

    else:  # Linux
        if shutil.which("ip"):
            out, _, _ = run_cmd("ip -brief addr show")
        else:
            out, _, _ = run_cmd("ifconfig -a")

        if out:
            print()
            for line in out.splitlines():
                print(f"  {C.DIM}{line}{C.RESET}")

            if "DOWN" in out:
                fail("One or more interfaces are DOWN.")
                fix("Bring it up with:  sudo ip link set <interface> up")
            elif "169.254." in out:
                fail("APIPA address detected. DHCP may have failed.")
                fix("Run: sudo dhclient -r && sudo dhclient <interface>")
            else:
                ok("All interfaces appear UP with valid addresses.")
        else:
            fail("Could not retrieve interface information.")
            fix("Ensure 'ip' or 'ifconfig' is installed.")


def check_gateway():
    section("2 · Default Gateway Reachability")

    gateway = None

    if IS_WINDOWS:
        out, _, _ = run_cmd("ipconfig")
        match = re.search(r"Default Gateway.*?:\s+([\d.]+)", out)
        if match:
            gateway = match.group(1)
    else:
        out, _, _ = run_cmd("ip route show default")
        match = re.search(r"via\s+([\d.]+)", out)
        if match:
            gateway = match.group(1)

    if not gateway or gateway == "0.0.0.0":
        fail("No default gateway found.")
        fix("Set a gateway manually or check your DHCP server.")
        fix("Linux : sudo ip route add default via <gateway_ip>")
        fix("Windows: netsh interface ip set address <adapter> static <ip> <mask> <gateway>")
        return

    info(f"Default gateway: {gateway}")
    ping_cmd = f"ping -n 4 {gateway}" if IS_WINDOWS else f"ping -c 4 -W 2 {gateway}"
    out, _, rc = run_cmd(ping_cmd, timeout=20)

    if rc == 0:
        # Extract avg RTT
        rtt_match = re.search(r"Average = (\d+)ms|avg.*?([\d.]+)/", out)
        rtt = rtt_match.group(1) or rtt_match.group(2) if rtt_match else "?"
        ok(f"Gateway is reachable. RTT ≈ {rtt} ms")
    else:
        fail("Gateway is NOT reachable.")
        fix("Check the physical/Wi-Fi connection.")
        fix("Reboot the router/modem.")
        fix("Temporarily disable the firewall to rule it out.")
        fix("Linux: sudo systemctl restart NetworkManager")
        fix("Windows: netsh winsock reset  (then reboot)")


def check_dns(custom_host=None):
    section("3 · DNS Resolution")

    test_hosts = [custom_host] if custom_host else ["google.com", "cloudflare.com", "github.com"]
    all_good = True

    for host in test_hosts:
        try:
            ip = socket.gethostbyname(host)
            ok(f"{host}  →  {ip}")
        except socket.gaierror as e:
            fail(f"Cannot resolve '{host}': {e}")
            all_good = False

    if not all_good:
        # Check current DNS servers
        if IS_WINDOWS:
            out, _, _ = run_cmd("ipconfig /all")
            dns_lines = [l.strip() for l in out.splitlines() if "DNS Servers" in l]
            for l in dns_lines:
                info(l)
        else:
            out, _, _ = run_cmd("cat /etc/resolv.conf")
            print(f"  {C.DIM}{out}{C.RESET}")

        fix("Try setting a public DNS server:")
        fix("  • Google  : 8.8.8.8  /  8.8.4.4")
        fix("  • Cloudflare: 1.1.1.1  /  1.0.0.1")
        fix("Linux : edit /etc/resolv.conf  →  nameserver 8.8.8.8")
        fix("Windows: Control Panel → Adapter → IPv4 Properties → DNS")
        fix("Windows CLI: netsh interface ip set dns <adapter> static 8.8.8.8")
    else:
        ok("DNS resolution is working correctly.")


def check_internet(target="8.8.8.8"):
    section("4 · Internet Connectivity")

    ping_cmd = f"ping -n 4 {target}" if IS_WINDOWS else f"ping -c 4 -W 2 {target}"
    out, _, rc = run_cmd(ping_cmd, timeout=20)

    if rc == 0:
        loss_match = re.search(r"(\d+)%\s*(packet\s*)?loss", out, re.IGNORECASE)
        loss = loss_match.group(1) if loss_match else "0"
        if int(loss) == 0:
            ok(f"Internet reachable ({target}). 0% packet loss.")
        elif int(loss) < 50:
            warn(f"Intermittent connectivity — {loss}% packet loss.")
            fix("Check Wi-Fi signal strength or cable quality.")
            fix("Restart modem/router.")
        else:
            fail(f"High packet loss ({loss}%). Connection unstable.")
            fix("Contact your ISP or reboot networking equipment.")
    else:
        fail(f"Cannot reach {target}. No internet access.")
        fix("Verify the gateway is reachable (check section 2).")
        fix("Reboot modem/router and wait 2 minutes.")
        fix("Contact your ISP if the problem persists.")


def check_ports(host=None, ports=None):
    section("5 · Port / Service Reachability")

    if host is None:
        host = ask("Enter host to test (e.g. google.com or 8.8.8.8)")
    if ports is None:
        raw = ask("Enter ports to test, comma-separated (e.g. 80,443,22,53)")
        ports = [int(p.strip()) for p in raw.split(",") if p.strip().isdigit()]

    for port in ports:
        try:
            s = socket.create_connection((host, port), timeout=5)
            s.close()
            ok(f"{host}:{port}  →  OPEN")
        except socket.timeout:
            fail(f"{host}:{port}  →  TIMEOUT (filtered or host down)")
            fix(f"Port {port} may be blocked by a firewall.")
        except ConnectionRefusedError:
            warn(f"{host}:{port}  →  REFUSED (host up, service not running)")
            fix(f"Start or install the service on port {port}.")
        except Exception as e:
            fail(f"{host}:{port}  →  ERROR: {e}")


def check_traceroute(target=None):
    section("6 · Traceroute (Path Analysis)")

    if target is None:
        target = ask("Enter target host/IP for traceroute (e.g. google.com)")

    cmd = f"tracert -d {target}" if IS_WINDOWS else f"traceroute -n {target}"

    if not IS_WINDOWS and not shutil.which("traceroute"):
        warn("'traceroute' not found.")
        fix("Linux: sudo apt install traceroute  OR  sudo yum install traceroute")
        return

    print(f"\n  {C.DIM}Running traceroute to {target} (may take up to 30s)…{C.RESET}\n")
    out, err, rc = run_cmd(cmd, timeout=60)

    if out:
        for line in out.splitlines():
            if "*  *  *" in line or "* * *" in line:
                print(f"  {C.YELLOW}{line}{C.RESET}")
            else:
                print(f"  {C.DIM}{line}{C.RESET}")

        stars = sum(1 for l in out.splitlines() if "* * *" in l or "*  *  *" in l)
        total = len([l for l in out.splitlines() if re.match(r"\s*\d+", l)])

        if total > 0 and stars / total > 0.5:
            warn(f"More than half the hops timed out ({stars}/{total}).")
            fix("Intermediate routers may block ICMP — not always a real problem.")
            fix("Check if the final destination responds (use port check).")
        else:
            ok("Traceroute completed. Path looks reasonable.")
    else:
        fail(f"Traceroute failed: {err}")


def check_firewall():
    section("7 · Firewall Status")

    if IS_WINDOWS:
        out, _, rc = run_cmd(
            'netsh advfirewall show allprofiles state'
        )
        if out:
            print()
            for line in out.splitlines():
                print(f"  {C.DIM}{line}{C.RESET}")
            if "ON" in out.upper():
                warn("Windows Firewall is ON for one or more profiles.")
                fix("To temporarily disable for testing:")
                fix("  netsh advfirewall set allprofiles state off")
                fix("  (Re-enable afterwards: netsh advfirewall set allprofiles state on)")
            else:
                ok("Windows Firewall appears to be OFF.")
        else:
            fail("Could not query firewall status (run as Administrator).")

    else:
        # Check ufw
        if shutil.which("ufw"):
            out, _, _ = run_cmd("sudo ufw status")
            print(f"  {C.DIM}{out}{C.RESET}")
            if "active" in out.lower():
                warn("UFW firewall is active.")
                fix("List rules: sudo ufw status verbose")
                fix("Allow a port: sudo ufw allow <port>/tcp")
                fix("Disable temporarily: sudo ufw disable")
            else:
                ok("UFW is inactive.")

        elif shutil.which("firewalld") or shutil.which("firewall-cmd"):
            out, _, _ = run_cmd("sudo firewall-cmd --state")
            print(f"  {C.DIM}{out}{C.RESET}")
            if "running" in out.lower():
                warn("firewalld is running.")
                fix("List zones: sudo firewall-cmd --list-all")
                fix("Open port: sudo firewall-cmd --permanent --add-port=<port>/tcp && sudo firewall-cmd --reload")
            else:
                ok("firewalld is not running.")

        elif shutil.which("iptables"):
            out, _, _ = run_cmd("sudo iptables -L -n --line-numbers")
            rules = [l for l in out.splitlines() if "DROP" in l or "REJECT" in l]
            if rules:
                warn(f"{len(rules)} DROP/REJECT rule(s) found in iptables.")
                for r in rules[:5]:
                    print(f"  {C.YELLOW}    {r}{C.RESET}")
                fix("Review iptables rules: sudo iptables -L -n -v")
                fix("Flush all rules (testing only): sudo iptables -F")
            else:
                ok("No DROP/REJECT rules found in iptables.")
        else:
            info("No known firewall manager found (ufw / firewalld / iptables).")


def check_speed():
    section("8 · Latency Benchmark (multi-target ping)")

    targets = {
        "Google DNS (8.8.8.8)": "8.8.8.8",
        "Cloudflare (1.1.1.1)": "1.1.1.1",
        "OpenDNS (208.67.222.222)": "208.67.222.222",
    }

    results = []
    for label, ip in targets.items():
        if IS_WINDOWS:
            cmd = f"ping -n 10 {ip}"
            pattern = r"Average = (\d+)ms"
        else:
            cmd = f"ping -c 10 -i 0.2 -W 2 {ip}"
            pattern = r"rtt.*/(\d+\.\d+)/"

        out, _, rc = run_cmd(cmd, timeout=30)
        if rc == 0:
            m = re.search(pattern, out)
            rtt = float(m.group(1)) if m else None
            loss_m = re.search(r"(\d+)%\s*(packet\s*)?loss", out, re.IGNORECASE)
            loss = int(loss_m.group(1)) if loss_m else 0
            results.append((label, rtt, loss))
        else:
            results.append((label, None, 100))

    print()
    for label, rtt, loss in results:
        if rtt is None:
            fail(f"{label:<35} → unreachable")
        elif loss > 0:
            warn(f"{label:<35} → {rtt:.1f} ms  |  {loss}% loss")
        elif rtt < 30:
            ok(f"{label:<35} → {rtt:.1f} ms  ✦ Excellent")
        elif rtt < 80:
            ok(f"{label:<35} → {rtt:.1f} ms  ✦ Good")
        elif rtt < 150:
            warn(f"{label:<35} → {rtt:.1f} ms  ✦ Fair")
        else:
            fail(f"{label:<35} → {rtt:.1f} ms  ✦ Poor")
            fix("High latency — check for background downloads, VPN overhead, or ISP issues.")


def full_scan():
    """Run all checks sequentially."""
    check_interface()
    check_gateway()
    check_dns()
    check_internet()
    check_firewall()
    check_speed()


def save_report():
    """Write the collected findings to a text file."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"netfix_report_{ts}.txt"
    filepath = os.path.join(os.path.expanduser("~"), filename)

    with open(filepath, "w") as f:
        f.write(f"NetFix Report — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"OS: {platform.system()} {platform.release()}\n")
        f.write("=" * 65 + "\n\n")
        for line in REPORT_LINES:
            f.write(line + "\n")

    print(f"\n  {C.GREEN}Report saved to: {filepath}{C.RESET}")


def summary():
    section("📋 Session Summary")

    fails  = [l for l in REPORT_LINES if l.startswith("[FAIL]")]
    warns  = [l for l in REPORT_LINES if l.startswith("[WARN]")]
    fixes  = [l for l in REPORT_LINES if l.startswith("[FIX]")]
    oks    = [l for l in REPORT_LINES if l.startswith("[OK]")]

    print(f"\n  {C.GREEN}Passed   : {len(oks)}{C.RESET}")
    print(f"  {C.YELLOW}Warnings : {len(warns)}{C.RESET}")
    print(f"  {C.RED}Failures : {len(fails)}{C.RESET}")

    if fails:
        print(f"\n  {C.RED}{C.BOLD}Issues detected:{C.RESET}")
        for l in fails:
            print(f"  {C.RED}• {l.replace('[FAIL]  ', '')}{C.RESET}")

    if fixes:
        print(f"\n  {C.YELLOW}{C.BOLD}Recommended actions:{C.RESET}")
        seen = set()
        for l in fixes:
            msg = l.replace("[FIX]   ", "")
            if msg not in seen:
                print(f"  {C.YELLOW}➜ {msg}{C.RESET}")
                seen.add(msg)

    if not fails and not warns:
        print(f"\n  {C.GREEN}{C.BOLD}🎉  No issues found! Your network looks healthy.{C.RESET}")

    save_q = ask("Save full report to file?", ["y", "n"])
    if save_q == "y":
        save_report()


# ─── Main interactive loop ────────────────────────────────────────────────────

def main():
    banner()

    while True:
        idx = menu("What would you like to do?", [
            "Run FULL diagnostic scan (all checks)",
            "Check network interface / IP address",
            "Check default gateway reachability",
            "Check DNS resolution",
            "Check internet connectivity",
            "Check specific host + port reachability",
            "Run traceroute (path analysis)",
            "Check firewall status",
            "Run latency benchmark",
            "View session summary & save report",
            "Exit",
        ])

        if   idx == 0:  full_scan()
        elif idx == 1:  check_interface()
        elif idx == 2:  check_gateway()
        elif idx == 3:
            custom = ask("Test a specific hostname? (press Enter to use defaults)")
            check_dns(custom or None)
        elif idx == 4:
            target = ask("Target IP to ping (press Enter for 8.8.8.8)")
            check_internet(target or "8.8.8.8")
        elif idx == 5:  check_ports()
        elif idx == 6:  check_traceroute()
        elif idx == 7:  check_firewall()
        elif idx == 8:  check_speed()
        elif idx == 9:  summary()
        elif idx == 10:
            print(f"\n  {C.CYAN}Goodbye! Stay connected. 👋{C.RESET}\n")
            sys.exit(0)

        input(f"\n  {C.DIM}Press Enter to return to the menu…{C.RESET}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {C.YELLOW}Interrupted by user. Bye!{C.RESET}\n")
        sys.exit(0)
