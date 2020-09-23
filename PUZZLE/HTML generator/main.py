import chess.pgn
from bs4 import BeautifulSoup
from urllib.request import urlopen
import json
import time
from io import StringIO
import fileinput
import re
import argparse
import os
from colorama import Fore, Back
from colorama import init
init()

# HTML output, cleaning it first
erase_html = open("generated_html_table.html", "w")
erase_html.write("")
erase_html.close()
file_html = open("generated_html_table.html", "a")

# puzzle counter
count = 1

# Declaring useful variable in different function
gameID = ""
manual_puzzles = {}

# Ability to input multiple json files and define the --manual option
parser = argparse.ArgumentParser()
parser.add_argument("--files", type=str, nargs="+", default=[""])
parser.add_argument("--manual", help="Add manual puzzles", action="store_true", default=False)
args = parser.parse_args()

# Launch the manual script if --manual was activated
# if args.manual:
from manual_input import dictio
manual_puzzles = dictio

# Store the json files in a list
json_puzzles = []

if args.files == [""]:
	args.files = list()
	for file in os.listdir("json"):
		file_path = "json/" + file
		args.files.append(file_path)

def ordering(json_shuffle):
	# print("IN: {}".format(json_shuffle))
	ordered = []

	order = input("ordering (ex: 4 2 1 3) - or type 'n' if no order: ")
	if order == "n":
		return json_shuffle
	else:
		order = order.split(" ")

		for x in range(len(order)):
			# print("Number {}".format(x))
			# print("LOOP: {}".format(order[x]))
			f = int(order[x])-1
			# print("LOOP equivalent: {}".format(json_shuffle[f]))
			ordered.append(json_shuffle[f])
		
	return ordered

# Fetching pgn from lichess for data
def fetch_lichess():
	global w_player
	global b_player
	global w_player_elo
	global b_player_elo
	global gameID
	global fen
	global turn
	global timecontrol
	global variant

	html = urlopen('https://lichess.org/{0}'.format(gameID))

	soup = BeautifulSoup(html, 'html.parser')
	pgnraw = soup.find("div", {"class": "pgn"})
	pgnclean = str(pgnraw)
	pgn_string = pgnclean[17:-6]
	pgn = StringIO(pgn_string)

	game = chess.pgn.read_game(pgn)

	# player name/elo & timecontrol
	w_player = game.headers["White"]
	w_player_elo =  game.headers["WhiteElo"]
	b_player = game.headers["Black"]
	b_player_elo =  game.headers["BlackElo"]
	timecontrol = game.headers["TimeControl"]
	variant = game.headers["Variant"]

	time.sleep(1)

def fen_convert(fen):
	fen_link = fen.split(" ")[0].replace("/", "H")
	if fen.split(" ")[1] == "b":
		fen_link += "&f=1"
	return fen_link

def extract():
	global count
	global gameID

	# Decrypt json & Record last_pos & last_move & gameID
	json_tree = json.loads(line)
	gameID = json_tree['game_id']
	last_pos = json_tree['last_pos']
	last_move = json_tree['last_move']

	# Create the final FEN position with last_pos+last_move
	board = chess.Board(last_pos)
	board.push_uci(last_move)
	fen = board.fen()

	# Which turn to move
	if board.turn == True:
		turn = '&#x26AA; White'
	else:
		turn = '&#x26AB; Black'

	fetch_lichess()

	# Generate the html between each <td></td> using all the data (for auto puzzles)
	td_str = """<td style="text-align: center;"><strong>{w} </strong>({we}) -<strong> {b} </strong>({be})<br /><a href="https://lichess.org/{id}">Gamelink</a>.<br />{t} to play.<br /><a href="https://lichess.org/analysis/{f}"><img src="https://chessdiagram.online/arrowgram.php?de=120&a={fl}" style="height:250px; width:250px" /></a></td>"""
	td = td_str.format(w=w_player, b=b_player, we=w_player_elo, be=b_player_elo, id=gameID, f=fen, fl=fen_convert(fen), t=turn)

	print(Fore.CYAN + "Creation of puzzle n°" + Fore.YELLOW + "{0}".format(count) + Fore.RESET + " (" + Fore.GREEN + "auto" + Fore.RESET + ")")
	count += 1

	return (td, timecontrol, variant)

