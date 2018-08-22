import datetime
import json
import psycopg2
import re
import requests
import time

TABLES = {
	'button_sets' : ['button_set_id serial primary key', 'button_set_name varchar(255)' ],
	'buttons'     : ['button_id integer primary key', 'button_name varchar(255) not null', 'button_set_id integer not null', 'tourney_legal boolean not null' ],
	'games'       : [
		'game_id integer primary key',
		'player_a varchar(255) not null',
		'player_b varchar(255) not null',
		'button_a integer not null',
		'button_b integer not null',
		'rounds_won_a integer not null',
		'rounds_won_b integer not null',
		'rounds_drawn integer not null',
		'a_won boolean not null',
		'game_start date not null',
		'last_move date not null',
	],
}

UNKNOWN_INDEX = 100001

def dbConnect():
	connString = "host='localhost' dbname='bmstats' user='craigcw' password='hello1'"
	return psycopg2.connect(connString)

def retrieveGameData(printOnly):
	loginBody = {
		'type' : 'login',
		'username' : 'hitchhucker',
		'password' : 'veramold',
	}
	login = requests.post('http://www.buttonweavers.com/api/responder', data = loginBody)
	loginResponse = json.loads(login.text)
	if loginResponse['status'] != 'ok':
		raise Exception('Login status was not ok:  ' + loginResponse['status'])

	conn = dbConnect()
	cur = conn.cursor()
	try:
		cur.execute('select value from properties where key = \'latestMove\'')
		prevLastMove = cur.fetchone()[0]
		print(prevLastMove)
		gamesList = []
		pageNum=1
		while True:
			statsBody = {
				'lastMoveMin' : str(int(prevLastMove) + 1),
				'status' : 'COMPLETE',
				'sortColumn' : 'lastMove',
				'sortDirection' : 'ASC',
				'numberOfResults' : '100',
				'page' : str(pageNum),
				'type' : 'searchGameHistory',
				'automatedApiCall' : 'false',
			}
			pageNum = pageNum + 1
			r = requests.post('http://www.buttonweavers.com/api/responder', data = statsBody, cookies = login.cookies)
			#if printOnly:
				#print(r.text)
				#return
			gameData = json.loads(r.text)
			if gameData['status'] != 'ok':
				raise Exception('Stats  status was not ok:  ' + gameData['status'])
			newGameList = gameData['data']['games']
			if len(newGameList) == 0:
				break
			gamesList.extend(newGameList)
		if printOnly:
			print(len(gamesList))
			return

		prevLastMove = 0
		for game in gamesList:
			sql = "select count(*) from games where game_id=%s"
			cur.execute(sql, (game['gameId'],))
			countResult = cur.fetchone()[0]
			if countResult != 0:
				print('Should not see same gameId twice: ' + str(game['gameId']))
				#raise Exception('Should not see same gameId twice: ' + str(game['gameId']))
				continue

			sql = "insert into games(game_id, player_a, player_b, button_a, button_b, rounds_won_a, rounds_won_b, rounds_drawn, a_won, game_start, last_move) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
			buttonA = getButtonId(game['buttonNameA'], cur)
			buttonB = getButtonId(game['buttonNameB'], cur)
			gameId = game['gameId']
			roundsWonA = int(game['roundsWonA'])
			roundsWonB = int(game['roundsWonB'])
			aWon = roundsWonA > roundsWonB
			gameStart = datetime.datetime.fromtimestamp(game['gameStart']).date()
			lastMove = datetime.datetime.fromtimestamp(game['lastMove']).date()
			cur.execute(sql, (gameId, game['playerNameA'], game['playerNameB'], buttonA, buttonB, 
				roundsWonA, roundsWonB, game['roundsDrawn'], aWon, gameStart, lastMove,))
			latestMove = max(prevLastMove, int(game['lastMove']))
		#cur.execute("insert into properties(key, value) values(%s, %s)", ('latestMove', str(latestMove),))
		cur.execute("update properties set value=%s where key=%s", (str(latestMove), 'latestMove',))
	finally:
		cur.close()
		conn.commit()


def getButtonId(buttonName, cur):
	global UNKNOWN_INDEX

	escapedButtonName = re.sub("'", "''", buttonName)
	#escapedButtonName = re.sub("\\(", "\(", escapedButtonName)
	#escapedButtonName = re.sub("\\)", "\)", escapedButtonName)
	cur.execute('select button_id from buttons where button_name=\'' + escapedButtonName + '\'')
	try:
		return cur.fetchone()[0]
	except TypeError:
		index = UNKNOWN_INDEX
		sql = "insert into buttons(button_id, button_name, button_set_id, tourney_legal) values(%s, %s, %s, %s)"
		cur.execute(sql, (index, buttonName, 1, False,))
		UNKNOWN_INDEX = UNKNOWN_INDEX + 1
		return index

retrieveGameData(False)
