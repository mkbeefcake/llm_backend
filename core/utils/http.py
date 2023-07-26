import asyncio

import aiohttp


async def http_get_bytes(url, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, **kwargs) as resp:
            return await resp.read()


async def http_get_json(url, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, **kwargs) as resp:
            return await resp.json()


async def http_post_for_json(url, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, **kwargs) as resp:
            return await resp.json()


async def http_post_for_byte(url, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, **kwargs) as resp:
            return await resp.read()
