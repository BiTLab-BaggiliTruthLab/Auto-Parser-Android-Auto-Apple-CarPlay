import speech_recognition as sr
import os,pathlib,sys,glob,datetime
import plistlib,sqlite3,tarfile
from columnar import columnar
import pandas as pd 
from IPython.display import HTML,display
import itertools
import hashlib
from shutil import copyfile

timestamp = ""
case = ""
foldername = ""
examiner = ""
md5 = ""
sha256 = ""
check_md5 = ""
check_sha256 = ""

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
						tar.extract(members[index], path='./{}/Settings'.format(foldername))
					elif path.parent.name in ('Assistant','audio','PhotoAlbumNameType'):
						tar.extract(members[index], path='./{}/Voice'.format(foldername))
					elif path.parent.name in ('CallHistoryDB'):
						tar.extract(members[index], path='./{}/Call_History'.format(foldername))
					elif path.parent.name in ('SMS'):
						tar.extract(members[index], path='./{}/SMS'.format(foldername))
					else:
						tar.extract(members[index], path='./{}/Other'.format(foldername))
	tar.close()

def voice_commands():
	wav = glob.glob('./{}/Voice/*.wav'.format(foldername))
	r = sr.Recognizer()
	print("No Siri audio file found.") if not wav else print("Siri Commands:")
	
	cmds = {'timestamp':[],'command':[]}
	for file in wav:
		exif = pathlib.Path(file).stat()
		ctime = datetime.datetime.utcfromtimestamp(exif.st_ctime)
		with sr.AudioFile(file) as source:
		    audio_data = r.record(source)
		    try:
		    	text = r.recognize_google(audio_data)
		    except:
		    	print("Not connected to internet.")
		    	return
		    cmds['timestamp'].append(str(ctime) + " UTC")
		    cmds['command'].append(text)
		   
	headers = list(cmds.keys())
	data = list(cmds.values())
	tab_row = []
	for i in range(len(data[0])):
		tab_row.append([data[0][i],data[1][i]])
	table = columnar(tab_row, headers)
	print(table)
	return cmds

def pl_open(file):
	with open(file, 'rb') as fp:
			cp = plistlib.load(fp)
	return cp

def carplay_pairings():
	print('CarPlay Pairings:\n')
	try:
		cp = pl_open('./{}/Settings/com.apple.carplay.plist'.format(foldername))
	except:
		print("./{}/Settings/com.apple.carplay.plist not found.".format(foldername))
		return

	pairing = cp['pairings'].keys()
	label,name,apps = [],[],[]
	for pair in pairing:
		try:
			pl = pl_open("./{}/Settings/".format(foldername)+ pair + "-CarDisplayDesiredIconState.plist")
			label.append(pl['metadata']['OEMIconLabel'])
			name.append(cp['pairings'][pair]['name'])
			apps.append(pl['iconLists'])
		except:
			print("./{}/Settings/".format(foldername)+ pair + "-CarDisplayIconState.plist not found.")

	if not label:
		return	

	app = []
	for j in range(len(apps)):
		app.append(list(itertools.chain.from_iterable(apps[j])))
	

	pairing = {'Paired To':[], 'Apps':app}
	for i in range(len(label)):
		if label[i].lower() == name[i].lower():
			pairing['Paired To'].append(label[i])
		else:
			pairing['Paired To'].append(label[i]+" "+name[i])

	headers = pairing['Paired To']
	data = pairing['Apps']
	diff = abs(len(data[0]) - len(data[1]))
	if len(data[0]) < len(data[1]):
		for k in range(diff):
			data[0].append("")
	elif len(data[0]) > len(data[1]):
		for k in range(diff):
			data[1].append("")
	else:
		pass

	tab_row = []
	for i in range(len(data[0])):
		tab_row.append([data[0][i],data[1][i]])
	table = columnar(tab_row, headers)
	print(table)
	return pairing


def call_history():
	print("Phone Call History:\n")
	path = "./{}/Call_History/CallHistory.storedata".format(foldername)
	if not os.path.exists(path):
		print("./{}/Call_History/CallHistory.storedata not found.".format(foldername))
		return

	try:
		connection = sqlite3.connect("./{}/Call_History/CallHistory.storedata".format(foldername))
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
		return calls
	except:
		print("Error with ./{}/Call_History/CallHistory.storedata".format(foldername))


def sms_history():
	print("SMS History:\n")
	path = "./{}/SMS/sms.db".format(foldername)
	if not os.path.exists(path):
		print("./{}/SMS/sms.db not found.".format(foldername))
		return
	try:
		connection = sqlite3.connect("./{}/SMS/sms.db".format(foldername))
		connection.text_factory = str
		cursor = connection.cursor()
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
		return sms
	except:
		print("Error with ./{}/SMS/sms.db".format(foldername))

