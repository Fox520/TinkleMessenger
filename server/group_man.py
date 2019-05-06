import datetime
import traceback
# return modified dictionary


def _get_date():
    now = datetime.datetime.now()
    return str(now.month)+"/"+str(now.day)+"/"+str(now.year)


def create_group(dictionary, gid, name="No name", description="no description", creator_name="", members=[]):
    try:
        dictionary[gid]
        #print "group already exists"
        return False  # group already exist
    except Exception as e:
        members = None
        members = []
        members.append(creator_name)
        dictionary[gid] = [
            {
                "name": name,
                "creator": creator_name,
                "admins": [creator_name],
                "members": members,
                "creation_date":_get_date(),
                "description": description
            }
        ]
        #print "group created"
        return dictionary


def get_content(dictionary, gid, key):
    """Used to access any of the keys of the group
    e.g. the group members list (array)
    """
    try:
        #print dictionary[gid][0][key]
        return dictionary[gid][0][key]
    except Exception as e:
        print((traceback.format_exc()))
        #print "Group does not exist"
        return False
# return modified dictionary


def delete_group(dictionary, gid):
    try:
        del dictionary[gid]
        return dictionary
    except Exception as e:
        print((traceback.format_exc()))
        #print "Group does not exist"
        return False

# return modified dictionary


def remove_member(dictionary, gid, member):
    try:
        if member != get_content(dictionary, gid, "creator"):
            members_array = get_content(dictionary, gid, "members")
            if member in members_array:
                members_array.remove(member)
                remove_admin(dictionary, gid, member)
                return [True, members_array,0]
            else:
                return [False,False,0]
        else:
            return [True, delete_group(dictionary, gid),1]
    except Exception as e:
        print((traceback.format_exc()))
        #print "unable to remove member"
        return [False]

# return modified dictionary


def add_member(dictionary, gid, member):
    try:
        members_array = get_content(dictionary, gid, "members")

        if member in members_array:
            return False  # already a member
        else:
            members_array.append(member)
            return dictionary

    except Exception as e:
        print((traceback.format_exc()))
        #print "cant add member"
        return


def check_is_member(dictionary, gid, member):
    try:
        members_array = get_content(dictionary, gid, "members")
        if member in members_array:
            return True
        else:
            return False
    except Exception as e:
        return False


def check_is_admin(dictionary, gid, member):
    try:
        admins_array = get_content(dictionary, gid, "admins")
        if member in admins_array:
            return True
        else:
            return False
    except Exception as e:
        return False


def check_is_creator(dictionary, gid, member):
    try:
        if member == get_content(dictionary, gid, "creator"):
            return True
        else:
            return False
    except Exception as e:
        print(e)


def add_admin(dictionary, gid, member):
    if check_is_member(dictionary, gid, member) == True:
        dictionary[gid][0]["admins"].append(member)
        return dictionary
    else:
        return False


def remove_admin(dictionary, gid, member):
    if check_is_admin(dictionary, gid, member) == True and member != get_content(dictionary, gid, "creator"):
        dictionary[gid][0]["admins"].remove(member)
        return dictionary
    else:
        return False


def get_groups(dictionary, userToTest):
    """Returns groups which the user is in"""
    temp = {}
    for k,v in list(dictionary.items()):
        #print dictionary[k][0]
        for t_name in dictionary[k][0]["members"]:
            if userToTest == t_name:
                temp[k] = dictionary[k][0]["name"] + \
                    ": " + dictionary[k][0]["description"]

    return temp
