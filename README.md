# Victorina bot

## Project description

This is a quiz bot. The bot can ask questions and check the answers to them. The repository has two scripts for Telegram and VK
At first place after registration and you will get all necessary tokens, see describtion in section instalation. For handeling user answers I have used reddis database.

To run telegram_bot:

```bash
python telegram_bot.py
```

To run vk bot:

```bash
python vk.py
```

Example of telegram bot (or you can find it here: @quiz_dvm_bot):
![Example](./images/examination_tg.gif)

Example of vk bot (or you can find it here: [vk bot of club - SZone-Online клан ГОРН](https://vk.com/club56009176), pick messages there):

![Example](./images/examination_vk.gif)

## Instalation

Python3 should be already installed. Then use pip (or pip3, if there is a conflict with Python2) to install dependencies:

```bash
pip install -r requirements.txt
```

There is enviroment variables using in the application, you will need tp create ```.env``` file. A ```.env``` file is a text file containing key value pairs of all the environment variables required by the application. You can see example of it below:

```python
# example of environment variables defined inside a .env file
TOKEN_TELEGRAM=1253123421:FFA1DSGOh_dfQACXYT5IiQwEBP5CwJozyP8
TG_TOKEN_LOGGING = 9817234321:SSA1DSGOh_dfQACXYT5IiQwEBP5CwCagaV7
TG_USER_ID=612578269
VK_KEY=eLbyo6isRjMrRssdsdsdddsaaafsaad
REDDIS_HOST=redis-12542.c300.eu-central-1-1.ec2.cloud.redislabs.com
REDDIS_PORT=12542
REDDIS_PASS=VwAxxIshJC1WdiDUuqPZN5CUtsP10FDW
```

TOKEN_TELEGRAM - to get it please writte to Telegram @BotFather bot, first you shall ```/start``` command, than ```/newbot```, than follow the instruction in Telegram.  

TG_TOKEN_LOGGING - to get it please writte to Telegram @BotFather bot, first you shall ```/start``` command, than ```/newbot```, than follow the instruction in Telegram.

TG_USER_ID - to get it please writte to Telegram @userinfobot. Send ```/start``` command to the bot.

VK_KEY - in the menu "Work with API" in the group management menu in VK

REDDIS_HOST, REDDIS_PORT, REDDIS_PASS - you will get [there](https://redislabs.com/)

## Project Goals

The code is written for educational purposes on online-course for web-developers [Devman](https://dvmn.org)
