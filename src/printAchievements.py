#!/usr/bin/python

from buttons import Buttons
from playerStats import PlayerStats

buttons = Buttons('../data/buttons.json')
stats = PlayerStats('../data/bmstats.json')

completed = []
close = []
for setName in buttons.getSets():
	needs = filter(lambda b: not stats.hasPlayedWith(b), buttons.getButtons(setName))
	if needs:
		print(setName + ': ' + ', '.join(map(str, needs)))
		if len(needs) <= 3:
			close.append(setName)
	else:
		completed.add(setName)

if completed:
	print('\n\nCOMPLETED: ' + ', '.join(map(str, completed)))
if close:
	print('\n\nCLOSE: ' + ', '.join(map(str, close)))
