import os,tarfile,sys,datetime,pathlib,glob,re
import xmltodict,sqlite3
from columnar import columnar
from shutil import copyfile
import pandas as pd
import hashlib

timestamp = ""
case = ""
foldername = ""
examiner = ""
md5 = ""
sha256 = ""
check_md5 = ""
check_sha256 = ""

def xml_open(file):
	with open(file,"r") as fp:
		dc = xmltodict.parse(fp.read())
	return dc

def extract(file,user_list=None):
	wordlist = []
	if user_list == None:
		try:
			with open('Default_lists/android_default_list.txt') as my_file:
				for line in my_file:
					wordlist.append(line[:-1])
		except FileNotFoundError:
			print("android_default_list.txt not found")
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
					if path.parent.name in ('app_session'):
						tar.extract(members[index], path='./{}/Voice'.format(foldername))
					elif path.parent.name in ('shared_prefs'):
						tar.extract(members[index], path='./{}/Settings'.format(foldername))
					elif path.parent.name in ('databases'):
						tar.extract(members[index], path='./{}/Comm'.format(foldername))
					else:
						tar.extract(members[index], path='./{}/Other'.format(foldername))
	tar.close()

def aauto():
	print("Android Auto:\n")
	path = "./{}/Comm/carservicedata.db".format(foldername)
	if not os.path.exists(path):
		print("./{}/Comm/carservicedata.db not found.".format(foldername))
		return

	try:
		connection = sqlite3.connect("./{}/Comm/carservicedata.db".format(foldername))
		connection.text_factory = str
		cursor = connection.cursor()
		rows = cursor.execute("SELECT manufacturer,datetime(connectiontime/1000,'unixepoch'),vehicleid,bluetoothaddress FROM allowedcars").fetchall()
		rows = rows[::-1]
		aauto = {'manufacturer':[],'vehicle id':[],'last connection':[],'bluetooth address':[]}
		for i in rows:
			aauto['manufacturer'].append(i[0])
			aauto['last connection'].append(i[1]+" UTC")
			aauto['vehicle id'].append(i[2])
			aauto['bluetooth address'].append(i[3])
			

		headers = list(aauto.keys())
		data = list(aauto.values())
		tab_row = []
		for i in range(len(data[0])):
			tab_row.append([data[0][i],data[1][i],data[2][i],data[3][i]])
		table = columnar(tab_row, headers)
		print(table)
		return aauto

	except:
		print("Error with ./{}/Comm/carservicedata.db".format(foldername))

def contacts():
	print("Contacts:\n")
	path = "./{}/Comm/contacts2.db".format(foldername)
	if not os.path.exists(path):
		print("./{}/Comm/contacts2.db not found.".format(foldername))
		return

	try:
		connection = sqlite3.connect("./{}/Comm/contacts2.db".format(foldername))
		connection.text_factory = str
		cursor = connection.cursor()
		rows = cursor.execute("SELECT M.data1 As Name, N.data1 As Number from data As M inner join data As N where (M.raw_contact_id=N.raw_contact_id and M.mimetype_id=7 and N.mimetype_id=5)").fetchall()
		rows = rows[::-1]
		cont = {'Name':[],'Number':[]}
		for i in rows:
			cont['Name'].append(i[0])
			cont['Number'].append(i[1])

		headers = list(cont.keys())
		data = list(cont.values())
		tab_row = []
		for i in range(len(data[0])):
			tab_row.append([data[0][i],data[1][i]])
		table = columnar(tab_row, headers)
		print(table)
		return cont

	except:
		print("Error with ./{}/Comm/contacts2.db".format(foldername))

def sms_history():
	print("SMS History:\n")
	path = "./{}/Comm/mmssms.db".format(foldername)
	if not os.path.exists(path):
		print("./{}/Comm/mmssms.db not found.".format(foldername))
		return

	try:
		connection = sqlite3.connect("./{}/Comm/mmssms.db".format(foldername))
		connection.text_factory = str
		cursor = connection.cursor()
		rows = cursor.execute("SELECT datetime(date/1000,'unixepoch'),address,type,body FROM sms").fetchall()
		rows = rows[::-1]
		sms = {'timestamp':[],'number':[],'origin':[],'text':[]}
		types = {1:'Received',2:'Sent',5:'Failed to send'}
		for i in rows:
			sms['timestamp'].append(i[0]+" UTC")
			sms['number'].append(i[1])
			sms['text'].append(i[3])
			sms['origin'].append(types[i[2]])
		
		headers = list(sms.keys())
		data = list(sms.values())
		tab_row = []
		for i in range(len(data[0])):
			tab_row.append([data[0][i],data[1][i],data[2][i],data[3][i]])
		table = columnar(tab_row, headers)
		print(table)
		return sms

	except:
		print("Error with ./{}/Comm/mmssms.db".format(foldername))

