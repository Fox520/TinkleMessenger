import hashlib,os,socket,threading,json, traceback

s = socket.socket()
host = "0.0.0.0"
port = 4405
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
s.bind((host,port))
s.listen(5)

WEB_ADDR = "http://127.0.0.1/"

AUDIO_FOLDER = "aud"
DOCUMENTS_FOLDER = "docs"
IMAGES_FOLDER = "img"

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def files_in_dir(directory):
    return os.listdir(directory)


def handleRequest(conn):
    try:
        #decode
        template = {}
        #print("first")
        data = json.loads(conn.recv(1024))
        media_type = data["media_type"]
        hash_request = data["hash"]
        HASH_FOUND = False
        #print("random")
        if media_type == "audio":
            ff = AUDIO_FOLDER
        elif media_type == "document":
            ff = DOCUMENTS_FOLDER
        elif media_type == "image":
            ff = IMAGES_FOLDER
        files =files_in_dir(ff)
        for fname in files:
            if md5(os.path.join(ff,fname)) == hash_request:
                HASH_FOUND = True
                template["file_path"] = WEB_ADDR+ff+"/"+fname
                #print(template["file_path"])
                break;

    
        template["type"] = "hash_request"
        template["result"] = HASH_FOUND
        #print("Found hash?",HASH_FOUND)
        conn.send(json.dumps(template))


    except:
        print(traceback.format_exc())


shutdown = False
print "FileControl - Public"
while not shutdown:
	conn,addr = s.accept()
	threading.Thread(target=handleRequest,args=(conn,)).start()