# extract json into a list()
for line in fileinput.input(args.files):
	files_lines = line.strip()
	# Filter the blank lines
	if re.match(r'^\s*$', files_lines):
		pass
	else:
		json_puzzles.append(files_lines)
try:
	json_puzzles = ordering(json_puzzles)
except:
	print("---No ordering processed---")

# declare the lists for the loop to fill
series = []
lichess4545 = []
lonewolf = []
others = []
chess960 = []
rapid = []
blitz = []
manual = []

# loop to generate all the data
for line in json_puzzles:
	puzzle = extract()
	# ordering puzzles by league
	if puzzle[1] == "5400+30":
		series.append(puzzle[0])
	elif puzzle[1] == "2700+45":
		lichess4545.append(puzzle[0])
	elif puzzle[1] == "1800+30":
		lonewolf.append(puzzle[0])
	elif puzzle[2] == "Chess960":
		chess960.append(puzzle[0])
	elif puzzle[1] == "900+10" and puzzle[2] == "Standard":
		rapid.append(puzzle[0])
	elif puzzle[1] == "180+2":
		blitz.append(puzzle[0])
	else:
		others.append(puzzle[0])

# Extract from dictionnary manual_puzzles to list
# in -> {0: (gameID, description, fen, turn),1: (gameID, description, fen, turn)...}
# looping for tuples: (gameID, description, fen, turn)
# out -> [(gameID, description, fen, turn),(gameID, description, fen, turn)...]
# And also order puzzle with ID and puzzle without
if manual_puzzles:
	ext_manual = ()
	manual = list()
	for x in manual_puzzles:
		ext_manual = manual_puzzles[x]
		fen = ext_manual[2]
		turn = ext_manual[3]
		if turn == "w" or turn == "white":
			turn = '&#9711; White'
		else:
			turn = '&#9899; Black'

		# If gameID
		try:
			# Test if gameID is more than one character
			temp_var_just_for_testing = ext_manual[0][1]

			gameID = ext_manual[0]
			extra_desc = ext_manual[1]
			fetch_lichess()

			# Generate the html between each <td></td> using all the data (for manual puzzles with ID)
			td_str = """<td style="text-align: center;"><strong>{w} </strong>({we}) -<strong> {b} </strong>({be})<br /><a href="https://lichess.org/{id}">Gamelink</a>.<br />{desc}<br />{t} to play.<br /><a href="https://lichess.org/analysis/{f}"><img src="https://chessdiagram.online/arrowgram.php?de=120&a={fl}" style="height:250px; width:250px" /></a></td>"""
			manual.append(td_str.format(w=w_player, b=b_player, we=w_player_elo, be=b_player_elo, id=gameID, f=fen, fl=fen_convert(fen), t=turn, desc=extra_desc))
			print(Fore.CYAN + "Creation of puzzle n°" + Fore.YELLOW + "{0}".format(count) + Fore.RESET + " (" + Fore.MAGENTA + "manual" + Fore.RESET + ")")
			count += 1

		# If no gameID
		except:
			# Without ID there is still the description input
			substitute = ext_manual[1]

			# Generate the html between each <td></td> using all the data (for manual puzzles without ID)
			td_str = """<td style="text-align: center;">{sub}<br />{t} to play.<br /><a href="https://lichess.org/analysis/{f}"><img src="https://chessdiagram.online/arrowgram.php?de=120&a={fl}" style="height:250px; width:250px" /></a></td>"""
			manual.append(td_str.format(f=fen, fl=fen_convert(fen), t=turn, sub=substitute))
			print(Fore.CYAN + "Creation of puzzle n°" + Fore.YELLOW + "{0}".format(count) + Fore.RESET + " (" + Fore.MAGENTA + "manual" + Fore.RESET + ")")
			count += 1