def report(cmds,pair,call,sms):
	copyfile('./style.css', './{}/style.css'.format(foldername))
	f = open("./{}/report.html".format(foldername),"w")
	f.write("<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>repl.it</title>\
		     <link href='style.css' rel='stylesheet' type='text/css' /></head><body><h1>Apple Carplay Forensics Report</h1>\
		     <div style='margin-left:auto;margin-right:auto;width:800px;height:250px;border:2px solid #000;'><h3>\
		     Filename: {}<br>Case: {}<br>Timestamp: {}<br>Examiner: {}<br>Before Analysis:<br>MD5: {}<br>SHA256: {}<br>After Analysis:<br>MD5: {}<br>SHA256: {}</h3></div>".format(foldername,case,timestamp,examiner,md5,sha256,check_md5,check_sha256))
	if not cmds:
		pass
	else:
		f.write("<h2>Recent Siri Voice Commands</h2>\n")
		df3 = pd.DataFrame(cmds)
		df3 = df3.style.set_properties(**{'text-align': 'center'},**{'width': '60px'}).set_table_attributes('class="center"').hide_index().render(uuid='t03')
		df3 = df3.replace("T_t03","t03")
		f.write(df3)

	f.write("<h2>Carplay Pairings</h2>\n")
	df4 = pd.DataFrame(pair)
	df4 = df4.style.set_properties(**{'text-align': 'left'},**{'width': '60px'}).set_table_attributes('class="center"').hide_index().render(uuid='t04')
	df4 = df4.replace("T_t04","t04")
	f.write(df4)
	f.write("<h2>Recent SMS</h2>\n")
	df2 = pd.DataFrame(sms)
	df2 = df2.style.set_properties(**{'text-align': 'left'},**{'width': '60px'}).set_table_attributes('class="center"').hide_index().render(uuid='t02')
	df2 = df2.replace("T_t02","t02")
	f.write(df2)
	f.write("<h2>Recent Phone Calls</h2>\n")
	df1 = pd.DataFrame(call)
	df1 = df1.style.set_properties(**{'text-align': 'center'},**{'width': '60px'}).set_table_attributes('class="center"').hide_index().render(uuid='t01')
	df1 = df1.replace("T_t01","t01")
	f.write(df1)
	f.write("</body></html>")
	f.close()


def report2():
	f = open("./{}/report.html".format(foldername),"w")
	f.write("<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>repl.it</title>\
		     <link href='style.css' rel='stylesheet' type='text/css' /></head><body><h1>Apple Carplay Forensics Report</h1>\
		     <div style='margin-left:auto;margin-right:auto;width:800px;height:200px;border:2px solid #000;'><h3>\
		     Filename: {}<br>Case: {}<br>Timestamp: {}<br>Examiner: {}<br>Before Analysis:<br>MD5: {}<br>SHA256: {}<br>After Analysis:<br>MD5: {}<br>SHA256: {}</h3></div>".format(foldername,case,timestamp,examiner,md5,sha256,check_md5,check_sha256))

def setup(file):
	global case,examiner,md5,sha256,foldername,timestamp
	timestamp = datetime.datetime.utcnow().strftime("%m/%d/%Y-%H:%M:%S UTC")
	case = input("Enter case #:")
	foldername = case+"-Apple"
	exmainer = input("Enter examiner name:")
	md5 = hashlib.md5(open(file,'rb').read()).hexdigest()
	print("MD5:",md5)
	sha256 = hashlib.sha256(open(file,'rb').read()).hexdigest()
	print("SHA256:",sha256)

def hash_check(file):
	global check_md5,check_sha256
	print("After Analysis:")
	check_md5 = hashlib.md5(open(file,'rb').read()).hexdigest()
	if md5 == check_md5:
		print("MD5:",check_md5,": Matched") 
		check_md5 += " : Matched"
	else: 
		print("MD5:",check_md5,": Not Matched") 
		check_md5 += " : Not Matched"
	
	check_sha256 = hashlib.sha256(open(file,'rb').read()).hexdigest()
	if sha256 == check_sha256:
		print("SHA256:",check_sha256,": Matched") 
		check_sha256 += " : Matched"
	else:
		print("SHA256:",check_sha256,": Not Matched")
		check_sha256 += " : Not Matched"


def apple(file,user_list=None):
	if user_list == None:
		setup(file)
		extract(file,user_list)
		cmds = voice_commands()
		pair = carplay_pairings()
		call = call_history()
		sms = sms_history()	
		hash_check(file)
		report(cmds,pair,call,sms)
	else:
		setup(file)
		extract(file,user_list)
		hash_check(file)
		report2()


