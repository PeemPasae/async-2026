# สำรอง: ใช้เมื่อ VPL ไม่มี aiohttp (ModuleNotFoundError)
import asyncio
import json
import urllib.request


def _get_json(url: str):
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode())


async def fetch_pokemon(pokemon_name: str):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"

    data = await asyncio.to_thread(_get_json, url)

    primary_type = data["types"][0]["type"]["name"]

    return {"name": pokemon_name, "type": primary_type}


async def get_pokemons_info():
    results = await asyncio.gather(
        fetch_pokemon("ditto"),
        fetch_pokemon("pikachu"),
        fetch_pokemon("charizard"),
    )
    return results


if __name__ == "__main__":
    print(asyncio.run(get_pokemons_info()))
