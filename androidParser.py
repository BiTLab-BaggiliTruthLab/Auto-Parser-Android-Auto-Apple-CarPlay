import os,tarfile,sys

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
					members[index].name = os.path.basename(members[index].name)
					tar.extract(members[index], path='./Android')
	tar.close()

def android(file,user_list=None):
	extract(file,user_list)


