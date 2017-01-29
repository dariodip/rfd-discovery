import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from twitter_analyser import web_socket_listener
from threading import Timer
import sys
import logging

SERVER_PORT = 9091
TWENTY_FOUR_HOURS = 24*60*60
BACKUP_TIME = 60*60
TEN_MINUTES = 10*60

logging.basicConfig(level=logging.INFO)
fh = logging.FileHandler("starter.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger_ = logging.getLogger(__name__)
logger_.addHandler(fh)

def choose_tweets(on_method = True):
    Timer(TEN_MINUTES, choose_tweets).start()
    if on_method:
        web_socket_listener.choose_rows()


application = tornado.web.Application([
    (r'/websocketserver', web_socket_listener.WebSocketListener),
])

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(SERVER_PORT)
    logger_.info("Server in ascolto sulla porta %d", SERVER_PORT)
    choose_tweets(False)
    server_instance = tornado.ioloop.IOLoop.instance()
    Timer(BACKUP_TIME, web_socket_listener.backup).start()
    Timer(TWENTY_FOUR_HOURS, web_socket_listener.save_file_and_close).start()
    server_instance.start()


