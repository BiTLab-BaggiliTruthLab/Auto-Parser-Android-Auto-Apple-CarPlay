import speech_recognition as sr
import os,tarfile,sys,glob,datetime
import pathlib
import plistlib
import sqlite3
import textwrap
from columnar import columnar

def extract(file,user_list=None):
	wordlist = []
	if user_list == None:
		try:
			with open('Default_lists/apple_default_list.txt') as my_file:
				for line in my_file:
					wordlist.append(line[:-1])
		except FileNotFoundError:
			print("apple_default_list.txt not found")
			sys.exit()
	else:
		try:
			with open(user_list) as my_file:
				for line in my_file:
					wordlist.append(line[:-1])
		except FileNotFoundError:
			print("Specified wordlist not found")
			sys.exit()

	tar = tarfile.open(file)
	members = tar.getmembers()
	names = tar.getnames()
	
	for name in names:
		for word in wordlist:
			if word in name:
				index = names.index(name)
				if members[index].isreg():
					path = pathlib.PurePath(members[index].name)
					members[index].name = os.path.basename(members[index].name)
					if path.parent.name in ('SpringBoard','Preferences','locationd'):
						tar.extract(members[index], path='./Apple/Settings')
					elif path.parent.name in ('Assistant','audio','PhotoAlbumNameType'):
						tar.extract(members[index], path='./Apple/Voice')
					elif path.parent.name in ('CallHistoryDB'):
						tar.extract(members[index], path='./Apple/Call_History')
					elif path.parent.name in ('SMS'):
						tar.extract(members[index], path='./Apple/SMS')
					else:
						tar.extract(members[index], path='./Apple/Other')

	tar.close()

def voice_commands():
	wav = glob.glob('./Apple/Voice/*.wav')
	r = sr.Recognizer()
	print("No Siri audio file found.") if not wav else print("Siri Commands:")
	
	cmds = {'timestamp':[],'command':[]}
	for file in wav:
		exif = pathlib.Path(file).stat()
		ctime = datetime.datetime.utcfromtimestamp(exif.st_ctime)
		with sr.AudioFile(file) as source:
		    audio_data = r.record(source)
		    text = r.recognize_google(audio_data)
		    cmds['timestamp'].append(str(ctime) + " UTC")
		    cmds['command'].append(text)
		   
	headers = list(cmds.keys())
	data = list(cmds.values())
	tab_row = []
	for i in range(len(data[0])):
		tab_row.append([data[0][i],data[1][i]])
	table = columnar(tab_row, headers)
	print(table)

def pl_open(file):
	with open(file, 'rb') as fp:
			cp = plistlib.load(fp)
	return cp

def carplay_pairings():
	print('CarPlay Pairings:\n')
	try:
		cp = pl_open('./Apple/Settings/com.apple.carplay.plist')
	except:
		print("./Apple/Settings/com.apple.carplay.plist not found.")
		return

	pairing = cp['pairings'].keys()
	label,name = [],[]
	for pair in pairing:
		try:
			pl = pl_open("./Apple/Settings/"+ pair + "-CarDisplayIconState.plist")
			label.append(pl['metadata']['OEMIconLabel'])
			name.append(cp['pairings'][pair]['name'])
		except:
			print("./Apple/Settings/"+ pair + "-CarDisplayIconState.plist not found.")

	if not label:
		return	

	pairing = {'Paired To':[]}

	for i in range(len(label)):
		if label[i].lower() == name[i].lower():
			pairing['Paired To'].append(label[i])
		else:
			pairing['Paired To'].append(label[i]+" "+name[i])

	headers = list(pairing.keys())
	data = list(pairing.values())
	tab_row = []
	for i in range(len(data[0])):
		tab_row.append([data[0][i]])
	table = columnar(tab_row, headers)
	print(table)


def call_history():
	print("Phone Call History:\n")
	path = "./Apple/Call_History/CallHistory.storedata"
	if not os.path.exists(path):
		print("./Apple/Call_History/CallHistory.storedata not found.")
		return

	try:
		connection = sqlite3.connect("./Apple/Call_History/CallHistory.storedata")
		connection.text_factory = str
		cursor = connection.cursor()
		rows = cursor.execute("SELECT datetime(ZDATE + 978307200, 'unixepoch'), time(ZDATE + 978307200 + ZDURATION,'unixepoch'),ZDURATION,ZORIGINATED,ZADDRESS FROM ZCALLRECORD").fetchall()
		rows = rows[::-1]
		origin = {0:'Incoming',1:'Outgoing'}
		calls = {'timestamp_duration':[],'received':[],'origin':[],'address':[]}
		for i in rows:
			calls['timestamp_duration'].append(i[0]+" - "+i[1]+" UTC")
			calls['origin'].append(origin[i[3]])
			calls['address'].append(i[4].decode("utf-8"))
			if i[2] == 0:
				calls['received'].append("Missed Call")
			else:
				calls['received'].append("")

		headers = list(calls.keys())
		data = list(calls.values())
		tab_row = []
		for i in range(len(data[0])):
			tab_row.append([data[0][i],data[1][i],data[2][i],data[3][i]])
		table = columnar(tab_row, headers)
		print(table)
	except:
		print("Error with ./Apple/Call_History/CallHistory.storedata")


def sms_history():
	print("SMS History:\n")
	path = "./Apple/SMS/sms.db"
	if not os.path.exists(path):
		print("./Apple/SMS/sms.db not found.")
		return
	try:
		connection = sqlite3.connect("./Apple/SMS/sms.db")
		connection.text_factory = str
		cursor = connection.cursor()
		my_wrap = textwrap.TextWrapper(width = 50,subsequent_indent="\t\t\t")
		rows = cursor.execute("SELECT  datetime(date/1000000000+978307200, 'unixepoch'),datetime(date_read+978307200, 'unixepoch'),date_read,text FROM message").fetchall()
		rows = rows[::-1]
		sms = {'time_received':[],'time_read':[],'text':[]}
		for i in rows:
			sms['time_received'].append(i[0]+" UTC")
			sms['text'].append(i[3])
			if i[2] == 0:
				sms['time_read'].append("SENT")
			else:
				sms['time_read'].append(i[1]+" UTC")

		headers = list(sms.keys())
		data = list(sms.values())
		tab_row = []
		for i in range(len(data[0])):
			tab_row.append([data[0][i],data[1][i],data[2][i]])
		table = columnar(tab_row, headers)
		print(table)
	except:
		print("Error with ./Apple/SMS/sms.db")

def apple(file,user_list=None):
	extract(file,user_list)
	voice_commands()
	carplay_pairings()
	call_history()
	sms_history()



