# Advanced Nmap Scanner (PyQt6 GUI)

## Introduction
Advanced Nmap Scanner is a beginner-friendly desktop GUI built with **PyQt6** on top of **Nmap**. It helps users run common network scans with **One click functions**, understand results through structured views (tabs/tree/table/graphs), and explore vulnerability information via **Vulners** and optional **AI-generated** remediation guidance.

## Key features
- **Onboarding guide**: built-in guided tour to help first-time users learn the UI.
- **Target validation**: supports single IPv4, domain names, and IPv4 ranges (e.g. `192.168.1.1-254`).
- **One click functions**
  - **Quick Scan**: fast overview for common ports and services.
  - **Comprehensive Scan**: deeper scan with broader coverage and host details (can take minutes).
  - **Vulnerability Scan**: runs Nmap NSE vulnerability scripts and enriches results with Vulners data.
  - **Custom Scan**: run custom Nmap arguments / scripts.
- **Readable outputs**
  - Text/terminal: original nmap output
  - Hierarchical **Tree View**: structured result and information about the scanned port.
  - Detailed per-host tabs: comprehensive/vulnerability flows.
  - Risk level field for ports (use **Encryption** as standard)
- **History & export**
  - Scans are stored under `History/` as JSON.
  - Export current/history results to **CSV** or **TXT**.
- **Vulnerability dashboard (Home)**
  - Latest CVEs and selected security alerts (via Vulners and external sources).

## Installation & requirements
### Prerequisites
- **Python 3.8+**
- **Nmap** installed
  - Windows: download from `https://nmap.org/download.html`
  - You will need the path to `nmap.exe` (example: `C:\Program Files (x86)\Nmap\nmap.exe`)

### Python libraries
- PyQt6
- python-nmap
- requests
- beautifulsoup4
- matplotlib
- vulners
- Openai-compatible client usage for AI remediation output

Install libraries using the project’s `requirements.txt` (the app also mentions a helper installer script in the user guide). You may also check your installed libraries through `pip list`.

### API Key
As the application required API keys to access several services, you should register your own API key.
- **Vulners**: go to [Vulners](https://vulners.com/) and register a new account. Then go to *Settings*->*API keys*->*Create new API-key*
- **OpenRouter**: go to [OpenRouter](https://openrouter.ai/) and register a new account. 
Go to the [Get API Key](https://openrouter.ai/workspaces/default/keys) or directly click the **Get API Key** once you login. Click **+ New Key** on the right hand corner and fill in the information.

## First launch & configuration
Launch the app through the command `python GUI.py` under your directory.
On first launch, you have to configure the initial setting of the application (e.g. Nmap path, API key) and the configuration is stored in `config.json`. The app also can guide you through the interface with onboarding.

Common configuration items:
- **Nmap path**: required to run scans (must specific initially).
- **Vulners API key**: used by the dashboard and vulnerability enrichment.
  - Note: Vulners free tier commonly has monthly credit limits, use your own key for reliable usage.
- **OpenRouter API key**: optional, used to generate “Vulnerability Solutions” explanations.

## How to use (scan types)
### Quick Scan
Designed for a fast overview.
- **Text Output tab**: quick summary + terminal-like output.
- **Tree View tab**: host/protocol/port hierarchy.

### Comprehensive Scan
Broader scan and richer host detail (may take several minutes).
- Includes a **Detailed Result** area showing per-host information such as addresses, vendor, uptime, OS match visualization, and port table entries.

### Vulnerability Scan
Time-consuming; recommended to scan one device at a time.
- **Vulnerability Result**: raw NSE output grouped by host/port.
- **Vulnerability Solutions**: optional AI-generated sections ordered as:
  - Issue
  - Risk
  - Fix Steps
  - Prevention
  - Action Plan

### Custom Scan
Run custom Nmap arguments/scripts (for advanced users).

## Types of log messages
The program writes logs to `scanner_log.log` in the application folder. Typical log entries include:
- **Startup/config errors**
  - failure to load `config.json`
  - missing/invalid API keys 
- **Scan/runtime errors**
  - invalid Nmap path
  - invalid input target (IP/domain/range)
  - Nmap scan exceptions or timeouts
- **Network/API errors**
  - HTTP errors when fetching Vulners/dashboard data
  - credit/limit errors from Vulners API
  - AI provider errors (invalid key, network failures, unexpected response formats)
- **Parsing/rendering errors**
  - errors creating Tree View content
  - errors creating vulnerability grids/tables

If something looks “stuck” in the UI, check `scanner_log.log` first.

## FAQs
### Do I need to know Nmap commands?
No. Quick/Comprehensive/Vulnerability scans work without memorizing flags. Custom Scan is optional.

### Should I close all open ports that appear?
Not necessarily. Open ports are normal for many systems/services, but every open port is potential attack surface. Harden exposed services, restrict access, and patch regularly.

### If a port is labeled “Low (Safe)”, is it guaranteed safe?
No. “Risk level” in this app is a heuristic (often related to encryption/exposure assumptions). Secure configuration, patching, authentication, and network segmentation still matter.

### Why is Vulnerability Scan slow?
It runs NSE scripts and may query external data sources; scanning many hosts or large port ranges can take a long time.

### Where are scan records stored?
Scan history is stored under `History/` as JSON. Removing files in that folder removes records from history.

## Troubleshooting
- **“Invalid path” / scan won’t start**: reselect your `nmap.exe` path in Settings.
- **Dashboard empty / Vulners errors**: your API key may be missing or out of credits.
- **AI solution tabs not showing**: verify OpenRouter key, network connectivity, and check `scanner_log.log`.
- **Long scans**: comprehensive/vulnerability scans can legitimately take minutes depending on network conditions.

## Project structure (high level)
- `GUI.py`: main window wiring.
- `Widgets/Scanner.py`: Quick/Comprehensive/Vulnerability scan UI and logic.
- `Widgets/CustomScanner.py`: Custom scan UI and logic.
- `Widgets/HomePage.py`: vulnerability dashboard.
- `Widgets/History.py`: scan history browsing/loading.
- `Widgets/MenuBar.py`: top menu, settings, export, onboarding trigger.
- `Widgets/OnboardingTour.py`: onboarding overlay/steps.
- `Widgets/function.py`: utilities (validation, storage, logging setup, link to Openroute, etc.).
- `Document/`: program necessary documents.

## Safety & disclaimer
Use this tool only on networks and hosts you own or have explicit permission to test. AI-generated remediation output is for reference only and should be validated by a qualified professional.

