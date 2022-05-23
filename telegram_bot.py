import logging
import os
import random
from functools import partial

import redis
from dotenv import load_dotenv
from telegram import Bot, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, Updater)

from load_quiz import fetch_quiz
from logging_handler import TelegramLogsHandler

logger = logging.getLogger(__name__)

QUISTION, SCORE, CHECK = range(3)


def menu(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            "Новый вопрос",
            "Сдаться",
            ],
        [
            "Мой счет"
            ]
        ]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    return reply_markup


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Я бот для викторин', reply_markup=menu(update, context))

    return QUISTION


def handle_solution_attempt(
    redis_base,
    update: Update,
    context: CallbackContext
    ) -> None:
    """Handle the answer on the user message."""
    user_id = update.message.from_user.id
    question = redis_base.get(user_id)
    answer = redis_base.get(question)
    decoded_answer, *_ = answer.decode('utf-8').strip('\n').strip('"').split('.')
    if update.message.text == decoded_answer:
        update.message.reply_text('Правильно!', reply_markup=menu(update, context))
    else:
        update.message.reply_text('Не правильно, попробуйте еще раз,\
                                  либо нажмите сдаться чтобы\
                                  увидеть правильный ответ',
                                  reply_markup=menu(update, context)
                                  )
    return CHECK


def handle_new_question_request(redis_base, quizs, update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    qestion, answer = random.choice(list(quizs.items()))
    redis_base.set(user_id, qestion)
    redis_base.set(qestion, answer)
    update.message.reply_text(text=f"{qestion}", reply_markup=menu(update, context))
    return CHECK


def handle_giveup(redis_base, update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    question = redis_base.get(user_id)
    answer = redis_base.get(question)
    decoded_answer, *_ = answer.decode('utf-8').strip('\n').strip('"').split('.')
    update.message.reply_text(
        text=f"Правильный ответ это: {decoded_answer}",
        reply_markup=menu(update, context)
                )
    return QUISTION


def score(update: Update, context: CallbackContext) -> int:
    #ToDO    
    return ConversationHandler.END


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
    folder = os.getenv('FOLDER')
    quizs = fetch_quiz(folder)
    redis_base = redis.Redis(host=redis_host, port=redis_port, password=redis_pass)
    logging_token = os.getenv('TG_TOKEN_LOGGING')
    logging_bot = Bot(token=logging_token)
    logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    logger.setLevel(logging.DEBUG)
    logger.addHandler(TelegramLogsHandler(tg_bot=logging_bot, chat_id=user_id))
    logger.info('Quiz tg bot запущен')
    """Start the bot."""
    updater = Updater(token)
    dispatcher = updater.dispatcher
    partial_new_question_request = partial(handle_new_question_request, redis_base, quizs)
    partial_handle_solution_attempt = partial(handle_solution_attempt, redis_base)
    partial_handle_giveup = partial(handle_giveup, redis_base)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            QUISTION: [
                MessageHandler(
                    Filters.regex("^(Новый вопрос)$"), partial_new_question_request
                    )
                ],
            CHECK: [
                MessageHandler(
                    Filters.regex("^(Новый вопрос)$"), partial_new_question_request
                    ),
                MessageHandler(
                    Filters.regex("^(Сдаться)$"), partial_handle_giveup
                    ),
                MessageHandler(
                    Filters.text & ~Filters.command, partial_handle_solution_attempt
                    ),
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
    main()
