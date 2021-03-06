import os,tarfile,sys,datetime,pathlib,glob,re
import xmltodict,sqlite3
from columnar import columnar

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
	print('Android Auto:\n')
	try:
		xml = xml_open('./{}/Settings/app_state_shared_preferences.xml'.format(foldername))
	except:
		print("./{}/Settings/app_state_shared_preferences.xml not found".format(foldername))
		return

	auto = {'Last_run':[]}
	epoch = int(xml['map']['long']['@value'])
	auto['Last_run'].append(datetime.datetime.utcfromtimestamp(epoch/1000).strftime("%m/%d/%Y %H:%M:%S UTC"))
	
	headers = auto.keys()
	data = auto['Last_run']
	tab_row = []
	for i in range(len(data)):
		tab_row.append([data[i]])
	table = columnar(tab_row, headers)
	print(table)
	return auto

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
		for i in rows:
			sms['timestamp'].append(i[0]+" UTC")
			sms['number'].append(i[1])
			sms['text'].append(i[3])
			if i[2] == 1:
				sms['origin'].append("Sent")
			else:
				sms['origin'].append("Received")
		
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
		rows = cursor.execute("SELECT datetime(date/1000,'unixepoch'),datetime(date/1000+duration,'unixepoch'),logtype,number FROM calls").fetchall()
		rows = rows[::-1]
		calls = {'timestamp_duration':[],'number':[]}
		for i in rows:
			if i[2] == 100:
				calls['timestamp_duration'].append(i[0]+" - "+i[1]+" UTC")
				calls['number'].append(i[3])
		
		headers = list(calls.keys())
		data = list(calls.values())
		tab_row = []
		for i in range(len(data[0])):
			tab_row.append([data[0][i],data[1][i]])
		table = columnar(tab_row, headers)
		print(table)
		return calls

	except:
		print("Error with ./{}/Comm/calllog.db".format(foldername))

def voice_commands():
	print("Android Assistant")
	pb = glob.glob('./{}/Voice/*.binarypb'.format(foldername))
	out_arr = {}
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

					
	headers = list(out_arr.keys())
	data = list(out_arr.values())
	tab_row = []
	for i in range(len(headers)):
		tab_row.append([headers[i],str.join("\n",data[i])])
		#print(str.join("\n",data[i]))
	table = columnar(tab_row,)
	print(table)
	return out_arr

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
	foldername = "Android"#case+"Apple"
	exmainer = input("Enter examiner name:")
	md5 = "9fe5cfd3a3b7b89cd91b421112d4d86b"#hashlib.md5(open(file,'rb').read()).hexdigest()
	print("MD5:",md5)
	sha256 = "df73ffd582c3121630531feeabadf2ce29315ba42c7791646bf47c8ff20cb071"#hashlib.sha256(open(file,'rb').read()).hexdigest()
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
	setup(file)
	#extract(file,user_list)
	#sett = aauto()
	#voice = voice_commands()
	#call = call_history()
	#sms = sms_history()
	#report()
