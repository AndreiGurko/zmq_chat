import zmq, sys, configparser
import threading


class Client:
    """
    В данном классе реализована логика клиентского приложения, как отправка и получение сообщений.
    Для реализации данного функционала использовались паттерны zmq: REQ-REP и PUB-SUB
    Для отправки сообщений на сервер используется паттерн REQ-REP
    Для получения сообщений от всех участников чата реализован паттерн подписчика SUB(subscriber)
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self._socket_frontend = None
        self._socket_backend = None

    def con_frontend(self):
        """
        метод осуществляет подключение к серверу используя паттерн zmq REQ-REP. Через сокет данного типа
        пользователь отправляет сообщения на сервер
        """
        context = zmq.Context()
        self._socket_frontend = context.socket(zmq.REQ)
        self._socket_frontend.connect('tcp://%s:%s' % (self.host, self.port))

    def get_socket_frontend(self):
        return self._socket_frontend

    def con_backend(self):
        """ метод используется для получения всех сообщений участников чата. Для получения сообщений от сервера
            используется паттерн zmq PUB-SUB.  """
        port = 5001  # нужно использовать другой порт для подключения к другому типу сокета
        context = zmq.Context()
        self._socket_backend = context.socket(zmq.SUB)
        self._socket_backend.setsockopt(zmq.SUBSCRIBE, b'')
        self._socket_backend.connect('tcp://%s:%s' % (self.host, port))

    def get_socket_backend(self):
        return self._socket_backend

    def run(self):
        """ Осуществляем подключение"""
        try:
            self.con_frontend()
        except Exception as e:
            print("Connection failed + %s" % e)
        try:
            self.con_backend()
        except Exception as e:
            print("Something wrong! Connection to server failed + %s" % e)
