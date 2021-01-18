import os
from time import sleep
from datetime import datetime, timedelta
import dateutil.parser
from dotenv import load_dotenv
import sys
import json
import logging
from ig import IG
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR')

_USERS_FILE = 'users.json'

handlers = [logging.FileHandler(
    'i2t.log', 'w+', 'utf-8'), logging.StreamHandler(sys.stdout)]
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    handlers=handlers)

logger = logging.getLogger()


class i2t:
    def __init__(self):
        self._ig = IG()
        with open(_USERS_FILE) as f:
            self.users = json.load(f)

    def update(self):
        for u in self.users:
            ig_user = u['instagram_user']
            t_channel = u['telegram_channel']
            since = u.get('last_time', None)
            since = datetime.fromisoformat(
                since) if since is not None else datetime.utcnow() - timedelta(weeks=8)

            if self.update_user(u, ig_user, t_channel, since):
                u['last_time'] = datetime.utcnow()

        self.update_last_time()

    def update_last_time(self):
        data = json.dumps(self.users,
                          indent=2,
                          sort_keys=True,
                          default=str)
        with open(_USERS_FILE, 'w') as f:
            f.write(data)

    def update_user(self, u: dict, ig_user: str, t_channel: str, last_time: datetime) -> bool:
        logger.debug(
            f'\nuser: {ig_user} | channel: {t_channel} | since: {last_time}')
        return self._ig.update(u, last_time, ig_user, t_channel)


def main():
    o = i2t()
    while(True):
        o.update()
        logger.debug('*' * 50)
        sleep(600)

    del(o)


if __name__ == '__main__':
    logger.debug(__name__)
    load_dotenv()
    main()