def call_history():
	print("Phone Call History:\n")
	path = "./{}/Comm/calllog.db".format(foldername)
	if not os.path.exists(path):
		print("./{}/Comm/calllog.db not found.".format(foldername))
		return

	try:
		connection = sqlite3.connect("./{}/Comm/calllog.db".format(foldername))
		connection.text_factory = str
		cursor = connection.cursor()
		rows = cursor.execute("SELECT datetime(date/1000,'unixepoch'),datetime(date/1000+duration,'unixepoch'),number,name,type FROM calls WHERE logtype == 100 ").fetchall()
		rows = rows[::-1]
		calls = {'timestamp_duration':[],'type':[],'contact':[],'number':[]}
		types = {1:'Incoming',2:'Outgoing',3:'Missed',5:'Rejected'}
		for i in rows:
			calls['timestamp_duration'].append(i[0]+" - "+i[1]+" UTC")
			calls['number'].append(i[2])
			calls['contact'].append(i[3])
			calls['type'].append(types[i[4]])
		
		headers = list(calls.keys())
		data = list(calls.values())
		tab_row = []
		for i in range(len(data[0])):
			tab_row.append([data[0][i],data[1][i],data[2][i],data[3][i]])
		table = columnar(tab_row, headers)
		print(table)
		return calls

	except:
		print("Error with ./{}/Comm/calllog.db".format(foldername))

def voice_commands():
	print("Android Assistant")
	pb = glob.glob('./{}/Voice/*.binarypb'.format(foldername))
	out_arr = {}
	incars = []
	for file in pb:
		with open(file, "rb") as f:
		    data = f.read()

		matches = []
		curpos = 0
		pattern = re.compile(b'(?<=BNDL\x03\x00\x00\x00\x18\x00\x00\x00v\x00e\x00l\x00v\x00e\x00t\x00:\x00q\x00u\x00e\x00r\x00y\x00_\x00s\x00t\x00a\x00t\x00e\x00:\x00q\x00u\x00e\x00r\x00y\x00\x00\x00\x00\x00\x04\x00\x00\x00/\x00\x00\x00c\x00o\x00m\x00.\x00g\x00o\x00o\x00g\x00l\x00e\x00.\x00a\x00n\x00d\x00r\x00o\x00i\x00d\x00.\x00a\x00p\x00p\x00s\x00.\x00g\x00s\x00a\x00.\x00s\x00h\x00a\x00r\x00e\x00d\x00.\x00s\x00e\x00a\x00r\x00c\x00h\x00.\x00Q\x00u\x00e\x00r\x00y)(.*)(?=\x72\x00\x65\x00\x63\x00\x6F\x00\x67\x00\x6E\x00\x69\x00\x7A\x00\x65\x00\x72\x00\x4C\x00\x61\x00\x6E\x00\x67\x00\x75\x00\x61\x00\x67\x00\x65\x00\x00\x00\x00\x00\x05\x00\x00\x00\x65\x00\x6E\x00\x2D\x00\x75\x00\x73)')   # the pattern to search
		while True:
		    m = pattern.search(data[curpos:])
		    if m is None: break
		    matches.append(m.group(0))#curpos + m.start())
		    curpos += m.end()

		if len(matches) != 0:
			if data[16:29] == b'car_assistant':
				incars.append('Yes')
			else:
				incars.append('No')

		for i in matches:
			s = ""
			for j in i:
				if int(j) > 127:
					pass
				else:
					s += chr(j)
			
			cmd = s[26:-8].replace('\x00','')
			if len(cmd) > 200:
				ind1 = cmd.find("recognizerLanguage")
				if file[17:] in out_arr:
				  out_arr[file[17:]].append(cmd[:ind1-2])
				else:
				  out_arr.update({file[17:]:[]})
				  out_arr[file[17:]].append(cmd[:ind1-2])

			else:

				if file[17:] in out_arr:
				  out_arr[file[17:]].append(cmd)
				else:
				  out_arr.update({file[17:]:[]})
				  out_arr[file[17:]].append(cmd)
	cmds = {'File':[],'User_commands':[],'In Car':incars}				
	headers = list(out_arr.keys())
	data = list(out_arr.values())
	tab_row = []
	for i in range(len(headers)):
		tab_row.append([headers[i],str.join("\n",data[i]),incars[i]])
		cmds['File'].append(headers[i])
		cmds['User_commands'].append(data[i])
	table = columnar(tab_row,cmds.keys())
	print(table)
	return cmds

