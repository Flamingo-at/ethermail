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
+ Register and replenish the balance <a href="https://captcha.guru/">captcha.guru</a>
+ Run the bot:
```python
python ethermail.py
```

## ✔️ Usage
+ ```Referral code``` - your referrals code
  + Example: ```https://ethermail.io/?afid=630f3vh16ec84729e1c017f3```, code = ```630f3vh16ec84729e1c017f3```
+ ```Captcha key``` - key from captcha.guru(the key is on the main page)
+ ```Delay(sec)``` - delay between referral registrations in seconds
+ ```Threads``` - number of simultaneous registrations

Temporary email addresses are used to register referrals

**Successfully registered referrals are saved in** ```registered.txt``` **in the format {email}:{address}:{private_key}**

## 📧 Contacts
+ Telegram - [@flamingoat](https://t.me/flamingoat)
