# -*- coding: utf-8 -*-
from kivy import platform
from kivy.core.window import Window
from kivy.metrics import dp
#from kivymd import fonts_path
import os
path = os.path.dirname(__file__)
def isAndroid():
    # On Android sys.platform returns 'linux2', so prefer to check the
    # presence of python-for-android environment variables (ANDROID_ARGUMENT
    # or ANDROID_PRIVATE).
    if 'ANDROID_ARGUMENT' in os.environ:
        return True
    else:
        return False

extension = "\\"
if isAndroid() == True:
    extension = "/"
fonts_path = os.path.join(path, "fonts"+extension)
# Feel free to override this const if you're designing for a device such as
# a GNU/Linux tablet.
if platform != "android" and platform != "ios":
    DEVICE_TYPE = "desktop"
elif Window.width >= dp(600) and Window.height >= dp(600):
    DEVICE_TYPE = "tablet"
else:
    DEVICE_TYPE = "mobile"

if DEVICE_TYPE == "mobile":
    MAX_NAV_DRAWER_WIDTH = dp(300)
    HORIZ_MARGINS = dp(16)
    STANDARD_INCREMENT = dp(56)
    PORTRAIT_TOOLBAR_HEIGHT = STANDARD_INCREMENT
    LANDSCAPE_TOOLBAR_HEIGHT = STANDARD_INCREMENT - dp(8)
else:
    MAX_NAV_DRAWER_WIDTH = dp(400)
    HORIZ_MARGINS = dp(24)
    STANDARD_INCREMENT = dp(64)
    PORTRAIT_TOOLBAR_HEIGHT = STANDARD_INCREMENT
    LANDSCAPE_TOOLBAR_HEIGHT = STANDARD_INCREMENT

TOUCH_TARGET_HEIGHT = dp(48)

FONTS = [
    {
        "name": "Roboto",
        "fn_regular": fonts_path + 'Roboto-Regular.ttf',
        "fn_bold": fonts_path + 'Roboto-Medium.ttf',
        "fn_italic": fonts_path + 'Roboto-Italic.ttf',
        "fn_bolditalic": fonts_path + 'Roboto-MediumItalic.ttf'
    },
    {
        "name": "RobotoLight",
        "fn_regular": fonts_path + 'Roboto-Thin.ttf',
        "fn_bold": fonts_path + 'Roboto-Light.ttf',
        "fn_italic": fonts_path + 'Roboto-ThinItalic.ttf',
        "fn_bolditalic": fonts_path + 'Roboto-LightItalic.ttf'
    },
    {
        "name": "Icons",
        "fn_regular": fonts_path + 'materialdesignicons-webfont.ttf'
    }
]
