"""
Tools to edit text files containing minecraft commands into current usable minecraft 1.12 mcfunction files
Usage:
	send a list where each element is 1 command into wanted method
	returns a new updated list
	does not change sent list

list of current functions:
	gotofunction, miscfindreplace, dumpmakefunctions, selectorcoords, tellrawtojson, makelower, parsemsb
"""

# changes msb standard function gotos into new minecraft 1.12 mcfunction commands
# 2017-10-01
def gotofunction(input_commands):
	edited_commands = []
	for command in input_commands:
		if command[-24:] == "minecraft:redstone_block" and command[:7] == 'execute' and command.find('fill') > -1:
			name = command[command.index('name=f')+6:].lower()
			name = name[:name.index("]")]
			selector = ''
			if command[8:].find('execute') > -1:
				selector = ' if ' + command[8:command.index(']')+1]
			command = "function eris:" + name + selector
		edited_commands.append(command)
	return edited_commands



# misc find and replaces
# 2017-09-30
def miscfindreplace(input_commands):
	edited_commands = []
	for command in input_commands:
		command = command.replace("type=Item", "type=item")				# lower case for nice syntax highlighting
		command = command.replace('MushroomCow','mooshroom')			# updates to the new name of the mob moeshroom
		command = command.replace('id:minecraft:', 'id:')				# a hacky way to update missing quotes around item ids in nbt data
		command = command.replace('LeashKnot','leash_knot')
		command = command.replace(',r=0',',r=1')
		# complex replaces
		if command.find("type=item") > -1 and command.find("kill") == -1:		# used to find any item variable calls and change them to armor_stand
			command = command.replace("type=item","type=armor_stand") 
		if command.find('Riding:'):												# changes any entity riding into the 'passengers' tag; might mess up things with squar brackets
			command = command.replace('Riding:','Passengers:[')
			curly = 0
			marker = []
			lock = False
			n_c = ''
			for l in command:
				n_c = n_c + l
				if l == '{':
					curly += 1
					lock = False
				elif l == '}':
					curly -= 1
				elif l == '[' and n_c[-12:] == "Passengers:[":		# if it is messing up square brackets add the exception here
					marker.append(curly)
					lock = True
				if lock == False and curly in marker:
					n_c= n_c + ']'
					marker.remove(curly)
			command = n_c
		if command.find("playsound") > -1 and len(command[command.index('playsound'):].split(' ')) < 10:		# playsound fix
			TO_REPLACE = ('random.pop','random.break','random.fizz','random.anvil_land','random.levelup','mob.wither.hurt','mob.enderdragon.wings','mob.enderdragon.hit','mob.zombie.uneffect','portal.trigger','mob.endermen.portal','random.chestopen','random.chestclose','portal.travel','firework.blast','mob.wither.death','mob.ghast.charge')
			REPLACE_WITH = ('entity.item.pickup', 'entity.item.break','block.fire.extinguish', 'block.anvil.land','entity.player.levelup','entity.wither.hurt','entity.enderdragon.flap','entity.enderdragon.hurt','entity.zombie_villager.converted','block.portal.trigger','entity.endermen.teleport','block.chest.open','block.chest.close','block.portal.travel','entity.firework.blast','entity.wither.death','entity.ghast.warn')
			for rep in TO_REPLACE:
				command = command.replace(rep,REPLACE_WITH[TO_REPLACE.index(rep)])
			parsed = command[command.index('playsound'):].split(' ')
			parsed.insert(2, 'master')
			new_c = ''
			for l in parsed:
				new_c+=l + ' '
			command = command[:command.index('playsound')] + new_c[:-1]
		command = command.replace(']]',']')								# quick fix for errored double ]]
		edited_commands.append(command)
	return edited_commands



# takes a dump of compiled MSB functions and puts them into mcfunctions
# this tool is unique in that it returns a list of functions as lists of the function name and commands
# 2017-10-01
def dumpmakefunctions(input_commands):
	functions = []
	function_names = []
	command_list = []
	for command in input_commands:
		if command[-15:] == "minecraft:stone":
			isolate = command[command.index("name=f")+6:]
			name = isolate[:isolate.index("]")].lower()
			function_names.append(name)
			functions.append(command_list)
			for c in command_list:
				if c[:1] == "/":
					c = c[1:]
			command_list = []
		else:
			command_list.append(command)
	return function_names, functions



