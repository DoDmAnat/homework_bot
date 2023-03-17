Telegram-bot
Телеграм-бот который отслеживает статус проверки домашней работы на Яндекс.Практикум.
Присылает сообщения, если статус изменен - взято в проверку, есть замечания, зачтено.
Технологии:
Python 3.9
python-dotenv 0.19.0
python-telegram-bot 13.7
Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:

git clone https://github.com/DoDmAnat/homework_bot
cd homework_bot
Cоздать и активировать виртуальное окружение:

python -m venv env
source env/bin/activate
Установить зависимости из файла requirements.txt:

python -m pip install --upgrade pip
pip install -r requirements.txt
Записать в переменные окружения (файл .env) необходимые ключи:

токен профиля на Яндекс.Практикуме
токен телеграм-бота
свой ID в телеграме
Запустить проект:

python homework.py
