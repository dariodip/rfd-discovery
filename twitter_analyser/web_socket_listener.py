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

pandas_cols = ['created_at', 'sentiment_word_count', 'sentiment_comparative', 'sentiment_score',
                 'sentiment_positive_count', 'sentiment_tokens', 'text', '_msgid', 'retweet_count',
                 'sentiment_negative_count']
session_data_frame = pd.DataFrame(columns=pandas_cols)
global_data_frame = pd.DataFrame(columns=pandas_cols)
CHOSEN_ROWS = 5


class WebSocketListener(tornado.websocket.WebSocketHandler):

    def open(self, ):
        print("Nuova connessione in entrata")

    def on_message(self, message):
        mgs_dict = json.loads(message)
        p_n_s = ParserAndSaver(mgs_dict)
        p_n_s.run()

    def on_close(self):

        print("Connessione chiusa")

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

def choose_rows():
    df_len = session_data_frame.shape[0]
    sample = rnd.sample(range(0,df_len), CHOSEN_ROWS)
    for s in sample:
        global_data_frame.loc[global_data_frame.shape[0]] = session_data_frame.loc[s]


def save_file_and_close():
    print("Saving files")
    global_data_frame.to_csv("crawled-tweets.csv", sep=";")
    quit()

def backup():
    threading.Timer(60*60, backup).start()
    print("Saving backup")
    global_data_frame.to_csv("crawled-tweets.csv.bak", sep=";")