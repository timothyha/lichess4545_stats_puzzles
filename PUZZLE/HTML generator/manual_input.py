import sys
from colorama import Fore, Back
from colorama import init
init()

# List of validate inputs
store = []
# Stock the answers
q_input = []
# Store q_input[] and output to store[] with a trigger if Exit is called
switch = ""
# Dictionary use as output for puzzlextract.py.
dictio = {}
# Increment to fill the dictionary properly
count = 0



# Number questions in the form
nf = 4
# All the questions we need ["TITLE", "ACTUAL QUESTION"]
q_msg = []
q_msg.append(["gameID", "Enter the gameID (www.lichess.org/<gameID>) - if it does not exist enter only one character like \"n\": "])
q_msg.append(["description", "Enter a description (like \"Shared by...\", or ther players info if you don't have a gameID): "])
q_msg.append(["FEN", "Enter FEN: "])
q_msg.append(["Turn", "Enter colors turn to move (w/b): "])

# Avoid the "out of range" of the different lists & Used to erase vars for new entry
def range_list():
	global store
	store = []
	for x in range(nf):
		store.append("")
		q_input.append("")

range_list()

# Go through all required input in form() and send to switch and then post() if no Cancel or Exit
def master():
	global switch

	for x in range(nf):
		while switch == "":
			# User instructions
			print("# Type " + Fore.RED + "exit" + Fore.RESET + " to cancel (only this entry) and start generate the HTML.")
			# From form() to switch
			switch = forms(x)
		# Test the trigger
		switch_behavior()

	if switch != "exit":
		post()

	return

# Commit the forms to the dictionary and ask for more entries
def post():
	global store
	global count

	# Show entry
	print("Entry n°" + Fore.YELLOW + str(count + 1) + ":" + Fore.RESET)
	for x in range(nf):
		print(q_msg[x][0] + ": " + Fore.CYAN + store[x] + Fore.RESET)

	# Ask for validation.
	print(Fore.MAGENTA)
	valid = input("Validate this entry (y/n) ? ")
	print(Fore.RESET)
	if valid == "y" or valid == "yes":
		# Commit the value of the form in the global dictionary
		dictio.update({count: store})
		count += 1
		print ("# " + Fore.YELLOW + "Stored." + Fore.RESET)
	# Cancel this entry
	else:
		print ("# " + Fore.YELLOW + "Cancelled." + Fore.RESET)

	# Erase data for a new entry
	range_list()

	# Continue or Exit
	print(Fore.MAGENTA)
	again = input("Add another entry? (y/n) ")
	print(Fore.RESET)
	if again == "y" or again == "yes":
		print("# " + Fore.YELLOW + "NEW ENTRY" + Fore.RESET + "\n ")
		master()
	# Nothing can come after this

	return

# All the data needed asked with input("question?") to the user
def forms(q_num):
	print(Fore.GREEN)
	q_input = input(q_msg[q_num][1])
	print(Fore.RESET)
	if all( [q_input != "", q_input != "exit"] ):
		store[q_num] = q_input

	return(q_input)


# Manage the Exit trigger
def switch_behavior():
	global switch
	if switch != "exit":
		switch = ""

# First launch
if count == 0:
	print("\n#########################################"
	"\n# " + Fore.YELLOW + "Welcome in the manual input interface." + Fore.RESET +
	"#\n#########################################"
	"\n#")
	master()

# END
print("# " + Fore.YELLOW + "END OF MANUAL INPUTS" + Fore.RESET)