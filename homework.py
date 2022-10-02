import logging
import os
import time

import requests
import telegram
from datetime import datetime
from dotenv import load_dotenv

from http import HTTPStatus
from exceptions import APIStatusError

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME: int = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(funcName)s - '
    + '%(lineno)d - %(message)s'
)
handler.setFormatter(formatter)


def send_message(bot, message):
    """Отправка сообщения в Telegram чат."""
    logger.info('Происходит отправка сообщения')
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as error:
        raise SystemError(f'Ошибка отправки сообщения, {error}')
    else:
        logger.info('Сообщение было отправлено.')


def get_api_answer(current_timestamp):
    """Запрос к эндпоинту."""
    logger.info('Начало проверки эндпоинта')
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    request_params = {'headers': HEADERS, 'params': params}
    try:
        response = requests.get(ENDPOINT, **request_params)
    except Exception:
        logging.exception('Ошибка запроса к эндпоинту')
    if response.status_code != HTTPStatus.OK:
        raise APIStatusError(f'Ошибка запроса к API:{response.status_code}')
    try:
        response = response.json()
    except Exception as error:
        raise Exception(f'Ошибка запроса json: {error}')
    return response


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
    verdict = HOMEWORK_VERDICTS[homework_status]
    if 'homework_name' not in homework or 'status' not in homework:
        raise KeyError('Отсутствует название домашки в homework')
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
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks:
                message = parse_status(homeworks[0])
                if prev_message != message:
                    send_message(bot, message)
                    prev_message = message
            else:
                logger.debug(f'Отсутствие в ответе новых статусов')
            current_timestamp = int(time.time())
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if prev_message != message:
                send_message(bot, message)
                prev_message = message
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
