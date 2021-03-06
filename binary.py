import re,glob
pb = glob.glob('./Android/Voice/*.binarypb')
out_arr = {}
for file in pb:
	with open(file, "rb") as f:
	    data = f.read()

	matches = []                # initializes the list for the matches
	curpos = 0                  # current search position (starts at beginning)
	pattern = re.compile(b'(?<=BNDL\x03\x00\x00\x00\x18\x00\x00\x00v\x00e\x00l\x00v\x00e\x00t\x00:\x00q\x00u\x00e\x00r\x00y\x00_\x00s\x00t\x00a\x00t\x00e\x00:\x00q\x00u\x00e\x00r\x00y\x00\x00\x00\x00\x00\x04\x00\x00\x00/\x00\x00\x00c\x00o\x00m\x00.\x00g\x00o\x00o\x00g\x00l\x00e\x00.\x00a\x00n\x00d\x00r\x00o\x00i\x00d\x00.\x00a\x00p\x00p\x00s\x00.\x00g\x00s\x00a\x00.\x00s\x00h\x00a\x00r\x00e\x00d\x00.\x00s\x00e\x00a\x00r\x00c\x00h\x00.\x00Q\x00u\x00e\x00r\x00y)(.*)(?=\x72\x00\x65\x00\x63\x00\x6F\x00\x67\x00\x6E\x00\x69\x00\x7A\x00\x65\x00\x72\x00\x4C\x00\x61\x00\x6E\x00\x67\x00\x75\x00\x61\x00\x67\x00\x65\x00\x00\x00\x00\x00\x05\x00\x00\x00\x65\x00\x6E\x00\x2D\x00\x75\x00\x73)')   # the pattern to search
	while True:
	    m = pattern.search(data[curpos:])     # search next occurence
	    if m is None: break                   # no more could be found: exit loop
	    matches.append(m.group(0))#curpos + m.start()) # append a pair (pos, string) to matches
	    curpos += m.end()          # next search will start after the end of found string


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
			print(len(cmd))
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
				
for i in out_arr:
	print(i)
	for j in out_arr[i]:
		print("\t"+j)
