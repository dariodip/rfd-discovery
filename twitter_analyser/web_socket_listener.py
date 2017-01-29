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
session_data_frame = pd.DataFrame(columns=pandas_cols)
global_data_frame = pd.DataFrame(columns=pandas_cols)
CHOSEN_ROWS = 5
BACKUP_TIME = 60*60



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

    def __init__(self, message_dict : dict):
        self.message_d = message_dict

    def run(self):
        pandas_row = []
        for k in pandas_cols:
            pandas_row.append(self.message_d[k])
        session_data_frame.loc[session_data_frame.shape[0]] = pandas_row
        logger_.debug("Messaggio aggiunto al data frame")

def choose_rows():
    logger_.info("Procedura di selezione delle righe iniziata.")
    df_len = session_data_frame.shape[0]
    sample = rnd.sample(range(0,df_len), CHOSEN_ROWS)
    for s in sample:
        global_data_frame.loc[global_data_frame.shape[0]] = session_data_frame.loc[s]
    logger_.info("Procedura di selezione delle righe terminata")


def save_file_and_close():
    logger_.info("Salvataggio del file")
    global_data_frame.to_csv("crawled-tweets.csv", sep=";")
    logger_.info("File salvato")
    quit()

def backup():
    threading.Timer(BACKUP_TIME, backup).start()
    logger_.info("Avvio backup")
    try:
        global_data_frame.to_csv("crawled-tweets.csv.bak", sep=";")
        logger_.info("Backup terminato con successo")
    except Exception:
        logger_.critical("Backup fallito")