# updates the x y z r tags in selectors to include x= y= z= r=
# 2017-09-30
def selectorcoords(input_commands):
	NUMBERS = '1234567890-'
	TAG_ORDER = 'xyzr'
	edited_commands = []
	for command in input_commands:
		if command.find('[') > -1:
			seltags = command[command.index('['):command.index(']')]
			if seltags[1] in NUMBERS:
				new = ''
				previous = ''
				cycle = 0
				for letter in seltags:
					if letter in NUMBERS and (previous == ',' or previous == '['):
						new = new + TAG_ORDER[cycle] + '='
						cycle += 1
					new = new + letter
					previous = letter		
				command = command.replace(seltags,new)
		edited_commands.append(command)
	return edited_commands



# fixes old tellraws to support proper JSON by adding quotation marks around everything
# 2017-10-01
def tellrawtojson(input_commands):
	CHANGE = ['show_text', 'text','color','underlined','true','false','hoverEvent','clickEvent','run_command','action','value', 'score', 'extra', "dark_red","red","gold","yellow","dark_green","green","aqua","dark_aqua","dark_blue","blue","light_purple","dark_purple","white","gray","dark_gray","black"]
	edited_commands = []
	for command in input_commands:
		if command.find('{') > -1 and (command.find('tellraw') > -1 or command.find('title') >-1):
			for c in CHANGE:
				re = '"'+c+'"'
				if command.find(re) == -1 and command[command.find(c)-1] in '{[:,':
					sub = command[command.index('{'):]
					sub = sub.replace(c, re)
					command = command[:command.index('{')] + sub
				if command.find("/"+re) > -1:							# fixes a case where an embeded run_command value like '/scoreboard' doesnt become '/"score"board'
					command = command.replace("/"+re,"/"+c)
			if command.find('show_"text"') > -1:						# fixes the case where "text" is applied to "show_text" 'text' bit
				command = command.replace('show_"text"',"show_text")
		edited_commands.append(command)
	return edited_commands



# goes through and changes all characters that are not in nbt tags to lower case
# 2017-10-01
def makelower(input_commands):
	commands = []
	for command in input_commands:
		new_c = ''
		index = 0
		while l != '{' and index < len(l):
			l = l[index]
			new_c += l.lower()
			index += 1
		new_c += l[index:]


# updates an MSB command set to a list of mcfunctions
# This tool is unique as it returns a list of new functions names, and a list of functions as a list of commands
# 2018-06-13
def parsemsb(commands):
	functions = []
	function_names = []
	var_init = []
	i = 0
	while i < len(commands) - 1:
		split = commands[i].split(' ')
		# case when a function or loop is found and it is not at the end of the document (actually has the possibility of having commands)
		if (split[0] == 'function' or split[0] == 'loop') and (i + 1 < len(commands) -1):
			name = split[1]
			sel = split[2]
			# index update to the next command (which should be in the loop or function structure)
			i += 1
			next = commands[i]
			next_split = next.split(" ")
			new_func = []
			function_names.append(name)
			# loop through the next commands until it ends, in which case we will know it is a new function/loop/var
			while next_split[0] != 'function' and next_split[0] != 'loop' and (i < len(commands)):
				# replace the MSB goto identifiers
				if next.find('run') > -1:
					next.replace('run ', "function qc:")
				# replace the selector shortcut
				next = next.replace("@"+name,sel)
				new_func.append(next)
				# special case of another command being on the last line of the document
				if i == len(commands)-1:
					break					# since the loop uses a look ahead I have to, Im sorry.
				# update the interior loop
				i += 1
				next = commands[i]
				next_split = next.split(" ")
			functions.append(new_func)
			# I have to go back an index now so that when the while loops around we can actually enter the "loop or function" if structure rather than skip past it
			i -= 1
		# case when a var declaration is found
		if split[0] == 'var':
			var_init.append("kill @e[type=armor_stand,name=" + split[1] + "]")
			var_init.append("summon minecraft:armor_stand 0 15 0 {Marker:1,Invulnerable:1,NoGravity:1,CustomNameVisible:1,CustomName:}" + split[1] + "}")
		i+=1
	function_names.append("var_init")
	functions.append(var_init)
	return function_names, functions
