import asyncio

import aiohttp


async def main():
    client = aiohttp.ClientSession()

    # Создание user
    response = await client.post(
        "http://127.0.0.1:8080/users",
        json={"name": "Barsik", "password": "T8765!!!!!!!!!88894"},
    )
    print(response.status)
    print(await response.json())

    # GET  user
    response = await client.get(
        "http://127.0.0.1:8080/users/1",
    )
    print(response.status)
    print(await response.json())


    # Изменение user
    response = await client.patch(
        "http://127.0.0.1:8080/users/1",
        json={"name": "Foxxxxx"},
    )
    print(response.status)
    print(await response.json())

    # Удаление user
    response = await client.delete(
        "http://127.0.0.1:8080/users/1",
    )
    print(response.status)
    print(await response.json())



    # Создание объявления
    response = await client.post(
        "http://127.0.0.1:8080/adverts",
        json={"header": "Notebook", "description": "LENOVO", "owner_id": 2},
    )
    print(response.status)
    print(await response.json())

    # Изменение объявления
    response = await client.patch(
        "http://127.0.0.1:8080/notes/1",
        json={"header": "Computer"},
    )
    print(response.status)
    print(await response.json())

    # Получение объявления
    response = await client.get(
        "http://127.0.0.1:8080/notes/1",
    )
    print(response.status)
    print(await response.json())

    # Удаление объявления
    response = await client.get(
        "http://127.0.0.1:8080/notes/1",
    )
    print(response.status)
    print(await response.json())



    await client.close()


asyncio.run(main())