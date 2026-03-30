# Advanced XSS Scanner

Advanced XSS Scanner is a Python-based tool built for automating XSS testing during web security assessments and bug bounty reconnaissance.

## Features

- URL collection using:
  - katana
  - gau
  - waybackurls
- Subdomain enumeration using subfinder
- Parameterized URL detection
- Async scanning using aiohttp
- Multiple XSS payload injection
- Results saved automatically

## Requirements

- Python 3
- aiohttp
- rich
- katana
- gau
- waybackurls
- subfinder

## Installation

Clone the repository:

git clone https://github.com/sapariya333-sys/advanced-xss-scanner

Move into the folder:

cd advanced-xss-scanner

Install Python dependencies:

pip install aiohttp rich

## Usage

Run the scanner:

python xss.py

Then enter the target domain when prompted.

Example:

example.com

## Disclaimer

This tool is created for educational purposes and authorized security testing only. Do not use it on systems without proper permission.

## Author

Parth  
