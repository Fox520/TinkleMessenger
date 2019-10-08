# -*- coding: utf-8 -*-
# encoding=utf8 
import json
import os
import random
import socket
import string
import threading
import time
import atexit
import traceback
import sys
import dataset

import group_man


# todo: remove name from statuses,friends,conditions,users databases
# send pm:> pm,[name]:[space]message
s = socket.socket()
host = "0.0.0.0"
port = 4404
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))

s.listen(1)

web_file = "web_file"


def get_web_addrress():
    with open(web_file, "r") as f:
        return f.read()


FILE_REMOVE = "accounts_remove"
USER_NOT_FOUND = "Admin - User Not Found"
USER_HOLD = "Admin - User is currently offline, to be delivered when they come back online"
GREETING = ["Man don't dance - 2018","Man's not hot - 2017","Man don't shower - 2019","2+2 is 4 minus 1 that free quick maths","You can't see me!","The eagle has landed","Hmm, why is the sky blue though?","Have a good time tinkling!","Let's Tinkle and Chill ;-)","Wow! This weather tho","Are you a human or a bot?","Showing you some love ;-)"]
FROM_INITIAL = ["Lone Wolf","Tenno"]
WEB_ADDRESS = get_web_addrress()
clients = []
clients_dict = {}
clients_hold = {}
statuses = {}
groups = {}
groups_mod_free = True
DP_LATE = WEB_ADDRESS + "display/"

# remove user from memory without restarting


def remove_user(name):
    try:
        clients_dict[name]
        clients_dict.pop(name)
        try:
            statuses.pop(name)
        except:
            pass
            #print("nothing in status")
        try:
            clients_hold.pop(name)
        except:
            pass
            #print("nothing in hold")
        result = group_man.get_groups(groups, name)
        #at least be in group
        if len(result) > 0:
            for group_id, values in list(result.items()):
                group_man.remove_member(groups, group_id, name)
                #print("removed "+name+" from "+group_id)
        #print("removal complete")

    except:
        print((traceback.format_exc()))


def check_users_to_remove():
    """runs in background
    if file exist call remove_user
    passing names in file
    """
    while True:
        if os.path.isfile(FILE_REMOVE) == True:
            names = f.readlines()
            for n in names:
                a = n.strip()
                if len(a) > 0:
                    remove_user(a)
            try:
                os.remove(FILE_REMOVE)
            except:
                pass
        else:
            time.sleep(432000) #5 days


def populate_client_dict():
    if os.path.isfile("friends.db"):
        db = dataset.connect('sqlite:///friends.db')
        for user in db['friends']:
            clients_dict[user['name']] = None
        print("populate complete")
    else:
        print("database does not exist")


