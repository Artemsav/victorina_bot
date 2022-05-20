import logging
import os
import time
import random

import vk_api as vk
from dotenv import load_dotenv
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from telegram import Bot
from logging_handler import TelegramLogsHandler
from load_victorins import fetch_victorins
import redis

logger = logging.getLogger(__name__)


def handle_new_question_request(event, vk_api, keyboard, victorins, redis_base):
    user_id = event.user_id
    qestion, answer = random.choice(list(victorins.items()))
    redis_base.set(user_id, qestion)
    redis_base.set(qestion, answer)
    vk_api.messages.send(
        user_id=user_id,
        message=f"{qestion}",
        random_id=get_random_id(),
        keyboard=keyboard
    )


def handle_giveup(event, vk_api, keyboard, redis_base):
    user_id = event.user_id
    question = redis_base.get(user_id)
    answer = redis_base.get(question)
    decoded_answer, *_ = answer.decode('utf-8').strip('\n').strip('"').split('.')
    vk_api.messages.send(
        user_id=user_id,
        message=f"Правильный ответ это: {decoded_answer}",
        random_id=get_random_id(),
        keyboard=keyboard
    )


def handle_solution_attempt(event, vk_api, keyboard, redis_base):
    user_id = event.user_id
    question = redis_base.get(user_id)
    answer = redis_base.get(question)
    decoded_answer, *_ = answer.decode('utf-8').strip('\n').strip('"').split('.')
    if event.text == decoded_answer:
        vk_api.messages.send(
            user_id=user_id,
            message='Правильно!',
            random_id=get_random_id(),
            keyboard=keyboard
            )
    else:
        vk_api.messages.send(
            user_id=user_id,
            message='Не правильно, попробуйте еще раз,\
                    либо нажмите сдаться чтобы\
                    увидеть правильный ответ',
            random_id=get_random_id(),
            keyboard=keyboard
            )


def score():
    #ToDo
    pass


def main():
    load_dotenv()
    token = os.getenv('VK_KEY')
    user_id = os.getenv('TG_USER_ID')
    logging_token = os.getenv('TG_TOKEN_LOGGING')
    redis_host = os.getenv('REDDIS_HOST')
    redis_port = os.getenv('REDDIS_PORT')
    redis_pass = os.getenv('REDDIS_PASS')
    redis_base = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_pass
        )
    logging_bot = Bot(token=logging_token)
    folder = os.getenv('FOLDER')
    victorins = fetch_victorins(folder)
    logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    logger.setLevel(logging.DEBUG)
    """Start the bot."""
    vk_session = vk.VkApi(token=token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()  # Переход на вторую строку
    keyboard.add_button('Получить счет', color=VkKeyboardColor.PRIMARY)
    keyboard = keyboard.get_keyboard()
    logger.addHandler(TelegramLogsHandler(tg_bot=logging_bot, chat_id=user_id))
    logger.info('Quiz vk bot запущен')
    for event in longpoll.listen():
        try:
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text == 'Привет':
                    vk_api.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        keyboard=keyboard,
                        message='Привет я бот для викторин!'
                        )
                elif event.text == 'Новый вопрос':
                    handle_new_question_request(
                        event,
                        vk_api,
                        keyboard,
                        victorins,
                        redis_base
                        )
                elif event.text == 'Сдаться':
                    handle_giveup(event, vk_api, keyboard, redis_base)
                elif event.text == 'Получить счет':
                    score()
                elif event.text:
                    handle_solution_attempt(
                        event,
                        vk_api,
                        keyboard,
                        redis_base
                        )
        except ConnectionError as exc:
            logger.error(exc)
            time.sleep(60)


if __name__ == '__main__':
    main()
