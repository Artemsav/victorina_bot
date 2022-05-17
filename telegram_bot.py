from binascii import Incomplete
from curses import raw
import requests
from os import listdir
from more_itertools import grouper
from pprint import pprint

all_victorins = listdir('quiz-questions/')

with open('quiz-questions/9gag.txt', encoding='KOI8-R') as file:
    text = file.read()
raw_quiz = text.split(sep='\n\n')
victorina_quiz = {}
quiestions = []
answer = []
for chunk in raw_quiz:
    if 'Вопрос ' in chunk:
        quiestions.append(chunk)
    if 'Ответ:' in chunk:
        answer.append(chunk)
quiest_answer = zip(quiestions, answer)
for quiestions, answers in quiest_answer:
    print(quiestions.split(':\n'), len(quiestions.split(':\n')))
    _, quiestion = quiestions.split(':\n')
    _, answer = answers.split(':')
    victorina_quiz[quiestion]=answer
print(victorina_quiz)
