# -*- coding: utf-8 -*-
import sqlite3,socket,json,threading,urllib
##########################
{
	"name":"",
	"password":""
}
web_file = "web_file"
def get_web_addrress():
	with open(web_file,"r") as f:
		return f.read()
WEB_ADDR = get_web_addrress()
s = socket.socket()
host = "0.0.0.0"
port = 4403
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
s.bind((host,port))
s.listen(5)
###########################
db = sqlite3.connect("users.db")
conn = db.cursor()
conn.execute('''CREATE TABLE IF NOT EXISTS users
             (first_name varchar(20) NOT NULL,
              password varchar(20) NOT NULL)''')
db.commit()
db.close()
###########################
def create_user(db,conn,name, pwd):

	try:
		conn.execute('INSERT INTO users(first_name, password) VALUES (?,?)', (str(name),str(pwd)))
		db.commit()
		return True
	except Exception as e:
		print "Error creating user:",e
		return False

def login(conn,name,pwd):
	find_user = ('SELECT * FROM users WHERE first_name=? AND password=?')
	conn.execute(find_user,(str(name),str(pwd)))
	result = conn.fetchall()
	if result:
		#print "user logged in"
		return True
	else:
		#print "not logged in"
		return False
def register(db,conn,name,pwd):
	test_result = check_if_name_exists(db,conn,name)
	if test_result == False:
		find_user = ('SELECT * FROM users WHERE first_name=? AND password=?')
		conn.execute(find_user,(str(name),str(pwd)))
		result = conn.fetchall()
		if result:
			#print "not register"
			return False
		else:
			create_user(db,conn,str(name),str(pwd))
			#print "register"
			return True
	else:
		return False

def check_if_name_exists(db,conn,name):
	aa = (str(name),)
	conn.execute('SELECT * FROM users WHERE first_name=? COLLATE NOCASE',aa)
	result = conn.fetchall()
	if result:#name is in
		return True
	else:#name not in
		return False

def create_image(name):
	urllib.urlopen(WEB_ADDR + "internal_dp.php?username="+name)
def initial(cli):
	db = sqlite3.connect("users.db")
	conn = db.cursor()
	temp_data = cli.recv(1024)
	data = json.loads(temp_data)
	if data["type"] == "login":
		name = data["name"]
		password = data["password"]
		result = login(conn,name, password)
		temp = {"type":"login","state":""}
		if result:
			temp["state"] = "success"
			temp["prof_link"] = WEB_ADDR + "display/"+name + ".png"
		else:
			temp["state"] = "fail"
		cli.send(json.dumps(temp))
		db.commit()
		db.close()
	elif data["type"] == "register":
		name = data["name"]
		password = data["password"]
		result = register(db,conn,name, password)
		temp = {"type":"register","state":""}
		if result:
			temp["state"] = "success"
			create_image(name)
			temp["prof_link"] = WEB_ADDR + "display/"+name+".png"
		else:
			temp["state"] = "fail"
		cli.send(json.dumps(temp))
		db.commit()
		db.close()
	#cli.close()

shutdown = False
print "GetName - Public"
while not shutdown:
	cli,addr = s.accept()
	t1 = threading.Thread(target=initial,args=(cli,)).start()
# if login("John","1111111111"):
# 	print "user is logged in and can proceed"
# else:
# 	register("John","1111111111")


