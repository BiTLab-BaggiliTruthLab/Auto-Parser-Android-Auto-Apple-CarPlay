import speech_recognition as sr
import os,tarfile,sys,glob,datetime
import pathlib
import plistlib

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
					else:
						tar.extract(members[index], path='./Apple/Other')

	tar.close()

def voice_commands():
	wav = glob.glob('./Apple/Voice/*.wav')

	r = sr.Recognizer()

	print("Siri Commands:")
	for file in wav:
		exif = pathlib.Path(file).stat()
		ctime = datetime.datetime.fromtimestamp(exif.st_ctime)
		with sr.AudioFile(file) as source:
		    audio_data = r.record(source)
		    text = r.recognize_google(audio_data)
		    print(ctime,"\t",text)
	print("\n")

def pl_open(file):
	with open(file, 'rb') as fp:
		cp = plistlib.load(fp)
	return cp

def carplay_pairings():
	print('CarPlay Pairings:\n')

	cp = pl_open('./Apple/Settings/com.apple.carplay.plist')

	pairing = cp['pairings'].keys()
	label,name = [],[]
	for pair in pairing:
		pl = pl_open("./Apple/Settings/"+ pair + "-CarDisplayIconState.plist")
		label.append(pl['metadata']['OEMIconLabel'])
		name.append(cp['pairings'][pair]['name'])

	for i in range(len(label)):
		if label[i].lower() == name[i].lower():
			print("\t"+label[i])
		else:
			print("\t"+label[i],name[i])

def apple(file,user_list=None):
	extract(file,user_list)
	voice_commands()
	carplay_pairings()



