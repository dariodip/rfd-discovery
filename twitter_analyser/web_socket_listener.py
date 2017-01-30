import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import json
import threading
import csv
import pandas as pd
import random as rnd
import sys
import logging

logging.basicConfig(level=logging.INFO)
fh = logging.FileHandler("server.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger_ = logging.getLogger(__name__)
logger_.addHandler(fh)

pandas_cols = ['created_at', 'sentiment_word_count', 'sentiment_comparative', 'sentiment_score',
                 'sentiment_positive_count', 'sentiment_tokens', 'text', '_msgid', 'retweet_count',
                 'sentiment_negative_count']
sorting_keys = ['sentiment_word_count', 'sentiment_tokens']
session_data_frame = pd.DataFrame(columns=pandas_cols)
global_data_frame = pd.DataFrame(columns=pandas_cols)
CHOSEN_ROWS = 5


class WebSocketListener(tornado.websocket.WebSocketHandler):

    def open(self):
        logger_.info("Connessione in entrata.")

    def on_message(self, message):
        logger_.debug("Ricevuto messaggio")
        mgs_dict = json.loads(message)
        p_n_s = ParserAndSaver(mgs_dict)
        p_n_s.run()

    def on_close(self):
        logger_.warning("Connessione chiusa")

    def check_origin(self, origin):
        return True

    def data_received(self, chunk):
        pass


class ParserAndSaver(threading.Thread):

    def __init__(self, message_dict: dict):
        self.message_d = message_dict

    def run(self):
        pandas_row = []
        for k in pandas_cols:
            pandas_row.append(self.message_d[k])
        session_data_frame.loc[session_data_frame.shape[0]] = pandas_row
        logger_.debug("Messaggio aggiunto al data frame")


def choose_rows():
    logger_.info("Procedura di selezione delle righe iniziata.")
    session_data_frame.sort_values(by=sorting_keys, inplace=True, ascending=False)
    #global_data_frame.append(session_data_frame.head(CHOSEN_ROWS))
    to_append = session_data_frame.head(CHOSEN_ROWS)
    for index, row in to_append.iterrows():
        global_data_frame.loc[global_data_frame.shape[0]] = row
    logger_.info("Procedura di selezione delle righe terminata")
    session_data_frame.drop(session_data_frame.index, inplace=True)


def save_file_and_close():
    logger_.info("Salvataggio del file")
    global_data_frame.to_csv("crawled-tweets.csv", sep=";")
    logger_.info("File salvato")
    quit()


def backup(backup_time: int):
    threading.Timer(backup_time, backup, [backup_time]).start()
    logger_.info("Prossimo backup programmato")
    logger_.info("Avvio backup")
    try:
        global_data_frame.to_csv("crawled-tweets.csv.bak", sep=";")
        logger_.info("Backup terminato con successo")
    except Exception:
        logger_.critical("Backup fallito")
