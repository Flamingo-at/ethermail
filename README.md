<h1 align="center">Ethermail</h1>

<p align="center">Registration of referrals for the <a href="https://ethermail.io/">Ethermail.io</a></p>
<p align="center">
<img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54">
</p>

## ⚡ Installation
+ Install [python](https://www.google.com/search?client=opera&q=how+install+python)
+ [Download](https://sites.northwestern.edu/researchcomputing/resources/downloading-from-github) and unzip repository
+ Install requirements:
```python
pip install -r requirements.txt
```

## 💻 Preparing
+ Open ```config.py``` with a text editor:
  + ```REF_CODE``` - your referrals code
    + Example: ```https://ethermail.io/?afid=630f3vh16ec84729e1c017f3```, code = ```630f3vh16ec84729e1c017f3```
  + ```THREADS``` - number of simultaneous registrations
  + ```DELAY``` - delay between referral registrations in seconds
  + ```PROXY_TYPE``` - Write ```1``` if you are going to use regular proxies or ```2``` if mobile proxies.

## ✔️ Usage
+ Run the bot:
```python
python ethermail.py
```
If you are running the code for the first time, a .txt will be created depending on your choice of proxy. Open the .txt and put your proxies there. For regular proxies, as many proxies as there are in the file, so many accounts will be registered. 

You can register 5 accounts on 1 ip, after which the ip will be banned.

Temporary email addresses are used to register referrals.

**Successfully registered referrals are saved in** ```registered.txt``` **in the format** ```{email}:{address}:{private_key}```

## 📧 Contacts
+ Telegram - [@flamingoat](https://t.me/flamingoat)
