# Telegram-bot
#### Описание:
Телеграм-бот для отслеживания статуса проверки домашней работы на Яндекс.Практикум. Присылает сообщения, когда статус изменен - взято в проверку, есть замечания, зачтено.

#### Стек технологий:
Python 3.7
python-dotenv 0.19.0
python-telegram-bot 13.7

#### Как запустить проект:
 - Клонировать репозиторий и перейти в него в командной строке:
```
git clone ...
```
```
cd homework_bot
```
- Cоздать и активировать виртуальное окружение:
```
python -m venv env
```
```
source venv/Scripts/activate
```
- Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
- Создаем .env файл с токенами:
```
PRACTICUM_TOKEN=<PRACTICUM_TOKEN>
TELEGRAM_TOKEN=<TELEGRAM_TOKEN>
CHAT_ID=<CHAT_ID>
```
- Запускаем бота:
```
python homework.py
```
