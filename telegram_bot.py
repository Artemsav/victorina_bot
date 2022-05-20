import logging
import os

from dotenv import load_dotenv
from telegram import Update, ForceReply, Bot, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, InlineQueryHandler, ConversationHandler
from logging_handler import TelegramLogsHandler
import random
import redis
from functools import partial

logger = logging.getLogger(__name__)

QUISTION, SCORE, CHECK = range(3)


def menu(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            "Новый вопрос",
            "Сдаться", 
            ],
            ["Мой счет"]
        ]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    return reply_markup


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Я бот для викторин', reply_markup=menu(update, context))

    return QUISTION


def handle_solution_attempt(update: Update, context: CallbackContext) -> None:
    """Handle the answer on the user message."""
    user_id = update.message.from_user.id
    question = redis_base.get(user_id)
    answer = redis_base.get(question)
    decoded_answer, *_ = answer.decode('utf-8').strip('\n').strip('"').split('.')
    logger.info(decoded_answer)
    if update.message.text == decoded_answer:
        update.message.reply_text('Правильно!', reply_markup=menu(update, context))
    else:
        update.message.reply_text('Не правильно, попробуйте еще раз, либо нажмите сдаться чтобы увидеть правильный ответ', reply_markup=menu(update, context))
    return CHECK


def handle_new_question_request(redis_base, update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    folder = 'quiz-questions/'
    qestion, answer = random.choice(list(fetch_victorins(folder).items()))
    redis_base.set(user_id, qestion)
    redis_base.set(qestion, answer)
    update.message.reply_text(text=f"{qestion}", reply_markup=menu(update, context))
    return CHECK


def handle_giveup(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    question = redis_base.get(user_id)
    answer = redis_base.get(question)
    decoded_answer, *_ = answer.decode('utf-8').strip('\n').strip('"').split('.')
    update.message.reply_text(text=f"Правильный ответ это: {decoded_answer}", reply_markup=menu(update, context))
    return QUISTION


def score(update: Update, context: CallbackContext) -> int:
    #ToDO
    
    return ConversationHandler.END


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


def cancel(update: Update, context: CallbackContext):
    """
    User cancelation function.
    Cancel conersation by user.
    """
    user = update.message.from_user
    logger.info("User {} canceled the conversation.".format(user.first_name))
    update.message.reply_text('Завершение викторины',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def handle_error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning(
        f'Update {update} caused error {context.error},traceback {context.error.__traceback__}'
        )


def main():
    load_dotenv()
    token = os.getenv('TOKEN_TELEGRAM')
    user_id = os.getenv('TG_USER_ID')
    redis_host = os.getenv('REDDIS_HOST')
    redis_port = os.getenv('REDDIS_PORT')
    redis_pass = os.getenv('REDDIS_PASS')
    folder = 'quiz-questions/'
    victorins= fetch_victorins(folder)
    #global redis_base
    redis_base = redis.Redis(host=redis_host, port=redis_port, password=redis_pass)
    logging_token = os.getenv('TG_TOKEN_LOGGING')
    logging_bot = Bot(token=logging_token)
    logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    logger.setLevel(logging.DEBUG)
    logger.addHandler(TelegramLogsHandler(tg_bot=logging_bot, chat_id=user_id))
    logger.info(f'Quiz bot запущен')
    logger.info(redis_base)
    """Start the bot."""
    updater = Updater(token)
    dispatcher = updater.dispatcher
    partial_new_question_request = partial(handle_new_question_request, redis_base)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            QUISTION: [
                MessageHandler(
                    Filters.regex("^(Новый вопрос)$"), partial_new_question_request
                    )
                ],
            CHECK: [
                MessageHandler(Filters.regex("^(Новый вопрос)$"), handle_new_question_request),
                MessageHandler(Filters.regex("^(Сдаться)$"), handle_giveup),
                MessageHandler(Filters.text & ~Filters.command, handle_solution_attempt),
                ],
            SCORE: [MessageHandler(Filters.regex("^(Мой счет)$"), score)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    dispatcher.add_handler(conv_handler)
    dispatcher.add_error_handler(handle_error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    #fetch_victorins('quiz-questions/')
    main()