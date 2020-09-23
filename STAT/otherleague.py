OTHERLEAGUE = input("full name of file and extention: ")

with open (OTHERLEAGUE, "r") as file:
    data=file.readlines()

trigger = 'Site "https://lichess.org/'
games = list()

for x in data:
	if x.find(trigger) != -1:
		games.append(x[27:-3])

print(games)

END = input("---End---")

# 27