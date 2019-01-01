import time
import functools
import jnius

def acquire_permissions(permissions, timeout=30):
    """
    blocking function for acquiring storage permission

    :param permissions: list of permission strings , e.g. ["android.permission.READ_EXTERNAL_STORAGE",]
    :param timeout: timeout in seconds
    :return: True if all permissions are granted
    """

    PythonActivity = jnius.autoclass('org.kivy.android.PythonActivity')
    Compat = jnius.autoclass('android.support.v4.content.ContextCompat')
    currentActivity = jnius.cast('android.app.Activity', PythonActivity.mActivity)

    checkperm = functools.partial(Compat.checkSelfPermission, currentActivity)

    def allgranted(permissions):
        """
        helper function checks permissions
        :param permissions: list of permission strings
        :return: True if all permissions are granted otherwise False
        """
        return reduce(lambda a, b: a and b,
                    [True if p == 0 else False for p in map(checkperm, permissions)]
                    )

    haveperms = allgranted(permissions)
    if haveperms:
        # we have the permission and are ready
        return True

    # invoke the permissions dialog
    currentActivity.requestPermissions(permissions, 0)

    # now poll for the permission (UGLY but we cant use android Activity's onRequestPermissionsResult)
    t0 = time.time()
    while time.time() - t0 < timeout and not haveperms:
        # in the poll loop we could add a short sleep for performance issues?
        haveperms = allgranted(permissions)

    return haveperms