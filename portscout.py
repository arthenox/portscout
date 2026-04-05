#!/usr/bin/env python3
import argparse
import socket
import sys
import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, SpinnerColumn
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

console = Console() if RICH_AVAILABLE else None

BANNER = """
[bold cyan]
 ██████╗  ██████╗ ██████╗ ████████╗███████╗ ██████╗  ██████╗ ██╗   ██╗████████╗
 ██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝██╔════╝ ██╔═══██╗██║   ██║╚══██╔══╝
 ██████╔╝██║   ██║██████╔╝   ██║   ███████╗██║      ██║   ██║██║   ██║   ██║   
 ██╔═══╝ ██║   ██║██╔══██╗   ██║   ╚════██║██║      ██║   ██║██║   ██║   ██║   
 ██║     ╚██████╔╝██║  ██║   ██║   ███████║╚██████╗ ╚██████╔╝╚██████╔╝   ██║   
 ╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝  ╚═════╝  ╚═════╝    ╚═╝   
[/bold cyan]
[dim]By arthenox | Professional Port Scanner | Stealthier & File Support[/dim]
"""

TOP_PORTS = [21, 22, 23, 25, 53, 80, 110, 139, 443, 445, 1433, 3306, 3389, 8080, 8443]

def grab_banner(sock):
    try:
        sock.settimeout(2.0)
        banner = sock.recv(1024).decode(errors='ignore').strip()
        if banner:
            return banner[:50]
        sock.sendall(b"\r\n")
        banner = sock.recv(1024).decode(errors='ignore').strip()
        return banner[:50]
    except:
        return "n/a"

def scan_port(target, port, timeout=1, grab=False):
    res = {"port": port, "open": False, "banner": ""}
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((target, port))
        if result == 0:
            res["open"] = True
            if grab:
                res["banner"] = grab_banner(sock)
        sock.close()
    except:
        pass
    return res

def parse_ports(port_spec):
    ports = set()
    if '-' in port_spec:
        s, e = map(int, port_spec.split('-'))
        ports.update(range(s, e+1))
    else:
        for p in port_spec.split(','):
            if p.strip(): ports.add(int(p.strip()))
    return sorted(ports)

def main():
    parser = argparse.ArgumentParser(description="PortScout – Professional Port Scanner")
    parser.add_argument("targets", help="Target IP, Domain, or .txt file")
    parser.add_argument("-p", "--ports", help="Ports (e.g. 80,443 or 1-1000)")
    parser.add_argument("--top", action="store_true", help="Scan top common ports")
    parser.add_argument("--grab", action="store_true", help="Enable banner grabbing")
    parser.add_argument("-t", "--threads", type=int, default=100)
    parser.add_argument("--timeout", type=float, default=1.5)
    parser.add_argument("-o", "--output", help="Save results (txt/json)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if RICH_AVAILABLE: console.print(BANNER)
    else: print("--- PortScout Professional ---\n")

    ports = TOP_PORTS if args.top or not args.ports else parse_ports(args.ports)

    target_list = []
    if args.targets.endswith('.txt') and os.path.exists(args.targets):
        with open(args.targets, 'r') as f:
            target_list = [line.strip() for line in f if line.strip()]
    else:
        target_list = [args.targets]

    final_results = {}

    for target in target_list:
        try:
            target_ip = socket.gethostbyname(target)
            if RICH_AVAILABLE: console.print(f"\n[bold blue]▶ Target:[/bold blue] {target} ({target_ip})")
            else: print(f"\n[*] Scanning {target} ({target_ip})...")
        except:
            print(f"[!] Could not resolve {target}")
            continue

        found_ports = []
        if RICH_AVAILABLE:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), console=console) as progress:
                task = progress.add_task(f"[cyan]Scanning {len(ports)} ports...", total=len(ports))
                with ThreadPoolExecutor(max_workers=args.threads) as executor:
                    futures = [executor.submit(scan_port, target_ip, p, args.timeout, args.grab) for p in ports]
                    for future in as_completed(futures):
                        res = future.result()
                        if res["open"]: found_ports.append(res)
                        progress.update(task, advance=1)
        else:
            with ThreadPoolExecutor(max_workers=args.threads) as executor:
                futures = [executor.submit(scan_port, target_ip, p, args.timeout, args.grab) for p in ports]
                for future in as_completed(futures):
                    res = future.result()
                    if res["open"]:
                        found_ports.append(res)
                        if args.verbose: print(f"[+] Port {res['port']} is OPEN")

        final_results[target] = found_ports

        if RICH_AVAILABLE and found_ports:
            table = Table(header_style="bold green")
            table.add_column("Port", justify="right")
            table.add_column("Service")
            if args.grab: table.add_column("Banner")
            
            for p in sorted(found_ports, key=lambda x: x['port']):
                try: service = socket.getservbyport(p['port'])
                except: service = "unknown"
                row = [str(p['port']), service]
                if args.grab: row.append(p['banner'])
                table.add_row(*row)
            console.print(table)

    if args.output:
        with open(args.output, 'w') as f:
            if args.output.endswith('.json'): json.dump(final_results, f, indent=4)
            else:
                for target, results in final_results.items():
                    f.write(f"Target: {target}\n" + "-"*20 + "\n")
                    for p in results: f.write(f"{p['port']} (Banner: {p.get('banner', 'N/A')})\n")
        print(f"\n[✓] Results saved to {args.output}")

if __name__ == "__main__":
    main()
