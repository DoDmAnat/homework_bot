from asyncio.log import logger
import logging
import os
from re import T
import time
from urllib import response

import requests
import telegram
from dotenv import load_dotenv

from asyncio import exceptions

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME: int = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.INFO,
    filename='program.log',
    format='%(asctime)s, %(levelname)s, %(message)s',
)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.addHandler(handler)

def send_message(bot, message):
    """Отправка сообщения в Telegram чат"""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception:
        logging.exception('Ошибка отправки сообщения')

def get_api_answer(current_timestamp):
    """Запрос к эндпоинту"""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception:
        logging.exception('Ошибка запроса к эндпоинту')
    return response.json()


def check_response(response):
    """Проверка API на корректность"""
    homework_list = response['homeworks']
    return homework_list


def parse_status(homework):
    """Извлечение статуса домашней работы"""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    

    verdict = HOMEWORK_STATUSES[homework_status]

    

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности переменных окружения"""
    if not TELEGRAM_CHAT_ID or not TELEGRAM_TOKEN or not PRACTICUM_TOKEN:
        return False
    return True


def main():
    """Основная логика работы бота."""

    if not check_tokens():
        error_message = 'Отсутствует переменная окружения'
        logger.critical(error_message)
        raise exceptions.MissingRequiredTokenException(error_message)

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time() - 0)

    ...

    while True:
        try:
            response = get_api_answer(current_timestamp)

            # ...

            # current_timestamp = 
            # time.sleep(RETRY_TIME)

        # except Exception as error:
        #     message = f'Сбой в работе программы: {error}'
        #     ...
        #     time.sleep(RETRY_TIME)
        # else:
        #     ...


if __name__ == '__main__':
    main()
