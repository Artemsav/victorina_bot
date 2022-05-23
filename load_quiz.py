import os


def fetch_quiz(folder):
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
            if type(quiestion) == list:
                quiestion = ' '.join(quiestion)
            _, *answer = ans.split(':')
            if type(answer) == list:
                answer = ''.join(answer)
            victorina_quiz[quiestion] = answer
    return victorina_quiz


if __name__ == '__main__':
    pass
