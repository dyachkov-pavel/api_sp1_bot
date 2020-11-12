import os
import time
import logging
import requests
import telegram
from dotenv import load_dotenv

LOG_FORMAT = '%(levelname)s %(asctime)s - %(message)s'
logging.basicConfig(level=logging.ERROR,
                    format=LOG_FORMAT)
logger = logging.getLogger()

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def parse_homework_status(homework):
    if 'homework_name' in homework and 'status' in homework:
        homework_name = homework['homework_name']
        homework_status = homework['status']
        if homework_status == 'rejected':
            verdict = 'К сожалению в работе нашлись ошибки.'
        else:
            verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    else: 
        logger.error(f'Key Error: homework_name and status were not founded')
        raise KeyError


def get_homework_statuses(current_timestamp):
    if current_timestamp is None: current_timestamp = int(time.time())
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    YANDEX_URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    try:
        homework_statuses = requests.get(
            YANDEX_URL, headers=headers, params=params)
        homework_statuses.json()
        return homework_statuses.json()
    except requests.exceptions.HTTPError as errh:
        logger.error(f'Http Error: {errh}')
        raise errh
    except requests.exceptions.ConnectionError as errc:
        logger.error(f'Error Connecting: {errc}')
        raise errc
    except requests.exceptions.Timeout as errt:
        logger.error(f'Timeout Error: {errt}')
        raise errt
    except requests.exceptions.RequestException as err:
        logger.error(f'OOps: Something Else {err}')
        raise err


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    tg_bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]), tg_bot)
            current_timestamp = new_homework.get('current_date')
            time.sleep(1200)
        except Exception as e:
            logger.error(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