# group id generator
def id_generator(size=50, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


# associates the name to key
def handle_secrets(conn):
    global clients_dict
    raw = conn.recv(512).decode("utf-8")
    raw_buff = json.loads(raw)
    handle, secret = raw_buff[0], raw_buff[1]
    clients_dict[handle] = [secret, conn]
    data = dict(name=handle, friend_requests="",
                friend_rejects="", friend_accepts="")
    print(data)
    auto_reply(conn, handle, secret, data)

# holds messages while client offline
# including: images, audio, documents & private msgs
# TODO: save to database to load after restart


def hold_unclaimed(blueprint):
    """holds messages while client offline
    including: images, audio, documents & private msgs
    """  
    global clients_hold
    #print "Adding to hold_unclaimed"
    name_to_hold = blueprint["to"]

    try:
        clients_hold[name_to_hold].append(blueprint)
    except KeyError:
        # make it list
        clients_hold[name_to_hold] = [blueprint]

# retrieve msg from hold
# verify key associated to name


def claim_hold(name, supersecret):
    global clients_hold, clients_dict
    try:
        output = None, None, None
        for key1, value1 in list(clients_dict.items()):
            for key0, value0 in list(clients_hold.items()):  # name, address
                if name == key1 or value0[0] == supersecret:
                    to_send_out = {
                        "type": "",
                        "to": "",
                        "from": "",
                        "time": "",
                        "link": "",
                        "msg": ""
                    }
                    to_send_out = {}
                    to_send_out[key0] = value0
                    connectionobj = value1[1]
                    output = True, connectionobj, to_send_out  # v0 is address ^

        if output[0] == True:
            del clients_hold[name]
        return output  # must return a list

    except Exception as e:
        print((traceback.format_exc()))


# sends the msgs in hold every 5 seconds
def do_aquireback(con, ade, from_who):

    for list_of_left_message in ade[from_who]:
        #bprint["msg"] = list_of_left_message
        con.send(bytes(json.dumps(list_of_left_message), "utf-8"))
        time.sleep(5)


def test_method(gid, i):
    global groups
    groups[gid] = [
        {
            "name": "group_name"+i,
            "creator": "creator_name"+i,
            "admins": ["creator_name"+i],
            "members": ["hey", "joe"],
            "creation_date":"_get_date()",
            "description": "here goes description"
        }
    ]


# special method for a group msg transaction
def do_group_reply(group_identifier, msg_from, content, connection, is_media=False, media_link=None, media_type=None):
    GROUP_IDENTIFIER = group_identifier
    GROUP_MSG = content
    try:
        if check_group_exist(GROUP_IDENTIFIER) == True:
            result = get_users_in_group(groups, group_identifier)
            if result[0] == True:
                group_members_names = result[1]  # [name1, name2]
                for member in group_members_names:
                    template = {}
                    # socket object
                    socket_for_member = clients_dict[member][1]
                    if is_media == True:
                        template["type"] = media_type
                        template["link"] = media_link

                    else:
                        template["type"] = "group_message"
                        template["msg"] = GROUP_MSG
                        template["link"] = DP_LATE + msg_from+".png"

                    template["from"] = msg_from
                    template["group_name"] = get_group_name(
                        groups, GROUP_IDENTIFIER)
                    template["group_identifier"] = GROUP_IDENTIFIER

                    try:
                        socket_for_member.send(bytes(json.dumps(template),"utf-8"))
                    except BaseException as e:
                        print((traceback.format_exc()))

    except BaseException as e:
        print((traceback.format_exc()))


# sends out message to everyone
def send_welcome_everyone(name):
    template = {}
    for c_name, c_conn in list(clients_dict.items()):
        try:
            c_conn[1].send(bytes("","utf-8"))
        except Exception as e:
            try:
                c_conn[1].close()
                clients.remove(c_conn[1])
            except Exception as e:
                pass
    template["type"] = "singleton"
    template["msg"] = _get_welcome(name)
    for c_name, c_connw in list(clients_dict.items()):
        try:

            c_connw[1].send(bytes(json.dumps(template),"utf-8"))
        except Exception as e:
            try:
                c_connw[1].close()
                clients.remove(c_connw[1])
            except:
                pass


def _get_welcome(name):
    welcomes = [name +"just joined the server - glhf!",
        name +" just joined. Everyone, look busy!",
        name +" just joined. Can I get a heal?",
        name +" joined your party.",
        name +" joined. You must construct additional pylons.",
        "Ermagherd."+ name +" is here.",
        "Welcome,"+name+" . Stay awhile and listen.",
        "Welcome,"+name+". We were expecting you.",
        "Welcome,"+name+" . We hope you brought pizza.",
        "Welcome "+name+". Leave your weapons by the door.",
        "A wild "+name+" appeared.",
        "Swoooosh. "+name+" just landed.",
        "Brace yourselves."+name+" just joined the server.",
        name+" just joined. Hide your bananas.",
        name+" just arrived. Seems OP - please nerf.",
        name+" just slid into the server.",
        "A "+name+" has spawned in the server.",
        "Big "+name+" showed up!",
        "Where’s "+name+"? In the server!",
        name+" hopped into the server. Kangaroo!!",
        name+" just showed up. Hold my beer."]
    return welcomes[random.randint(0,len(welcomes)-1)]


def do_private_reply(to_name, msg_from, content, connection):
    T_O_Name = to_name
   # private = T_O.find(":")+2 #where private message starts
    PM_MSG = content
   # the_time =data["time"]
    try:

        if T_O_Name in clients_dict:  # and T_O_Name != msg_from:
            template = {}
            socket_for_pm = clients_dict[T_O_Name][1]  # get the socket
            template["type"] = "status_comment"
            template["from"] = T_O_Name
            template["msg"] = PM_MSG
            template["prof_img"] = DP_LATE + msg_from+".png"

            try:
                socket_for_pm.send(bytes(json.dumps(template),"utf-8"))  # send the pm
            except Exception as e:

                try:

                    hold_unclaimed(template)
                    time.sleep(1)
                except Exception as e:  # incase they disconnect
                    connection.close()  # then close their connection

        else:
            pass
    except Exception as e:

        print("status_comment Error:", e)


def check_group_exist(identifier):
    try:
        groups[identifier]
        return True
    except Exception as e:
        print((traceback.format_exc()))
        return False

# INPUT: groups dictionary, group id
# OUTPUT: BOOLEAN, LIST


def get_users_in_group(dictionary, identifier):
    """Returns members of a group.
    True if any and the list (array) as second argument returned
    """
    try:
        members_array = group_man.get_content(
            dictionary, identifier, "members")
        return True, members_array
    except BaseException as e:
        print((traceback.format_exc()))
        return False, None


def get_group_name(dictionary, identifier):
    try:
        return group_man.get_content(dictionary, identifier, "name")
    except Exception as e:
        print((traceback.format_exc()))
        return "null"


def write_group_to_database(dictionary):
    db = dataset.connect('sqlite:///groups.db')
    table = db['groups']
    for k in dictionary:
        members_serialized = json.dumps(dictionary[k][0]["members"])
        admins_serialized = json.dumps(dictionary[k][0]["admins"])
        q = dict(gid=k, name=dictionary[k][0]["name"], members=members_serialized,
                 creator=dictionary[k][0]["creator"], admins=admins_serialized,
                 creation_date=dictionary[k][0]["creation_date"], description=dictionary[k][0]["description"])
        table.insert_ignore(q, ["gid"])


def delete_group_database(k):
    db = dataset.connect('sqlite:///groups.db')
    table = db['groups']
    table.delete(gid=k)


def populate_group_database():
    global groups
    if os.path.isfile("groups.db"):
        db = dataset.connect('sqlite:///groups.db')
        for grp in db['groups']:
            groups[grp["gid"]] = [
                {
                    "name": grp["name"],
                    "creator": grp["creator"],
                    "admins": json.loads(grp["admins"]),
                    "members": json.loads(grp["members"]),
                    "creation_date":grp["creation_date"],
                    "description": grp["description"]
                }
            ]
    else:
        print("group database does not exist")


def auto_reply(connection, handle, my_key, ddaattaa):
    global groups
    global clients_hold, clients_dict, groups_mod_free
    db = dataset.connect('sqlite:///friends.db')
    table = db['friends']
    table.insert_ignore(ddaattaa, ["name"])
    data_status = dict(name=handle, password=my_key,
                       text="Brace yourselves! The cat sees it all ;-)", link=WEB_ADDRESS+"defaultstatus.jpg")
    # when setting new status, compare my_key to password fetch
    db2 = dataset.connect('sqlite:///statuses.db')
    stat_table = db2['stats']
    stat_table.insert_ignore(data_status, ["name"])
    # don't use from data recvd since can be changed  maybe handle == recvd from
    msg_from = handle
    while True:
        try:
            try:
                data = str(connection.recv(4096).decode("utf-8"))
                data = json.loads(data)
                template = {
                    "type": "",
                    "from": "",
                    "link": "",
                    "msg": "",
                    "to": ""
                }
            except:
                # print("Issue with loading the message")
                return

            try:  # my_name,to_who_img,link_img
                type_msg = data["type"]

                if type_msg == "image" or type_msg == "audio" or type_msg == "document":
                    link_img = data["link"]
                    try:
                        group_based = data["group_based"]
                        group_id = data["group_id"]
                    except:
                        group_based = False
                        group_id = None

                    # their current socket
                    if group_based == False:
                        clients_dict[msg_from][1] = data["to"]
                        try:
                            socket_for_img = clients_dict[data["to"]][1]
                        except:
                            socket_for_img = ""
                        template["to"] = data["to"]
                    template["type"] = "image"
                    if type_msg == "audio":
                        template["type"] = "audio"
                    elif type_msg == "document":
                        template["type"] = "document"

                    template["from"] = msg_from
                   # template["time"] = the_time
                    template["link"] = link_img

                    if 1 > 0:  # my_name != to_who_img:# and to_who_img in clients_dict:
                        try:
                            try:
                                if group_based == True:
                                    do_group_reply(
                                        group_id, msg_from, "null", connection, True, link_img, template["type"])
                                socket_for_img.sendall(json.dumps(template))
                                #print "Sent the image"
                            except Exception as e:
                                #print e
                                #print "Adding to hold_unclaimed"
                                if group_based == False:
                                    hold_unclaimed(template)
                                    connection.send(bytes(json.dumps(
                                        {"type": "singleton", "msg": USER_HOLD}), "utf-8"))

                        except BaseException as e:
                            print("Error:", e)
                            hold_unclaimed(template)
                            connection.send(bytes(json.dumps(
                                {"type": "singleton", "msg": USER_HOLD}),"utf-8"))

            except BaseException as e:
                # print(traceback.format_exc())
                return

            # idk what this line does forgot
            clients_dict[handle] = [my_key, connection]
            if type_msg == "private_message":
                T_O_Name = data["to"]
               # private = T_O.find(":")+2 #where private message starts
                PM_MSG = data["msg"]
               # the_time =data["time"]
                try:

                    if T_O_Name in clients_dict:  # and T_O_Name != msg_from:
                        # get the socket
                        try:
                            socket_for_pm = clients_dict[T_O_Name][1]
                        except:
                            socket_for_pm = ""
                        template["type"] = "private_message"
                        template["from"] = msg_from
                       # template["time"] = the_time
                        template["to"] = T_O_Name
                        template["msg"] = PM_MSG
                        template["prof_img"] = DP_LATE + msg_from+".png"

                        try:
                            # send the pm
                            socket_for_pm.send(bytes(json.dumps(template),"utf-8"))
                            #send back to sender too
                            connection.send(bytes(json.dumps(template),"utf-8"))
                        except Exception as e:
                            #print "Cannot reach pm, adding ",T_O_Name,"to hold_unclaimed"

                            try:

                                hold_unclaimed(template)
                                connection.send(bytes(json.dumps(template),"utf-8"))
                                # connection.send(bytes(json.dumps(
                                #     {"type": "singleton", "msg": USER_HOLD}),"utf-8"))
                                # connection.send(bytes(json.dumps(template),"utf-8"))
                            except Exception as e:  # incase they disconnect
                                #print "CallbackError:",e
                                connection.close()  # then close their connection

                    else:
                        #print "[-] Name Not Found! [-]"
                        connection.send(bytes(json.dumps(
                            {"type": "singleton", "msg": USER_NOT_FOUND}),"utf-8"))
                except:
                    print((traceback.format_exc()))

            elif type_msg == "AQUIREDATA!":
                res = claim_hold(msg_from, my_key)
                try:
                    if res[0] == True:  # True,connectionobj,value0
                        con, ade = res[1], res[2]  # res[2] is a list
                        threading.Thread(target=do_aquireback(
                            con, ade, msg_from)).start()
                except:
                    print((traceback.format_exc()))

            elif type_msg == "status_comment":
               # print data
                content = data["msg"]
                T_O_Name = data["to"]
                if T_O_Name in clients_dict:  # and T_O_Name != msg_from:
                    template = {}
                    socket_for_pm = clients_dict[T_O_Name][1]  # get the socket
                    template["type"] = "status_comment"
                    template["msg"] = content
                    template["prof_img"] = DP_LATE + msg_from+".png"
                    template["to"] = T_O_Name
                    template["from"] = msg_from
                    try:
                        socket_for_pm.send(bytes(json.dumps(template),"utf-8"))
                    except Exception as e:
                        hold_unclaimed(template)
                # threading.Thread(target=do_private_reply,args=(data["to"],msg_from,content,connection)).start()

            elif type_msg == "list!":  # this will remove all currently inactive clients i.e. the ones offline
                for c_name, c_conn in list(clients_dict.items()):
                    try:
                        c_conn[1].send(bytes("","utf-8"))
                    except Exception as e:
                        #print "ErrorList:",e
                        try:
                            c_conn[1].close()
                            clients.remove(c_conn[1])
                        except:
                            pass
                       # del clients_dict[c_name]

                list_cli = len(clients_dict)
                connection.send(bytes(str(list_cli),"utf-8"))
            elif type_msg == "status_update":
                st_text = data["text"]
                st_link = data["link"]
                st_from = msg_from

                if db2["stats"].find_one(name=st_from)["password"] == my_key:

                    old_data = dict(name=st_from, password=my_key,
                                    text=st_text, link=st_link)
                    stat_table.update(old_data, ["name"])
                    # print("Update complete")
                else:
                    # print("Status update failed")
                    pass

            elif type_msg == "status_get":
                st_which_user = data["which_user"]
                link_status = db2["stats"].find_one(name=st_which_user)["link"]
                text_status = db2["stats"].find_one(name=st_which_user)["text"]
                try:
                    m_id = data["method_id"]
                except:
                    m_id = None
                temp_status = {"type": "status_feedback",
                               "text": text_status,
                               "link": link_status,
                               "method_id": m_id}
                connection.send(bytes(json.dumps(temp_status), "utf-8"))

            elif type_msg == "whoisonline--req_fri":  # request friend
                template["type"] = "whoisonline--req_fri"
                list_clients = []
                for c_name, c_conn in list(clients_dict.items()):
                    abc = db["friends"].find_one(name=msg_from)[
                        "friend_accepts"]
                   # print abc
                    if c_name not in abc:  # not in current friends
                        list_clients.append(c_name)
                    template["msg"] = list_clients
                    connection.send(bytes(json.dumps(template), "utf-8"))
            elif type_msg == "whoisonline--status":  # request friend
                template["type"] = "whoisonline--status"
                list_status = []
                # Add since they aren't in their own friends list
                list_status.append({
                    "name": msg_from,
                    "link": db2["stats"].find_one(name=msg_from)["link"],
                    "text": db2["stats"].find_one(name=msg_from)["text"]
                })
                for c_name, c_conn in list(clients_dict.items()):
                    abc = db["friends"].find_one(name=msg_from)[
                        "friend_accepts"]
                    if c_name in abc:  # in current friends
                        temp = {}
                        temp["name"] = c_name
                        temp["link"] = db2["stats"].find_one(name=c_name)["link"]
                        temp["text"] = db2["stats"].find_one(name=c_name)["text"]

                        list_status.append(temp)
                template["msg"] = list_status
                connection.send(bytes(json.dumps(template), "utf-8"))

            elif type_msg == "whoisonline--acpt":  # accept friend from request here
                template["type"] = "whoisonline--acpt"
                list_accept = []
                for c_name, c_conn in list(clients_dict.items()):
                    abc = db["friends"].find_one(name=msg_from)[
                        "friend_requests"]
                    if c_name in abc:
                        list_accept.append(c_name)
                    template["msg"] = list_accept
                    connection.send(bytes(json.dumps(template),"utf-8"))

            elif type_msg == "whoisonline--friends":  # accept friend from request here
                template["type"] = "whoisonline--friends"
                list_current = []
                for c_name, c_conn in list(clients_dict.items()):
                    abc = db["friends"].find_one(name=msg_from)[
                        "friend_accepts"]
                    if c_name in abc:
                        list_current.append(c_name)
                    template["msg"] = list_current
                    connection.send(bytes(json.dumps(template),"utf-8"))

            elif type_msg == "request_accept":
                # Remove first from requesting
                oka = data["req_name"]
                current_reqs = db["friends"].find_one(
                    name=msg_from)["friend_requests"]
                old_req = current_reqs.replace(oka+",", "")
                old_data_req = dict(name=msg_from, friend_requests=old_req)
                table.update(old_data_req, ["name"])
                # Now add to accepted
                current_acc = db["friends"].find_one(
                    name=msg_from)["friend_accepts"]
                new = current_acc + oka + ","
                new_data_acc = dict(name=msg_from, friend_accepts=new)
                table.update(new_data_acc, ["name"])  # moved to accepted
                # add client to oka accepted
                current_acc = db["friends"].find_one(
                    name=oka)["friend_accepts"]
                new = current_acc + msg_from + ","
                new_data_acc = dict(name=oka, friend_accepts=new)
                table.update(new_data_acc, ["name"])

            elif type_msg == "new_request":
                oka = data["req_name"]
                current_reqs = db["friends"].find_one(
                    name=oka)["friend_requests"]
                new_current_reqs = current_reqs + msg_from+","
                new_data_req = dict(name=oka, friend_requests=new_current_reqs)
                table.update(new_data_req, ["name"])
                #print db["friends"].find_one(name=oka)["friend_requests"]

            elif type_msg == "show_requests":
                print(db["friends"].find_one(name=msg_from)["friend_requests"])

            elif type_msg == "reject_request":
                # Remove first from requesting
                oka = data["req_name"]
                current_reqs = db["friends"].find_one(
                    name=msg_from)["friend_requests"]
                #new_req = current_reqs +oka +","
                old_req = current_reqs.replace(oka+",", "")
                old_data_req = dict(name=msg_from, friend_requests=old_req)
                table.update(old_data_req, ["name"])
                current_reqs = db["friends"].find_one(
                    name=msg_from)["friend_rejects"]
                new_current_reqs = current_reqs + oka+","
                new_data_req = dict(
                    name=msg_from, friend_rejects=new_current_reqs)
                table.update(new_data_req, ["name"])

            elif type_msg == "broadcast":
                # could set link here to send for all
                for c_name, c_conn in list(clients_dict.items()):
                    try:
                        c_conn[1].send(bytes("","utf-8"))
                    except Exception as e:
                        #print "Error2:",e
                        try:
                            c_conn[1].close()
                            clients.remove(c_conn[1])
                        except Exception as e:
                            pass
                            #print "Cant send to all:",e
                        #del clients_dict[c_name]

                template["type"] = "broadcast"
                template["from"] = msg_from
                template["msg"] = data["msg"]
                template["prof_img"] = DP_LATE + msg_from+".png"
                for c_name, c_connw in list(clients_dict.items()):
                    try:
                        c_connw[1].send(bytes(json.dumps(template),"utf-8"))
                    except Exception as e:
                        try:
                            c_connw[1].close()
                            clients.remove(c_connw[1])
                        except:
                            pass
            elif type_msg == "group_message":
                do_group_reply(data["group_id"], msg_from,
                               data["msg"], connection)

            elif type_msg == "create_group":
                description = data["group_desc"]
                group_name = data["group_name"]
                grp_id = id_generator()

                output = group_man.create_group(
                    groups, grp_id, group_name, description, msg_from)
                if output != False:
                    while groups_mod_free == False:
                        time.sleep(0.3)
                    groups_mod_free = False
                    groups = output
                    groups_mod_free = True
                    msg = group_name+" created successfully"
                    write_group_to_database(groups)
                else:
                    msg = group_name+" not created"
                template = {}
                template["type"] = "singleton"
                template["msg"] = msg
                connection.send(bytes(json.dumps(template),"utf-8"))

            elif type_msg == "delete_group":
                group_id = data["group_id"]
                if msg_from == group_man.check_is_creator(groups, group_id, msg_from):
                    out = group_man.delete_group(groups, group_id)
                    if out != False:
                        while groups_mod_free == False:
                            time.sleep(0.3)
                        groups_mod_free = False
                        groups = out
                        groups_mod_free = True
                        template = {}
                        template["type"] = "singleton"
                        template["msg"] = "Group deleted"
                        connection.send(bytes(json.dumps(template),"utf-8"))
                    else:
                        template = {}
                        template["type"] = "singleton"
                        template["msg"] = "Failed to deleted group"
                        connection.send(bytes(json.dumps(template), "utf-8"))

            elif type_msg == "add_member":
                member_name = data["member_name"]
                group_id = data["group_id"]
                template = {}
                template["type"] = "singleton"
                if member_name != msg_from:
                    if member_name in db["friends"].find_one(name=msg_from)["friend_accepts"]:
                        output = group_man.add_member(
                            groups, group_id, member_name)
                        if output != False:
                            while groups_mod_free == False:
                                time.sleep(0.3)
                            groups_mod_free = False
                            groups = output
                            groups_mod_free = True
                            template["msg"] = "Successfully added " + \
                                member_name
                        else:
                            template["msg"] = "Failed to add "+member_name
                else:
                    template = {}
                    template["type"] = "singleton"
                    template["msg"] = "Can't add yourself"
                    connection.send(bytes(json.dumps(template),"utf-8"))

            elif type_msg == "remove_member":
                member_name = data["member_name"]
                group_id = data["group_id"]
                if group_man.check_is_admin(groups, group_id, msg_from) == True:
                    if group_man.check_is_member(groups, group_id, member_name) == True:
                        output = group_man.remove_member(
                            groups, group_id, member_name)
                        if output[0] == True:
                            while groups_mod_free == False:
                                time.sleep(0.3)
                            groups_mod_free = False
                            groups = output[1]
                            #write_group_to_database(groups)
                            groups_mod_free = True
                            template = {}
                            template["type"] = "singleton"
                            extra = ""
                            if output[2] == 1:
                                extra = " & group was sent to the void"
                                delete_group_database(group_id)
                            if member_name == msg_from:
                                template["msg"] = "You removed yourself"+extra
                            else:
                                template["msg"] = "You removed "+member_name
                            connection.send(bytes(json.dumps(template),"utf-8"))
                        else:
                            template = {}
                            template["type"] = "singleton"
                            template["msg"] = "Failed to remove "+member_name
                            connection.send(bytes(json.dumps(template),"utf-8"))
                    else:
                        template = {}
                        template["type"] = "singleton"
                        template["msg"] = member_name + " not part of group"
                        connection.send(bytes(json.dumps(template),"utf-8"))
                else:
                    template = {}
                    template["type"] = "singleton"
                    template["msg"] = "Insufficient privileges to remove"
                    connection.send(bytes(json.dumps(template),"utf-8"))
            elif type_msg == "add_admin":
                group_id = data["group_id"]
                member_name = data["member_name"]
                if group_man.check_is_admin(groups, group_id, msg_from):
                    out = group_man.add_admin(groups, group_id, member_name)
                    if out != False:
                        while groups_mod_free == False:
                            time.sleep(0.3)
                        groups_mod_free = False
                        groups = out
                        groups_mod_free = True
                        riv = member_name+" is an admin"
                    else:
                        riv = "Failed to add "+member_name+" admin status"
                    template = {}
                    template["type"] = "singleton"
                    template["msg"] = riv
                    connection.send(bytes(json.dumps(template),"utf-8"))
            elif type_msg == "remove_admin":
                group_id = data["group_id"]
                member_name = data["member_name"]
                if group_man.check_is_admin(groups, group_id, msg_from):
                    out = group_man.remove_admin(groups, group_id, member_name)
                    if out != False:
                        while groups_mod_free == False:
                            time.sleep(0.3)
                        groups_mod_free = False
                        groups = out
                        groups_mod_free = True
                        riv = member_name+" is no longer an admin"
                    else:
                        riv = "Failed to remove "+member_name+" admin status"
                    template = {}
                    template["type"] = "singleton"
                    template["msg"] = riv
                    connection.send(bytes(json.dumps(template),"utf-8"))

            elif type_msg == "get_group_members":
                group_id = data["group_id"]
                current_members = group_man.get_content(
                    groups, group_id, "members")
                # print(current_members)
                if msg_from in current_members:
                    template = {}
                    template["type"] = "get_group_members"
                    template["members"] = current_members
                    template["group_id"] = group_id
                    template["from"] = msg_from
                    connection.send(bytes(json.dumps(template),"utf-8"))

            # remove, groups should be private and "add" members only
            elif type_msg == "get_groups":
                template = {}
                template["type"] = "get_groups"
                template["msg"] = group_man.get_groups(groups, msg_from)
                connection.send(bytes(json.dumps(template), "utf-8"))

            elif type_msg == "group_info":
                gid = data["group_id"]
                template["type"] = "group_info"
                template["name"] = group_man.get_content(groups, gid, "name")
                template["creator"] = group_man.get_content(groups, gid, "creator")
                template["admins"] = group_man.get_content(groups, gid, "admins")
                template["creation_date"] = group_man.get_content(groups, gid, "creation_date")
                template["description"] = group_man.get_content(groups, gid, "description")
                template["num_members"] = len(group_man.get_content(groups, gid, "members"))
                connection.send(bytes(json.dumps(template),"utf-8"))

            elif type_msg == "initial_data":
                # send friends list, and global messages [50%] plus anything necessary
                template["type"] = "whoisonline--friends"
                list_current = []
                try:

                    for c_name, c_conn in list(clients_dict.items()):
                        abc = db["friends"].find_one(name=msg_from)[
                            "friend_accepts"]
                        if c_name in abc:
                            list_current.append(c_name)
                        template["msg"] = list_current
                        if len(list_current):
                            connection.send(bytes(json.dumps(template), "utf-8"))
                        else:
                            print("no friends")
                except:
                    print("snaaaaaaaaaaaapp")
                time.sleep(2)
                grps = group_man.get_groups(groups, msg_from)
                if len(grps):
                    template = {}
                    template["type"] = "get_groups"
                    template["msg"] = grps
                    connection.send(bytes(json.dumps(template), "utf-8"))
                else:
                    print("not in groups")

        except socket.error as e:
            print("socket error, breaking")
            print(e)
            break
        except:
            print("-------------------------------massive")
            print((traceback.format_exc()))


def exit_handler():
    #print 'My application is ending!'
    write_group_to_database(groups)


atexit.register(exit_handler)

# # initialise
populate_client_dict()
populate_group_database()

print("Server - Public")

while True:
    try:
        #print("accepting")
        conn, addr = s.accept()
        if conn not in clients:
            clients.append(conn)

        #print "connection from {} on {}".format(addr[0],addr[1])
        threading.Thread(target=handle_secrets, args=(conn,)).start()
    except KeyboardInterrupt as e:
        print("exiting program...")
        sys.exit()
