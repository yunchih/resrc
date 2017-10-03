# Copyright 2017 Yunchih Chen <yunchih@csie.ntu.edu.tw>

import dbus, logging
from gi.repository import GLib
from dbus import SystemBus, SessionBus, Interface
from dbus.mainloop.glib import DBusGMainLoop
from resrc.utils import quit
from resrc.users import Users

class Systemd:
    def __init__(self, dest, object_path, interface):
        bus = SystemBus()
        node = bus.get_object(dest, object_path)
        self.iface = Interface(node, dbus_interface=interface)

    def run(self, method, *args, **kwargs):
        f = getattr(self.iface, method)
        return f(*args)

    @staticmethod
    def dict_to_dbus_properties(ct):
        props = []
        for (key, value) in ct:
            if isinstance(value, int):
                props.append(dbus.Struct((key, dbus.UInt64(value))))
            else:
                props.append(dbus.Struct((key, dbus.String(value))))

        return dbus.Array(props)

class UsersResourceManager:

    def __init__(self, ruleset=[], dry_run=False, all_user=False, apply_existing=False):
        self.ruleset = ruleset
        self.dry_run = dry_run
        self.all_user = all_user

        if len(ruleset) == 0:
            quit("No rules installed!")

        DBusGMainLoop(set_as_default=True)

        self.sd_logind  = Systemd('org.freedesktop.login1', '/org/freedesktop/login1',
                'org.freedesktop.login1.Manager')
        self.sd_manager = Systemd('org.freedesktop.systemd1', '/org/freedesktop/systemd1', 'org.freedesktop.systemd1.Manager')

        if apply_existing:
            unit_list = self.sd_get_unit_list()
            uids = self.sd_get_uids_from_units(unit_list)

            for _uid in uids:
                uid, gid = 0, 0

                try:
                    uid = int(_uid)
                    gid = Users.get_user_gid(uid)
                    logging.info("Existing user detected: %d" % uid)
                except KeyError:
                    # just in case
                    logging.error("Existing user detected but uid not found: %d" % uid)

                self.apply_rule(uid, gid)

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

        self.apply_rule(uid, gid)

    def apply_rule(self, uid, gid):
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
            self.sd_manager.run("SetUnitProperties", sd_unit, sd_runtime, properties)
            logging.info("Resource limitation imposed on user: %d" % uid)
        except Exception as e:
            logging.error("Failed imposing resource limit on %d: %s" % (uid, e))

    def sd_get_unit_list(self):
        try:
            return self.sd_manager.run("ListUnits")
        except Exception as e:
            logging.error("Failed getting all units: " + e)

    def sd_get_uids_from_units(self, units):
        r = re.compile("^user-[0-9]*\.slice")
        r2 = re.compile("[0-9]+")
        unit_names = [u[0] for u in units]
        user_slices = [u for u in unit_names if re.match(r, u)]
        return [re.search(r2, u).group(0) for u in user_slices]
