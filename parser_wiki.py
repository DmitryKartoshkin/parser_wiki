import asyncio
import aiohttp
from bs4 import BeautifulSoup
from collections import Counter
import csv


URL = "https://ru.wikipedia.org/wiki/Категория:Животные_по_алфавиту"
csv_file = "beasts.csv"

alphabet = []
alphabet_eng = [chr(i).upper() for i in range(97, 123)]
alphabet_rus = [chr(i).upper() for i in range(1072, 1104)]

LETTERS = alphabet_eng + alphabet_rus


def _writing_to_file(dict_: dict):
    with open(csv_file, 'w', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for k, v in dict_.items():
            list_ = [k, v]
            writer.writerow(list_)


async def get_url_text(params, session):
    async with session.get(URL, params=params) as response:
        return await response.text()


async def count_animals(letter, session, params=None):
    if params is None:
        params = {"title": "Категория:Животные_по_алфавиту", "from": letter}

    text = await get_url_text(params, session)
    soup = BeautifulSoup(text, "html.parser")
    animal_block = soup.find('div', attrs={'class': 'mw-category-columns'})
    animals = animal_block.text.split("\n")

    if animals[0] != letter:
        return

    sres = animals[1:-1]
    sres_list = [i[0] for i in sres if i[0] == letter]
    alphabet.extend(sres_list)

    if len(animals) < 201:
        return

    params = {
        "title": "Категория:Животные_по_алфавиту",
        "pagefrom": animals[-1],
    }
    await count_animals(letter, session, params)


async def main():
    tasks = []

    async with aiohttp.ClientSession() as session:
        for letter in LETTERS:
            task = asyncio.create_task(count_animals(letter, session))
            tasks.append(task)

        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
    count = Counter(alphabet)
    sorted_alphabet = dict(sorted(count.items()))
    _writing_to_file(sorted_alphabet)

