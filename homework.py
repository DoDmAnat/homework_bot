import logging
import os
import time

import requests
import telegram
from datetime import datetime
from dotenv import load_dotenv

from http import HTTPStatus

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
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)


def send_message(bot, message):
    """Отправка сообщения в Telegram чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception:
        logging.exception('Ошибка отправки сообщения')
    logger.debug('Сообщение было отправлено.')


def get_api_answer(current_timestamp):
    """Запрос к эндпоинту."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception:
        logging.exception('Ошибка запроса к эндпоинту')
    if response.status_code != HTTPStatus.OK:
        response.raise_for_status()
    logger.debug('Успешный запрос.')
    return response.json()


def check_response(response):
    """Проверка API на корректность."""
    if response['homeworks'] is None:
        raise Exception('В ответе API нет словаря с домашками')
    if len(response['homeworks']) == 0:
        raise Exception('За последнее время нет домашек')
    if not isinstance(response['homeworks'], list):
        raise TypeError('Домашки приходят не в виде списка')
    logger.debug('Корректный формат ответа')
    return response['homeworks']


def parse_status(homework):
    """Извлечение статуса домашней работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES[homework_status]

    if verdict is None:
        raise KeyError('Статус домашней работы не определен')

    logger.debug('Status was parsed successfully.')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности переменных окружения."""
    if not TELEGRAM_CHAT_ID or not TELEGRAM_TOKEN or not PRACTICUM_TOKEN:
        logger.critical('Нет доступа к токенам!')
        return False
    logger.debug('Переменные окружения доступны.')
    return True


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        exit()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    prev_message = f'Время: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    send_message(
        bot=bot,
        message=prev_message
    )

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            current_timestamp = response['current_date']
            for homework in homeworks:
                status = parse_status(homework[0])
                send_message(bot, status)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
