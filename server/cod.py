import socket,threading,json,dataset
s = socket.socket()
host = "0.0.0.0"
port = 4400
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
s.bind((host,port))
s.listen(5)


def Handle(conn):
    try:
        data_temp1 = json.loads(conn.recv(512))
        db = dataset.connect('sqlite:///conditions1.db')
        table = db['conditions']
        blob = dict(name=data_temp1["from"],last_seen=data_temp1["ls"],key=data_temp1["key"])

        table.insert_ignore(blob,["name"])
        data_temp1 = ""
        while True:
            data_temp = json.loads(conn.recv(512))
            if data_temp["type"] == "get_conditions":
                #print "is get conditions"
                #print data_temp
                try:

                    oka = data_temp["user_fetch"]
                    aa = db["conditions"].find_one(name=oka)["last_seen"]
                    #bb = db["conditions"].find_one(name=oka)["typing"]
                except Exception as e:
                    print e
                    aa = "last seen"
                    #bb = ""
                template = {
                        "type":"conditions",
                        "ls":aa
                        }
                conn.send(json.dumps(template))

            elif data_temp["type"] == "set_last_seen":
                #print "setting last seen"
                client = data_temp["from"]
                test_key = data_temp["key"]
                if db["conditions"].find_one(name=client)["key"] == test_key:
                    old_data = dict(name=client,last_seen=data_temp["ls"])
                    table.update(old_data,["name"])
                
                
    except Exception as e:
        pass
        


shutdown = False
print "Conditions - Public"
while not shutdown:
    conn,addr = s.accept()
    t1 = threading.Thread(target=Handle,args=(conn,)).start()

s.close()
