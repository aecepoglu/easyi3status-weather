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
				'full_text': '?'
			})

		self.minWindSpeed = config.get('minWindSpeed', 5)
		self.isBusy = False
		self.hasError = False
		self.wantedHours = config.get('wantedHours', list(range(0, 23, 3)))
		self.wantedHoursCount = int(12 / 4) + 1

		self.update()
	
	def work(self):
		resp = requests.get(self.apiUrl)

		if resp.status_code != 200:
			self.error('bad_req')
			return
		
		jsonobj = resp.json()
		lastDoneIndex = None

		for index in range(0, min(len(jsonobj['list']), self.wantedHoursCount)):
			record = jsonobj['list'][index]	
			prevRecord = jsonobj['list'][index -1] if index > 0 else None

			itsTime = time.gmtime(record['dt'])

			if itsTime.tm_hour not in self.wantedHours:
				self.values[index * 2]['full_text'] = ''
				self.values[index * 2 + 1]['full_text'] = ''
				continue

			recordDescriptions = [
				str(int(record['main']['temp'])) + u'°'
			]

			if prevRecord is None or prevRecord['weather'][0]['id'] != record['weather'][0]['id']:
				recordDescriptions.append(record['weather'][0]['description'])

			if record['wind']['speed'] > self.minWindSpeed:
				recordDescriptions.append(
					Module.getCardinalWindDirection(record['wind']['deg']) + ' ' + str(record['wind']['speed']),
				)

			lastDoneIndex = index
			self.values[index * 2]['full_text'] = time.strftime('%H:%M', itsTime)
			self.values[index * 2 + 1]['full_text'] = ' '.join(recordDescriptions)
			self.values[index * 2 + 1]['separator_block_width'] = 10

		if lastDoneIndex is not None:
			self.values[lastDoneIndex * 2 + 1]['separator_block_width'] = 40

	def update(self):
		if not self.hasError and not self.isBusy:
			Thread(target=self.work).start()

