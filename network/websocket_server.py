#!/usr/bin/env python

"""
required for basic Web connector

authentication
    against u/p in setting file?

manage multi-user websockets
    track users, etc

act as gateway to pubsub system
    subscribe_to_topic ( per websocket )
    publish_to_topic
    handle_message

"""

import asyncio
import json
from multiprocessing import Process, Queue
import queue
import threading
import websockets

from multiprocessing import Process, Queue

class Websocket_Server_Async():
    def __init__(self, incoming_message_queue):
        self.incoming_message_queue = incoming_message_queue
        self.STATE = {"message": 0}
        self.USERS = set()

    async def register(self,websocket):
        self.USERS.add(websocket)
        #await self.notify_users()

    async def unregister(self,websocket):
        self.USERS.remove(websocket)
        #await self.notify_users()

    async def publish(self,topic,message):
        if self.USERS:  # asyncio.wait doesn't accept an empty list
            tb_packet = json.dumps({"topic": topic, "message": message})
            await asyncio.wait([user.send(tb_packet) for user in self.USERS])

    async def counter(self,websocket, path):
        # register(websocket) sends user_event() to websocket
        await self.register(websocket)
        try:
            print(websocket, path)
            await websocket.send(json.dumps({"topic": "state", **self.STATE}))
            async for message in websocket:
                data = json.loads(message)
                if data["action"] == "minus":
                    self.STATE["value"] -= 1
                    if self.USERS:  # asyncio.wait doesn't accept an empty list
                        message = self.json.dumps({"topic": "state", **self.STATE})
                        await asyncio.wait([user.send(message) for user in self.USERS])
                elif data["action"] == "plus":
                    self.STATE["value"] += 1
                    if self.USERS:  # asyncio.wait doesn't accept an empty list
                        message = json.dumps({"topic": "state", **self.STATE})
                        await asyncio.wait([user.send(message) for user in self.USERS])
                else:
                    print("unsupported event: {}", data)
        finally:
            await self.unregister(websocket)

class Websocket_Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.websocket_server_async = False
        self.queue = queue.Queue()
        self.start()

    async   def add_to_queue(self, topic, message):
        #await self.websocket_server_async.notify_users()
        print("q", topic, message)
        await self.websocket_server_async.publish(topic, message)
        #self.queue.put((topic, message))

    def run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.websocket_server_async = Websocket_Server_Async(self.queue)
        http_interface = websockets.serve(self.websocket_server_async.counter, "localhost", 6789)
        asyncio.get_event_loop().run_until_complete(http_interface)
        asyncio.get_event_loop().run_forever()

###########################

class Websocket_Server_Process(Process):

    def __init__(self, queue, idx, **kwargs):
        super(Processor, self).__init__()
        self.queue = queue
        self.idx = idx
        self.kwargs = kwargs

    def run(self):
        """Build some CPU-intensive tasks to run via multiprocessing here."""
        hash(self.kwargs) # Shameless usage of CPU for no gain...

        ## Return some information back through multiprocessing.Queue
        ## NOTE: self.name is an attribute of multiprocessing.Process
        self.queue.put("Process idx={0} is called '{1}'".format(self.idx, self.name))



































if __name__ == "__main__":
    NUMBER_OF_PROCESSES = 5

    ## Create a list to hold running Processor object instances...
    processes = list()

    q = Queue()  # Build a single queue to send to all process objects...
    for i in range(0, NUMBER_OF_PROCESSES):
        p=Processor(queue=q, idx=i)
        p.start()
        processes.append(p)

    # Incorporating ideas from this answer, below...
    #    https://stackoverflow.com/a/42137966/667301
    [proc.join() for proc in processes]
    while not q.empty():
        print "RESULT: {0}".format(q.get()) 

