import asyncio
import aiohttp

from re import findall
from web3.auto import w3
from loguru import logger
from aiohttp import ClientSession
from eth_account.messages import encode_defunct
from pyuseragents import random as random_useragent


async def create_email(client: ClientSession) -> str:
    try:
        response = await client.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1")
        email = (await response.json())[0]
        return email
    except Exception:
        logger.error("Failed to create email")
        await asyncio.sleep(1)
        return await create_email(client)


async def create_wallet() -> tuple[str, str]:
    account = w3.eth.account.create()
    return str(account.address), str(account.privateKey.hex())


async def create_signature(private_key: str) -> str:
    message = encode_defunct(
        text='I have read and accept the terms and conditions of the website.')
    signed_message = w3.eth.account.sign_message(message, private_key)
    return signed_message.signature.hex()


async def get_token(client: ClientSession) -> str:
    try:
        response = await client.get(f'https://ethermail.io/?afid={ref}')
        return findall(r'xAccessToken:"(.+)"', await response.text())[0]
    except:
        raise


async def register(client: ClientSession, address: str, private_key: str):
    try:
        response = await client.post('https://ethermail.io/frontend-api/account/authenticate',
                                     json={
                                         "message": "I have read and accept the terms and conditions of the website.",
                                         "web3Address": address,
                                         "signature": await create_signature(private_key),
                                         "scope": 'master',
                                         "token": True
                                     })
        data = (await response.json())['success']
        if not data:
            raise
    except:
        raise


async def worker():
    while True:
        try:
            async with aiohttp.ClientSession(
                headers={"user-agent": random_useragent()}
            ) as client:

                address, private_key = await create_wallet()
                email = await create_email(client)

                logger.info("Get token")
                access_token = await get_token(client)

                client.headers.update({
                    'cookie': f'afid={ref}',
                    'referer': f'https://ethermail.io/?afid={ref}',
                    'x-access-token': access_token
                })

                logger.info('Registration')
                await register(client, address.lower(), private_key)

                logger.info('Add email')
                await client.post('https://ethermail.io/api/users/onboarding',
                                  json={
                                      "email": email
                                  })
        except:
            logger.error('Error\n')
        else:
            with open('registered.txt', 'a', encoding='utf-8') as file:
                file.write(f'{email}:{address}:{private_key}\n')
            logger.success('Successfully\n')

        await asyncio.sleep(delay)


async def main():
    tasks = [asyncio.create_task(worker()) for _ in range(threads)]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    print("Bot Ethermail @flamingoat\n")

    ref = input('Referral code: ')
    delay = int(input('Delay(sec): '))
    threads = int(input('Threads: '))

    asyncio.run(main())