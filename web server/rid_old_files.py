import time, os, stat

def file_age_in_seconds(pathname):
	return time.time() - os.stat(pathname)[stat.ST_MTIME]

dirs = ["img","aud","status","docs"]
dont_touch = ["default.png","cat.jpg"]
special_directory = "display"
def do_checks():
	for directory in dirs:

		for f in os.listdir(directory):
			fullpath = os.path.join(directory,f)
			if f not in dont_touch:
				kk = file_age_in_seconds(fullpath)
				if kk >= 864000:#10 days
					try:
						os.remove(fullpath)
					except:
						pass
	for f in os.listdir(special_directory):
		try:
			ext = os.path.splitext(f)[1]
			# jpg are leftover after conversion to png
			if ext == ".jpg":
				os.remove(os.path.join(special_directory,f))
		except:
			pass

while True:
	do_checks()
	time.sleep(86400)#1 day
	