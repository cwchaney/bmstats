#!/usr/bin/python

import json

class PlayerStats:
	def __init__(self, filename):
		with open(filename, 'r') as fileIn:
			data = json.load(fileIn)
		if ('status' not in data) or ('message' not in data):
			raise Exception('Problem fetching games')
		if data['status'] != 'ok':
			raise Exception(message)
		if data['message'] != 'Sought games retrieved successfully.':
			raise Exception(message)

		gameList = data['data']['games']
		self.playedWith = {}
		self.playedAgainst = {}
		for game in gameList:
			myButton = game['buttonNameA']
			if myButton not in self.playedWith:
				self.playedWith[myButton] = 1
			else:
				self.playedWith[myButton] = self.playedWith[myButton] + 1

			oppButton = game['buttonNameB']
			if oppButton not in self.playedAgainst:
				self.playedAgainst[oppButton] = 1
			else:
				self.playedAgainst[oppButton] = self.playedAgainst[oppButton] + 1

	def hasPlayedWith(self, buttonName):
		return buttonName in self.playedWith

	def hasPlayedAgainst(self, buttonName):
		return buttonName in self.playedAgainst

	def numPlaysWith(self, buttonName):
		return 0 if not self.hasPlayedWith(buttonName) else self.playedWith[buttonName]

	def numPlaysAgainst(self, buttonName):
		return 0 if not self.hasPlayedAgainst(buttonName) else self.playedAgainst[buttonName]

#filename = '../data/bmstats.txt'

#stats = PlayerStats(filename)

#print(stats.numPlaysWith('Angel'))
#print(stats.numPlaysAgainst('Jose'))

