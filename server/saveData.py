import socket,threading,sys,time,json,os.path
s = socket.socket()
host = "0.0.0.0"
port = 4402
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
s.bind((host,port))

s.listen(5)


clients_data = "clients_data.dat"

def make_file():
    if os.path.isfile(clients_data):
        pass
    else:
        #not exist so create
        with open(clients_data,"wb") as fa: #'w' to empty
            pass

make_file()


def WriteData(conn):
        data = conn.recv(512)
        loaded_data = json.loads(data)
        try:
            username = loaded_data[0]
            full_name = loaded_data[1]
            email_address = loaded_data[2]
            to_write = username+" - "+full_name+" - "+email_address+"\n"
            #not necessary right now
            #might be useful later
            with open(clients_data,"a") as f:
                f.write(to_write)
        except:
            pass


shutdown = False
print "SaveData - Public"
while not shutdown:
	conn,addr = s.accept()
	threading.Thread(target=WriteData,args=(conn,)).start()

s.close()
