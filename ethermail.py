import os
import ctypes
import asyncio
import platform

from web3.auto import w3
from loguru import logger
from aiohttp import ClientSession
from aiohttp_proxy import ProxyConnector
from eth_account.messages import encode_defunct
from pyuseragents import random as random_useragent
from tenacity import retry, retry_if_exception, stop_after_attempt

from config import THREADS, REF_CODE, DELAY, PROXY_TYPE

logger.add("logger.log", format="{time:YYYY-MM-DD | HH:mm:ss.SSS} | {level} \t| {function}:{line} - {message}")


async def create_email(client: ClientSession) -> str:
    try:
        response = await client.get('https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1')
        email = (await response.json())[0]
        return email
    except Exception:
        logger.error('Failed to create email')
        await asyncio.sleep(2)
        return await create_email(client)


async def create_wallet() -> tuple[str, str]:
    account = w3.eth.account.create()
    return account.address, account.key.hex()


async def create_signature(private_key: str, nonce: str) -> str:
    message = encode_defunct(text=nonce)
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
        raise Exception(f'Error get nonce | {error}')


@retry(retry=retry_if_exception(Exception), stop=stop_after_attempt(2), reraise=True)
async def register(client: ClientSession, address: str, private_key: str) -> str:
    try:
        response = await client.post('https://ethermail.io/api/auth/login',
                                     json={
                                         'web3Address': address,
                                         'signature': await create_signature(private_key, 'By signing this message you agree to the Terms and Conditions and Privacy Policy\n\nNONCE: 1')
                                     })
        data = await response.json()
        token = data['token']
        return token
    except Exception as error:
        raise Exception(f'Error registration | {error}')


@retry(retry=retry_if_exception(Exception), stop=stop_after_attempt(2), reraise=True)
async def add_email(client: ClientSession, email: str):
    try:
        response = await client.post('https://ethermail.io/api/users/email/validate',
                                     json={
                                         'email': email
                                     })
        response.raise_for_status()
    except Exception as error:
        raise Exception(f'Error add email | {error}')


@retry(retry=retry_if_exception(Exception), stop=stop_after_attempt(2), reraise=True)
async def onboarding(client: ClientSession, email: str):
    try:
        response = await client.post('https://ethermail.io/api/users/onboarding',
                                     json={
                                         'email': email
                                     })
        response.raise_for_status()
    except Exception as error:
        raise Exception(f'Error add email | {error}')


@retry(retry=retry_if_exception(Exception), stop=stop_after_attempt(2), reraise=True)
async def keys(client: ClientSession, address: str, private_key: str):
    try:
        response = await client.post('https://ethermail.io/api/users/keys',
                                     json={
                                         'web3Address': f'{address}@ethermail.io',
                                         'web3Signature': await create_signature(private_key, 'ThorProtocol: \n\nAPPID:ryYjjq9Ff2uhwhnWNo8Cr8aF')
                                     })
        response.raise_for_status()
    except Exception as error:
        raise Exception(f'Error add email | {error}')


async def reg(q: asyncio.Queue = None, proxy: str = None, proxy_url: str = None):
    try:
        if PROXY_TYPE == 1:
            proxy = await q.get()
            ip, port, login_proxy, pass_proxy = proxy.split(':')
            proxy = f'http://{login_proxy}:{pass_proxy}@{ip}:{port}'
        proxy_connect = ProxyConnector.from_url(proxy)

        async with ClientSession(
            connector=proxy_connect,
            headers={
                'content-type': 'application/json',
                'origin': 'https://ethermail.io',
                'user-agent': random_useragent()
            }) as client:

            response = await client.get(f'https://ethermail.io/?afid={REF_CODE}')
            session_id = (response.headers.get('Set-Cookie')).split(' ')[0]

            address, private_key = await create_wallet()
            email = await create_email(client)
            
            client.headers.update({'cookie': f'{session_id} afid={REF_CODE}'})

            logger.info('Get nonce')
            await get_nonce(client, address.lower())

            logger.info('Registration')
            token = await register(client, address.lower(), private_key)

            logger.info('Add email')
            await add_email(client, email)

            logger.info('Add key')
            await keys(client, address.lower(), private_key)

    except Exception as error:
        logger.error(error)

    else:
        with open('registered.txt', 'a') as file:
            file.write(f'{email}:{address}:{private_key}\n')
        logger.success('Successfully')

    finally:
        if PROXY_TYPE == 2:
            logger.info('Change IP...')
            async with ClientSession() as change_ip:
                await change_ip.get(proxy_url)
        await asyncio.sleep(DELAY)


async def worker(q: asyncio.Queue = None, proxy: str = None, proxy_url: str = None):
    if PROXY_TYPE == 1:
        while not q.empty():
            await reg(q)
    else:
        while True:
            await reg(proxy, proxy_url)


async def main():
    if PROXY_TYPE == 1:
        with open('proxy.txt', 'r') as file:
            proxies = file.read().splitlines()

        q = asyncio.Queue()
        for proxy in proxies:
            q.put_nowait(proxy)
        parameters = {'q': q}

    else:
        proxies = json.loads(open('mobile_proxy.txt', 'r').read())
        parameters = {'proxy': proxies['proxy'],
                      'proxy_url': proxies['proxy_url']}

    tasks = [asyncio.create_task(worker(**parameters)) for _ in range(THREADS)]
    await asyncio.gather(*tasks)


def check_file():
    if PROXY_TYPE == 1:
        if not os.path.exists('proxy.txt'):
            with open('proxy.txt', 'a') as f:
                f.write("ip:port:login:pass")
            print('In the created file put the proxy in the format as specified in the file\nAfter press enter...')
            input()
    else:
        if not os.path.exists('mobile_proxy.txt'):
            with open('mobile_proxy.txt', 'a') as f:
                f.write('{\n"proxy": "http://login:pass@ip:port",\n"proxy_url": "link to change ip"\n}')
            print('In the created file put the mobile proxy in the format as specified in the file\nAfter press enter...')
            input()


def choose_type(prompt: str, valid_options: list = [1, 2]) -> int:
    user_input = int(input(prompt))
    if user_input not in valid_options:
        print('Choose one of the options')
        return choose_type(prompt)
    return user_input


def update_console_title(my_info):
    ctypes.windll.kernel32.SetConsoleTitleW(my_info)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    update_console_title('Bot Ethermail Flamingo-at')

    check_file()

    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

    asyncio.run(main())

    if PROXY_TYPE == 1:
        logger.debug('Input Enter to exit...')
        input()