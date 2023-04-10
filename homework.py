import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv


load_dotenv()


logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


PRACTICUM_TOKEN: str = os.getenv('pr_token')
TELEGRAM_TOKEN: str = os.getenv('telega_token')
TELEGRAM_CHAT_ID: str = os.getenv('telega_id')


RETRY_PERIOD: int = 600
ENDPOINT: str = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS: dict[str, str] = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS: dict = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens() -> bool:
    """Проверяем доступность переменных окружения."""
    tokens: list[str] = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    return all(tokens)


def send_message(bot: telegram.Bot, message: str) -> None:
    """Отправляем сообщение в Telegram чат."""
    try:
        logger.info('Начало отправки сообщения в Telegram чат')
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logger.error(f'Сообщение в чат не отправлено: {error}')
    else:
        logger.debug(f'Сообщение в чат отправлено: {message}')


def get_api_answer(timestamp: int) -> dict:
    """Делаем запрос к эндпоинту API-сервиса."""
    payload: dict = {'from_date': timestamp}
    try:
        logger.info(f'Запрос к эндпоинту {ENDPOINT} API-сервиса')
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=payload
        )
    except Exception as error:
        logger.error(f'Ошибка при запросе к API: {error}. '
                     f'Параметры запроса: {payload}')
        raise Exception(f'Ошибка при запросе к API: {error}')
    if homework_statuses.status_code != HTTPStatus.OK:
        status_code = homework_statuses.status_code
        logger.error(f'Сбой в работе программы: Эндпоинт {ENDPOINT} '
                     f'с параметрами {homework_statuses} недоступен. '
                     f'Ответ API: {status_code}.')
        raise Exception(f'Ответ API: {status_code}')
    try:
        return homework_statuses.json()
    except Exception as error:
        logger.error(f'Ошибка ответа из формата json: {error}')
        raise Exception(f'Ошибка ответа из формата json: {error}')


def check_response(response: dict) -> dict:
    """Проверяем ответ API."""
    logger.info("Проверка ответа API на корректность")
    if not isinstance(response, dict):
        logger.error('Ответ API отличен от словаря')
        raise TypeError('Ответ API отличен от словаря')
    if 'homeworks' not in response:
        logger.error('Ошибка словаря по ключу homeworks')
        raise KeyError('Ошибка словаря по ключу homeworks')
    if 'current_date' not in response:
        logger.error('Ошибка словаря по ключу current_date')
        raise KeyError('Ошибка словаря по ключу current_date')
    if not isinstance(response.get('homeworks'), list):
        logger.error('Список домашних работ пуст')
        raise TypeError('Список домашних работ пуст')
    try:
        return response.get('homeworks')[0]
    except Exception as error:
        raise Exception(f'Не получен список домашних работ:{error}')


def parse_status(homework: dict) -> str:
    """Получаем статус домашней работы."""
    if 'homework_name' not in homework:
        raise KeyError('Отсутствует ключ homework_name в ответе API')
    if 'status' not in homework:
        raise KeyError('Отсутствует ключ status в ответе API')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_VERDICTS:
        logger.error(f'Неизвестный статус работы: {homework_status}')
        raise KeyError(f'Неизвестный статус работы: {homework_status}')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main() -> None:
    """Основная логика работы бота."""
    if not check_tokens():
        message = ('Доступны не все переменные окружения, которые '
                   'необходимы для работы программы')
        logger.critical(message)
        sys.exit(message)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    last_message = ''
    last_error = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            check = check_response(response)
            message = parse_status(check)
            if last_message != message:
                last_message = message
                send_message(bot, last_message)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if error != last_error:
                send_message(bot, message)
                last_error = error
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        filename='main.log',
        filemode='w',
        format='%(asctime)s - %(levelname)s - %(message)s - %(name)s'
    )
    main()
