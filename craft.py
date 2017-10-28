import websocket
import uuid
from uuid import UUID
import json
import keyboard
import asyncio
import threading

class Craft:

	def __init__(self, execName, pid, guid=None):
		self.execName = execName
		self.pid = pid
		self.guid = guid or str(uuid.uuid1())
		
	def keyboard_hook(self, event):
		self.eventHandler({'type': 'kbd', 'msg': event})
	
	def setEventHandler(self, eventHandler):
		self.eventHandler = eventHandler
		
	def on_open(self, ws):
		msg = {}
		msg['message_type'] = 'register'
		msg['plugin_guid'] = self.guid
		msg['PID'] = self.pid
		msg['execName'] = self.execName
		msg['manifestPath'] = ''
		msg = json.dumps(msg).encode()
		ws.send(msg)
		keyboard.hook(self.keyboard_hook)
		
	def on_close(self, ws):
		ws.close()
		keyboard.unhook(self.keyboard_hook)
		print('close')
		
	def on_message(self, ws, msg):
		msg = json.loads(msg)
		self.eventHandler({'type': 'craft', 'msg': msg})
		
	def connect(self):
		#websocket.enableTrace(True)
		ws = websocket.WebSocketApp(
			"ws://localhost:10134",
			on_open=self.on_open,
			on_message=self.on_message,
			on_close=self.on_close
		)
		ws.run_forever()
		#wst = threading.Thread(target=ws.run_forever)
		#wst.daemon = True
		#wst.start()
		
		
if __name__ == '__main__':
	def f(e):
		print(e)
	c = Craft('notepad++.exe', 9772)
	c.setEventHandler(f)
	c.connect()
		