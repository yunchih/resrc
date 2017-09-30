# Copyright 2017 Yunchih Chen <yunchih@csie.ntu.edu.tw>

import dbus, logging
from gi.repository import GLib
from dbus import SystemBus, SessionBus, Interface
from dbus.mainloop.glib import DBusGMainLoop
from resrc.utils import quit
from resrc.users import Users

class UsersResourceManager:

    def __init__(self, ruleset=[], dry_run=False, all_user=False):
        self.ruleset = ruleset
        self.dry_run = dry_run
        self.all_user = all_user

        if len(ruleset) == 0:
            quit("No rules installed!")

        DBusGMainLoop(set_as_default=True)

        self._bus = SystemBus()
        self.logind = self._bus.get_object('org.freedesktop.login1', '/org/freedesktop/login1')
        self.logind_iface = Interface(self.logind, dbus_interface='org.freedesktop.login1.Manager')

        self.manager = self._bus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        self.manager_iface = Interface(self.manager, dbus_interface='org.freedesktop.systemd1.Manager')

    def run(self):
        self.loop = GLib.MainLoop()
        self.loop.run()

    def monitor_new_user(self):
        try:
            self.logind_iface.connect_to_signal("UserNew", self._new_user_handler, sender_keyword='sender')
        except dbus.DBusException as e:
            logging.error("Failed registering user signal handler: " + e)

    def _new_user_handler(self, slice_id, obj_path="", sender=""):
        uid, gid = 0, 0

        try:
            uid = int(slice_id)
            gid = Users.get_user_gid(uid)
            logging.info("New user detected: %d" % uid)
        except KeyError:
            # just in case
            logging.error("New user detected but uid not found: %d" % uid)
            return

        if not uid or not gid: # exclude root and malformed uid, gid
            return

        for entry in self.ruleset:
            # Only apply the first matched rule
            if self.all_user or entry.match(uid, gid):
                r = entry.get_rules().rules
                if (not self.dry_run) and r:
                    self.sd_set_unit_properties(uid, r)
                logging.info("UID {0} matches rule \"{1}\"".format(uid, entry.get_rules().name))
                break

    def sd_set_unit_properties(self, uid, properties):
        sd_unit = dbus.String("user-%d.slice" % uid)
        sd_runtime = dbus.Boolean(True)

        try:
            self.manager_iface.SetUnitProperties(sd_unit, sd_runtime, properties)
            logging.info("Resource limitation imposed on user: %d" % uid)
        except dbus.DBusException as e:
            logging.error("Failed imposing resource limit on %d: %s" % (uid, e))

    @staticmethod
    def dict_to_dbus_properties(ct):
        props = []
        for (key, value) in ct:
            if isinstance(value, int):
                props.append(dbus.Struct((key, dbus.UInt64(value))))
            else:
                props.append(dbus.Struct((key, dbus.String(value))))

        return dbus.Array(props)
