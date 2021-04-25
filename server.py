import zmq
import threading


class Server:
    """
    Класс реализует логику сервера. Сервер получает сообщения от пользователей и отправляет полученное
    сообщение всем учатсникам чата. Здесь реализован паттерн zmq SUB-PUB. В данном случаем сервер
    выступае в роли издателя (publisher)
    """
    def __init__(self):
        self.host = ''
        self.port = 5000  # порт для подключения клиентов к серверу
        self.port2 = 5001  # порт для публикаций сообщений

    def connect(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind('tcp://*:%s' % self.port)  # подключаем сервер к сокету в через который будут приходить сообщения
        print('server is starting...')
        socket_pub = context.socket(zmq.PUB)  # подключаем сервер к сокету через который будут рассылаться сообщения
        socket_pub.bind('tcp://*:%s' % self.port2)

        while True:
            mes = socket.recv_string()  # получаем сообщение от клиента
            print('server has a connection')
            print('mes = %s' % mes)
            socket.send_string('')  # согласно паттерну REQ-REP отправляем ответ клиенту
            socket_pub.send_string(mes)  # отправляем сообщение всем участникам чата


if __name__ == '__main__':
    try:
        server = Server()
        threading.Thread(target=server.connect).start()
    except Exception as e:
        print('Connection failed %s' % e)
