from kivy.logger import Logger
from kivy.clock import Clock

from jnius import autoclass
from jnius import cast

# python-for-android provides this
from android import activity

PythonActivity = autoclass('org.kivy.android.PythonActivity')
Intent = autoclass('android.content.Intent')
Uri = autoclass('android.net.Uri')

# Value of MediaStore.Images.Media.DATA
MediaStore_Images_Media_DATA = "_data"

# Custom request codes
RESULT_LOAD_IMAGE = 1

Activity = autoclass('android.app.Activity')
# Activity is only used to get these codes. Could just hardcode them.
    # /** Standard activity result: operation canceled. */
    # public static final int RESULT_CANCELED    = 0;
    # /** Standard activity result: operation succeeded. */
    # public static final int RESULT_OK           = -1;
    # /** Start of user-defined activity results. */
    # Not sure what this means
    # public static final int RESULT_FIRST_USER   = 1;

def user_select_image(callback):
    """Open Gallery Activity and call callback with absolute image filepath of image user selected.
    None if user canceled.
    """

    # PythonActivity.mActivity is the instance of the current Activity
    # BUT, startActivity is a method from the Activity class, not from our
    # PythonActivity.
    # We need to cast our class into an activity and use it
    currentActivity = cast('android.app.Activity', PythonActivity.mActivity)

    # Forum discussion: https://groups.google.com/forum/#!msg/kivy-users/bjsG2j9bptI/-Oe_aGo0newJ
    def on_activity_result(request_code, result_code, intent):
        if request_code != RESULT_LOAD_IMAGE:
            Logger.warning('user_select_image: ignoring activity result that was not RESULT_LOAD_IMAGE')
            return

        if result_code == Activity.RESULT_CANCELED:
            Clock.schedule_once(lambda dt: callback(None), 0)
            return

        if result_code != Activity.RESULT_OK:
            # This may just go into the void...
            raise NotImplementedError('Unknown result_code "{}"'.format(result_code))

        selectedImage = intent.getData();  # Uri
        filePathColumn = [MediaStore_Images_Media_DATA]; # String[]
        # Cursor
        cursor = currentActivity.getContentResolver().query(selectedImage,
                filePathColumn, None, None, None);
        cursor.moveToFirst();

        # int
        columnIndex = cursor.getColumnIndex(filePathColumn[0]);
        # String
        picturePath = cursor.getString(columnIndex);
        cursor.close();
        Logger.info('android_ui: user_select_image() selected %s', picturePath)

        # This is possibly in a different thread?
        Clock.schedule_once(lambda dt: callback(picturePath), 0)
        activity.unbind(on_activity_result=on_activity_result)

    # See: http://pyjnius.readthedocs.org/en/latest/android.html
    activity.bind(on_activity_result=on_activity_result)

    intent = Intent()

    # http://programmerguru.com/android-tutorial/how-to-pick-image-from-gallery/
    # http://stackoverflow.com/questions/18416122/open-gallery-app-in-android
    intent.setAction(Intent.ACTION_PICK)
    # TODO internal vs external?
    intent.setData(Uri.parse('content://media/internal/images/media'))
    # TODO setType(Image)?

    currentActivity.startActivityForResult(intent, RESULT_LOAD_IMAGE)