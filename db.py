import os
import pymongo
from pymongo.errors import ConnectionFailure
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

logger = logging.getLogger()


class DB:
    def __init__(self):
        logger.debug('DB setup')

        server = os.environ.get('I2T_DB_SERVER')
        user = os.environ.get('I2T_DB_USER')
        password = os.environ.get('I2T_DB_PASS')
        dbname = os.getenv('I2T_DB_NAME', 'db')

        self.client = pymongo.MongoClient(
            f'mongodb+srv://{user}:{password}@{server}/{dbname}?retryWrites=true&w=majority')

        self.collection = self.client[dbname].targets
        logger.debug('mongodb connected')

    def __del__(self):
        self.client.close()

    def get_last_time(self, user):
        logger.debug(f'get last time from user: {user}')

        last_month = datetime.utcnow() - relativedelta(days=os.getenv('I2T_DAYSBACK', 30))
        logger.debug(f'last_month from env or default: {last_month}')

        last_time = self.collection.find_one({'user': user})
        if last_time is not None:
            logger.debug(last_time)
            last_time = last_time.get('last_time')

        last_time = last_month if last_time is None else last_time
        logger.debug(f'returning {last_time}')

        return last_time

    def set_last_time(self, user):
        logger.debug('set last time')

        result = self.collection.update_one(
            {'user': user}, {"$set": {'last_time': datetime.utcnow()}})
        is_success = result.modified_count == 1
        logger.debug(is_success)

        return is_success
