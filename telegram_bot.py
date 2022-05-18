import logging
import os
import re
from secrets import choice

from dotenv import load_dotenv
from telegram import Update, ForceReply, Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from logging_handler import TelegramLogsHandler
import random
import redis

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    '''user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Привет {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )'''
    keyboard = [
        [
            InlineKeyboardButton("Новый вопрос", callback_data='1'),
            InlineKeyboardButton("Сдаться", callback_data='2')
            ],
            [InlineKeyboardButton("Мой счет", callback_data='3')]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Привет! Я бот для викторин', reply_markup=reply_markup)


def check_messages(update: Update, context: CallbackContext) -> None:
    """Handle the answer on the user message."""
    user_id = update.message.from_user.id
    answer = redis_base.get(user_id)
    logger.info(answer)
    if update.message.text==answer:
        update.message.reply_text('Правильно!')
    else:
        update.message.reply_text(f'Не правильно, вот корректный ответ {answer}')


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    if query.data == '1':
        logger.info(f'{query.data} in if')
        folder = 'quiz-questions/'
        key, value = random.choice(list(fetch_victorins(folder).items()))
        logger.info(f'{value}')
        redis_base.set(user_id, key)
        query.edit_message_text(text=f"{key}") 


def fetch_victorins(folder):
    victorina_quiz = {}
    quiestions = []
    answers = []
    #os.listdir(folder)
    all_victorins = [1]
    for victorin in all_victorins:
        #os.path.join(folder, victorin)
        with open('quiz-questions/9gag.txt', encoding='KOI8-R') as file:
            text = file.read()
        raw_quiz = text.split(sep='\n\n')
        for chunk in raw_quiz:
            if 'Вопрос ' in chunk:
                quiestions.append(chunk)
            if 'Ответ:' in chunk:
                answers.append(chunk)
        quiest_answer = zip(quiestions, answers)
        for quiest, ans in quiest_answer:
            _, *quiestion = quiest.split(':\n')
            if type(quiestion)==list:
                quiestion = ' '.join(quiestion)
            _, *answer = ans.split(':')
            if type(answer)==list:
                answer = ''.join(answer)
            victorina_quiz[quiestion]=answer
    return victorina_quiz




def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    load_dotenv()
    token = os.getenv('TOKEN_TELEGRAM')
    user_id = os.getenv('TG_USER_ID')
    redis_host = os.getenv('REDDIS_HOST')
    redis_port = os.getenv('REDDIS_PORT')
    redis_pass = os.getenv('REDDIS_PASS')
    folder = 'quiz-questions/'
    victorins= fetch_victorins(folder)
    global redis_base
    redis_base = redis.Redis(host=redis_host, port=redis_port, password=redis_pass)
    logging_token = os.getenv('TG_TOKEN_LOGGING')
    logging_bot = Bot(token=logging_token)
    logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    logger.setLevel(logging.DEBUG)
    logger.addHandler(TelegramLogsHandler(tg_bot=logging_bot, chat_id=user_id))
    logger.info(f'Quiz bot запущен')
    """Start the bot."""
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, check_messages))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    #fetch_victorins('quiz-questions/')
    main()