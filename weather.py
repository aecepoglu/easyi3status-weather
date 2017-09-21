import requests
import json
import time
from threading import Thread
from statusModule import EasyI3StatusModule

class Module(EasyI3StatusModule):
	cardinalLookup = [
		'N',
		'NNE',
		'NE',
		'ENE',
		'E',
		'ESE',
		'SE',
		'SE',
		'SSE',
		'SE',
		'SSE',
		'S',
		'SSW',
		'SW',
		'WSW',
		'W',
		'WNW',
		'NW',
		'NNW'
	]

	@classmethod
	def getCardinalWindDirection(myClass, degrees):
		segment = int((degrees + 11.25) / 22.5)
		return myClass.cardinalLookup[segment]

	def error(self, msg, terminate = False):
		self.values = [{
			'full_text': msg,
			'color': '#FF0000',
			'separator_block_width': 40
		}]
		if terminate:
			self.hasError = True

	def __init__(self, config):
		self.validDuration = 3600 #1 hour

		if 'appid' not in config:
			self.error('no_appid', terminate=True)
			return

		self.apiUrl = ''.join(('http://api.openweathermap.org/data/2.5/forecast',
			'?id=' + str(config.get('city', 6955677)), #use Ankara by default
			'&APPID=' + config['appid'],
			'&units=' + config.get('units', 'metric')
		))
		
		if 'language' in config:
			self.apiUrl += '&lang=' + config['language']

		self.values = []
		for i in range(0, 4):
			self.values.append({
				'full_text': '?',
				'separator': False,
				'separator_block_width': 5,
				'color': '#9090ff'
			})
			self.values.append({
				'full_text': '?',
				'separator_block_width': 40 if (i is 3) else 10
			})

		self.minWindSpeed = config.get('minWindSpeed', 5)
		self.isBusy = False
		self.hasError = False

		self.update()
	
	def work(self):
		resp = requests.get(self.apiUrl)

		if resp.status_code != 200:
			self.error('bad_req')
			return
		
		jsonobj = resp.json()

		for index in range(0, 4):
			record = jsonobj['list'][index]
			prevRecord = jsonobj['list'][index - 1] if (index > 0) else None

			recordDescriptions = [
				str(int(record['main']['temp'])) + u'°'
			]

			if prevRecord is None or prevRecord['weather'][0]['id'] != record['weather'][0]['id']:
				recordDescriptions.append(record['weather'][0]['description'])

			if record['wind']['speed'] > self.minWindSpeed:
				recordDescriptions.append(
					Module.getCardinalWindDirection(record['wind']['deg']) + ' ' + str(record['wind']['speed']),
				)

			self.values[index * 2]['full_text'] = time.strftime('%H:%M', time.gmtime(record['dt']))
			self.values[index * 2 + 1]['full_text'] = ' '.join(recordDescriptions)

	def update(self):
		if not self.hasError and not self.isBusy:
			Thread(target=self.work).start()
