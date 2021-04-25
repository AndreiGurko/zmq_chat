import curses
import time
import threading
import sys, os
sys.path.append(os.getcwd())

import configparser

import client
from curses import wrapper

HOST = ''
PORT = ''

def bottom_window(window, socket_backend):
    """ метод реализует логику создания нижней части консольного окна для вывода полученных сообщений """
    window_lines, window_cols = window.getmaxyx()  # получаем размеры текущего окна
    bottom_line = window_lines - (window_lines - 1)  # устанавливается нижняя граница
    window.bkgd(curses.A_NORMAL, curses.color_pair(2))
    window.scrollok(1)  # установлена опция контроля выхода строк за пределы окна
    while True:
        window.addstr(bottom_line, 1, socket_backend.recv_string())  # печать сообщения из сокета
        window.scroll(-1)  # устанавливаем прокрутку окна вниз на одну линию
        window.refresh()  # обновляем окно

def top_window(window, socket_frontend):
    """ метод реализует логику создания верхней части консольного окна для ввода сообщений от пользователя"""
    window.bkgd(curses.A_NORMAL, curses.color_pair(2))
    window.clear()  # очищаем окно при создании окна
    window.refresh()  # обновляем окно при создании окна
    while True:
        window.clear()  # очищаем окно после каждого ввода
        window.box()  # рисуем границы окна для ввода сообщений
        window.refresh()  # обновляем окно
        window.addstr(1, 1, 'you: ')  # печать строки приглашающей к вводу сообщения
        str = window.getstr(1, 6).decode('utf-8')  # считывание строки
        if str is not None and str != "":  # контроль ввода пустых строк
            socket_frontend.send_string(str)  # отправляем сообщение на сервер
            socket_frontend.recv_string()  # получаем ответ согласно паттерну zmq REQ-REP
        time.sleep(0.01)


def main(stdscr):
    ### curses set up
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # установка системных параметров для консольного окна
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.echo()  # активируем вывод введенных символо
    curses.curs_set(0)  # делаем курсор невидемым

    window_height = curses.LINES  # получение границ окна (высота)
    window_width = curses.COLS  # получение границ окна (ширина)
    division_line = int(window_height * 0.8)  # расчитываем линию разграничения между окнам ввода-вывода

    lines = window_height - (window_height - division_line)  # промежуточная переменная для расчета границ
    bottom_pad = stdscr.subpad(lines, window_width, window_height - lines, 0)  # создание нижней панели
    top_pad = stdscr.subpad(window_height - division_line, window_width, 0, 0)  # создание верхней панели
    new_client = client.Client(HOST, PORT)  # создаем клиента
    new_client.run()
    socket_frontend = new_client.get_socket_frontend()  # получение сокета для отправки сообщений на сервер
    socket_backend = new_client.get_socket_backend()  # получение сокета для получения сообщений от всех уч. чата

    # запуск потока для создания панели для отправки сообщений
    bottom_thread = threading.Thread(target=bottom_window, args=(bottom_pad, socket_backend))
    bottom_thread.start()

    # запуск потока для создания панели для получения сообщений всех участников чата
    top_thread = threading.Thread(target=top_window, args=(top_pad, socket_frontend))
    top_thread.start()


def read_conf():
    """ метод для чтения конфигурации (хост, порт) из файла конфигурации """
    path = 'config.ini'
    config = configparser.ConfigParser()
    config.read(path)
    host = config.get('Settings', 'host')
    port = config.get('Settings', 'port')
    return [host, port]


if __name__ == '__main__':
    try:
        if len(sys.argv) < 3:
            conf_con = read_conf()
            HOST = conf_con[0]
            PORT = conf_con[1]
        else:
            HOST = sys.argv[1]
            PORT = sys.argv[2]

        wrapper(main)
    except Exception as e:
        print('Something wrong with connection %s' % e)
