import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from twitter_analyser import web_socket_listener
from threading import Timer
import sys

TEN_MINUTES = 10*60
TWENTY_FOUR_HOURS = 24*60*60

def choose_tweets(on_method = True):
    Timer(TEN_MINUTES, choose_tweets).start()
    if on_method:
        web_socket_listener.choose_rows()


application = tornado.web.Application([
    (r'/websocketserver', web_socket_listener.WebSocketListener),
])

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(9091)
    print("Server in ascolto")
    choose_tweets(False)
    server_instance = tornado.ioloop.IOLoop.instance()
    Timer(TWENTY_FOUR_HOURS, web_socket_listener.save_file_and_close).start()
    server_instance.start()