def report(voice,sett,cont,call,sms):
	copyfile('./style.css', './{}/style.css'.format(foldername))
	f = open("./{}/report.html".format(foldername),"w")
	f.write("<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>Android Auto</title>\
		     <link href='style.css' rel='stylesheet' type='text/css' /></head><body><h1>Android Auto Forensics Report</h1>\
		     <div style='margin-left:auto;margin-right:auto;width:800px;height:250px;border:2px solid #000;'><h3>\
		     Filename: {}<br>Case: {}<br>Timestamp: {}<br>Examiner: {}<br>Before Analysis:<br>MD5: {}<br>SHA256: {}<br>After Analysis:<br>MD5: {}<br>SHA256: {}</h3></div>".format(foldername,case,timestamp,examiner,md5,sha256,check_md5,check_sha256))
	
	if not voice:
		pass
	else:
		f.write("<h2>Recent Android Assistant Voice Commands</h2>\n")
		df1 = pd.DataFrame(voice)
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'width': '60px'}).set_table_attributes('class="center"').hide_index().render(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not sett:
		pass
	else:
		f.write("<h2>Android Auto</h2>\n")
		df2 = pd.DataFrame(sett)
		df2 = df2.style.set_properties(**{'text-align': 'left'},**{'width': '60px'}).set_table_attributes('class="center"').hide_index().render(uuid='t04')
		df2 = df2.replace("T_t04","t04")
		f.write(df2)

	if not cont:
		pass
	else:
		f.write("<h2>Contacts</h2>\n")
		df3 = pd.DataFrame(cont)
		df3 = df3.style.set_properties(**{'text-align': 'left'},**{'width': '60px'}).set_table_attributes('class="center"').hide_index().render(uuid='t04')
		df3 = df3.replace("T_t04","t04")
		f.write(df3)

	if not call:
		pass
	else:
		f.write("<h2>Recent Phone Calls</h2>\n")
		df4 = pd.DataFrame(call)
		df4 = df4.style.set_properties(**{'text-align': 'center'},**{'width': '60px'}).set_table_attributes('class="center"').hide_index().render(uuid='t01')
		df4 = df4.replace("T_t01","t01")
		f.write(df4)

	if not sms:
		pass
	else:
		f.write("<h2>Recent SMS</h2>\n")
		df5 = pd.DataFrame(sms)
		df5 = df5.style.set_properties(**{'text-align': 'left'},**{'width': '60px'}).set_table_attributes('class="center"').hide_index().render(uuid='t02')
		df5 = df5.replace("T_t02","t02")
		f.write(df5)
	
	f.write("</body></html>")
	f.close()

def report2():
	copyfile('./style.css', './{}/style.css'.format(foldername))
	f = open("./{}/report.html".format(foldername),"w")
	f.write("<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>Android Auto</title>\
		     <link href='style.css' rel='stylesheet' type='text/css' /></head><body><h1>Android Auto Forensics Report</h1>\
		     <div style='margin-left:auto;margin-right:auto;width:800px;height:200px;border:2px solid #000;'><h3>\
		     Filename: {}<br>Case: {}<br>Timestamp: {}<br>Examiner: {}<br>Before Analysis:<br>MD5: {}<br>SHA256: {}<br>After Analysis:<br>MD5: {}<br>SHA256: {}</h3></div>".format(foldername,case,timestamp,examiner,md5,sha256,check_md5,check_sha256))

def setup(file):
	global case,examiner,md5,sha256,foldername,timestamp
	timestamp = datetime.datetime.utcnow().strftime("%m/%d/%Y-%H:%M:%S UTC")
	case = input("Enter case #:")
	foldername = case+"-Android"
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

def android(file,user_list=None):
	if user_list == None:
		setup(file)
		extract(file,user_list)
		voice = voice_commands()
		sett = aauto()
		cont = contacts()
		call = call_history()
		sms = sms_history()
		hash_check(file)
		report(voice,sett,cont,call,sms)
	else:
		setup(file)
		extract(file,user_list)
		hash_check(file)
		report2()
