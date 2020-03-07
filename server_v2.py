# from time import sleep
from time import time
from socket import *
from hashlib import md5
import threading


class socketServer:
    def __init__(self, ip, port):
        self.cache_table = {} # {username, [content]} # content: [{"source": source, "time": time, "content": content}, {}, ...]
        self.passwd_table = {}
        # self.ip = ip
        # self.port = port
        self.my_socket = socket(AF_INET, SOCK_STREAM)
        self.my_socket.bind((ip, port))
        self.my_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.my_socket.listen(10)

    '''
        {"mode": "register", "username": username, "passwd": passwd}
        {"mode": "login", "username": username, "pwdhash": pwdhash}
        {"mode": "send", "source": source, "target": target}
    '''
    
    def run(self):
        while True:
            conn, addr = self.my_socket.accept()
            t = threading.Thread(target=self._service, args=(conn,))
            t.start()
        
    def _service(self, conn):
        while True:
            # print(self.cache_table)
            message = conn.recv(1024).decode("utf-8")
            # print(message)
            if message == "exit":
                break
            message = eval(message)
            if message["mode"] == "register":

                username = message["username"]
                passwd = message["passwd"]

                if username not in self.passwd_table:

                    self.passwd_table.update({username: passwd})
                    self.cache_table.update({username: []})
                    self._send(conn, b"1") # 1: register successfully
                else:
                    self._send(conn, b"-1")
                
            elif message["mode"] == "login":
                
                username = message["username"]
                pwdhash = message["pwdhash"]
                if username in self.passwd_table:
                    if md5(self.passwd_table[username].encode("utf-8")).hexdigest() == pwdhash:
                        self._send(conn, b"1")
                    else:
                        self._send(conn, b"-2")
                else:
                    self._send(conn, b"-1")
                    
            elif message["mode"] == "send":
                source = message["source"]
                target = message["target"]
                content = message["content"]
                if target in self.cache_table:
                    self._send(conn, b"1")
                    self.cache_table[target].append({"source": source, "time": time(), "content": content})
                else:
                    self._send(conn, b"-1")
                
            elif message["mode"] == "refresh":
                username = message["username"]
                if username in self.cache_table:
                    self._send(conn, str(self.cache_table[username]).encode("utf-8"))
                    self.cache_table[username] = []
                else:
                    self._send(conn, b"-1")
        conn.close()


    def _send(self, client, message):
        client.send(message)
        
if __name__ == "__main__":
    print("START")
    S = socketServer("127.0.0.1", 1234)
    S.run()