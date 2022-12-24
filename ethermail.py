import asyncio
import aiohttp

from re import findall
from web3.auto import w3
from loguru import logger
from aiohttp import ClientSession
from eth_account.messages import encode_defunct
from pyuseragents import random as random_useragent


async def sending_captcha(client: ClientSession):
    try:
        response = await client.get(f'http://api.captcha.guru/in.php?key={user_key}&method=userrecaptcha \
            &googlekey=6LdmCaMhAAAAAHuCRyI8Y_K3JbITDhW623QkEPIi&pageurl=https://ethermail.io/')
        data = await response.text()
        if 'ERROR' in data:
            logger.error(print(data))
            return(await sending_captcha(client))
        id = data[3:]
        return(await solving_captcha(client, id))
    except:
        raise Exception()


async def solving_captcha(client: ClientSession, id: str):
    for i in range(100):
        try:
            response = await client.get(f'http://api.captcha.guru/res.php?key={user_key}&action=get&id={id}')
            data = await response.text()
            if 'ERROR' in data:
                logger.error(print(data))
                raise Exception()
            elif 'OK' in data:
                return(data[3:])
            return(await solving_captcha(client, id))
        except:
            raise Exception()
    raise Exception()


async def create_email(client: ClientSession):
    try:
        response = await client.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1")
        email = (await response.json())[0]
        return email
    except Exception:
        logger.error("Failed to create email")
        await asyncio.sleep(1)
        return await create_email(client)


async def create_wallet():
    account = w3.eth.account.create()
    return(str(account.address), str(account.privateKey.hex()))


async def create_signature(private_key: str):
    message = encode_defunct(
        text='I have read and accept the terms and conditions of the website.')
    signed_message = w3.eth.account.sign_message(message, private_key)
    return(signed_message.signature.hex())


async def get_token(client: ClientSession, useragent: str):
    try:
        response = await client.get(f'https://ethermail.io/?afid={ref}',
                                    headers={
                                        'user-agent': useragent
                                    })
        data = await response.text()
        return(findall(r'data-csrf-token="(.+)"', data)[0])
    except:
        raise Exception()


async def register(client: ClientSession, address: str, private_key: str, csrf_token: str, useragent: str):
    try:
        response = await client.post('https://ethermail.io/account/login',
                                     json={
                                         "message": "I have read and accept the terms and conditions of the website.",
                                         "web3Address": address,
                                         'recaptchaResponse': await sending_captcha(client),
                                         "signature": await create_signature(private_key),
                                         "remember": 'true',
                                         "_csrf": csrf_token
                                     }, headers={
                                         'referer': f'https://ethermail.io/?afid={ref}',
                                         'user-agent': useragent
                                     })
        data = await response.text()
        if '404 Error' in data:
            raise Exception()
    except:
        raise Exception()


async def add_email(client: ClientSession, email: str, useragent: str):
    try:
        await client.post('https://ethermail.io/api/users/onboarding',
                          json={
                              "email": email
                          }, headers={
                              'referer': f'https://ethermail.io/?afid={ref}',
                              'user-agent': useragent
                          })
    except:
        raise Exception()


async def worker():
    while True:
        try:
            async with aiohttp.ClientSession() as client:

                address, private_key = await create_wallet()
                useragent = random_useragent()
                email = await create_email(client)

                logger.info('Get token')
                csrf_token = await get_token(client, useragent)

                logger.info('Registration')
                await register(client, address.lower(), private_key, csrf_token, useragent)

                logger.info('Add email')
                await add_email(client, email, useragent)

        except:
            logger.exception('Error\n')
        else:
            logger.info('Saving data')
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
    user_key = input('Captcha key: ')
    delay = int(input('Delay(sec): '))
    threads = int(input('Threads: '))

    asyncio.run(main())
