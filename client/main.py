# -*- coding: utf-8 -*-
# encoding=utf-8
# TODO: Work on `about` dialog

from __future__ import division

import codecs
import simplejson as json
import os
import re
import os.path
import random
import shutil
import socket
import string
import sys
import threading
import time
import hashlib
import traceback
import dataset
import requests

from functools import partial
from kivy import Config
from kivy.app import App
from kivy.clock import Clock

from kivy.core.window import Window

Window.softinput_mode = "below_target"  # resize to accomodate keyboard
from kivy.effects.opacityscroll import OpacityScrollEffect
from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.properties import StringProperty
from kivy.resources import resource_add_path  # To compile to exe
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage, Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.filechooser import FileChooserIconView
#
from kivy.utils import get_color_from_hex

from kivymd.toast import toast
from kivymd.bottomsheet import MDListBottomSheet
from kivymd.theming import ThemeManager
from kivymd.button import MDRaisedButton
from kivymd.dialog import MDDialog
from kivymd.list import OneLineListItem, TwoLineListItem, TwoLineAvatarListItem, ThreeLineAvatarListItem, MDList
from kivymd.textfields import MDTextField
from kivymd.label import MDLabel
from kivymd.snackbars import Snackbar

from spin_load import ProgressSpinner

from magnet import Magnet
from random import sample, randint

os.environ['KIVY_GL_BACKEND'] = 'sdl2'

Config.set('graphics', 'multisamples', '0')  # sdl error
Config.set('kivy', 'window_icon', 'img/tinkle_logo.png')

json_settings = json.dumps([
    {
        "type": "bool",
        "title": "Show images",
        "desc": "Display received images in popup",
        "section": "General",
        "key": "autoshow_img"

    }

])


def isAndroid():
    # On Android sys.platform returns 'linux2', so prefer to check the
    # presence of python-for-android environment variables (ANDROID_ARGUMENT
    # or ANDROID_PRIVATE).
    if 'ANDROID_ARGUMENT' in os.environ:
        return True
    else:
        return False


home = os.path.expanduser('~')
if isAndroid() == True:
    path_music = os.path.join('/sdcard', 'Download')
    path_images = os.path.join('/sdcard', 'Download')
    path_docs = os.path.join('/sdcard', 'Download')

else:
    path_music = os.path.join(home, "Music")
    path_images = os.path.join(home, "Pictures")
    path_docs = os.path.join(home, "Desktop")

ALL_GROUPS = None

other_files = "others"
resource_folder = "resources"
receiver_name = ""
group_name = "null"
OLD_GROUP_ID = ""
DEFAULT_ACCOUNT = False
DEFAULT_STATUS = "cat.jpg"
MAX_FILE_SIZE = 15000000
MSG_CHECK_DELAY = 0.5
LOADING_IMAGE = os.path.join(resource_folder, "tinkle_loading.png")
client_file = os.path.join(other_files, "s2adwkbje2gbxhh4yi0k")
save_messages_file = os.path.join(other_files, "ydr6yxohmvy92o0ex1ql")
IS_GROUP_MEDIA = False
save_messages = True
chat_was_on = False
was_here = False
was_on = False
ishere = False

color_file = os.path.join(other_files, "fi9a494os0tn22gelfxt")
global_status_pic = ""
global_status_text = ""
update_convo = False
new_data_to_add = ""
new_data_to_add_group = ""
current_group_id = ""
current_group_desc = ""
group_info_dict = {"name": "", "creator": "",
                   "description": "", "admins": [], "creation_date": ""}

thecurrentonline = ""
img_file = os.path.join(other_files, "yqx53umh1ozf5mqc623t")
aud_file = os.path.join(other_files, "la79qqkrkznjx0450hrb")
doc_file = os.path.join(other_files, "hhwq11qr7n2l0mmvhmgm")
status_file = os.path.join(other_files, "kjagsdfhkasgidfhka1")
dm_file = os.path.join(other_files, "dgffq8jryv7lp6mrr6v2")
backup_file = os.path.join(path_docs, "Tinkle_Backup.dat")
priv = os.path.join(other_files, "wcuy1gvvpglye1s77lgi")
comments_file = os.path.join(other_files, "jsdahfvkusafgdilaksbf")

should_do_bak = True
was_here_img = False
was_here_aud = False
was_here_doc = False
was_here_status = False
was_here_friend_req = False
was_here_friends_accept = False
was_here_find_friends = False
was_here_members_group = False
current_group_members = None
current_share_img = ""
current_share_aud = ""
current_share_doc = ""
current_share_status = ""
check_if_got = False

port_conditions = 4400
port_profile_pic = 4401
port_data = 4402
port_name = 4403
port_chat = 4404
port_files = 4405
avail_img_ext = [".jpg", ".png", ".gif"]
avail_aud_ext = [".mp3", ".wav", ".ogg"]
avail_doc_ext = [".doc", ".pdf", ".xls", ".docx", ".zip", ".rar", ".apk"]
#########
fil_avail_img_ext = ["*.jpg", "*.png", "*.gif"]
fil_avail_aud_ext = ["*.mp3", "*.wav", "*.ogg"]
fil_avail_doc_ext = ["*.doc", "*.pdf", "*.xls",
                     "*.docx", "*.zip", "*.rar", "*.apk"]
try:
    if os.path.isfile(color_file):
        with open(color_file, "rb") as f:
            chat_clr_value = f.read()
    else:
        chat_clr_value = "#ffffff"
except Exception as e:
    print(e)
ACTION = "#ff5722"
NAV_COLOR = "#00A1F1"
IS_TYPING = False


