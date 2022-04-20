import inspect
import logging

import pymongo

from utilities import constants

class Utils():

    def ilogger(logLevel=logging.DEBUG):
        # Set class/method name from where it's called
        logger_name = inspect.stack()[1][3]
        # create logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(logLevel)
        # Create console handler or file handler
        ch = logging.StreamHandler()
        fh = logging.FileHandler(constants.LOG_FILE, mode=constants.LOG_FILE_MODE)
        # Create Formatter
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s : %(message)s')
        # Add Formatter to console or File Handler
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        # Add console or File Handler to logger
        logger.addHandler(ch)
        logger.addHandler(fh)
        return logger

    def iclient():
        client = pymongo.MongoClient(constants.MONGO_CONNECTION_URL)
        dbName = constants.DB_NAME
        collectionName = constants.COLLECTION_NAME

        return client[dbName][collectionName]