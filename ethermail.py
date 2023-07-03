import asyncio

from web3.auto import w3
from loguru import logger
from aiohttp import ClientSession
from eth_account.messages import encode_defunct
from pyuseragents import random as random_useragent
from tenacity import retry, retry_if_exception, stop_after_attempt


async def create_email(client: ClientSession) -> str:
    try:
        response = await client.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1")
        email = (await response.json())[0]
        return email
    except Exception:
        logger.error("Failed to create email")
        await asyncio.sleep(2)
        return await create_email(client)


async def create_wallet() -> tuple[str, str]:
    account = w3.eth.account.create()
    return str(account.address), str(account.key.hex())


async def create_signature(private_key: str) -> str:
    message = encode_defunct(text='By signing this message you agree to the Terms and Conditions and Privacy Policy\n\nNONCE: 1')
    signed_message = w3.eth.account.sign_message(message, private_key)
    return signed_message.signature.hex()


@retry(retry=retry_if_exception(Exception), stop=stop_after_attempt(2), reraise=True)
async def get_nonce(client: ClientSession, address: str):
    try:
        response = await client.post('https://ethermail.io/api/auth/nonce',
                                     json={
                                         'walletAddress': address
                                     })
        response.raise_for_status()
    except Exception as error:
        raise Exception(f'Error get token | {error}')


@retry(retry=retry_if_exception(Exception), stop=stop_after_attempt(2), reraise=True)
async def register(client: ClientSession, address: str, private_key: str):
    try:
        response = await client.post('https://ethermail.io/api/auth/login',
                                     json={
                                         "web3Address": address,
                                         "signature": await create_signature(private_key)
                                     })
        response.raise_for_status()
    except Exception as error:
        raise Exception(f'Error registration | {error}')


@retry(retry=retry_if_exception(Exception), stop=stop_after_attempt(2), reraise=True)
async def add_email(client: ClientSession, email: str):
    try:
        response = await client.post('https://ethermail.io/api/users/email/validate',
                                     json={
                                         "email": email
                                     })
        response.raise_for_status()
    except Exception as error:
        raise Exception(f'Error add email | {error}')


async def worker():
    while True:
        try:
            async with ClientSession(
                headers={"user-agent": random_useragent()}
            ) as client:

                address, private_key = await create_wallet()
                email = await create_email(client)

                logger.info("Get nonce")
                await get_nonce(client, address.lower())

                client.headers.update({
                    'content-type': 'application/json',
                    'origin': 'https://ethermail.io',
                    'cookie': f'afid={ref}',
                    'referer': f'https://ethermail.io/?afid={ref}',
                })

                logger.info('Registration')
                await register(client, address.lower(), private_key)

                logger.info('Add email')
                await add_email(client, email)

        except Exception as error:
            logger.error(error)

        else:
            with open('registered.txt', 'a') as file:
                file.write(f'{email}:{address}:{private_key}\n')
            logger.success('Successfully')

        await asyncio.sleep(delay)


async def main():
    tasks = [asyncio.create_task(worker()) for _ in range(threads)]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    print("Bot Ethermail @flamingoat\n")
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    ref = input('Referral code: ')
    delay = int(input('Delay(sec): '))
    threads = int(input('Threads: '))

    asyncio.run(main())