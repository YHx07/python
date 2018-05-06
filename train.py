"""
coding: utf-8
Создание модели по набору текстов
Павлов Дмитрий
МФТИ 2018
Ревью №1
Версия №0.1.3
"""

import re
import os
import argparse
import json
from collections import Counter

# Командный интерфейс
parser = argparse.ArgumentParser(description='Создание модели. Модель нужна '
                                             'для генерации текстов '
                                             'программой generate.py.')
parser.add_argument('--input-dir',
                    help='Путь к директории с коллекцией .txt документов. '
                         'По этим текстам программа обучится создавть свои '
                         'тексты.',
                    required=True,
                    dest='dir')

parser.add_argument('--model',
                    help='Путь к файлу, в который сохраняется модель. '
                         'Модель нужна для сохранения статистики, полученной '
                         'после обучения.',
                    required=True)

parser.add_argument('--lc',
                    help='Привести тексты к нижнему регистру.',
                    action='store_const',
                    const=True)


def train(file_for_train, lowercase, bigrams, used):
    """ Функция, дополняющая модель по данным из текста
   Возвращает модель, дополненную новыми данными

   param: file_for_train -файл с текстом по которому будет обучаться программа
   param: lowercase - переменная, отвечающая за приведение слов, сохраняемых
   в модели, к нижнему регистру
   param: bigrams - cписок пар
   param: used - список слов, которые есть в bigrams"""
    # ------------------------------------------------------------------- #

    with open(file_for_train, 'r', encoding='utf-8') as file_for_train:
        # Достаем часть текста
        for line in file_for_train:
            # Разрешенные символы
            reg = re.compile('[^A-Za-zА-Яа-яё]')
            # Удаляем лишние символы (оставляем нужные)
            line = reg.sub(' ', line)

            # Если необходимо убрать заглавные буквы
            if lowercase:
                line = line.lower()

            line = line.split()
            # Проходим по куску текста
            for i in range(len(line) - 1):
                # 2 подряд идущие слова объединяем
                # в словосочетание, записываем их в словарь
                pair = line[i] + ' ' + line[i + 1]
                bigrams.append(pair)
                used.append(line[i])

            # Если слово последнее, но встречалось раньше,
            # то оно не особенное
            if line and line[-1] not in used:
                pair = line[-1]
                bigrams.append(pair)
    return bigrams


def get_bigrams(directory, lowercase):
    """ Поиск .txt файлов в директории
   Возвращает список пар слов

   param: directory - директория с файлами для обучения
   param: lowercase - переменная, отвечающая за приведение слов, сохраняемых
       в модели, к нижнему регистру

   Возвращает список, состоящий из '<слово 1>' '<слово 2>' """
    # ---------------------------------------------------------------- #

    # Список пар
    bigrams = []

    # Слова которые есть в bigrams
    used = []

    # Поиск файлов в директории
    for top, dirs, files in os.walk(directory):
        for i in files:
            # Путь к файлу
            path = str(os.path.join(top, i))

            # Разделяем имя файла на 2 части: заголовок и формат
            filename, file_extension = os.path.splitext(path)

            # Если .тхт, то обрабатываем его
            if file_extension == '.txt':
                # Обрабатываемый файл
                file = str(os.path.normpath(path))
                # Обновление модели по данным из текущего файла
                bigrams = train(file, lowercase, bigrams, used)
    return bigrams


if __name__ == '__main__':
    # Парсинг аргументов
    namespace = parser.parse_args()

    # Файл для записи модели
    with open(namespace.model, 'w', encoding='utf-8') as model_f:

        # Список пар слов преобразуется в словарь
        # Ключ - пара слов, значение - сколько раз встречалась эта пара
        bigrams = Counter(get_bigrams(namespace.dir, namespace.lc))

        # Запись в файл созданной модели
        json.dump(bigrams, model_f)
