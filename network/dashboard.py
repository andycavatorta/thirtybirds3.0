from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
import queue
import time
import threading
import socketserver
import datetime
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

tb_path = os.path.dirname(os.path.realpath(__file__))

clients = []
class SimpleChat(WebSocket):

    def setTBRef(self, tb_ref):
        self.tb_ref = tb_ref

    def handleMessage(self):
       print("got ws message", self.data)
       trigger_map = {
           "pull_from_github" : self.tb_ref.tb_pull_from_github,
           "reboot" : self.tb_ref.restart
       }

       try:
         print(trigger_map[self.data]())
       except Exception as e:
           print("Got Exception", e)


    def handleConnected(self):
    #    print(self.address, 'connected')
       for client in clients:
          client.sendMessage(self.address[0] + u' - connected')
       clients.append(self)

    def handleClose(self):
       clients.remove(self)
    #    print(self.address, 'closed')
       for client in clients:
          client.sendMessage(self.address[0] + u' - disconnected')

    def sendToClients(self, message):
    #    print("Sending message to clinet : ", message)
       for client in clients:
          client.sendMessage(message)

class Message_Receiver(threading.Thread):
    def __init__(
            self, 
            tb_ref,
            _websocket
            ):
        print("Initialized Dashboard.py")
        self.tb_ref = tb_ref
        self.websocket = _websocket
        self.websocket.setTBRef(self.websocket, tb_ref)
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.start()
    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))

    def generate_system_status(self):
        status_report = self.tb_ref.hardware_management.get_system_status()
        status_report["tb_git_timestamp"] = self.tb_ref.tb_get_git_timestamp()
        status_report["tb_scripts_version"] = self.tb_ref.tb_get_scripts_version()
        status_report["app_git_timestamp"] = self.tb_ref.app_get_git_timestamp()
        status_report["app_scripts_version("] = self.tb_ref.app_get_scripts_version()
        status_report["hostname"] = self.tb_ref.get_hostname()
        status_report["local_ip"] = self.tb_ref.get_local_ip()
        status_report["global_ip"] = self.tb_ref.get_global_ip()
        status_report["online_status"] = self.tb_ref.get_online_status()
        status_report["connections"] = self.tb_ref.check_connections()
        status_report["msg_timestamp"] = datetime.datetime.now()
        self.add_to_queue("status",status_report)

    def run(self):
        while True:
            try:
                topic, message = self.queue.get(block=True, timeout=self.tb_ref.settings.Dashboard.refresh_interval)
                # print("message",message)
                message_json = json.dumps([topic, message])
                self.websocket.sendToClients(self.websocket,message_json)
                # self.websocket.sendToClients(message_json)

            except queue.Empty:
                self.generate_system_status()

def status_receiver(message):
    message_receiver.add_to_queue("status_event",message)

def exception_receiver(message):
    message_receiver.add_to_queue("exception_event",message)

message_receiver = False

def init(tb_ref):
    global message_receiver
    server_address = ('0.0.0.0', tb_ref.settings.Dashboard.http_port)    
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    os.chdir(tb_path)  # optional
    #httpd.serve_forever()
    httpd_thread = threading.Thread(target=httpd.serve_forever)
    httpd_thread.start()    

    server = SimpleWebSocketServer('', tb_ref.settings.Dashboard.websocket_port, SimpleChat)
    server_thread = threading.Thread(target=server.serveforever)
    server_thread.start()

    message_receiver = Message_Receiver(tb_ref, server.websocketclass)
