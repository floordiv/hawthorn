import socket
from threading import Thread

from syst.output import println


class AdminShell:
    def __init__(self, ip, port, users=None):
        if users is None:
            users = {'floordiv': 'creator'}

        self.addr = (ip, port)
        self.users = users

        self.sock = socket.socket()

    def start(self):
        ...

    def connlistener(self):
        while True:
            conn, addr = self.sock.accept()

    def connhandler(self, conn):
        ip, port = conn.getpeername()
        visible_addr = ip + ':' + str(port)
