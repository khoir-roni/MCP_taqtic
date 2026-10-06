#!/usr/bin/env python3
"""
tactiq_mcp_client.py

Klien CLI mandiri untuk berinteraksi dengan Tactiq MCP Server via stdio bridge (mcp-remote).
Memungkinkan mahasiswa S2 melihat daftar rekaman kuliah, mencari topik pertemuan,
dan mengambil metadata rapat langsung dari terminal.

Penggunaan:
    python scripts/tactiq_mcp_client.py list [--limit 5]
    python scripts/tactiq_mcp_client.py search --query "Metodologi"
    python scripts/tactiq_mcp_client.py get --id "MEETING_ID"
"""

import sys
import os
import json
import subprocess
import argparse

MCP_SERVER_URL = "https://mcp.tactiq.io"

class TactiqMCPClient:
    def __init__(self):
        npx_cmd = "npx.cmd" if os.name == "nt" else "npx"
        self.proc = subprocess.Popen(
            [npx_cmd, "-y", "mcp-remote", MCP_SERVER_URL],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.req_id = 1
        self._initialize()

    def _send_request(self, method, params=None):
        payload = {
            "jsonrpc": "2.0",
            "id": self.req_id,
            "method": method,
            "params": params or {}
        }
        self.req_id += 1
        self.proc.stdin.write(json.dumps(payload) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            return None
        return json.loads(line)

    def _send_notification(self, method, params=None):
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }
        self.proc.stdin.write(json.dumps(payload) + "\n")
        self.proc.stdin.flush()

    def _initialize(self):
        self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "TactiqCLIClient", "version": "1.0.0"}
        })
        self._send_notification("notifications/initialized")

    def call_tool(self, tool_name, args=None):
        resp = self._send_request("tools/call", {
            "name": tool_name,
            "arguments": args or {}
        })
        if not resp:
            return {"error": "No response from MCP server"}
        if "error" in resp:
            return resp
        result = resp.get("result", {})
        structured = result.get("structuredContent")
        if structured:
            return structured
        for content in result.get("content", []):
            if content.get("type") == "text":
                try:
                    return json.loads(content["text"])
                except Exception:
                    return {"text": content["text"]}
        return result

    def close(self):
        try:
            self.proc.terminate()
        except Exception:
            pass

def cmd_list(client, limit):
    print(f"\n[Info] Mengambil {limit} rekaman terbaru dari Tactiq MCP...\n")
    data = client.call_tool("list_recent_meetings", {"limit": limit})
    results = data.get("results", [])
    if not results:
        print("Tidak ada rekaman yang ditemukan.")
        return

    print(f"{'ID':<24} | {'Tanggal':<12} | {'Durasi':<10} | {'Judul Pertemuan'}")
    print("-" * 80)
    for m in results:
        mid = m.get("id", "-")
        date_raw = m.get("createdAt", "-")[:10]
        dur_sec = m.get("durationSeconds", 0)
        dur_str = f"{dur_sec // 60}m {dur_sec % 60}s"
        title = m.get("title", "Untitled")
        print(f"{mid:<24} | {date_raw:<12} | {dur_str:<10} | {title}")

def cmd_search(client, query):
    print(f"\n[Info] Mencari pertemuan dengan kata kunci: '{query}'...\n")
    data = client.call_tool("search_meetings", {"query": query})
    results = data.get("results", [])
    if not results:
        print("Tidak ada hasil yang cocok dengan pencarian.")
        return

    print(f"{'ID':<24} | {'Tanggal':<12} | {'Judul Pertemuan'}")
    print("-" * 70)
    for m in results:
        mid = m.get("id", "-")
        date_raw = m.get("createdAt", "-")[:10]
        title = m.get("title", "Untitled")
        print(f"{mid:<24} | {date_raw:<12} | {title}")

def cmd_get(client, meeting_id):
    print(f"\n[Info] Membaca detail pertemuan ID: {meeting_id}...\n")
    data = client.call_tool("get_meeting", {"id": meeting_id})
    if data.get("error") == "access_required":
        print("[Perhatian] Akun Tactiq saat ini memerlukan paket Team / 14-day trial untuk membaca detail transkrip penuh via MCP.")
        print("URL Upgrade / Trial:", data.get("url", "https://app.tactiq.io/billing"))
    else:
        print(json.dumps(data, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Tactiq MCP Client CLI untuk Studi S2")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # list
    p_list = subparsers.add_parser("list", help="Tampilkan daftar pertemuan/kuliah terbaru")
    p_list.add_argument("--limit", type=int, default=5, help="Jumlah pertemuan (default: 5)")

    # search
    p_search = subparsers.add_parser("search", help="Cari pertemuan berdasarkan kata kunci")
    p_search.add_argument("--query", required=True, help="Kata kunci pencarian")

    # get
    p_get = subparsers.add_parser("get", help="Ambil detail pertemuan berdasarkan ID")
    p_get.add_argument("--id", required=True, help="Meeting ID dari Tactiq")

    args = parser.parse_args()

    client = TactiqMCPClient()
    try:
        if args.subcommand == "list":
            cmd_list(client, args.limit)
        elif args.subcommand == "search":
            cmd_search(client, args.query)
        elif args.subcommand == "get":
            cmd_get(client, args.id)
    finally:
        client.close()

if __name__ == "__main__":
    main()