def sec_generator(size=50, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


the_key = ""


def generate_key():
    global the_key
    try:
        if os.path.isfile(priv):
            with open(priv, "rb") as f:
                the_key = f.read()
        else:
            with open(priv, "wb") as f:
                bbq = sec_generator()
                f.write(bbq)
                the_key = bbq
    except Exception as e:
        print(e)


def get_password():
    global the_key
    if the_key != "":
        return the_key
    with open(priv, "rb") as f:
        the_key = f.read()
        return the_key


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


directory = "req_sent"
chats_directory = "chats_directory"
comments_db_name = 'sqlite:///comments_status.db'
comments_status_db_file = 'comments_status.db'
transitions = (
    'out_sine', 'out_quint', 'out_quart', 'out_quad', 'out_expo',
    'out_cubic', 'out_circ', 'out_bounce', 'out_back', 'linear',
    'in_sine', 'in_quint', 'in_quart', 'in_quad', 'in_out_sine',
    'in_out_quint', 'in_out_quart', 'in_out_quad', 'in_out_expo',
    'in_out_cubic', 'in_out_circ', 'in_out_bounce', 'in_out_back',
    'in_expo', 'in_cubic', 'in_circ', 'in_bounce', 'in_back',
)

if not os.path.exists(directory):
    os.makedirs(directory)
if not os.path.exists(chats_directory):
    os.makedirs(chats_directory)
if not os.path.exists(other_files):
    os.makedirs(other_files)

WEB_ADDR = "http://127.0.0.1/"

_web_address = None
_server_ip = None


def return_site_web_address():
    # return "127.0.0.1"
    global _web_address
    # fetch address from web and write it
    if _web_address != None:
        return _web_address
    try:
        a = requests.get(WEB_ADDR + "navigation/web_address")
        p = a.text.strip()
        _web_address = p
        return p
    except Exception as e:
        print(e)


def return_server_address():
    # return "127.0.0.1"
    global _server_ip
    if _server_ip != None:
        return _server_ip
    # fetch address from web and write it
    try:
        a = requests.get(WEB_ADDR + "navigation/server_ip")
        p = a.text.strip()
        _server_ip = p
        return p
    except Exception as e:
        print(e)


def create_file_sent_req(name_client):
    with open(os.path.join(directory, name_client), "w") as f:
        f.write("")


def return_sent_req():
    return os.listdir(directory)


def delete_file_sent(name_client):
    try:
        os.remove(os.path.join(directory, name_client))
    except Exception as e:
        print(traceback.format_exc())


def check_if_exist(filename):
    if os.path.isfile(filename):
        return True
    else:
        return False


def create_file(filename):
    with open(filename, "wb") as f:
        f.write("")


def return_file_log(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            new_log = []
            raw_log = f.read().split('\n')
            for i in raw_log:
                if len(i) > 0:
                    new_log.append(i)
            return new_log


def append_to_file(filename, data):
    tt = data["from"] + "`" + data["msg"] + "`" + data["prof_img"] + "\n"
    with open(os.path.join(chats_directory, filename), "a") as f:
        f.write(tt)


def check_name():
    if os.path.isfile(client_file) == True:
        with open(client_file, "rb") as f:
            client_name = f.read()
            if len(client_name) > 4:
                return True, client_name
            else:
                return False, None
    else:
        return False, None


def write_name(foo_name, should_write=True, pwda=""):
    # ASK FOR NAME
    global name, DEFAULT_ACCOUNT
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nhost = return_server_address()
    nport = port_name
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if pwda == "":
        pwda = get_password()
        DEFAULT_ACCOUNT = True
    try:
        sock.connect((nhost, nport))
        # temp_data = {"type": "login", "name": foo_name, "password": pwda}
        temp_data = {"type": "login", "name": foo_name, "password": pwda}
        sock.send(bytes(json.dumps(temp_data), "utf-8"))
        data = sock.recv(1024).decode("utf-8")
        name_test_server = json.loads(data)
        sock.close()
        if name_test_server["type"] == "login":
            if name_test_server["state"] == "success":
                # login success
                if should_write == True:
                    with open(client_file, "wb") as f:
                        f.write(foo_name)
                return True, "login"
            else:
                # print("falacy")
                # print(name_test_server)
                return False, "login"  # not exists call register

        if should_write == True:
            try:
                with open(client_file, "wb") as f:
                    f.write(foo_name)
            except BaseException as e:
                print(e)
    except Exception as e:
        print(traceback.format_exc())
        print("Server not reachable at write_name func")
        return None, None


def exceedLimit(f):
    try:
        if os.stat(f).st_size > MAX_FILE_SIZE:
            return True
        else:
            return False
    except:
        # maybe file not here
        return False


def global_notify(msg):
    toast(msg)


if isAndroid() == True:
    from jnius import autoclass, PythonJavaClass, java_method, cast
    from android import activity
    from android.runnable import run_on_ui_thread

    autoclass('org.jnius.NativeInvocationHandler')


    @run_on_ui_thread
    def _toast(text, length_long=False):
        Toast = autoclass('android.widget.Toast')
        context = autoclass('org.kivy.android.PythonActivity').mActivity
        duration = Toast.LENGTH_LONG if length_long else Toast.LENGTH_SHORT
        String = autoclass('java.lang.String')
        c = cast('java.lang.CharSequence', String(text))
        t = Toast.makeText(context, c, duration)
        t.show()


def global_snackbar(msg):
    Snackbar(text=msg).show()


class A:
    def get_the_name(self):
        global name
        return name


def write_status_comments(name, msg, link):
    try:
        db = dataset.connect('sqlite:///comments_status.db')
        table = db['comments']
        table.insert(dict(name=name, msg=msg, link=link))
    except BaseException as e:
        print("Error writing:", e)


def doHashCheckServer(fname, media_type):
    fhash = md5(fname)
    try:
        template = {}
        template["media_type"] = media_type
        template["hash"] = fhash
        fsock = socket.socket()
        fsock.connect((return_server_address(), port_files))
        fsock.send(bytes(json.dumps(template), "utf-8"))
        result = json.loads(fsock.recv(1024).decode("utf-8"))
        if result["type"] == "hash_request":
            if result["result"] == True:
                return [True, result["file_path"]]
            else:
                return [False, ""]
    except:
        print(traceback.format_exc())
        return [False, ""]


generate_key()

##########################################################


Builder.load_string("""
#:include kv/signinscreen.kv
#:include kv/registrationscreen.kv
#:include kv/creategroupscreen.kv
#:include kv/getnamescreens.kv
#:include kv/advancedscreen.kv
#:include kv/newstatusscreen.kv
#:include kv/displaystatusscreen.kv
#:include kv/privatechatscreen.kv
#:include kv/groupchatscreen.kv
#:include kv/statuscommentscreen.kv
#:include kv/groupextras.kv
#:include kv/profilepicscreen.kv
#:include kv/mediasharescreens.kv
#:include kv/mainscreen.kv
#:include kv/variouspopups.kv
#:import path_music __main__.path_music
#:import path_images __main__.path_images
#:import path_docs __main__.path_docs
#:import fil_avail_doc_ext __main__.fil_avail_doc_ext
#:import fil_avail_aud_ext __main__.fil_avail_aud_ext
#:import fil_avail_img_ext __main__.fil_avail_img_ext
#:import chat_clr_value __main__.chat_clr_value
#:import ACTION __main__.ACTION
#:import NAV_COLOR __main__.NAV_COLOR
#:import LOADING_IMAGE __main__.LOADING_IMAGE 
#:import get_color_from_hex __main__.get_color_from_hex
#:import ProgressSpinner __main__.ProgressSpinner
#:import Clock __main__.Clock
#:import get_random_color kivy.utils.get_random_color
#:import OpacityScrollEffect __main__.OpacityScrollEffect

#:import MDToolbar kivymd.toolbar.MDToolbar
#:import NavigationLayout kivymd.navigationdrawer.NavigationLayout
#:import MDThemePicker kivymd.pickers.MDThemePicker
#:import MDTab kivymd.tabs.MDTab
#:import MDTabbedPanel kivymd.tabs.MDTabbedPanel

<MyImageButton@ButtonBehavior+AsyncImage>:

<MyNavigationDrawerIconButton@NavigationDrawerIconButton>:
    icon: 'checkbox-blank-circle'

<MainNavigationDrawer@MDNavigationDrawer>:
    drawer_logo: "resources/tinkle_loading.png"
    
    MyNavigationDrawerIconButton:
        text: "Show Friend Requests"
        on_release:
            app.manage_screens("names_for_friend_req","add")
            app.change_screen("names_for_friend_req")
    MyNavigationDrawerIconButton:
        text: "Change Profile Picture"
        on_release:
            app.decide_change_dp()
    MyNavigationDrawerIconButton:
        text: "New Status"
        on_release:
            app.manage_screens("status_screen","add")
            app.change_screen("status_screen")
    MyNavigationDrawerIconButton:
        text: "Check Statuses"
        on_release:
            app.manage_screens("names_for_status","add")
            app.change_screen("names_for_status")

    MyNavigationDrawerIconButton:
        text: "Change theme"
        on_release:
            MDThemePicker().open()


<DumpScreen>:
    BoxLayout:
        canvas:
            Rectangle:
                pos: self.pos
                size: self.size
                source: LOADING_IMAGE

<-AvatarSampleWidget>:
    canvas:
        Rectangle:
            texture: self.texture
            size: self.width + 20, self.height + 20
            pos: self.x - 10, self.y - 10       

    """)


class ILeftBody:
    '''Pseudo-interface for widgets that go in the left container for
    ListItems that support it.

    Implements nothing and requires no implementation, for annotation only.
    '''
    pass


class AvatarSampleWidget(ILeftBody, AsyncImage):
    pass


# Name: advanced_screen


class AdvancedScreen(Screen):
    def __init__(self, **kwargs):
        super(AdvancedScreen, self).__init__(**kwargs)
        self.ml = self.ids["ml"]
        self.add_two_line("view members", "show members of the group")
        self.add_two_line("add friend", "add a friend to the group")
        self.add_two_line(
            "group information", "show group information e.g. group creation date, admins etc.")

    def on_back_pressed(self, *args):
        Tinkle().change_screen("group_convo")
        Tinkle().manage_screens("advanced_screen", "remove")

    def on_menu_pressed(self, *args):
        pass

    def add_two_line(self, short_info, long_info):
        img_to_use = {
            "view members": "img/group.png",
            "add friend": "img/group_add.png",
            "group information": "img/info.png"

        }
        a = TwoLineAvatarListItem(
            text=long_info, secondary_text=short_info, font_style="Body1",
            on_release=lambda *args: self.open_more(short_info))

        a.add_widget(AvatarSampleWidget(source=img_to_use[short_info]))
        self.ml.add_widget(a)

    def open_more(self, short_info):
        if short_info == "view members":
            # print "changing to view members screen"  # you can remove/make admin there
            Tinkle().manage_screens("group_members", "add")
            Tinkle().change_screen("group_members")
        elif short_info == "add friend":
            # print "changing to add friend screen"
            Tinkle().manage_screens("names_friends_group", "add")
            Tinkle().change_screen("names_friends_group")

        elif short_info == "group information":
            # print "changing to group information screen"
            try:
                global s
                template = {}
                template["type"] = "group_info"
                template["group_id"] = current_group_id
                s.send(bytes(json.dumps(template), "utf-8"))
                threading.Thread(target=global_notify,
                                 args=("Not yet implemented.",)).start()
            except:
                threading.Thread(target=global_notify,
                                 args=("Error while getting info",)).start()


# Name: group_members


class GroupMembers(Screen):
    def __init__(self, **kwargs):
        super(GroupMembers, self).__init__(**kwargs)
        self.ml = self.ids["ml"]

    def on_back_pressed(self, *args):
        Tinkle().change_screen("advanced_screen")
        Tinkle().manage_screens("group_members", "remove")

    def on_menu_pressed(self, *args):
        pass

    def send_background(self):
        template = {
            "type": "get_group_members",
            "group_id": current_group_id
        }
        s.send(bytes(json.dumps(template), "utf-8"))

    def on_leave(self):
        self.ids.ml.clear_widgets()

    def do_checks(self, *args):
        if was_here_members_group == True:
            self.event.cancel()
            self.ids.ml.clear_widgets()
            # print("adding names")
            for each_user in current_group_members:
                if len(each_user) >= 4:  # and each_user != A().get_the_name():
                    self.add_member_name(each_user)

    def on_enter(self):
        self.ml = self.ids["ml"]
        self.ids.ml.clear_widgets()
        threading.Thread(target=self.send_background).start()
        self.event = Clock.schedule_interval(self.do_checks, 0.3)

    def on_leave(self):
        try:
            self.event.cancel()
        except:
            print(traceback.format_exc())
        Tinkle().manage_screens("group_members", "remove")

    def add_member_name(self, member_name):
        magnet = Magnet(transitions={'pos': sample(transitions, 1)[0],
                                     'size': sample(transitions, 1)[0]},
                        duration=random.random())

        magnet.add_widget(
            Button(text=member_name, on_release=partial(self.popup_menu, member_name)))
        self.ml.add_widget(magnet, index=randint(0, len(self.ml.children)))

    def popup_menu(self, member_name, *args):

        txt = "1. Make admin\n2. Remove admin\n3. Remove from group"

        content = MDLabel(font_style='Subhead',
                          text=txt,
                          size_hint_y=None,
                          valign='top')

        content.bind(texture_size=content.setter('size'))
        self.dialog = MDDialog(title="Options",
                               content=content,
                               auto_dismiss=True)

        self.dialog.add_action_button("1",
                                      action=partial(self.begin_method_in_thread, self.make_admin, member_name))
        self.dialog.add_action_button("2",
                                      action=partial(self.begin_method_in_thread, self.remove_admin, member_name))
        self.dialog.add_action_button("3",
                                      action=partial(self.begin_method_in_thread, self.remove_from_group, member_name))
        self.dialog.open()

    def begin_method_in_thread(self, method, param, *args):
        threading.Thread(target=method, args=(param,)).start()

    def make_admin(self, member_name, *args):
        try:
            template = {}
            template["type"] = "add_admin"
            template["group_id"] = current_group_id
            template["member_name"] = member_name
            s.send(bytes(json.dumps(template), "utf-8"))
        except:
            print(traceback.format_exc())
        self.dialog.dismiss()

    def remove_admin(self, member_name, *args):
        try:
            template = {}
            template["type"] = "remove_admin"
            template["group_id"] = current_group_id
            template["member_name"] = member_name
            s.send(bytes(json.dumps(template), "utf-8"))
        except:
            print(traceback.format_exc())
        self.dialog.dismiss()

    def remove_from_group(self, member_name, *args):
        try:
            template = {}
            template["type"] = "remove_member"
            template["group_id"] = current_group_id
            template["member_name"] = member_name
            s.send(bytes(json.dumps(template), "utf-8"))
        except:
            print(traceback.format_exc())
        self.dialog.dismiss()


# Name: names_friends_group


class GetFriendsAddGroup(Screen):
    global s

    def __init__(self, **kwargs):
        self.register_event_type('on_back_pressed')
        self.register_event_type('on_menu_pressed')
        super(GetFriendsAddGroup, self).__init__(**kwargs)

    def on_back_pressed(self, *args):
        Tinkle().change_screen("advanced_screen")

    def on_menu_pressed(self, *args):
        pass

    def on_leave(self):
        self.ids.ldml.clear_widgets()
        Tinkle().manage_screens("names_friends_group", "remove")

    def on_enter(self):
        global was_here_friends_accept
        self.ldml = self.ids["ldml"]
        threading.Thread(target=self.send_background).start()
        while was_here_friends_accept != True:
            pass

        self.ids.ldml.clear_widgets()
        for each_user in current_friends_accept:
            if len(each_user) >= 4 and A().get_the_name() not in each_user:
                self.add_one_line(each_user)

    def send_background(self):
        template = {
            "type": "whoisonline--friends"
        }
        s.send(bytes(json.dumps(template), "utf-8"))

    def add_one_line(self, data):
        self.ldml.add_widget(OneLineListItem(text=data,
                                             markup=True,
                                             text_size=(self.width, None),
                                             size_hint_y=None,
                                             font_size=(self.height / 20),
                                             on_release=partial(self.change_to_img, data)))  # data is the clients' name

    def change_to_img(self, img_client, *args):
        global receiver_name
        member_name = img_client
        txt = "Do you want to add " + member_name + "?"

        content = MDLabel(font_style='Subhead',
                          text=txt,
                          size_hint_y=None,
                          valign='top')

        content.bind(texture_size=content.setter('size'))
        self.dialog = MDDialog(title="Options",
                               content=content,
                               size_hint=(.8, None),
                               height=dp(200),
                               auto_dismiss=True)

        self.dialog.add_action_button("Yes",
                                      action=partial(self.add_friend_group, member_name))
        self.dialog.add_action_button("No",
                                      action=lambda *x: self.dialog.dismiss())
        self.dialog.open()

    def add_friend_group(self, friend_name, *args):
        try:
            template = {}
            template["type"] = "add_member"
            template["member_name"] = friend_name
            template["group_id"] = current_group_id
            s.send(bytes(json.dumps(template), "utf-8"))
            self.dialog.dismiss()
            Tinkle().change_screen("advanced_screen")
        except:
            print(traceback.format_exc())


class SignInScreen(Screen):

    def __init__(self, **kwargs):
        super(SignInScreen, self).__init__(**kwargs)
        self.alias = self.ids["alias"]
        self.prg_spin = self.ids["prg_spin"]
        self.bs_menu_1 = None
        if os.path.isfile(client_file):
            with open(client_file, "rb") as f:
                temp_string = f.read()
                self.alias.text = temp_string

    def on_enter(self):
        Tinkle().manage_screens("dump_screen", "remove")

    def _signin(self):
        temp_pw = ""
        result = write_name(self.alias.text, False, temp_pw)
        if result[0] == True:
            self.prg_spin.stop_spinning()
            global name
            name = self.alias.text
            Tinkle().manage_screens("Chat", "add")
            self.manager.current = "Chat"
        elif result[0] == False:
            self.prg_spin.stop_spinning()
            threading.Thread(target=global_notify, args=(
                "Invalid signin credentials",)).start()
        elif result[0] == None:
            self.prg_spin.stop_spinning()
            threading.Thread(target=global_notify, args=(
                "unable to connect",)).start()

    def show_bottom_sheet(self):
        if not self.bs_menu_1:
            self.bs_menu_1 = MDListBottomSheet()
            self.bs_menu_1.add_item(
                "Recover account from backup file",
                lambda x: self.recover_backup())

        self.bs_menu_1.open()

    def export_key(self):

        try:
            shutil.copy2(priv, home)
            threading.Thread(target=global_notify, args=(
                "Saved: " + os.path.join(home, priv),)).start()
        except Exception as e:
            threading.Thread(target=global_notify, args=(
                "Failed, check permissions",)).start()
            self.display_password(get_password())

    def write_new_data(self, new_name, new_key):
        global the_key
        with open(client_file, "wb") as f:
            f.write(new_name)
        with open(priv, "wb") as f:
            f.write(new_key)
            the_key = ""

    def do_android(self):
        if isAndroid() == True:
            import android_image_select
            reload(android_image_select)
            android_image_select.user_select_image(self.img_callback)
        else:
            print("not android")

    def img_callback(self, path):
        print(path)

    def recover_backup(self):
        if os.path.isfile(backup_file):
            with open(backup_file, "rb") as f:
                data = f.read()
                _n, _p = data.split("\n")
                self.write_new_data(_n, _p)
                self.alias.text = _n
        else:
            threading.Thread(target=global_notify, args=(
                "Backup file not found",)).start()
            return None, None

    def display_password(self, themsg):
        box = GridLayout(rows=2)
        box.add_widget(
            MDTextField(readonly=True, text=themsg, multiline=True, background_color=get_color_from_hex(chat_clr_value),
                        background_normal="",
                        auto_dismiss=True))
        box.add_widget(MDRaisedButton(
            text="dismiss", on_release=lambda *args: popup.dismiss()))

        popup = Popup(title="your key", content=box)
        popup.open()


class Registration(Screen):
    def __init__(self, **kwargs):
        self.register_event_type('on_back_pressed')
        self.register_event_type('on_menu_pressed')
        super(Registration, self).__init__(**kwargs)
        self.prg_spin = self.ids["prg_spin"]

    def on_back_pressed(self, *args):
        Tinkle().change_screen("signin_screen")

    def on_menu_pressed(self, *args):
        pass

    # def on_enter(self):
    #     if isAndroid() == True:
    #         import permission_helper
    #         perms = ["android.permission.READ_EXTERNAL_STORAGE",
    #                  "android.permission.WRITE_EXTERNAL_STORAGE"]

    #         haveperms = permission_helper.acquire_permissions(perms)
    #         print(haveperms)
    #         threading.Thread(target=global_notify, args=(
    #             "perms: "+str(haveperms),)).start()

    def register_user(self, name_reg, pwd):
        # reg them
        # if true write file
        # else call login screen again and notify user
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            nhost = return_server_address()
            nport = port_name
            sock.connect((nhost, nport))
            temp = {"type": "register", "name": name_reg, "password": pwd}
            sock.send(bytes(json.dumps(temp), "utf-8"))
            tdata = sock.recv(1024).decode("utf-8")
            data = json.loads(tdata)
            if data["state"] == "success":
                with open(client_file, "wb") as f:
                    f.write(name_reg)
                return True
            elif data["state"] == "fail":
                return False
        except Exception as e:
            return None

    def test_name_chars(self, string_to_test):
        inv_chars = [" ", "`", "~", "!", "@", "$", "%",
                     "(", ")", "[", "]", "{", "}", "\\", ",", ".", "<", ">", "?"]
        for l in string_to_test:
            if l in inv_chars:
                return True
        return False

    def call_check_name_function(self):
        global name

        self.temp_name = self.ids["username"]
        self.full_name = self.ids["first_name"].text + \
                         " " + self.ids["last_name"].text
        self.email_address = self.ids["email_address"]
        tt_name = self.temp_name.text
        b = tt_name.lstrip(" ")  # strip first only
        tt_name = b.replace("\\", "")
        self.temp_name.text = tt_name
        try:
            char_result = self.test_name_chars(self.temp_name.text)
            if len(tt_name) < 4 or char_result or len(tt_name) > 12:
                if char_result == True:
                    threading.Thread(target=global_notify, args=(
                        "Illegal symbol in username",)).start()
                else:
                    threading.Thread(target=global_notify, args=(
                        "Invalid username length",)).start()
                # self.temp_name.text = ""
                self.prg_spin.stop_spinning()
                self.manager.current = "registration_screen"

            else:
                if len(self.full_name) >= 5 and len(self.email_address.text) > 7:
                    # re to match email
                    email_valid = False
                    pattern = re.compile(
                        r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
                    if len(pattern.findall(self.email_address.text)) > 0:
                        email_valid = True
                    if email_valid == True:

                        answer = self.register_user(
                            self.temp_name.text, get_password())
                        if answer == True:
                            threading.Thread(target=self.upload_data).start()
                            name = self.temp_name.text
                            self.prg_spin.stop_spinning()
                            self.ChangeScreen()
                        elif answer == False:
                            self.prg_spin.stop_spinning()
                            threading.Thread(target=global_notify, args=(
                                "Username already taken",)).start()
                        elif answer == None:
                            self.prg_spin.stop_spinning()
                            threading.Thread(target=global_notify, args=(
                                "Oops! connection issue",)).start()
                    else:
                        threading.Thread(target=global_notify, args=(
                            "Enter valid email address",)).start()
                    self.prg_spin.stop_spinning()

                else:
                    if len(self.email_address.text) < 8:
                        threading.Thread(target=global_notify, args=(
                            "Email address too short",)).start()
                    elif len(self.full_name) < 5:
                        threading.Thread(target=global_notify, args=(
                            "first/second name too short",)).start()
                    else:
                        threading.Thread(target=global_notify, args=(
                            "Username taken",)).start()

                    self.prg_spin.stop_spinning()
                    self.manager.current = "registration_screen"

        except Exception as e:
            print(traceback.format_exc())
            threading.Thread(target=global_notify, args=(
                "Oops! Connection issue :-|",)).start()

    def ChangeScreen(self):
        self.prg_spin.stop_spinning()
        Tinkle().manage_screens("Chat", "add")
        self.manager.current = "Chat"

    def upload_data(self):
        try:
            soc = socket.socket()
            host = return_server_address()
            list_of_data = [self.temp_name.text,
                            self.full_name, self.email_address.text]
            dupped_list = json.dumps(list_of_data)
            soc.connect((host, port_data))
            soc.send(bytes(dupped_list, "utf-8"))
        except Exception as e:
            print(e)

    def delete_client_file(self):
        try:
            os.remove(client_file)
        except Exception as e:
            print(traceback.format_exc())


###############################################################

# Name: create_group_screen


class CreateGroupScreen(Screen):
    def __init__(self, **kwargs):
        super(CreateGroupScreen, self).__init__(**kwargs)

    def on_back_pressed(self, *args):
        Tinkle().change_screen("Chat")
        Tinkle().manage_screens("create_group_screen", "remove")

    def on_menu_pressed(self, *args):
        pass

    def create_group(self, group_name, group_description):
        global s
        if len(group_name) < 4:
            threading.Thread(target=global_notify,
                             args=("name too short",)).start()
        elif len(group_name) > 12:
            threading.Thread(target=global_notify,
                             args=("name too long",)).start()
        else:
            try:
                template = {}
                template["type"] = "create_group"
                template["group_name"] = group_name
                template["group_desc"] = group_description
                threading.Thread(target=self.send_data_in_thread,
                                 args=(s, template)).start()
                Tinkle().change_screen("Chat")
                Tinkle().manage_screens("create_group_screen", "remove")
            except:
                print(traceback.format_exc())

    def send_data_in_thread(self, s, template):
        try:
            s.send(bytes(json.dumps(template), "utf-8"))
        except:
            print("error sending group info")
            print(traceback.format_exc())


# Name: dump_screen


class DumpScreen(Screen):
    pass


# Name: names_for_status


class GetNamesForStatusScreen(Screen):
    global s

    def __init__(self, **kwargs):
        self.register_event_type('on_back_pressed')
        self.register_event_type('on_menu_pressed')
        super(GetNamesForStatusScreen, self).__init__(**kwargs)

    def on_back_pressed(self, *args):
        Tinkle().change_screen("Chat")
        Tinkle().manage_screens("display_status", "remove")

    def on_menu_pressed(self, *args):
        pass

    def do_checks(self, *args):
        if was_here_status == True:
            self.event.cancel()
            self.ids.ldml.clear_widgets()
            # print("adding names")
            for each_user in current_share_status:
                if len(each_user) >= 4:  # and each_user != A().get_the_name():
                    self.add_one_line(each_user)
            self.add_one_line(A().get_the_name())

    def on_enter(self):
        self.ldml = self.ids["ldml"]
        Tinkle().manage_screens("display_status", "remove")
        threading.Thread(target=self.send_background).start()
        self.event = Clock.schedule_interval(self.do_checks, 0.3)

    def send_background(self):
        template = {
            "type": "whoisonline--status"
        }
        s.send(bytes(json.dumps(template), "utf-8"))

    def add_one_line(self, data):
        self.ldml.add_widget(OneLineListItem(text=data,
                                             markup=True,
                                             text_size=(self.width, None),
                                             size_hint_y=None,
                                             font_size=(self.height / 20),
                                             on_press=lambda *args: self.change_to_doc(
                                                 data)))  # data is the clients' name

    def change_to_doc(self, status_client):
        with open(status_file, "wb") as f:
            f.write(status_client)
        Tinkle().manage_screens("display_status", "add")
        self.manager.current = "display_status"

    def on_leave(self):
        try:
            self.event.cancel()
        except:
            print(traceback.format_exc())
        Tinkle().manage_screens("names_for_status", "remove")


# Name: names_for_find_friends


class GetNamesForFindFriendsScreen(Screen):
    global s

    def __init__(self, **kwargs):
        self.register_event_type('on_back_pressed')
        self.register_event_type('on_menu_pressed')
        super(GetNamesForFindFriendsScreen, self).__init__(**kwargs)

    def on_back_pressed(self, *args):
        Tinkle().change_screen("Chat")

    def on_menu_pressed(self, *args):
        pass

    def do_checks(self, *args):
        if was_here_find_friends == True:
            self.event.cancel()
            self.ids.ldml.clear_widgets()
            print(current_find_friends)
            for each_user in current_find_friends:
                if len(each_user) >= 4:  # and A().get_the_name() not in each_user:
                    print(each_user)
                    self.add_one_line(each_user)

            print("done wif refreshing mate")

    def refresh_screen(self):
        print("doing the refresh tings")
        self.ldml = self.ids["ldml"]
        threading.Thread(target=self.send_background).start()
        self.event = Clock.schedule_interval(self.do_checks, 0.3)

    def send_background(self):
        template = {
            "type": "whoisonline--req_fri"
        }
        s.send(bytes(json.dumps(template), "utf-8"))

    def add_one_line(self, data):
        self.ldml.add_widget(
            OneLineListItem(text=data, on_release=lambda *args: self.change_to_img(data)))  # data is the clients' name

    def change_to_img(self, img_client):
        self.main_pop = MDDialog(
            title='Confirm', size_hint=(.8, .3), text_button_ok='Yes',
            text="Send friend request to %s?" % img_client,
            text_button_cancel='Cancel',
            events_callback=partial(self.do_sending, img_client))
        self.main_pop.open()

    def do_sending(self, img_client, *args):
        if args[0] == "Yes":
            a = {"type": "new_request", "req_name": img_client}
            s.send(bytes(json.dumps(a), "utf-8"))
            threading.Thread(target=global_notify, args=(
                "Request sent to " + img_client,)).start()
            create_file_sent_req(img_client)


# Name: names_for_friend_req


class GetNamesForFriendRequestsScreen(Screen):
    global s

    def __init__(self, **kwargs):
        self.register_event_type('on_back_pressed')
        self.register_event_type('on_menu_pressed')
        super(GetNamesForFriendRequestsScreen, self).__init__(**kwargs)

    def on_back_pressed(self, *args):
        Tinkle().change_screen("Chat")

    def on_menu_pressed(self, *args):
        pass

    def do_checks(self, *args):
        if was_here_friend_req == True:
            self.event.cancel()
            self.ids.ldml.clear_widgets()
            # print("adding names")
            for each_user in current_friend_req:
                if len(each_user) >= 4 and A().get_the_name() not in each_user:
                    self.add_one_line(each_user)

    def refresh_screen(self):
        print("doing the refreshing")
        self.ldml = self.ids["ldml"]
        self.event = Clock.schedule_interval(self.do_checks, 0.3)
        threading.Thread(target=self.send_background).start()

    def send_background(self):
        template = {
            "type": "whoisonline--acpt"
        }
        s.send(bytes(json.dumps(template), "utf-8"))

    def add_one_line(self, data):
        self.ldml.add_widget(OneLineListItem(text=data,
                                             markup=True,
                                             text_size=(self.width, None),
                                             size_hint_y=None,
                                             font_size=(self.height / 20),
                                             on_press=lambda *args: self.change_to_img(
                                                 data)))  # data is the clients' name

    def change_to_img(self, img_client):

        self.main_pop = MDDialog(
            title='Confirm', size_hint=(.8, .3), text_button_ok='Yes',
            text="Do you want to a friend request from %s?" % img_client,
            text_button_cancel='Cancel',
            events_callback=partial(self.callback_request, img_client))
        self.main_pop.open()

    def callback_request(self, img_client, *args):
        if args[0] == "Yes":
            self.call_accept_friend(img_client)
        else:
            self.call_reject_friend(img_client)

    def call_accept_friend(self, img_client):
        self.main_pop.dismiss
        a = {"type": "request_accept", "req_name": img_client}
        s.send(bytes(json.dumps(a), "utf-8"))
        try:
            self.main_pop.dismiss()
        except:
            pass
        delete_file_sent(img_client)
        # self.manager.current = "Chat"

    def call_reject_friend(self, img_client):
        self.main_pop.dismiss
        a = {"type": "reject_request", "req_name": img_client}
        s.send(bytes(json.dumps(a), "utf-8"))
        try:
            self.main_pop.dismiss()
        except Exception as e:
            pass
        delete_file_sent(img_client)
        # self.manager.current = "Chat"


# Name: names_for_friends_accept


class GetNamesForCurrentFriendsScreen(Screen):
    global s

    def __init__(self, **kwargs):
        self.register_event_type('on_back_pressed')
        self.register_event_type('on_menu_pressed')
        super(GetNamesForCurrentFriendsScreen, self).__init__(**kwargs)

    def on_back_pressed(self, *args):
        Tinkle().change_screen("Chat")

    def on_menu_pressed(self, *args):
        pass

    def do_checks(self, *args):
        if was_here_friends_accept == True:
            self.event.cancel()
            self.ids.ldml.clear_widgets()
            for each_user in current_friends_accept:
                if len(each_user) >= 4 and A().get_the_name() not in each_user:
                    self.add_one_line(each_user)

    # Get current friends from server
    def refresh_screen(self):
        self.ldml = self.ids["ldml"]
        self.event = Clock.schedule_interval(self.do_checks, 0.3)
        threading.Thread(target=self.send_background).start()

    def send_background(self):
        template = {
            "type": "whoisonline--friends"
        }
        s.send(bytes(json.dumps(template), "utf-8"))

    def add_one_line(self, data):
        self.ldml.add_widget(OneLineListItem(text=data,
                                             markup=True,
                                             text_size=(self.width, None),
                                             size_hint_y=None,
                                             font_size=(self.height / 20),
                                             on_press=lambda *args: self.change_to_img(
                                                 data)))  # data is the clients' name

    def change_to_img(self, img_client):
        global receiver_name
        receiver_name = img_client
        Tinkle().manage_screens("convo", "add")
        Tinkle().change_screen("convo")


class PopGroupInfo(Popup):
    def on_open(self):
        self.ml = self.ids["ml"]
        for k, v in group_info_dict.items():
            if k == "name":
                self.add_one_line("Group name: " + str(v))
            elif k == "creator":
                self.add_one_line("Created by: " + str(v))
            elif k == "admins":
                self.add_one_line("Admins: " + str(v))
            elif k == "creation_date":
                self.add_one_line("Date created: " + str(v))
            elif k == "description":
                self.add_one_line("Description: " + str(v))
            elif k == "num_members":
                self.add_one_line("Number of members " + str(v))

    def add_one_line(self, data):
        self.ml.add_widget(OneLineListItem(text=data,
                                           markup=True,
                                           text_size=(self.width, None),
                                           size_hint_y=None,
                                           font_size=(self.height / 20)))  # data is the clients' name


class PopGetGroups(Popup):

    def on_open(self):
        self.ml = self.ids["ml"]
        for k, v in ALL_GROUPS.items():
            together = v.split(":")
            gName = together[0]
            gDesc = together[1]
            self.add_two_line(gName, gDesc, k)

    def add_two_line(self, group_name, group_description, group_id):
        msg_to_add = group_name + ": " + group_description
        a = TwoLineListItem(text=msg_to_add,
                            secondary_text=group_id,
                            markup=True,
                            text_size=(self.width, None),
                            size_hint_y=None,
                            font_style="Body1",
                            on_release=partial(self.change_to_group_chat, group_name, group_description, group_id))
        self.ml.add_widget(a)

    def change_to_group_chat(self, g_name, g_description, g_id, *args):
        global group_name, current_group_id, current_group_desc
        group_name = g_name
        current_group_id = g_id
        current_group_desc = g_description
        Tinkle().manage_screens("group_convo", "add")
        self.close_popup()
        Tinkle().change_screen("group_convo")

    def close_popup(self):
        self.dismiss()


# Name: convo


class Conversation(Screen):
    global s

    def __init__(self, **kwargs):
        self.register_event_type('on_back_pressed')
        self.register_event_type('on_menu_pressed')
        super(Conversation, self).__init__(**kwargs)
        self.bs_menu_1 = None
        self.message = self.ids["message"]
        self.mld = self.ids["mld"]
        self.prev_msg = ""

    def initial_conditions(self):
        try:
            self.soc = socket.socket()
            self.soc.connect((return_server_address(), port_conditions))
            template = {
                "from": A().get_the_name(),
                "key": get_password(),
                "ls": str(time.ctime())
            }
            self.soc.send(bytes(json.dumps(template), "utf-8"))
        except Exception as e:
            print(e)

    def refresh_msgs(self):
        self.clear_log()
        threading.Thread(target=self.insert_data).start()

    def on_back_pressed(self, *args):
        Tinkle().change_screen("Chat")

    def on_menu_pressed(self, *args):
        pass

    def add_two_line(self, from_who, msg_to_add, prof_img):
        a = TwoLineListItem(text=msg_to_add, secondary_text=from_who)
        # a.add_widget(AvatarSampleWidget(source=prof_img))
        self.mld.add_widget(a)

    def add_three_line(self, from_who, msg_to_add, prof_img):
        a = ThreeLineListItem(text=msg_to_add[:70] + "...", secondary_text=from_who,
                              on_release=lambda *args: self.out_quick(from_who, msg_to_add))
        # a.add_widget(AvatarSampleWidget(source=prof_img))
        self.mld.add_widget(a)

    def clear_log(self):
        self.ids.mld.clear_widgets()

    def delete_logs(self):
        try:
            os.remove(self.full_path)
        except Exception as e:
            print(e)

    def insert_data(self):
        global receiver_name, new_data_to_add
        self.full_path = os.path.join(chats_directory, receiver_name)
        if check_if_exist(self.full_path) == False:
            create_file(self.full_path)
        else:
            results_of_log_check = return_file_log(self.full_path)
            if results_of_log_check != None:
                for mx in results_of_log_check:
                    if len(mx) > 0:
                        tx_name, tx_message, tx_prof_link = mx.split("`")
                        temp_link = re.findall(
                            'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', tx_prof_link)
                        tx_prof_link.replace(
                            temp_link[0], return_site_web_address()[:-1])
                        self.apply_correct(tx_name, tx_message, tx_prof_link)
        self.event = Clock.schedule_interval(self.handle_msg1, MSG_CHECK_DELAY)

    def on_enter(self):
        global IS_GROUP_MEDIA
        IS_GROUP_MEDIA = False
        threading.Thread(target=self.insert_data).start()
        threading.Thread(target=self.initial_conditions).start()

    def handle_msg1(self, *args):
        global new_data_to_add
        if self.prev_msg != new_data_to_add:
            self.apply_correct(
                new_data_to_add["from"], new_data_to_add["msg"], new_data_to_add["link"])
            self.prev_msg = new_data_to_add

    def apply_correct(self, the_name, the_message, prof_img=DEFAULT_STATUS):
        if the_name == A().get_the_name():
            the_name = "You"
        if len(the_message) > 80:
            self.add_three_line(the_name, the_message, prof_img)
        else:
            self.add_two_line(the_name, the_message, prof_img)

    def send_msg(self):
        global s
        try:
            # send the message to server
            check_bef_send = self.message.text.replace(" ", "")
            sanitized = self.message.text.replace("`", "")
            if len(check_bef_send) > 0 and len(check_bef_send) <= 250:
                template = {
                    "type": "private_message",
                    "msg": sanitized,
                    "to": receiver_name,
                    "from_who": A().get_the_name()
                }
                s.send(bytes(json.dumps(template), "utf-8"))  # get the name
                self.message.text = ""
        except Exception as e:
            # self.data.text += "An error occured while sending."
            threading.Thread(target=global_notify, args=(
                "Unable to send message",)).start()
            print(traceback.format_exc())

    def show_bottom_sheet(self):
        if not self.bs_menu_1:
            self.bs_menu_1 = MDListBottomSheet()
            self.bs_menu_1.add_item(
                "Share image",
                lambda x: self.decide_share_image())
            self.bs_menu_1.add_item(
                "Share audio",
                lambda x: self.callback_for_menu_items(
                    "for_selecting_audio"))
            self.bs_menu_1.add_item(
                "Share file",
                lambda x: self.callback_for_menu_items(
                    "for_selecting_docs"))
            self.bs_menu_1.add_item(
                "Refresh",
                lambda x: self.refresh_msgs())
            self.bs_menu_1.add_item(
                "Clear chat",
                lambda x: self.clear_log())
            self.bs_menu_1.add_item(
                "Delete chat",
                lambda x: self.delete_logs())
            self.bs_menu_1.add_item(
                "Back",
                lambda x: self.callback_for_menu_items(
                    "Chat"))
        self.bs_menu_1.open()

    def callback_for_menu_items(self, scn):
        try:
            # Tinkle().manage_screens(scn, "add")
            Tinkle().change_screen(scn)
        except:
            print(traceback.format_exc())

    def decide_share_image(self):
        if isAndroid() == True:
            self.android_share_image()
        else:
            Tinkle().manage_screens("for_selecting", "add")
            Tinkle().change_screen("for_selecting")

    def android_share_image(self):
        try:
            if isAndroid() == True:
                import android_image_select
                reload(android_image_select)
                android_image_select.user_select_image(
                    self.start_callback_in_thread)
                reload(android_image_select)
            else:
                print("Not Android")

        except:
            print(traceback.format_exc())

    def start_callback_in_thread(self, path):
        if path != None:
            bx = GridLayout(rows=2, cols=1)
            bx.add_widget(Image(source=path))
            btns_layout = GridLayout(
                rows=1, cols=2, size_hint_y=None, height=60)
            btns_layout.add_widget(MDRaisedButton(size_hint_y=None, height=self.parent.height * 0.111,
                                                  text="Cancel", on_release=self.can))
            btns_layout.add_widget(MDRaisedButton(size_hint_y=None, height=self.parent.height * 0.111,
                                                  text="Send", on_release=partial(self.pro, path)))
            bx.add_widget(btns_layout)
            self.bagPop = Popup(title="Back to cancel",
                                content=bx)

            self.bagPop.open()

        else:
            print("No image selected.")

    def pro(self, path, *args):
        print("proceed")
        threading.Thread(target=self._gallery_callback, args=(path,)).start()
        self.bagPop.dismiss()

    def can(self, *args):
        print("cancel")
        self.bagPop.dismiss()

    def _gallery_callback(self, path):
        self.filename = path
        try:
            if exceedLimit(self.filename) == True:
                threading.Thread(target=global_notify,
                                 args=("File exceeds 15MB limit",)).start()
                return
            condition = doHashCheckServer(self.filename, "image")
            if condition[0] == True:
                should_do_upload = False
                complete_link = condition[1]
            else:
                should_do_upload = True
        except:
            should_do_upload = True

        url_for_img = return_site_web_address() + "man_images.php"
        url_for_img_no_php = return_site_web_address() + "img/"
        c_extension = os.path.splitext(self.filename)[1]

        if c_extension in avail_img_ext:
            extension = c_extension
            my_name = str(A().get_the_name())
            tempo_img_file = my_name + "-" + \
                             ''.join(random.choice(string.ascii_lowercase + string.digits)
                                     for _ in range(7)) + extension

            with open(self.filename, "rb") as f:
                orag = f.read()
            with open(tempo_img_file, "wb") as fb:
                fb.write(orag)
            link_img = url_for_img_no_php + tempo_img_file
            bibo = {}
            bibo["type"] = "image"
            bibo["link"] = link_img
            bibo["to"] = receiver_name
            if should_do_upload == True:
                threading.Thread(target=self.upload_image, args=(
                    tempo_img_file, url_for_img, bibo)).start()
                threading.Thread(target=global_notify, args=(
                    "Sharing in background",)).start()
            else:
                bibo["link"] = complete_link
                s.send(bytes(json.dumps(bibo), "utf-8"))
                self.remove_file(tempo_img_file)
                threading.Thread(target=global_notify, args=(
                    "Upload complete, used cache",)).start()

    def upload_image(self, fname, urlll, dumped_list):
        with open(fname, "rb") as f:
            files = {'testname': f}
            r = requests.post(urlll, files=files)
        s.send(bytes(json.dumps(dumped_list), "utf-8"))
        threading.Thread(target=global_notify,
                         args=("upload complete",)).start()
        self.remove_file(fname)

    def remove_file(self, fname):
        try:
            os.remove(fname)
        except:
            pass

    def on_leave(self):
        global new_data_to_add
        self.prev_msg = ""
        try:

            self.event2.cancel()
            self.event3.cancel()
        except Exception as e:
            print(traceback.format_exc())
        try:
            self.soc.close()
        except Exception as e:
            print(traceback.format_exc())
        new_data_to_add = ""
        Tinkle().manage_screens("names_for_friends_accept", "add")
        self.ids.mld.clear_widgets()


# Name: group_convo


class GroupConversation(Screen):
    global s

    def __init__(self, **kwargs):
        self.register_event_type('on_back_pressed')
        self.register_event_type('on_menu_pressed')
        super(GroupConversation, self).__init__(**kwargs)
        self.message = self.ids["message"]
        self.mld = self.ids["mld"]
        self.prev_msg = ""
        self.bs_menu_1 = None

    def on_enter(self):
        global IS_GROUP_MEDIA
        IS_GROUP_MEDIA = True
        if OLD_GROUP_ID != current_group_id:
            self.clear_log()
            threading.Thread(target=self.insert_data).start()

    def refresh_msgs(self):
        self.clear_log()
        threading.Thread(target=self.insert_data).start()

    def on_back_pressed(self, *args):
        Tinkle().change_screen("Chat")

    def on_menu_pressed(self, *args):
        pass

    def add_two_line(self, from_who, msg_to_add, prof_img):
        a = TwoLineListItem(text=msg_to_add, secondary_text=from_who)
        # a.add_widget(AvatarSampleWidget(source=prof_img))
        self.mld.add_widget(a)

    def add_three_line(self, from_who, msg_to_add, prof_img):
        a = ThreeLineAvatarListItem(text=msg_to_add[:70] + "...",
                                    secondary_text=from_who,
                                    markup=True,
                                    text_size=(self.width, None),
                                    size_hint_y=None,
                                    font_style="Body1",
                                    on_release=lambda *args: self.out_quick(from_who, msg_to_add))
        a.add_widget(AvatarSampleWidget(source=prof_img))
        self.mld.add_widget(a)

    def clear_log(self):
        self.ids.mld.clear_widgets()

    # group texts not saved yet so won't work
    def delete_logs(self):
        try:
            os.remove(self.full_path)
        except Exception as e:
            print(e)

    def insert_data(self):
        self.event = Clock.schedule_interval(self.handle_msg1, MSG_CHECK_DELAY)

    def handle_msg1(self, *args):
        # print("checking for messages")
        global new_data_to_add_group
        if self.prev_msg != new_data_to_add_group:
            # print(new_data_to_add_group)
            self.apply_correct(
                new_data_to_add_group["from"], new_data_to_add_group["msg"], new_data_to_add_group["link"])
            self.prev_msg = new_data_to_add_group

    def apply_correct(self, the_name, the_message, prof_img=DEFAULT_STATUS):
        if the_name == A().get_the_name():
            the_name = "You"
        if len(the_message) > 80:
            self.add_three_line(the_name, the_message, prof_img)
        else:
            self.add_two_line(the_name, the_message, prof_img)

    def send_msg(self):
        global s
        try:
            # send the message to server
            check_bef_send = self.message.text.replace(" ", "")
            sanitized = self.message.text.replace("`", "")
            if len(check_bef_send) > 0 and len(check_bef_send) <= 250:
                template = {
                    "type": "group_message",
                    "msg": sanitized,
                    "group_id": current_group_id,
                    "from_who": A().get_the_name()
                }
                s.send(bytes(json.dumps(template), "utf-8"))  # get the name
                self.message.text = ""
        except Exception as e:
            threading.Thread(target=global_notify, args=(
                "Unable to send message",)).start()

    def show_bottom_sheet(self):
        if not self.bs_menu_1:
            self.bs_menu_1 = MDListBottomSheet()
            self.bs_menu_1.add_item(
                "Share image",
                lambda x: self.decide_share_image())
            self.bs_menu_1.add_item(
                "Share audio",
                lambda x: self.callback_for_menu_items(
                    "for_selecting_audio"))
            self.bs_menu_1.add_item(
                "Share file",
                lambda x: self.callback_for_menu_items(
                    "for_selecting_docs"))
            self.bs_menu_1.add_item(
                "Extra bits",
                lambda x: self.callback_for_menu_items(
                    "advanced_screen"))
            self.bs_menu_1.add_item(
                "Refresh",
                lambda x: self.refresh_msgs())
            self.bs_menu_1.add_item(
                "Clear chat",
                lambda x: self.clear_log())
            self.bs_menu_1.add_item(
                "Back",
                lambda x: self.callback_for_menu_items(
                    "Chat"))
        self.bs_menu_1.open()

    def callback_for_menu_items(self, scn):
        try:
            Tinkle().manage_screens(scn, "add")
            Tinkle().change_screen(scn)
        except:
            print(traceback.format_exc())

    def decide_share_image(self):
        if isAndroid() == True:
            self.android_share_image()
        else:
            Tinkle().manage_screens("for_selecting", "add")
            Tinkle().change_screen("for_selecting")

    def android_share_image(self):
        try:
            if isAndroid() == True:
                import android_image_select
                reload(android_image_select)
                android_image_select.user_select_image(
                    self.start_callback_in_thread)
                reload(android_image_select)
            else:
                print("Not Android")

        except:
            print(traceback.format_exc())

    def start_callback_in_thread(self, path):
        if path != None:
            bx = GridLayout(rows=2, cols=1)
            bx.add_widget(Image(source=path))
            btns_layout = GridLayout(
                rows=1, cols=2, size_hint_y=None, height=60)
            btns_layout.add_widget(MDRaisedButton(size_hint_y=None, height=self.parent.height * 0.111,
                                                  text="Cancel", on_release=self.can))
            btns_layout.add_widget(MDRaisedButton(size_hint_y=None, height=self.parent.height * 0.111,
                                                  text="Send", on_release=partial(self.pro, path)))
            bx.add_widget(btns_layout)
            self.bagPop = Popup(title="Back to cancel",
                                content=bx)

            self.bagPop.open()

        else:
            print("No image selected.")

    def pro(self, path, *args):
        print("proceed")
        threading.Thread(target=self._gallery_callback, args=(path,)).start()
        self.bagPop.dismiss()

    def can(self, *args):
        print("cancel")
        self.bagPop.dismiss()

    def _gallery_callback(self, path):
        self.filename = path
        try:
            if exceedLimit(self.filename) == True:
                threading.Thread(target=global_notify,
                                 args=("File exceeds 15MB limit",)).start()
                return
            condition = doHashCheckServer(self.filename, "image")
            if condition[0] == True:
                should_do_upload = False
                complete_link = condition[1]
            else:
                should_do_upload = True
        except:
            should_do_upload = True

        url_for_img = return_site_web_address() + "man_images.php"
        url_for_img_no_php = return_site_web_address() + "img/"
        c_extension = os.path.splitext(self.filename)[1]

        if c_extension in avail_img_ext:
            extension = c_extension
            my_name = str(A().get_the_name())
            tempo_img_file = my_name + "_" + \
                             ''.join(random.choice(string.ascii_lowercase + string.digits)
                                     for _ in range(7)) + extension

            with open(self.filename, "rb") as f:
                orag = f.read()
            with open(tempo_img_file, "wb") as fb:
                fb.write(orag)
            link_img = url_for_img_no_php + tempo_img_file
            bibo = {}
            bibo["type"] = "image"
            bibo["link"] = link_img
            bibo["group_based"] = True
            bibo["group_id"] = current_group_id
            if should_do_upload == True:
                threading.Thread(target=self.upload_image, args=(
                    tempo_img_file, url_for_img, bibo)).start()
                threading.Thread(target=global_notify, args=(
                    "Sharing in background",)).start()
            else:
                bibo["link"] = complete_link
                s.send(bytes(json.dumps(bibo), "utf-8"))
                self.remove_file(tempo_img_file)
                threading.Thread(target=global_notify, args=(
                    "Upload complete, used cache",)).start()

    def upload_image(self, fname, urlll, dumped_list):
        with open(fname, "rb") as f:
            files = {'testname': f}
            r = requests.post(urlll, files=files)
        s.send(bytes(json.dumps(dumped_list), "utf-8"))
        threading.Thread(target=global_notify,
                         args=("upload complete",)).start()
        self.remove_file(fname)

    def remove_file(self, fname):
        try:
            os.remove(fname)
        except:
            pass

    def on_leave(self):
        global new_data_to_add, OLD_GROUP_ID
        OLD_GROUP_ID = current_group_id
        # self.prev_msg = ""
        # new_data_to_add = ""

        # Tinkle().manage_screens("group_convo", "remove")
        # Tinkle().manage_screens("advanced_screen", "remove")
        Tinkle().manage_screens("group_members", "remove")
        Tinkle().manage_screens("names_friends_group", "remove")
        try:
            self.event.cancel()
        except:
            pass

        # self.ids.mld.clear_widgets()


class GenericPop:
    def pop_it(self):
        popup = Popup(title="Stopped",
                      content=Label(text="Tap outside"),
                      size_hint=(.6, .6), pos_hint={'x': .2, 'y': .2})
        popup.open()


class MyFileChooser(FileChooserIconView):
    filters = fil_avail_img_ext
    rootpath = home

    # FileChooserIconView.filters = fil_avail_img_ext

    def on_selection(self, *args):
        self.preview_img(args[1][0])

    def on_submit(*args):
        global fp
        fp = args[1][0]
        popup.dismiss()
        Status().upload_status(fp)

    def preview_img(self, src):
        popup = Popup(title="Press escape to close",
                      content=Image(source=src))
        popup.open()


# Name: status_screen


class Status(Screen):
    def __init__(self, **kwargs):
        global s
        self.register_event_type('on_back_pressed')
        self.register_event_type('on_menu_pressed')
        super(Status, self).__init__(**kwargs)
        self.btn_set_pic = self.ids["btn_set_pic"]

    def on_back_pressed(self, *args):
        Tinkle().change_screen("Chat")

    def on_menu_pressed(self, *args):
        pass

    def select_pic(self, ssa):
        global popup, text_to_send
        text_to_send = ssa
        if isAndroid() == True:
            import android_image_select
            reload(android_image_select)
            android_image_select.user_select_image(self.begin_after_gallery)
            reload(android_image_select)

        else:
            popup = Popup(title='Select File',
                          content=MyFileChooser())
            popup.open()

    def id_generator(self, size=10, chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def begin_after_gallery(self, path):
        if path != None:
            # Confirming
            bx = BoxLayout()
            bx.add_widget(Image(source=path))
            bx.add_widget(MDRaisedButton(size_hint=(0.1, 0.1),
                                         text="cancel", on_release=self.can))
            bx.add_widget(MDRaisedButton(size_hint=(0.1, 0.1),
                                         text="send", on_release=self.pro))
            self.bagPop = Popup(title="Press back to close",
                                content=bx)

            self.bagPop.open()

        else:
            print("No image selected.")

    def pro(self, *args):
        print("proceed")
        threading.Thread(target=self.upload_status, args=(path,)).start()
        self.bagPop.dismiss()

    def can(self, *args):
        print("cancel")
        self.bagPop.dismiss()

    def upload_status(self, fname):
        global text_to_send
        extension = os.path.splitext(fname)[1]
        new_name = "status_" + self.id_generator() + extension
        if exceedLimit(fname) == True:
            threading.Thread(target=global_notify,
                             args=("File exceeds 15MB limit",)).start()
            return
        with open(new_name, "wb") as temp:
            with open(fname, "rb") as temp2:
                temp.write(temp2.read())

        with open(new_name, "rb") as f:
            files = {'testname': f}
            r = requests.post(return_site_web_address() +
                              "man_status.php", files=files)
        site_path = return_site_web_address() + "status/" + new_name

        template = {"type": "status_update",
                    "text": text_to_send,
                    "from": A().get_the_name(),
                    "link": site_path}
        try:
            s.send(bytes(json.dumps(template), "utf-8"))
            threading.Thread(target=global_notify, args=(
                "status update complete",)).start()
        except BaseException as e:
            print(traceback.format_exc())
            threading.Thread(target=global_notify, args=(
                "status failed to update",)).start()
        self.remove_file(new_name)
        if isAndroid() == True:
            pass
        else:
            Tinkle().change_screen("Chat")

    def remove_file(self, filename):
        try:
            os.remove(filename)
        except BaseException as e:
            pass

    def on_leave(self):
        Tinkle().manage_screens("status_screen", "remove")


# Name: display_status


class DisplayStatus(Screen):
    def __init__(self, **kwargs):
        super(DisplayStatus, self).__init__(**kwargs)
        self.comment = self.ids["comment"]
        self.act_view = self.ids["act_view"]
        self.register_event_type('on_back_pressed')
        self.register_event_type('on_menu_pressed')

    img_src = StringProperty(DEFAULT_STATUS)
    txt_stat = StringProperty("loading...")
    global s, global_status_pic, global_status_text

    def on_back_pressed(self, *args):
        Tinkle().manage_screens("names_for_status", "add")
        Tinkle().change_screen("names_for_status")
        Tinkle().manage_screens("display_status", "remove")

    def on_menu_pressed(self, *args):
        pass

    def calling(self, *args):
        Tinkle().manage_screens("view_status_comments", "add")
        # open replies screen
        Tinkle().change_screen("view_status_comments")

    def send_status_comment(self):
        try:
            if len(self.comment.text) > 0:
                threading.Thread(target=global_notify,
                                 args=("sending reply...",)).start()
                template = {}
                template["type"] = "status_comment"
                template["to"] = self.the_target_name
                template["msg"] = self.comment.text
                try:
                    s.send(bytes(json.dumps(template), "utf-8"))
                except Exception as e:
                    pass
                self.comment.text = ""
            else:
                threading.Thread(target=global_notify, args=(
                    "enter valid text",)).start()
        except Exception as e:
            threading.Thread(target=global_notify, args=(
                "can't send comment",)).start()

    def on_enter(self):
        template = {}
        Tinkle().manage_screens("names_for_status", "remove")
        from kivy.uix.actionbar import ActionBar  # crashes if import outside
        from kivy.uix.actionbar import ActionButton
        with open(status_file, "rb") as f:
            self.the_target_name = f.read()
        if self.the_target_name == A().get_the_name():
            self.reps_button = ActionButton(
                size_hint_x=None, size=self.size, text="replies", font_size=sp(18))
            self.reps_button.bind(on_release=self.calling)
            self.act_view.add_widget(self.reps_button)
        template["type"] = "status_get"
        template["which_user"] = self.the_target_name
        s.send(bytes(json.dumps(template), "utf-8"))
        self.event = Clock.schedule_interval(self.update_things, 2)

    def update_things(self, dt):
        global ishere
        if ishere == False:
            if global_status_pic != "":
                self.img_src = global_status_pic
                self.txt_stat = global_status_text
                if self.the_target_name == A().get_the_name():
                    self.comment.disabled = True
                else:
                    self.comment.disabled = False
                self.event.cancel()
                # Clock.unschedule(self.update_things)

    def show_img_pop(self, src):
        the_pic = AsyncImage(source=src)
        popup = Popup(title="",
                      content=the_pic)
        popup.open()

    def save_status(self):
        threading.Thread(target=self._download_status).start()

    def _download_status(self):
        if self.img_src != DEFAULT_STATUS:
            url = self.img_src
            local_filename = url.split('/')[-1]
            abs_local_filename = os.path.join(path_images, local_filename)
            # NOTE the stream=True parameter
            r = requests.get(url, stream=True)
            try:

                with open(abs_local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)
                threading.Thread(target=global_notify, args=(
                    "Saved:" + abs_local_filename,)).start()
            except:
                threading.Thread(target=global_notify, args=(
                    "Error while saving status",)).start()

    def on_leave(self):
        try:
            self.act_view.remove_widget(self.reps_button)
            self.event.cancel()

        except Exception as e:
            print(traceback.format_exc())


# Name: view_status_comments


class StatusComments(Screen):
    def __init__(self, **kwargs):
        super(StatusComments, self).__init__(**kwargs)
        self.ml = self.ids["ml"]

    def on_back_pressed(self, *args):
        Tinkle().manage_screens("status_comment", "remove")
        Tinkle().change_screen("display_status")

    def on_menu_pressed(self, *args):
        pass

    def on_enter(self):
        if check_if_exist(comments_status_db_file) == True:
            db = dataset.connect(comments_db_name)
            table = db['comments']
            for user in db["comments"]:
                self.apply_correct(user["name"], user["msg"], user["link"])
        else:
            self.add_two_line(
                "self", "No comments yet, come back later", DEFAULT_STATUS)

    def apply_correct(self, the_name, the_message, prof_img):
        if len(the_message) > 80:
            self.add_three_line(the_name, the_message, prof_img)
        else:
            self.add_two_line(the_name, the_message, prof_img)

    def add_two_line(self, from_who, msg_to_add, prof_img):
        a = TwoLineAvatarListItem(text=msg_to_add, secondary_text=from_who)
        # a.add_widget(AvatarSampleWidget(source=prof_img))
        self.ml.add_widget(a)

    def add_three_line(self, from_who, msg_to_add, prof_img):
        a = ThreeLineAvatarListItem(text=msg_to_add[:38] + "...",
                                    secondary_text=from_who,
                                    markup=True,
                                    text_size=(self.width, None),
                                    size_hint_y=None,
                                    font_style="Body1",
                                    on_press=lambda *args: self.out_quick(from_who, msg_to_add))
        a.add_widget(AvatarSampleWidget(source=prof_img))
        self.ml.add_widget(a)

    def on_leave(self):
        self.ml.clear_widgets()
        Tinkle().manage_screens("status_comment", "remove")


# Name: Chat


class Chat(Screen):

    def __init__(self, **kwargs):
        super(Chat, self).__init__(**kwargs)
        self.message = self.ids["message"]
        self.ml = self.ids["ml"]
        self.bs_menu_1 = None
        self.bs_menu_2 = None

    def callback_for_menu_items(self, sc):
        if sc == "profile_Pic":
            if isAndroid() == True:
                pass
            else:
                Tinkle().manage_screens(sc, "add")
                Tinkle().change_screen(sc)
        else:
            Tinkle().manage_screens(sc, "add")
            Tinkle().change_screen(sc)

    def show_bottom_sheet(self):
        if not self.bs_menu_1:
            self.bs_menu_1 = MDListBottomSheet()
            self.bs_menu_1.add_item(
                "Friends",
                lambda x: self.callback_for_menu_items(
                    "names_for_friends_accept"))
            self.bs_menu_1.add_item(
                "Find Friends",
                lambda x: self.callback_for_menu_items(
                    "names_for_find_friends"))
            self.bs_menu_1.add_item(
                "Refresh",
                lambda x: self.refresh_msgs())
            self.bs_menu_1.add_item(
                "Clear chat",
                lambda x: self.clear_log())
            self.bs_menu_1.add_item(
                "Delete chat",
                lambda x: self.delete_logs())
        self.bs_menu_1.open()

    def show_bottom_sheet_chat(self):
        if not self.bs_menu_2:
            self.bs_menu_2 = MDListBottomSheet()
            self.bs_menu_2.add_item(
                "Groups",
                lambda x: self.get_groups_list())

            self.bs_menu_2.add_item(
                "Refresh",
                lambda x: self.refresh_msgs())
            self.bs_menu_2.add_item(
                "Clear chat",
                lambda x: self.clear_log())
            self.bs_menu_2.add_item(
                "Settings",
                lambda x: Tinkle().open_settings())
            self.bs_menu_2.add_item(
                "Options",
                lambda x: self.show_more_options())
            self.bs_menu_2.add_item(
                "Tinkle",
                lambda x: self.show_about())
        self.bs_menu_2.open()

    def get_groups_list(self):
        template = {}
        template["type"] = "get_groups"
        s.send(bytes(json.dumps(template), "utf-8"))

    def add_one_line(self, data):
        self.ml.add_widget(OneLineListItem(text=data))

    def add_one_line_special(self, data, from_who):
        self.ml.add_widget(OneLineListItem(text=data, on_release=lambda *args: self.change_convo(from_who)))

    def change_convo(self, name_from):
        global receiver_name
        receiver_name = name_from
        Tinkle().manage_screens("convo", "add")
        Tinkle().change_screen("convo")

    def add_two_line(self, from_who, msg_to_add, prof_img):
        a = TwoLineListItem(text=msg_to_add, secondary_text=from_who)
        # a.add_widget(AvatarSampleWidget(source=prof_img))
        self.ml.add_widget(a)

    def add_three_line(self, from_who, msg_to_add, prof_img):
        a = ThreeLineAvatarListItem(text=msg_to_add[:70] + "...",
                                    secondary_text=from_who,
                                    markup=True,
                                    text_size=(self.width, None),
                                    size_hint_y=None,
                                    font_style="Body1",
                                    on_press=lambda *args: self.out_quick(from_who, msg_to_add))
        a.add_widget(AvatarSampleWidget(source=prof_img))
        self.ml.add_widget(a)

    def show_about(self):
        about_text = "Made with love from my room ;-)\nSend reports, issues or improvements to:\n[insertemail]@gmail.com OR +26481XXXX"
        content = MDLabel(font_style='Subtitle2', text=about_text)
        content.bind(texture_size=content.setter('size'))
        self.dialog = MDDialog(title="Tinkle Messenger", content=content)

        # self.dialog.add_action_button("Dismiss",
        #                               action=lambda *x: self.dialog.dismiss())
        self.dialog.open()

    def out_quick(self, thefrom, themsg):
        box = GridLayout(rows=2)
        box.add_widget(
            MDTextField(readonly=True, text=themsg, multiline=True, background_color=get_color_from_hex(chat_clr_value),
                        background_normal="",
                        auto_dismiss=False))
        box.add_widget(MDRaisedButton(
            text="dismiss", on_release=lambda *args: popup.dismiss()))

        popup = Popup(title=thefrom, content=box)
        popup.open()

    def call_generic_pop_from_kv(self):
        GenericPop().pop_it()

    def clear_log(self):
        self.ids.ml.clear_widgets()

    def pop1(self, src):
        popup = Popup(title="Please wait for image to load",
                      content=src)
        popup.open()

    def download_file_arbi(self, url, media_type=""):
        if 1 == 0:  # isAndroid() == True:
            import permission_helper
            perms = ["android.permission.READ_EXTERNAL_STORAGE",
                     "android.permission.WRITE_EXTERNAL_STORAGE"]

            haveperms = permission_helper.acquire_permissions(perms)
            print(haveperms)
        if media_type == "audio":
            local_filename = os.path.join(path_music, url.split('/')[-1])
        elif media_type == "image":
            local_filename = os.path.join(path_images, url.split('/')[-1])
        elif media_type == "document":
            local_filename = os.path.join(path_docs, url.split('/')[-1])
        # NOTE the stream=True parameter
        r = requests.get(url, stream=True)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        self.add_one_line("File saved here: " + local_filename)
        return local_filename

    def download_audio(self, url_audio, audio_name):
        try:

            location_audio = self.download_file_arbi(url_audio, "audio")

        except BaseException as e:
            threading.Thread(target=global_notify, args=(
                "Error occured while downloading audio file",)).start()

    def download_doc(self, url_doc, doc_name):
        try:
            global path_docs
            self.download_file_arbi(url_doc, "document")
        except BaseException as e:
            threading.Thread(target=global_notify, args=(
                "Unable to download document",)).start()

    def download_image(self, url_img, img_name_new):
        try:
            saved_img = self.download_file_arbi(url_img, "image")
            try:
                with open("atp_img.dat", "rb") as f:
                    chosen = f.read()
                    if chosen == "1":
                        # "https://pbs.twimg.com/profile_images/763046576050757632/1KdfLvwt.jpg"
                        the_pic = AsyncImage(source=saved_img)
                        self.pop1(the_pic)
            except BaseException as e:
                print(traceback.format_exc())

        except BaseException as e:
            print(traceback.format_exc())
            threading.Thread(target=global_notify, args=(
                "Unable to save image",)).start()

    def PlayAudio(self, audio_name):
        global tmp
        try:
            tmp.play()
        except Exception as e:
            pass

    def refresh_msgs(self):
        self.clear_log()
        results_of_log_check = self.read_messages_from_log()
        if results_of_log_check != None:
            for mx in results_of_log_check:
                if len(mx) > 0:
                    tx_name, tx_message, tx_prof_link = mx.split("`")
                    self.apply_correct(tx_name, tx_message, tx_prof_link)

    def send_msg(self):
        global s, the_key
        try:
            # send the message to server
            check_bef_send = self.message.text.replace(" ", "")
            sanitized = self.message.text.replace("`", "")
            if len(check_bef_send) > 0 and len(check_bef_send) <= 250:
                template = {
                    "type": "broadcast",
                    "from": A().get_the_name(),
                    "msg": self.message.text,
                }
                s.send(bytes(json.dumps(template), "utf-8"))  # get the name
                self.message.text = ""
        except Exception as e:
            # self.data.text += "An error occured while sending."
            threading.Thread(target=global_notify, args=(
                "Error: Unable to send message",)).start()

    def split_data(self, data):
        point = data.find("-")
        the_name = data[:point - 1]
        the_message = data[point + 2:]
        if point == -1:
            the_name = None
            the_message = data
        return the_name, the_message

    def apply_correct(self, the_name, the_message, prof_img=DEFAULT_STATUS):
        if len(the_message) > 80:
            self.add_three_line(the_name, the_message, prof_img)
        else:
            self.add_two_line(the_name, the_message, prof_img)

    def delete_logs(self, *args):
        global save_messages_file
        try:
            os.remove(save_messages_file)
            threading.Thread(target=global_notify,
                             args=("logs removed",)).start()
        except Exception as e:
            threading.Thread(target=global_notify, args=(
                "unable to delete file",)).start()
        try:
            self.dialog.dismiss()
        except:
            pass

    def write_the_message(self, the_name, the_message, prof_img):
        global save_messages_file
        together = the_name + "`" + the_message + "`" + prof_img + "\n"
        if os.path.exists(save_messages_file):
            append_write = 'a'  # append if already exists
        else:
            append_write = 'w'  # make a new file if not
        with codecs.open(save_messages_file, append_write) as f:
            f.write(together)

    def read_messages_from_log(self):
        global save_messages_file
        if os.path.exists(save_messages_file):
            with open(save_messages_file, "r") as f:
                new_log = []
                raw_log = f.read().split('\n')
                for i in raw_log:
                    if len(i) > 0:
                        new_log.append(i)
                return new_log
        else:
            return None

    def show_more_options(self, *args):

        txt = "1. Delete messages\n2. Create Group\n3. Create backup"
        content = MDLabel(font_style='Subhead',
                          text=txt,
                          size_hint_y=None,
                          valign='top')

        content.bind(texture_size=content.setter('size'))
        self.dialog = MDDialog(title="Options",
                               content=content,
                               auto_dismiss=True)
        self.dialog.add_action_button("1",
                                      action=partial(self.delete_logs))
        self.dialog.add_action_button("2",
                                      action=partial(self.change_to_create_group))
        self.dialog.add_action_button("3",
                                      action=partial(self._start_backup))
        self.dialog.open()

    def _start_backup(self, *args):
        threading.Thread(target=Tinkle().client_backup).start()
        self.dialog.dismiss()

    def change_to_create_group(self, *args):
        Tinkle().manage_screens("create_group_screen", "add")
        self.dialog.dismiss()
        Tinkle().change_screen("create_group_screen")

    def call_change_profile_pic(self, *args):
        threading.Thread(target=ChangeProPic().get_rolling).start()

    def msgg(self):
        global s, name
        global thecurrentonline, check_if_got
        global current_share_img, was_here_img
        global current_share_aud, was_here_aud
        global current_share_doc, was_here_doc
        global current_share_status, was_here_status
        global current_find_friends, was_here_find_friends
        global current_friends_accept, was_here_friends_accept
        global current_friend_req, was_here_friend_req
        global global_status_text, global_status_pic
        global new_data_to_add, receiver_name, new_data_to_add_group
        global was_here_members_group, current_group_members
        location_notification = os.path.join(os.getcwd(), "song.mp3")

        while True:  # Here is msgg function loop
            try:
                data = s.recv(1024).decode("utf-8")  # FF1102
                data = json.loads(data)
                type_msg = data["type"]
                try:
                    data["msg"]
                except:
                    # print(traceback.format_exc())
                    data["msg"] = "empty_null"
                if type_msg == "private_message":
                    try:  # if screen is private pass to convo else write to file
                        if sm.current == "convo" and data["from"] == receiver_name or data[
                            "from"] == A().get_the_name():
                            append_to_file(receiver_name, data)
                            new_data_to_add = data
                            type_msg = ""
                            data = ""
                        else:
                            if check_if_exist(os.path.join(chats_directory, data["from"])) == True:
                                # append to file
                                append_to_file(data["from"], data)
                                # setting if user wants notification one line
                                self.add_one_line_special(
                                    "New text: " + data["from"], data["from"])
                                Snackbar(text="New text from " + data["from"], button_text="open",
                                         button_callback=partial(
                                             self.change_convo, data["from"])).show()

                                if data["from"] != A().get_the_name():
                                    threading.Thread(target=self.PlayAudio, args=(
                                        location_notification,)).start()
                                type_msg = ""
                                data = ""

                            else:
                                create_file(os.path.join(
                                    chats_directory, data["from"]))
                                # append to file
                                append_to_file(data["from"], data)
                                self.add_one_line(
                                    "Text from: " + data["from"])
                                Snackbar(text="New text from " + data["from"], button_text="open",
                                         button_callback=partial(
                                             self.change_convo, data["from"])).show()

                                if data["from"] != A().get_the_name():
                                    threading.Thread(target=self.PlayAudio, args=(
                                        location_notification,)).start()
                                type_msg = ""
                                data = ""

                    except Exception as e:
                        print("Cannot play ring:", e)
                if type_msg == "group_message":
                    try:  # if screen is private pass to convo else write to file
                        if sm.current == "group_convo" and data["group_identifier"] == current_group_id or data[
                            "from"] == A().get_the_name():
                            # append_to_file(receiver_name, data)
                            new_data_to_add_group = data
                            type_msg = ""
                            data = ""

                    except Exception as e:
                        print(e)
                if type_msg == "image":
                    # from_who_img, url_img, img_name = self.parse_image(data)
                    from_who_img = data["from"]
                    url_img = data["link"]
                    img_name = data["link"][:-7]
                    img_name_new = from_who_img + "-" + img_name
                    threading.Thread(target=self.download_image, args=(
                        url_img, img_name_new)).start()
                    data = ""

                elif type_msg == "audio":  # Note: make like docs parser
                    from_who_aud = data["from"]
                    url_aud = data["link"]
                    aud_name = data["link"][:-7]
                    threading.Thread(target=global_notify, args=(
                        "Receiving soundclip from" + from_who_aud,)).start()
                    aud_name_new = from_who_aud + "-" + aud_name
                    threading.Thread(target=self.download_audio, args=(
                        url_aud, aud_name_new)).start()
                    data = ""
                elif type_msg == "document":
                    from_who_doc = data["from"]
                    url_doc = data["link"]
                    doc_name = data["link"][:-7]
                    threading.Thread(target=global_notify, args=(
                        "Receiving document from" + from_who_doc,)).start()
                    doc_name_new = from_who_doc + "-" + doc_name
                    threading.Thread(target=self.download_doc,
                                     args=(url_doc, doc_name_new)).start()
                    data = ""
                elif type_msg == "singleton":
                    self.add_one_line(str(data["msg"]))
                    data = ""
                elif type_msg == "status_comment":
                    write_status_comments(
                        data["from"], data["msg"], data["prof_img"])
                    threading.Thread(target=self.PlayAudio, args=(
                        location_notification,)).start()

                elif type_msg == "get_groups":
                    global ALL_GROUPS
                    ALL_GROUPS = data["msg"]
                    PopGetGroups().open()

                elif type_msg == "group_info":
                    global group_info_dict

                    group_info_dict["name"] = data["name"]
                    group_info_dict["creator"] = data["creator"]
                    group_info_dict["admins"] = data["admins"]
                    group_info_dict["creation_date"] = data["creation_date"]
                    group_info_dict["description"] = data["description"]
                    group_info_dict["num_members"] = data["num_members"]
                    PopGroupInfo().open()

                elif type_msg == "broadcast":
                    if data["from"] == "Admin":
                        self.apply_correct(data["from"], data["msg"])
                        save_messages = False
                    else:
                        save_messages = True
                    if save_messages == True and data != "":
                        self.apply_correct(
                            data["from"], data["msg"], data["prof_img"])
                        self.write_the_message(
                            data["from"], data["msg"], data["prof_img"])
                elif type_msg == "status_feedback":
                    global_status_text = data["text"]
                    global_status_pic = data["link"]
                else:
                    try:
                        if len(data) > 0:
                            the_name = data["from"]
                            if True:
                                if type_msg == "whoisonline--status":
                                    current_share_status = data["msg"]
                                    was_here_status = True
                                elif type_msg == "whoisonline--req_fri":
                                    current_find_friends = data["msg"]
                                    was_here_find_friends = True
                                elif type_msg == "whoisonline--acpt":
                                    current_friend_req = data["msg"]
                                    was_here_friend_req = True
                                elif type_msg == "whoisonline--friends":
                                    current_friends_accept = data["msg"]
                                    was_here_friends_accept = True

                                elif type_msg == "get_group_members":
                                    was_here_members_group = True
                                    # print("DATA:",data)
                                    current_group_members = data["members"]
                                    # print("MEMBERS:",current_group_members)

                                else:
                                    the_message = data["msg"]
                                    if len(the_message) > 0:
                                        self.add_one_line(the_message)
                                        # the_name,the_message = "",""

                    except Exception as e:
                        print(traceback.format_exc())
            except Exception as e:
                showed_it = False
                if showed_it == False:
                    showed_it = True
                    print(traceback.format_exc())

    # def on_enter(self):
    #     self.add_one_line("From this is my texthttp://127.0.0.1/display/default.png")

    def on_enter(self):
        global chat_was_on

        if chat_was_on == False:
            chat_was_on = True
            global s, the_key, name
            try:
                Tinkle().manage_screens("registration_screen", "remove")
                Tinkle().manage_screens("signin_screen", "remove")
            except:
                print(traceback.format_exc())
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                host = return_server_address()
                port = port_chat
                s.connect((host, port))
                # self.send_init_msg()
                tpa = [name, the_key]
                s.send(bytes(json.dumps(tpa), "utf-8"))
                initial = s.recv(512).decode("utf-8")  # the server greeting
                initial = json.loads(initial)
                self.add_two_line(
                    initial["from"], initial["greeting"], initial["img_link"])
                threading.Thread(target=global_notify, args=(
                    "Keep Calm and Tinkle on...",)).start()

                threading.Thread(target=self.load_previous_msg).start()
                threading.Thread(target=self.msgg).start()
                Clock.schedule_once(self.get_missed, 6)
            except BaseException as e:
                print(traceback.format_exc())
                threading.Thread(target=global_notify, args=(
                    "Unable to connect",)).start()

    def load_previous_msg(self):
        if DEFAULT_ACCOUNT == True:
            results_of_log_check = self.read_messages_from_log()
            if results_of_log_check != None:
                for mx in results_of_log_check:
                    if len(mx) > 0:
                        tx_name, tx_message, tx_prof_link = mx.split("`")
                        temp_link = re.findall(
                            'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', tx_prof_link)
                        tx_prof_link.replace(
                            temp_link[0], return_site_web_address()[:-1])
                        self.apply_correct(tx_name, tx_message, tx_prof_link)

    def get_missed(self, *args):
        global s
        template = {
            "type": ""
        }
        template["type"] = "AQUIREDATA!"
        s.send(bytes(json.dumps(template), "utf-8"))


# Name: for_selecting
class ShareImage(BoxLayout, Screen):
    # only called on desktop
    global s

    def __init__(self, **kwargs):
        self.filename = ""
        self.register_event_type('on_back_pressed')
        self.register_event_type('on_menu_pressed')
        super(ShareImage, self).__init__(**kwargs)

    def on_back_pressed(self, *args):
        if IS_GROUP_MEDIA == True:
            Tinkle().change_screen("group_convo")
        else:
            Tinkle().change_screen("convo")

    def on_menu_pressed(self, *args):
        pass

    # preview image in popup
    def select(self, filename):
        try:
            self.filename = filename[0]
            self.preview_img(self.filename)
        except Exception as e:
            print(traceback.format_exc())

    def preview_img(self, src):
        popup = Popup(title="Preview",
                      content=Image(source=src),
                      size_hint=(.9, .7), pos_hint={'x': .2, 'y': .2})
        popup.open()

    def upload_image(self, fname, urlll, dumped_list):
        with open(fname, "rb") as f:
            files = {'testname': f}
            r = requests.post(urlll, files=files)
        s.send(bytes(json.dumps(dumped_list), "utf-8"))
        threading.Thread(target=global_notify,
                         args=("upload complete",)).start()
        self.remove_file(fname)

    def remove_file(self, fname):
        try:
            os.remove(fname)
        except:
            pass

    # OUTPUT: random string of specified length
    def id_generator(size=7, chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    # LOGIC: create temp copy of image, upload, delete

    def send_it(self):
        global receiver_name, IS_GROUP_MEDIA
        if IS_GROUP_MEDIA == True:
            self.recvr = group_name
        else:
            self.recvr = receiver_name
        if len(self.filename) > 5:
            try:
                try:
                    if exceedLimit(self.filename) == True:
                        threading.Thread(target=global_notify,
                                         args=("File exceeds 15MB limit",)).start()
                        return
                    condition = doHashCheckServer(self.filename, "image")
                    if condition[0] == True:
                        should_do_upload = False
                        complete_link = condition[1]
                    else:
                        should_do_upload = True
                except:
                    should_do_upload = True
                person_to = self.recvr
                url_for_img = return_site_web_address() + "man_images.php"
                url_for_img_no_php = return_site_web_address() + "img/"
                c_extension = os.path.splitext(self.filename)[1]
                if c_extension in avail_img_ext:
                    extension = c_extension
                    # create temp_file for randomness of filename
                    my_name = str(A().get_the_name())
                    tempo_img_file = my_name + "-" + \
                                     ''.join(random.choice(string.ascii_lowercase + string.digits)
                                             for _ in range(7)) + extension
                    with open(self.filename, "rb") as f:
                        orag = f.read()
                    with open(tempo_img_file, "wb") as fb:
                        fb.write(orag)
                    link_img = url_for_img_no_php + tempo_img_file
                    bibo = {}
                    bibo["type"] = "image"
                    bibo["link"] = link_img

                    if IS_GROUP_MEDIA == True:
                        bibo["group_based"] = True
                        bibo["group_id"] = current_group_id
                    else:
                        bibo["to"] = self.recvr

                    if should_do_upload == True:
                        threading.Thread(target=self.upload_image, args=(
                            tempo_img_file, url_for_img, bibo)).start()
                        # threading.Thread(target=global_notify, args=(
                        #     "Sharing in background",)).start()
                    else:
                        bibo["link"] = complete_link
                        s.send(bytes(json.dumps(bibo), "utf-8"))
                        self.remove_file(tempo_img_file)
                        threading.Thread(target=global_notify, args=(
                            "Upload complete, used cache",)).start()
                    if IS_GROUP_MEDIA == True:
                        Tinkle().change_screen("group_convo")
                        IS_GROUP_MEDIA = False
                    else:
                        Tinkle().change_screen("convo")

            except BaseException as e:
                print(traceback.format_exc())
                threading.Thread(target=global_notify,
                                 args=("Unable to send",)).start()
                IS_GROUP_MEDIA = False
                Tinkle().change_screen("Chat")

    def on_leave(self):
        Tinkle().manage_screens("for_selecting", "remove")


# Name: for_selecting_audio


class ShareAudio(BoxLayout, Screen):
    global s

    def __init__(self, **kwargs):
        self.register_event_type('on_back_pressed')
        self.register_event_type('on_menu_pressed')
        super(ShareAudio, self).__init__(**kwargs)

    def on_back_pressed(self, *args):
        if IS_GROUP_MEDIA == True:
            Tinkle().change_screen("group_convo")
        else:
            Tinkle().change_screen("convo")

    def on_menu_pressed(self, *args):
        pass

    def stop_sound(self):
        self.tmp.unload()

    def percent_to_play(self, num, src):
        a = (num / 100) * src.length
        return a

    def play_percent(self):
        self.tmp = SoundLoader.load(self.filename)
        self.tmp.play()
        play_time = self.percent_to_play(10, self.tmp)
        Clock.schedule_once(lambda dt: self.stop_sound(), play_time)

    def select(self, filename):
        try:
            self.filename = filename[0]
            # self.play_percent()#freezes program when loading file into memory
        except Exception as e:
            pass

    def upload_audio(self, fname, urlll, dumped_list):
        global s
        # files = {"testname":open(fname,"rb")}
        # r = requests.post(urlll,files=files)
        with open(fname, "rb") as f:
            files = {'testname': f}
            r = requests.post(urlll, files=files)
        s.send(bytes(json.dumps(dumped_list), "utf-8"))
        self.remove_file(fname)

    def remove_file(self, fname):
        try:
            os.remove(fname)
        except BaseException as e:
            pass

    def id_generator(size=7, chars=string.ascii_lowercase + string.digits):
        # do from random import choice
        return ''.join(random.choice(chars) for _ in range(size))

    def send_it_audio(self):  # this is upload part
        global receiver_name, IS_GROUP_MEDIA
        if IS_GROUP_MEDIA == True:
            self.recvr = group_name
        else:
            self.recvr = receiver_name
        if len(self.filename) > 5:
            try:
                try:
                    if exceedLimit(self.filename) == True:
                        threading.Thread(target=global_notify,
                                         args=("File exceeds 15MB limit",)).start()
                        return
                    condition = doHashCheckServer(self.filename, "audio")
                    if condition[0] == True:
                        should_do_upload = False
                        complete_link = condition[1]
                    else:
                        should_do_upload = True
                except:
                    should_do_upload = True
                person_to = self.recvr
                host = return_site_web_address()
                url_for_aud = host + "man_audio.php"
                url_for_aud_no_php = host + "aud/"
                c_extension = os.path.splitext(self.filename)[1]
                if c_extension in avail_aud_ext:
                    extension = c_extension
                    # msg_to_server_my_name = str(A().get_the_name())#add name first
                    # msg_to_server_img = str(file_buffer_string)#add the image
                    # create temp_file for randomness of filename
                    my_name = str(A().get_the_name())
                    tempo_aud_file = my_name + "_" + \
                                     ''.join(random.choice(string.ascii_lowercase + string.digits)
                                             for _ in range(7)) + extension
                    with open(self.filename, "rb") as f:
                        orag = f.read()
                    with open(tempo_aud_file, "wb") as fb:
                        fb.write(orag)

                    link_aud = url_for_aud_no_php + tempo_aud_file
                    # dumped_list = my_name+"|"+to_who_aud+"~"+link_aud#my_name,to_who_img,link_img
                    bibo = {}
                    bibo["type"] = "audio"
                    bibo["link"] = link_aud
                    if IS_GROUP_MEDIA == True:
                        bibo["group_based"] = True
                        bibo["group_id"] = current_group_id
                    else:
                        bibo["to"] = self.recvr

                    if should_do_upload == True:
                        threading.Thread(target=self.upload_audio, args=(
                            tempo_aud_file, url_for_aud, bibo)).start()
                        threading.Thread(target=global_notify, args=(
                            "Sharing in background",)).start()
                    else:
                        bibo["link"] = complete_link
                        s.send(bytes(json.dumps(bibo), "utf-8"))
                        self.remove_file(tempo_aud_file)
                        threading.Thread(target=global_notify, args=(
                            "Upload complete, used cache",)).start()
                    if IS_GROUP_MEDIA == True:
                        Tinkle().change_screen("group_convo")
                        IS_GROUP_MEDIA = False
                    else:
                        Tinkle().change_screen("convo")

            except BaseException as e:
                threading.Thread(target=global_notify,
                                 args=("Unable to send",)).start()
                IS_GROUP_MEDIA = False
                Tinkle().change_screen("Chat")

    def on_leave(self):
        Tinkle().manage_screens("for_selecting_audio", "remove")


# Name: for_selecting_docs


class ShareDocument(BoxLayout, Screen):
    global s

    def __init__(self, **kwargs):
        self.register_event_type('on_back_pressed')
        self.register_event_type('on_menu_pressed')
        super(ShareDocument, self).__init__(**kwargs)

    def on_back_pressed(self, *args):
        if IS_GROUP_MEDIA == True:
            Tinkle().change_screen("group_convo")
        else:
            Tinkle().change_screen("convo")

    def on_menu_pressed(self, *args):
        pass

    def select(self, filename):
        try:
            self.filename = filename[0]
        except Exception as e:
            print(e)

    def upload_doc(self, fname, urlll, dumped_list):
        global s
        files = {"testname": open(fname, "rb")}
        try:
            r = requests.post(urlll, files=files)
            with open(fname, "rb") as f:
                files = {'testname': f}
                r = requests.post(urlll, files=files)
            s.send(bytes(json.dumps(dumped_list), "utf-8"))
            self.remove_file(fname)
        except Exception as e:
            print(e)

    def remove_file(self, fname):
        try:
            os.remove(fname)
        except Exception as e:
            pass

    def id_generator(size=7, chars=string.ascii_lowercase + string.digits):
        # do from random import choice
        return ''.join(random.choice(chars) for _ in range(size))

    def send_it(self):  # this is upload part
        global receiver_name, IS_GROUP_MEDIA
        if IS_GROUP_MEDIA == True:
            self.recvr = group_name
        else:
            self.recvr = receiver_name
        if len(self.filename) > 5:
            try:
                if exceedLimit(self.filename) == True:
                    threading.Thread(target=global_notify,
                                     args=("File exceeds 15MB limit",)).start()
                    return
                condition = doHashCheckServer(self.filename, "document")
                if condition[0] == True:
                    should_do_upload = False
                    complete_link = condition[1]
                else:
                    should_do_upload = True
                person_to = self.recvr
                host = return_site_web_address()
                url_for_doc = host + "man_documents.php"
                url_for_doc_no_php = host + "docs/"
                c_extension = os.path.splitext(self.filename)[1]
                if c_extension in avail_doc_ext:
                    extension = c_extension
                    # create temp_file for randomness of filename
                    my_name = str(A().get_the_name())
                    tempo_doc_file = my_name + "_" + \
                                     ''.join(random.choice(string.ascii_lowercase + string.digits)
                                             for _ in range(7)) + extension
                    with open(self.filename, "rb") as f:
                        orag = f.read()
                    with open(tempo_doc_file, "wb") as fb:
                        fb.write(orag)

                    to_who_doc = self.recvr
                    link_doc = url_for_doc_no_php + tempo_doc_file
                    bibo = {}
                    bibo["type"] = "document"
                    bibo["link"] = link_doc

                    if IS_GROUP_MEDIA == True:
                        bibo["group_based"] = True
                        bibo["group_id"] = current_group_id
                    else:
                        bibo["to"] = self.recvr

                    if should_do_upload == True:
                        threading.Thread(target=self.upload_doc, args=(
                            tempo_doc_file, url_for_doc, bibo)).start()
                        threading.Thread(target=global_notify, args=(
                            "Sharing in the background",)).start()
                    else:
                        bibo["link"] = complete_link
                        s.send(bytes(json.dumps(bibo), "utf-8"))
                        self.remove_file(tempo_doc_file)
                        threading.Thread(target=global_notify, args=(
                            "Upload complete, used cache",)).start()
                    if IS_GROUP_MEDIA == True:
                        Tinkle().change_screen("group_convo")
                        IS_GROUP_MEDIA = False
                    else:
                        Tinkle().change_screen("convo")

            except BaseException as e:
                print(e)
                threading.Thread(target=global_notify,
                                 args=("Unable to send",)).start()
                IS_GROUP_MEDIA = False
                Tinkle().change_screen("Chat")

    def on_leave(self):
        Tinkle().manage_screens("for_selecting_docs", "remove")


# change profile pic android specific

class ChangeProPic:

    def get_rolling(self):
        if isAndroid() == True:
            import android_image_select
            reload(android_image_select)
            from jnius import autoclass
            autoclass('org.kivy.android.PythonActivity$ActivityResultListener')
            android_image_select.user_select_image(self.start_send_in_thread)
            reload(android_image_select)
        else:
            threading.Thread(target=global_notify,
                             args=("Android only!",)).start()

    def start_send_in_thread(self, path):
        if path != None:
            bx = GridLayout(rows=2, cols=1)
            bx.add_widget(Image(source=path))
            btns_layout = GridLayout(
                rows=1, cols=2, size_hint_y=None, height=60)
            btns_layout.add_widget(MDRaisedButton(size_hint_y=None, height=self.parent.height * 0.111,
                                                  text="Cancel", on_release=self.can))
            btns_layout.add_widget(MDRaisedButton(size_hint_y=None, height=self.parent.height * 0.111,
                                                  text="Send", on_release=partial(self.pro, path)))
            bx.add_widget(btns_layout)
            self.bagPop = Popup(title="Back to cancel",
                                content=bx)

            self.bagPop.open()

        else:
            print("No image selected.")

    def pro(self, path, *args):
        print("proceed")
        threading.Thread(target=self.send_it, args=(path,)).start()
        self.bagPop.dismiss()

    def can(self, *args):
        print("cancel")
        self.bagPop.dismiss()

    def upload_image(self, fname, urlll):
        with open(fname, "rb") as f:
            files = {'testname': f}
            r = requests.post(urlll, files=files)
        threading.Thread(target=global_notify, args=(
            "Upload complete, now updating",)).start()
        self.remove_file(fname)
        new_display_link = return_site_web_address() + "display/" + fname + ".png"
        old_link = return_site_web_address() + "display/" + fname
        result = self.do_something(
            new_display_link, A().get_the_name(), get_password(), old_link)
        if result[0] == True:
            threading.Thread(target=global_notify,
                             args=("Update complete",)).start()
        elif result[0] == False:
            threading.Thread(target=global_notify,
                             args=("Update failed",)).start()
        elif result[0] == None:
            threading.Thread(target=global_notify, args=(
                "Connection error",)).start()

    def do_something(self, image_link, my_name, my_pass, old_link):
        some_soc = socket.socket()
        host = return_server_address()
        port = port_profile_pic
        try:
            some_soc.connect((host, port))
            template = {"type": "update_pic", "name": my_name,
                        "password": my_pass, "link": image_link, "original_link": old_link}
            some_soc.send(bytes(json.dumps(template), "utf-8"))
            temp_data = some_soc.recv(1024).decode("utf-8")
            temp = json.loads(temp_data)
            if temp["update_reply"] == "success":
                new_link = temp["new_link"]
                return True, new_link
            elif temp["update_reply"] == "fail":
                return False, False

        except Exception as e:
            return None, None

    def remove_file(self, fname):
        try:
            os.remove(fname)
        except Exception as e:
            pass

    def id_generator(size=7, chars=string.ascii_lowercase + string.digits):
        # do from random import choice
        return ''.join(random.choice(chars) for _ in range(size))

    def send_it(self, path):  # this is upload part
        if path != None:
            self.filename = path
            if exceedLimit(self.filename) == True:
                threading.Thread(target=global_notify,
                                 args=("File exceeds 15MB limit",)).start()
                return
            host = return_site_web_address()
            url_for_img = host + "man_display.php"
            url_for_img_no_php = host + "display/"
            c_extension = os.path.splitext(self.filename)[1]
            if c_extension in avail_img_ext:
                threading.Thread(target=global_notify,
                                 args=("Uploading",)).start()
                extension = c_extension
                # create temp_file for randomness of filename
                my_name = str(A().get_the_name())
                tempo_img_file = my_name + "-" + \
                                 ''.join(random.choice(string.ascii_lowercase + string.digits)
                                         for _ in range(7)) + extension
                with open(self.filename, "rb") as f:
                    orag = f.read()
                with open(tempo_img_file, "wb") as fb:
                    fb.write(orag)

                threading.Thread(target=self.upload_image, args=(
                    tempo_img_file, url_for_img)).start()
            else:
                threading.Thread(target=global_notify, args=(
                    "File type not supported",)).start()
        else:
            print("No image selected")


# Name: profile_Pic


class Profile_Pic(BoxLayout, Screen):
    def __init__(self, **kwargs):
        self.register_event_type('on_back_pressed')
        self.register_event_type('on_menu_pressed')
        super(Profile_Pic, self).__init__(**kwargs)

    def on_back_pressed(self, *args):
        Tinkle().change_screen("Chat")

    def on_menu_pressed(self, *args):
        pass

    def select(self, filename):
        try:
            self.filename = filename[0]
            self.preview_img(self.filename)
        except Exception as e:
            print(e)

    def preview_img(self, src):
        popup = Popup(title="Preview",
                      content=Image(source=src),
                      size_hint=(.9, .7))
        popup.open()

    def upload_image(self, fname, urlll):
        with open(fname, "rb") as f:
            files = {'testname': f}
            r = requests.post(urlll, files=files)
        threading.Thread(target=global_notify, args=(
            "Upload complete, now updating",)).start()
        self.remove_file(fname)
        new_display_link = return_site_web_address() + "display/" + fname + ".png"
        old_link = return_site_web_address() + "display/" + fname
        result = self.do_something(
            new_display_link, A().get_the_name(), get_password(), old_link)
        if result[0] == True:
            threading.Thread(target=global_notify,
                             args=("Update complete",)).start()
        elif result[0] == False:
            threading.Thread(target=global_notify,
                             args=("Update failed",)).start()
        elif result[0] == None:
            threading.Thread(target=global_notify, args=(
                "Connection error",)).start()

    def do_something(self, image_link, my_name, my_pass, old_link):
        some_soc = socket.socket()
        host = return_server_address()
        port = port_profile_pic
        try:
            some_soc.connect((host, port))
            template = {"type": "update_pic", "name": my_name,
                        "password": my_pass, "link": image_link, "original_link": old_link}
            some_soc.send(bytes(json.dumps(template), "utf-8"))
            temp_data = some_soc.recv(1024).decode("utf-8")
            temp = json.loads(temp_data)
            if temp["update_reply"] == "success":
                new_link = temp["new_link"]
                # self.make_change_effect(new_link)
                return True, new_link
            elif temp["update_reply"] == "fail":
                return False, False

        except Exception as e:
            return None, None

    def remove_file(self, fname):
        try:
            os.remove(fname)
        except Exception as e:
            pass

    def id_generator(size=7, chars=string.ascii_lowercase + string.digits):
        # do from random import choice
        return ''.join(random.choice(chars) for _ in range(size))

    def send_it(self):  # this is upload part

        host = return_site_web_address()
        url_for_img = host + "man_display.php"
        url_for_img_no_php = host + "display/"
        c_extension = os.path.splitext(self.filename)[1]
        if c_extension in avail_img_ext:
            if exceedLimit(self.filename) == True:
                threading.Thread(target=global_notify,
                                 args=("File exceeds 15MB limit",)).start()
                return
            threading.Thread(target=global_notify, args=("Uploading",)).start()
            extension = c_extension
            # create temp_file for randomness of filename
            my_name = str(A().get_the_name())
            tempo_img_file = my_name + "-" + \
                             ''.join(random.choice(string.ascii_lowercase + string.digits)
                                     for _ in range(7)) + extension
            with open(self.filename, "rb") as f:
                orag = f.read()
            with open(tempo_img_file, "wb") as fb:
                fb.write(orag)

            threading.Thread(target=self.upload_image, args=(
                tempo_img_file, url_for_img)).start()
            self.manager.current = "Chat"
        else:
            threading.Thread(target=global_notify, args=(
                "File type not supported",)).start()

    def on_leave(self):
        Tinkle().manage_screens("profile_Pic", "remove")


class Tinkle(App):
    global sm
    theme_cls = ThemeManager()
    theme_cls.primary_palette = 'Lime'
    theme_cls.theme_style = "Light"
    sm = ScreenManager()

    # dynamically add/remove screens to consume less memory

    def change_screen(self, screen_name):
        if sm.has_screen(screen_name):
            sm.current = screen_name
        else:
            print("Screen [" + screen_name + "] does not exist.")

    def manage_screens(self, screen_name, action):
        scns = {
            "dump_screen": DumpScreen,
            "profile_Pic": Profile_Pic,
            "advanced_screen": AdvancedScreen,
            "Chat": Chat,
            "convo": Conversation,
            "group_convo": GroupConversation,
            "display_status": DisplayStatus,
            "view_status_comments": StatusComments,
            "create_group_screen": CreateGroupScreen,
            "status_screen": Status,
            "for_selecting": ShareImage,
            "for_selecting_audio": ShareAudio,
            "for_selecting_docs": ShareDocument,
            "names_for_status": GetNamesForStatusScreen,
            "names_for_find_friends": GetNamesForFindFriendsScreen,
            "names_for_friend_req": GetNamesForFriendRequestsScreen,
            "names_for_friends_accept": GetNamesForCurrentFriendsScreen,
            "group_members": GroupMembers,
            "names_friends_group": GetFriendsAddGroup
        }
        try:

            if action == "remove":
                if sm.has_screen(screen_name):
                    sm.remove_widget(sm.get_screen(screen_name))
                # print("Screen ["+screen_name+"] removed")
            elif action == "add":
                if sm.has_screen(screen_name):
                    print("Screen [" + screen_name + "] already exists")
                else:
                    sm.add_widget(scns[screen_name](name=screen_name))
                    print(screen_name + " added")
                    # print("Screen ["+screen_name+"] added")
        except:
            print(traceback.format_exc())
            print("Traceback ^.^")

    def change_screen(self, sc):
        # centralize screen changing
        sm.current = sc

    def decide_change_dp(self):
        # if android: use gallery
        if isAndroid() == True:
            ChangeProPic().get_rolling()
        else:
            self.manage_screens("profile_Pic", "add")
            Tinkle().change_screen("profile_Pic")

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def client_backup(self):
        with open(backup_file, "wb") as f:
            f.write(A().get_the_name() + "\n")
            f.write(get_password())
            threading.Thread(target=global_notify, args=(
                "Backup file: " + backup_file,)).start()

    def display_settings(self, settings):
        try:
            p = self.settings_popup
        except AttributeError:
            self.settings_popup = Popup(content=settings,
                                        title='Settings')
            p = self.settings_popup
        if p.content is not settings:
            p.content = settings
        p.open()

    def build(self):
        global sm
        # Your build code here...
        # add this line right before "return"
        self.bind(on_start=self.post_build_init)
        if isAndroid() == True:
            # TileTransition doesnt work properly on phones [black screen]
            from moretransitions import BlurTransition
            sm = ScreenManager(transition=BlurTransition())
        else:
            from moretransitions import TileTransition
            sm = ScreenManager(transition=TileTransition())

        sm.add_widget(SignInScreen(name="signin_screen"))
        sm.add_widget(Registration(name="registration_screen"))
        # sm.add_widget(Chat(name="Chat"))
        return sm

    def post_build_init(self, ev):
        win = self._app_window
        win.bind(on_keyboard=self._key_handler)

    def _key_handler(self, *args):
        key = args[1]
        # 1000 is "back" on Android
        # 27 is "escape" on computers
        # 1001 is "menu" on Android
        if key in (1000, 27):
            try:
                sm.current_screen.dispatch("on_back_pressed")
            except Exception as e:
                print(e)
            return True
        elif key == 1001:
            try:
                sm.current_screen.dispatch("on_menu_pressed")
            except Exception as e:
                print(e)
            return True

    def build_config(self, config):
        config.setdefaults("General", {"autoshow_img": 0})

    def build_settings(self, settings):
        settings.add_json_panel("Tinkle", self.config, data=json_settings)

    def on_config_change(self, config, section, key, value):

        if key == "autoshow_img":
            self.write_img_display(value)

    def write_img_display(self, value):
        with open("atp_img.dat", "wb") as f:
            f.write(value)


def resourcePath():  # To compile to exe
    '''Returns path containing content - either locally or in pyinstaller tmp file'''
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS)

    return os.path.join(os.path.abspath("."))


if __name__ == "__main__":
    resource_add_path(resourcePath())
    Tinkle().run()
