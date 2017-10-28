#import asyncio

#from obswsrc import OBSWS
#from obswsrc.requests import ResponseStatus, StartStreaming, GetVolume, SetSceneItemPosition, SetSceneItemTransform, GetCurrentScene, SetSourceRender, StartStopStreaming
import time
import math
from craft import Craft
from obswebsocket import obsws
from obswebsocket.requests import *
from enum import Enum

SCENE_NAME = 'scene'
SOURCE_NAME = 'camera'

last_request_time = 0.

ws = None

def reconnect():
	global ws
	ws = obsws('localhost', 4444, 'password')
	ws.connect()
	
	
def request(*args, **kwargs):
	global ws
	if ws is None:
		reconnect()
	try:
		res = ws.call(*args, **kwargs)
	except:
		ws = None
	return res
	
class Source:
	def __init__(self, scene, source):
		self.scene = scene
		self.source = source
		self.x = 0.
		self.y = 0.
		self.x_scale = 1.
		self.y_scale = 1.
		self.rotation = 0.
		self.cx = 0
		self.cy = 0
		self.visible = True
	
	def init(self):
		self.x = 0.
		self.y = 0.
		self.x_scale = 1.
		self.y_scale = 1.
		self.rotation = 0.
		self.cx = 0
		self.cy = 0
		self.visible = True
		request(SetSceneItemPosition(
			item=self.source, 
			x=self.x, 
			y=self.y, 
			scene_name=self.scene))
		request(SetSceneItemTransform(
			item=self.source, 
			x_scale=self.x_scale, 
			y_scale=self.y_scale, 
			scene_name=self.scene, 
			rotation=self.rotation))
		res = request(GetCurrentScene())
		print(res.getSources())	
		src = list(filter(lambda x: x['name'] == self.source, res.getSources()))[0]
		self.cx, self.cy = src['source_cx'], src['source_cy']
	
	def moveXY(self, x, y):
		print('move', x, y)
		self.x += x
		self.y += y
		request(SetSceneItemPosition(
			item=self.source, 
			x=self.x, 
			y=self.y, 
			scene_name=self.scene))
	
	def rotate(self, deg):
		self.rotation += deg
		if self.rotation >= 360.:
			self.rotation -= 360.
		if self.rotation < 0.:
			self.rotation += 360.
		request(SetSceneItemTransform(
			item=self.source, 
			x_scale=self.x_scale, 
			y_scale=self.y_scale, 
			scene_name=self.scene, 
			rotation=self.rotation))
			
	def scale(self, scale):
		self.x_scale += scale
		self.y_scale += scale
		request(SetSceneItemTransform(
			item=self.source, 
			x_scale=self.x_scale, 
			y_scale=self.y_scale, 
			scene_name=self.scene, 
			rotation=self.rotation))
	
	def rotateCenter(self, deg):
		return
		center_x, center_y = self.getCenter()
		self.x -= center_x
		self.y -= center_y
		self.rotation += deg
		sinx = math.sin(self.rotation / 180. * math.pi)
		cosx = math.cos(self.rotation / 180. * math.pi)
		self.x, self.y  = cosx * self.x + -sinx * self.y , sinx * self.x + cosx * self.y
		self.x += center_x
		self.y += center_y
		request(SetSceneItemTransform(
			item=self.source, 
			x_scale=self.x_scale, 
			y_scale=self.y_scale, 
			scene_name=self.scene, 
			rotation=self.rotation))
		request(SetSceneItemPosition(
			item=self.source, 
			x=self.x, 
			y=self.y, 
			scene_name=self.scene))
		
	def getCenter(self):
		center_x, center_y = self.cx * self.x_scale / 2.0, self.cy * self.y_scale / 2.0
		sinx = math.sin(self.rotation / 180. * math.pi)
		cosx = math.cos(self.rotation / 180. * math.pi)
		center_x, center_y = cosx * center_x + -sinx * center_y, sinx * center_x + cosx * center_y
		center_x += self.x
		center_y += self.y
		return center_x, center_y
		
	def toggleVisible(self):
		self.visible = not self.visible
		request(SetSourceRender(
			source=self.source,
			scene_name=self.scene,
			render=self.visible))
			
	def toggleStreaming(self):
		request(StartStopStreaming())
		
MODE = Enum('MODE',
	' '.join([
		'MOVE_X', # z
		'MOVE_Y', # x
		'SCALE', # c
		'ROTATE', # b
	])
)
vvvvvvssss
mode = MODE.MOVE_X
keys = 'zxcb'
def handleEvent(event):
	global src
	global mode
	if event['type'] == 'craft':
		event = event['msg']
		if event['message_type'] == 'crown_turn_event':
			if mode == MODE.MOVE_X:
				src.moveXY(event['delta'], 0)
			elif mode == MODE.MOVE_Y:
				src.moveXY(0, event['delta'])
			elif mode == MODE.SCALE:
				src.scale(event['delta'] / 100)
			elif mode == MODE.ROTATE:
				src.rotate(event['delta'] / 10)
			elif mode == MODE.VISIBLE:
				src.toggleVisible()
			elif mode == MODE.STREAM:
				src.toggleStreaming()
				
	elif event['type'] == 'kbd':
		event = event['msg']
		
		if event.event_type == 'down':
			if event.name == 'r':
				src.init()
			elif event.name == 's':
				src.toggleStreaming()
			elif event.name == 'v':
				src.toggleVisible()
			elif event.name in keys:
				mode = list(MODE.__members__.values())[keys.index(event.name)]
	
def main():
	global src
	src = Source(SCENE_NAME, SOURCE_NAME)
	src.init()
	craft = Craft('notepad++.exe', 1972, 'c17b2e0d-0d62-4bc1-a824-87fe81eec617')
	craft.setEventHandler(handleEvent)
	craft.connect()
	

main()