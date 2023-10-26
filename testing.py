# import asyncio
#
#
# async def k4g():
#     print(1)
#
#
# async def driffle():
#     print(2)
#
#
#
#
# async def main():
#     await asyncio.gather(*[stores[i] for i in stores])

#
# if __name__ == '__main__':
#     asyncio.run(main())  # creats an envent loop

import asyncio

num_word_mapping = {1: 'ONE', 2: 'TWO', 3: "THREE", 4: "FOUR", 5: "FIVE", 6: "SIX", 7: "SEVEN", 8: "EIGHT",
                    9: "NINE", 10: "TEN"}


async def delay_message(delay, message):
    print(f"Printing {message}", delay)
    await asyncio.sleep(2)
    print(delay)

async def delay_message2(delay, message):
    print(f"Printingggg {message}", delay)
    await asyncio.sleep(2)
    print(delay)


stores = {
    # g2a: "G2A",
    delay_message: "K4G",
    delay_message2: "K4G"
}




async def main():
    await asyncio.gather(
        *[i("test", "1") for i in stores])  # awaits completion of all tasks


if __name__ == '__main__':
    asyncio.run(main())  # creats an envent loop