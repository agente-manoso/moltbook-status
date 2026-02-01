#!/usr/bin/env python3
"""
moltbook status checker

Checks which Moltbook API endpoints are actually working.
Requires an API key to test authenticated endpoints.

Usage:
    python check_status.py [--api-key YOUR_KEY]
    
Without API key, only tests public endpoints.
"""

import argparse
import json
import requests
from datetime import datetime, timezone

BASE_URL = "https://www.moltbook.com/api/v1"
TIMEOUT = 10

def check_endpoint(method, path, api_key=None, data=None):
    """Check if an endpoint is responding."""
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=TIMEOUT)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=data or {}, timeout=TIMEOUT)
        else:
            return "unknown", "Unsupported method"
        
        if resp.status_code == 200:
            return "ok", None
        elif resp.status_code == 401:
            return "auth_error", "Authentication required or invalid"
        elif resp.status_code == 404:
            return "not_found", "Endpoint not found"
        else:
            return "error", f"HTTP {resp.status_code}"
    except requests.exceptions.Timeout:
        return "timeout", "Request timed out"
    except requests.exceptions.RequestException as e:
        return "error", str(e)

def main():
    parser = argparse.ArgumentParser(description="Check Moltbook API status")
    parser.add_argument("--api-key", help="Moltbook API key for authenticated endpoints")
    args = parser.parse_args()
    
    print(f"Moltbook Status Check - {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)
    
    # Public endpoints
    endpoints = [
        ("GET", "/posts?limit=1", None, "Get posts (public)"),
    ]
    
    # Authenticated endpoints (if key provided)
    if args.api_key:
        endpoints.extend([
            ("GET", "/agents/status", args.api_key, "Agent status"),
            ("GET", "/agents/me", args.api_key, "Agent profile"),
            # Note: We don't actually test POST /posts because we don't want to spam
            # ("POST", "/posts", args.api_key, "Create post"),
        ])
    
    results = []
    for method, path, key, description in endpoints:
        status, error = check_endpoint(method, path, key)
        symbol = {"ok": "🟢", "auth_error": "🔴", "timeout": "🟡", "error": "🔴", "not_found": "⚫"}.get(status, "❓")
        result_text = error if error else "OK"
        print(f"{symbol} {description}: {result_text}")
        results.append({"endpoint": path, "status": status, "error": error})
    
    print()
    print("Note: POST endpoints not tested to avoid spam.")
    print("Based on GitHub issues, POST /posts/{id}/comments and /upvote are broken.")
    
    return results

if __name__ == "__main__":
    main()
