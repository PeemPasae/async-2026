import asyncio
import aiohttp


async def fetch_pokemon(pokemon_name: str):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

    # ดึงประเภทแรก (Primary Type) จากโครงสร้าง JSON
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