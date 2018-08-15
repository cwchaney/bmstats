#!/usr/bin/python

import psycopg2
import re

class DbPlayerStats:

	def hasPlayedWith(self, buttonName):
		return self.numPlaysWith(buttonName) > 0

	def hasPlayedAgainst(self, buttonName):
		return self.numPlaysAgainst(buttonName) > 0

	def numPlaysWith(self, buttonName):
		conn = self._dbConnect()
		cur = conn.cursor()
		try:
			buttonId = self.getButtonId(buttonName, cur)
			sql = "select count(*) from games where (player_a='coastliner' and button_a=%s) or (player_b='coastliner' and button_b=%s)"
			cur.execute(sql, (buttonId, buttonId, ))
			return cur.fetchone()[0]
		finally:
			cur.close()
			conn.commit()

	def numPlaysAgainst(self, buttonName):
		conn = self._dbConnect()
		cur = conn.cursor()
		try:
			buttonId = self.getButtonId(buttonName, cur)
			sql = "select count(*) from games where (player_a='coastliner' and button_b=%s) or (player_b='coastliner' and button_a=%s)"
			cur.execute(sql, (buttonId, buttonId, ))
			return cur.fetchone()[0]
		finally:
			cur.close()
			conn.commit()

	def _dbConnect(self):
		connString = "host='localhost' dbname='bmstats' user='craigcw' password='hello1'"
		return psycopg2.connect(connString)

	def getButtonId(self, buttonName, cur):
		escapedButtonName = re.sub("'", "''", buttonName)
		cur.execute('select button_id from buttons where button_name=\'' + escapedButtonName + '\'')
		return cur.fetchone()[0]

#stats = DbPlayerStats()
#print(stats.hasPlayedAgainst('Angora'))

