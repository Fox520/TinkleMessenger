import sqlite3,socket,json,threading,os,requests
from PIL import Image, ImageOps, ImageDraw
s = socket.socket()
host = "0.0.0.0"
port = 4401
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
s.bind((host,port))
s.listen(5)
###########################
web_file = "web_file"
def get_web_addrress():
	with open(web_file,"r") as f:
		return f.read()
WEB_ADDRESS = get_web_addrress() + "man_display.php"
def does_exist(conn,name, password):
	find_user = ('SELECT * FROM users WHERE first_name=? AND password=?')
	conn.execute(find_user,(str(name),str(password)))
	result = conn.fetchall()
	if result:
		#print "user logged in"
		return True
	else:
		#print "not logged in"
		return False
def download_file(url,fname):
	ext = ""
	if os.path.splitext(url)[0] == ".png":
		ext = ".png"
	else:
		ext = ".jpg"
	local_filename = fname + ext
	# NOTE the stream=True parameter
	r = requests.get(url, stream=True)
	with open(local_filename, 'wb') as f:
		for chunk in r.iter_content(chunk_size=1024): 
			if chunk: # filter out keep-alive new chunks
				f.write(chunk)
				#f.flush() commented by recommendation from J.F.Sebastian
	return local_filename
def do_manipulation(image_link,the_name,original_link):
	is_active = False
	filename = download_file(original_link,the_name)
	if os.path.splitext(filename)[1] == ".png":
		reduce_image_size(filename)
		make_image_round_thumb(filename)
		upload_new_image(filename)
		image_name = filename
		os.remove(image_name)
		is_active = True
	elif os.path.splitext(filename)[1] == ".jpg":
		new_name = do_manipulation_image(filename)
		upload_new_image(new_name)
		image_name = new_name
		os.remove(image_name)
		is_active = True

	do_delete(filename)

	if is_active:
		image_link = WEB_ADDRESS+"display/"+image_name
		return image_link
	elif is_active == False:
		image_link = WEB_ADDRESS+"display/default.png"
		return image_link
def upload_new_image(new_name):
	#print "uploading",new_name
	with open(new_name,"rb") as f:
		files = {'testname': f}
		r = requests.post(WEB_ADDRESS,files=files)

def do_delete(ff):
	try:
		os.remove(ff)
	except Exception as e:
		pass

def reduce_image_size(fname):
	im = Image.open(fname)
	im = im.resize((383,383),Image.ANTIALIAS)
	im.save(fname, quality=95, optimize=True)

def do_manipulation_image(filename):#return new link
	im = Image.open(filename)
	temp_new_name = os.path.splitext(filename)[0]+".png"
	im.save(temp_new_name)
	reduce_image_size(temp_new_name)
	make_image_round_thumb(temp_new_name)
	return temp_new_name
def make_image_round_thumb(fname):
	im = Image.open(fname)
	bigsize = (im.size[0] * 3, im.size[1] * 3)
	mask = Image.new('L', bigsize, 0)
	draw = ImageDraw.Draw(mask) 
	draw.ellipse((0, 0) + bigsize, fill=255)
	mask = mask.resize(im.size, Image.ANTIALIAS)
	im.putalpha(mask)
	im.save(fname)
def initial(cli):
	db = sqlite3.connect("users.db")
	conn = db.cursor()
	temp_data = cli.recv(1024).decode("utf-8")
	data = json.loads(temp_data)
	if data["type"] == "update_pic":
		name = data["name"]
		password = data["password"]
		result = does_exist(conn,name, password)
		temp = {"type":"update_pic","update_reply":""}
		if result:
			temp["update_reply"] = "success"
			new_link = do_manipulation(data["link"],name,data["original_link"])
			temp["new_link"] = new_link

		else:
			temp["update_reply"] = "fail"
		cli.send(bytes(json.dumps(temp),"utf-8"))
	cli.close()

shutdown = False
print("Handle Pics - Public")
while not shutdown:
	cli,addr = s.accept()
	t1 = threading.Thread(target=initial,args=(cli,)).start()