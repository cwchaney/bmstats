#!/usr/bin/python

import json

class Buttons:
	def __init__(self, filename):
		with open(filename, 'r') as fileIn:
			data = json.load(fileIn)
		if ('status' not in data) or ('message' not in data):
			raise Exception('Problem fetching games')
		if data['status'] != 'ok':
			raise Exception(message)
		if data['message'] != 'Button data retrieved successfully.':
			raise Exception(message)

		buttonList = data['data']
		self.sets = {}
		for button in buttonList:
			buttonName = button['buttonName']
			setName = button['buttonSet']
			if setName not in self.sets:
				self.sets[setName] = { 'legal': [], 'notLegal': [] }

			tl = button['isTournamentLegal']
			if tl:
				self.sets[setName]['legal'].append(buttonName)
			else:
				self.sets[setName]['notLegal'].append(buttonName)

	def getButtons(self, setName, legal=None):
		if setName == 'Miscellaneous':
			rv = self.getMiscellaneousButtons(legal)
		elif legal == None:
			rv = self.sets[setName]['legal'] + self.sets[setName]['notLegal']
		elif legal:
			rv = self.sets[setName]['legal']
		else:
			rv = self.sets[setName]['notLegal']
		return sorted(rv)

	def getMiscellaneousButtons(self, legal):
		buttons = []
		for s in list(self.sets):
			if len(self.getButtons(s)) <= 2:
				buttons = buttons + self.getButtons(s, legal)

		return buttons

	def getSets(self):
		#return sorted(list(self.sets))
		return sorted(filter(lambda s: len(self.getButtons(s)) > 2, list(self.sets)) + ['Miscellaneous'])

#filename = '../data/buttons.json'

#buttons = Buttons(filename)
#misc = buttons.getButtons('Miscellaneous', False)
#print misc
#print len(misc)