# Format everything that is not data related to html
header = """<p style="text-align: justify; margin-left: 40px;"><em>Click on the images for the solution.</em></p><table align="center" style="width:90%">"""
tr_lichess4545 = """<tr><td colspan=4><p style="text-align:center"><a href="/team4545/"><img alt="team4545" src="https://image.ibb.co/hvqm3b/2018_01_21_2.png" /></a></p></td></tr>"""
tr_lonewolf = """<tr><td colspan=4><p style="text-align:center"><a href="/lonewolf/"><img alt="Lonewolf" src="/media/uploads/2019/04/30/lonewolf.PNG" /></a></p></td></tr>"""
tr_series = """<tr><td colspan=4><p style="text-align:center"><span style="font-size:14px">Series</span></p></td></tr>"""
tr_chess960 = """<tr><td colspan=4><p style="text-align:center"><a href="https://www.lichess4545.com/chess960/"><img alt="" src="/media/uploads/2018/06/25/960_5DSFC2P.PNG" style="height:50px; width:267px" /></a></p></td></tr>"""
tr_rapid = """<tr><td colspan=4><p style="text-align:center"><span style="font-size:14px">Rapid</span></p></td></tr>"""
tr_blitz = """<tr><td colspan=4><p style="text-align:center"><a href="/blitzbattle/"><img alt="Blitz-battle" src="https://image.ibb.co/fmnWrT/logo_blitz.png" width="266" /></a></p></td></tr>"""
tr_others = """<tr><td colspan=4><p style="text-align:center"><span style="font-size:14px">Others (or just wrong time control)</span></p></td></tr>"""
tr_manual = """<tr><td colspan=4><p style="text-align:center"><span style="font-size:14px">Shared by the community</span> (can contain imperfect puzzles.)</p></td></tr>"""
tr_open = """<tr>"""
tr_close = """</tr>"""
foot = """</table><p style="text-align: right;">Chessboard images provided by&nbsp;<a href="https://www.apronus.com/">apronus</a>.</p>"""

# Starting writing HTML
file_html.write(header)

# Repeat the script for each league separately
def each_league(league, tr_league):
	# Title (league) of the following puzzles
	file_html.write(tr_league)

	# Caculate the number of row needed
	row_calc = 0
	for x in league:
		row_calc += 1
	row = row_calc // 4
	rest = row_calc % 4

	# Increment variable for targeting the correct element in the list
	u = 0

	# Generating full rows (= 4 puzzles)
	if row != 0:
		for x in range(row):
			file_html.write(tr_open)
			for i in range(4):
				file_html.write(league[u])
				u += 1
			file_html.write(tr_close)
			row -= 1

	# Last row or less than 4 puzzles in this league
	if rest != 0:
		file_html.write(tr_open)
		for i in range(rest):
			file_html.write(league[u])
			u += 1
		file_html.write(tr_close)

# Check if any entry before comiting the script
if lichess4545:
	each_league(lichess4545, tr_lichess4545)
if lonewolf:
	each_league(lonewolf, tr_lonewolf)
if series:
	each_league(series, tr_series)
if others:
	each_league(others, tr_others)
if chess960:
	each_league(chess960, tr_chess960)
if rapid:
	each_league(rapid, tr_rapid)
if blitz:
	each_league(blitz, tr_blitz)
if manual:
	each_league(manual, tr_manual)

# Closing html
file_html.write(foot)

# End of the script
file_html.close()
print("\n\n# Output generated in the file " + Fore.GREEN + "\"generated_html_table.html\"" + Fore.RESET + \
	  "\n########################" \
	  "\n# " + Fore.YELLOW + "End of the Generator." + Fore.RESET + \
	  "#\n########################" \
	  "\n#")