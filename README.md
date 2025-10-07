# Mini Offensive Toolkit
## What this project is

Mini Offensive Toolkit is my personal, lab-only collection of lightweight offensive utilities for learning and red-team practice.
This is a learning project — not a drop-in replacement for commercial/red-team frameworks. It deliberately reimplements small, focused features (recon primitives, safe validators) so I can understand the attack lifecycle end-to-end and build reliable detection/defense knowledge in parallel.

Important: This repository is for use in isolated lab environments you own or explicitly control. Do not run these tools against third-party systems. Misuse is illegal and unethical.



## Current tools (Recon phase)

These are the modules I’ve implemented so far:

#### Port scanner

Implemented with Python socket-based scanning.

Includes basic banner grabbing to capture server headers/service banners.

Next steps: add lightweight vulnerability heuristics and passive fingerprinting.

#### Subdomain enumerator

Wordlist-driven discovery using HTTP probes.

Uses concurrent workers (threading) to speed enumeration.

Next steps: integrate passive OSINT sources and result deduplication.

#### Directory brute-forcer

Directory and file enumeration against web targets using concurrent HTTP requests.

Supports basic wordlists and customizable paths.

Next steps: add response fingerprinting (to reduce false positives) and respect robots.txt by default.