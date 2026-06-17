#!/bin/bash
pip install -q requests beautifulsoup4 lxml 2>/dev/null
cd /root/ClaudeProjects/TopSecret
python3 xsharing_scraper.py --max-pages 100
echo "DONE"
