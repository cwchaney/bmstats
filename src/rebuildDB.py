import json
import psycopg2

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
		'a_won boolean not null',
		'game_start date not null',
		'last_move date not null',
	],
}

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

dropTables()
createTables()
initializeButtonData('../data/buttons.json')
