#!/usr/bin/env python2
import sys, os, pwd, logging
import gobject
import dbus
from dbus import SystemBus, SessionBus, Interface
from dbus.mainloop.glib import DBusGMainLoop

class UserResourceManager:

    def __init__(self, target_uid):
        DBusGMainLoop(set_as_default=True)

        self._bus = SystemBus()
        self.logind = self._bus.get_object('org.freedesktop.login1', '/org/freedesktop/login1')
        self.logind_iface = Interface(self.logind, dbus_interface='org.freedesktop.login1.Manager')

        self.manager = self._bus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        self.manager_iface = Interface(self.manager, dbus_interface='org.freedesktop.systemd1.Manager')

        self.target_uid = target_uid

    def run(self):
        self.loop = gobject.MainLoop()
        self.loop.run()

    def new_user_handler(self, slice_id, obj_path="", sender=""):
        uid = int(slice_id)
        logging.info("New user detected: %d" % uid)
        if uid == self.target_uid:
            # Example resource constraint:
            # MemoryLimit = 40G = 1024 * 1024 * 1024 * 40 = 42949672960

            sd_unit = dbus.String(str(slice_id) + ".slice")
            sd_runtime = dbus.Boolean(True)
            sd_properties = dbus.Array([dbus.Struct(["MemoryLimit","42949672960"])])

            try:
                self.manager_iface.SetUnitProperties(sd_unit, sd_runtime, sd_properties)
                logging.info("Resource limitation imposed on user: %d" % uid)
            except dbus.DBusException as e:
                logging.error("Failed imposing resource limit on %d: %s" % (uid, e))

    def monitor_new_user(self):
        try:
            self.logind_iface.connect_to_signal("UserNew", self.new_user_handler, sender_keyword='sender')
        except dbus.DBusException as e:
            logging.error("Failed registering user signal handler: " + e)

if __name__ == '__main__':

    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Systemd resource manager started")

    try:
        target_user = sys.argv[1]
        target_uid = pwd.getpwnam(target_user).pw_uid
        logging.info("Targeting user: " + target_user)
    # No argument provided
    except IndexError:
        target_uid = -1
    except KeyError as err:
        target_uid = -1
        logging.error("User not found: " + sys.argv[1])
        sys.exit(1)

    manager = UserResourceManager(target_uid)
    manager.monitor_new_user()
    manager.run()
