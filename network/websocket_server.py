import threading
import time

from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

clients = []
class SimpleChat(WebSocket):

    def handleMessage(self):
       for client in clients:
          if client != self:
             client.sendMessage(self.address[0] + u' - ' + self.data)

    def handleConnected(self):
       print(self.address, 'connected')
       for client in clients:
          client.sendMessage(self.address[0] + u' - connected')
       clients.append(self)

    def handleClose(self):
       clients.remove(self)
       print(self.address, 'closed')
       for client in clients:
          client.sendMessage(self.address[0] + u' - disconnected')

    def sendToClients(self, message):
       for client in clients:
          client.sendMessage(message)


server = SimpleWebSocketServer('', 8000, SimpleChat)
x = threading.Thread(target=server.serveforever)
x.start()


def init():



while True:
    t = time.time()
    server.websocketclass.sendToClients(server.websocketclass,str(t))
    time.sleep(1)
    print(t)
