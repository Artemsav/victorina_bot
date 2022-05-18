import logging
import os

from dotenv import load_dotenv
from telegram import Update, ForceReply, Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from logging_handler import TelegramLogsHandler


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


def echo_messages(update: Update, context: CallbackContext) -> None:
    """Handle the answer message from dialogflow on the user message."""
    update.message.reply_text(update.message.text)


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    update.message.edit_text(text="Selected option: {}".format(query.data))


def fetch_victorins(folder):
    victorina_quiz = {}
    quiestions = []
    answers = []
    all_victorins = os.listdir(folder)
    for victorin in all_victorins:
        with open(os.path.join(folder, victorin), encoding='KOI8-R') as file:
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
            victorina_quiz[quiestion]=answer
    return victorina_quiz


def main():
    load_dotenv()
    token = os.getenv('TOKEN_TELEGRAM')
    user_id = os.getenv('TG_USER_ID')
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
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo_messages))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    #fetch_victorins('quiz-questions/')
    main()