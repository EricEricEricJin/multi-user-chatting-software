from socket import *
from time import sleep
from time import asctime
from time import localtime
from hashlib import md5
import threading

class clientCmdline:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.my_socket = socket(AF_INET, SOCK_STREAM)
        self.my_login = False
        self.my_username = ""
        

        # self.my_socket.settimeout(2)
        # self.my_socket.setblocking(True)
        try:
            self.my_socket.connect((self.ip, self.port))
        except:
            print("CANT CONNECT")
            exit()
        print("CONNECTED")
    
    def run(self):
        self.thread_continue = True
        t = threading.Thread(target = self._refresh, args = ())
        t.start()
        while True:
            command = input()
            
            if command == "register":
                username = input("Username: ")
                passwd = input("Password: ")
                self._send(str({"mode": "register", "username": username, "passwd": passwd}).encode("utf-8"))

                reg_status = self._receive()
                if reg_status == b"1":
                    print("Register success")
                elif reg_status == b"-1":
                    print("Register failure")
                else: 
                    raise(Exception)
                    
                
            elif command == "login":
                username = input("Username: ")
                passwd = input("Password: ")
                self._send(str({"mode": "login", "username": username, "pwdhash": md5(passwd.encode("utf-8")).hexdigest()}).encode("utf-8"))
                try:
                    login_status = self._receive()
                    
                    if login_status == b"-1":
                        print("Login failure: wrong username")
                    elif login_status == b"-2":
                        print("Login failure: wrong password")
                    elif login_status == b"1":
                        self.my_login = True
                        self.my_username = username
                    else:
                        raise(Exception)
                except:
                    print("Server not respond")
                        
            elif command == "send":
                if self.my_login == True:
                    target = input("Target: ")
                    content = input("Content: ")
                    self._send(str({"mode": "send", "source": self.my_username, "target": target, "content": content}).encode("utf-8"))
                    try:
                        send_status = self._receive()
                        if send_status == b"1":
                            print("Send success")
                        elif send_status == b"-1":
                            print("Error target")
                        else:
                            raise Exception
                    except:
                        print("Server not respond")
                else:
                    print("Login first")
            elif command == "exit":
                self._send("exit".encode("utf-8"))
                self.thread_continue = False
                exit()
                    
            else:
                print("Invalid input")
                
    def _refresh(self):
        while True:
            if self.thread_continue == False:
                break
            # print("R")
            sleep(0.2)
            if self.my_login == True:
                self._send(str({"mode": "refresh", "username": self.my_username}).encode("utf-8"))
                
                refresh_status = self._receive()
                if refresh_status == b"-1":
                    print("Error!")
                else:
                    refresh_status = eval(refresh_status)
                    for i in range(len(refresh_status)):
                        # print(refresh_status[i])
                        print("From %s at %s: %s" %(refresh_status[i]["source"], asctime(localtime(refresh_status[i]["time"])), refresh_status[i]["content"]))

                
    def _send(self, message):
        self.my_socket.send(message)
    
    def _receive(self):
        return self.my_socket.recv(1024)
    

if __name__ == "__main__":
    C = clientCmdline("127.0.0.1", 1234)
    # C = clientCmdline("45.249.94.168", 1234)
    C.run()