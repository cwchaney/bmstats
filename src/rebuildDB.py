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

def createTables():
	conn = dbConnect()
	cur = conn.cursor()
	for table, columns in TABLES.items():
		command = "CREATE TABLE " + table + " ( "
		first = True
		for column in columns:
			if first:
				first = False
			else:
				command = command + ", "
			command = command + column
		command = command + " )"
		cur.execute(command)
	cur.close()
	conn.commit()

def initializeButtonData(filename):
	conn = dbConnect()
	cur = conn.cursor()
	with open(filename, 'r') as fileIn:
		data = json.load(fileIn)

	buttonList = data['data']
	sets = {}

	# Create special unknown set
	cur.execute("insert into button_sets(button_set_name) values('Unknown')")
	sets['Unknown'] = 1
	
	for button in buttonList:
		buttonName = button['buttonName']
		setName = button['buttonSet']

		if setName not in sets:
			sql = "insert into button_sets(button_set_name) values(%s) returning button_set_id"
			cur.execute(sql, (setName,))
			sets[setName] = cur.fetchone()[0]
		buttonSetId = sets[setName]

		sql = "insert into buttons(button_id, button_name, button_set_id, tourney_legal) values(%s, %s, %s, %s)"
		buttonId = button['buttonId']
		buttonName = button['buttonName']
		tourneyLegal = button['isTournamentLegal']
		cur.execute(sql, (buttonId, buttonName, str(buttonSetId), tourneyLegal,))

	cur.close()
	conn.commit()

def dropTables():
	conn = dbConnect()
	cur = conn.cursor()
	try:
		for table in list(TABLES):
			command = "DROP TABLE " + table
			cur.execute(command)
	except (Exception, psycopg2.ProgrammingError) as error:
		# EAT IT
		pass
	finally:
		cur.close()
		conn.commit()

def retrieveGameData(pageNum):
	#login
	loginBody = {
		'type' : 'login',
		'username' : 'hitchhucker',
		'password' : 'veramold',
	}
	login = requests.post('http://www.buttonweavers.com/api/responder', data = loginBody)
	loginResponse = json.loads(login.text)
	if loginResponse['status'] != 'ok':
		raise Exception('Login status was not ok:  ' + loginResponse['status'])

	statsBody = {
		'lastMoveMin' : '1390000000',
		'status' : 'COMPLETE',
		'sortColumn' : 'lastMove',
		'sortDirection' : 'ASC',
		'numberOfResults' : '100',
		'page' : str(pageNum),
		'type' : 'searchGameHistory',
		'automatedApiCall' : 'false',
	}
	r = requests.post('http://www.buttonweavers.com/api/responder', data = statsBody, cookies = login.cookies)
	statsResponse = json.loads(r.text)
	if statsResponse['status'] != 'ok':
		raise Exception('Stats  status was not ok:  ' + statsResponse['status'])

	with open('save_%03d.txt' % pageNum, 'w') as outputFile:
		print(r.text, file=outputFile)

def saveGameData(filename):
	with open(filename, 'r') as fileIn:
		gameData = json.load(fileIn)

	conn = dbConnect()
	cur = conn.cursor()
	try:
		gamesList = gameData['data']['games']
		for game in gamesList:
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

#dropTables()
#createTables()
#initializeButtonData('../data/buttons.json')
#for i in range(1, 377):
	##getGameData(i, False)
	#saveGameData('../data/games/save_%03d.txt' % i)
	#print("Page " + str(i))
	##time.sleep(300) # 5 minutes
