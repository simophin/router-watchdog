#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = ["tapo", "aiohttp"]
# ///
import asyncio
import os
from datetime import datetime
import aiohttp

from tapo import ApiClient


async def main():

    tapo_username = os.getenv("TAPO_USERNAME")
    tapo_password = os.getenv("TAPO_PASSWORD")
    ip_address = os.getenv("IP_ADDRESS")

    client = ApiClient(tapo_username, tapo_password)
    device = await client.p110(ip_address)

    async def check_internet():
        # Perform an HTTP GET request to google.com
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://www.google.com", timeout=5) as resp:
                    return resp.status == 200
        except Exception:
            return False

    failure_count = 0
    while True:
        success = await check_internet()
        if success:
            print(f"[{datetime.now()}] Internet OK")
            failure_count = 0
        else:
            failure_count += 1
            print(f"[{datetime.now()}] Internet DOWN (fail {failure_count})")
            if failure_count >= 5:
                print(f"[{datetime.now()}] Restarting plug due to 5 consecutive failures...")
                await device.off()
                await asyncio.sleep(2)
                await device.on()
                failure_count = 0
                await asyncio.sleep(60)
        await asyncio.sleep(60)


def get_quarter_start_month(today: datetime) -> int:
    return 3 * ((today.month - 1) // 3) + 1


if __name__ == "__main__":
    asyncio.run(main())