#!/usr/bin/env python2

# Copyright 2017 Yunchih Chen <yunchih@csie.ntu.edu.tw>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
#     The above copyright notice and this permission notice shall be included in
#     all copies or substantial portions of the Software.
#
#     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#     IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#     FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#     AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#     LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#     FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#     IN THE SOFTWARE.

import sys, os, pwd, grp, logging, argparse
import dbus
from gi.repository import GLib
from dbus import SystemBus, SessionBus, Interface
from dbus.mainloop.glib import DBusGMainLoop
from ConfigParser import SafeConfigParser

CONFIG_FILE  = "logind-hook.conf"
DESCRIPTION  = "Limit total system resources available to a user within all her sessions."
VERSION      = 1.1
EXAMPLE_USAGE = """
Note:
    Please see `man systemd.cgroups(5)` for a list of available resource types.

Example:
    Apply the `MemoryLimit` Systemd resource rule to the user `john`:
        $ %(prog)s --users john --rules MemoryLimit=53687091200

    Apply the `MemoryLimit` Systemd resource to all users:
        $ %(prog)s --all-users --rules MemoryLimit=53687091200

"""

class UserResourceManager:

    def __init__(self, target_uids=[], target_gids=[], rules={}, all_user=False):
        DBusGMainLoop(set_as_default=True)

        self._bus = SystemBus()
        self.logind = self._bus.get_object('org.freedesktop.login1', '/org/freedesktop/login1')
        self.logind_iface = Interface(self.logind, dbus_interface='org.freedesktop.login1.Manager')

        self.manager = self._bus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        self.manager_iface = Interface(self.manager, dbus_interface='org.freedesktop.systemd1.Manager')

        self.target_uids = target_uids
        self.target_gids = target_gids
        self.sd_properties = self._to_sd_props(rules)
        self.all_user = all_user

        if all_user:
            logging.info("Targeting all users")

    def run(self):
        self.loop = GLib.MainLoop()
        self.loop.run()

    def monitor_new_user(self):
        try:
            self.logind_iface.connect_to_signal("UserNew", self._new_user_handler, sender_keyword='sender')
        except dbus.DBusException as e:
            logging.error("Failed registering user signal handler: " + e)

    def _to_sd_props(self, ct):
        props = []
        for (key, value) in ct.items():
            if isinstance(value, (int, long)):
                props.append(dbus.Struct((key, dbus.UInt64(value))))
            else:
                props.append(dbus.Struct((key, dbus.String(value))))

        return dbus.Array(props)

    def _new_user_handler(self, slice_id, obj_path="", sender=""):
        uid, gid = 0, 0

        try:
            uid = int(slice_id)
            gid = pwd.getpwuid(uid).pw_gid
            logging.info("New user detected: %d" % uid)
        except KeyError:
            # just in case
            logging.error("New user detected but uid not found: %d" % uid)

        if not uid or not gid: # exclude root and malformed uid, gid
            return

        if self.all_user or (uid in self.target_uids) or (gid in self.target_gids):
            sd_unit = dbus.String("user-%d.slice" % uid)
            sd_runtime = dbus.Boolean(True)

            try:
                self.manager_iface.SetUnitProperties(sd_unit, sd_runtime, self.sd_properties)
                logging.info("Resource limitation imposed on user: %d" % uid)
            except dbus.DBusException as e:
                logging.error("Failed imposing resource limit on %d: %s" % (uid, e))

def quit(*args):
    if len(args):
        logging.error(str(args[0]) % args[1:])
    sys.exit(1)

def get_group_id(gname):
    try:
        return grp.getgrnam(gname).gr_gid
    except KeyError as err:
        quit("Group not found: %s", g)

def parse_users(users):
    _uids, _users = [], []
    _gids, _groups = [], []

    for u in users:
        if not u:
            continue
        # group
        elif u[0] == "@" and len(u) > 1:
            g = u[1:]
            gid = get_group_id(g)
            if gid > 0: # exclude root user
                _gids.append(gid)
                _groups.append(g)

        # normal user
        else:
            try:
                uid = pwd.getpwnam(u).pw_uid
                if uid > 0: # exclude root user
                    _uids.append(uid)
                    _users.append(u)
            except KeyError as err:
                quit("User not found: %s", u)

    if _users:
        logging.info("Targeting users: %s", ",".join(_users))

    if _groups:
        logging.info("Targeting groups: %s", ",".join(_groups))

    return _uids, _gids

def atoi(s):
    try:
        return int(s)
    except ValueError:
        return s

def parse_rules(rules):
    _rules = {}
    print(rules)
    rules = rules.split(",")
    for r in rules:
        try:
            k, v = r.split("=")
            if not k or not v:
                raise ValueError
        except ValueError:
            quit("Invalid rule: %s", r)

        logging.info("Adding rules: %s = %s", k, v)
        _rules[k] = atoi(v)

    return _rules

def bind_rules(uids, gids, rules):
    return (True, True)

def parse_config():
    p = SafeConfigParser()
    p.read()
    for user in p.sections():
        if not user:
            continue
        if user[0] == "@":
            g = user[1:]
            _gids.append(get_group_id(g))
            _groups.append(g)
        elif user == "all":
            pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description=DESCRIPTION,
            formatter_class=argparse.RawTextHelpFormatter,
            epilog=EXAMPLE_USAGE)
    parser.add_argument("--config", "-c", action="store", default="",
            help="Using a configuration file as input")
    parser.add_argument("--users", "-u", nargs="+", action="store", default=[],
            help="(Optional) A list of users to be constrained")
    parser.add_argument("--all-users", "-a", action="store_true",
            help="(Optional) Apply the constraints to all users")
    parser.add_argument("--rules", "-r", action="store", default="",
            help="(Required) A comma-seperated list of rules to be applied")
    parser.add_argument("--debug", action="store_true",
            help="Show debug output")
    parser.add_argument("--version", "-v", action="version", version="%(prog)s " + str(VERSION))

    args = parser.parse_args()
    level = logging.DEBUG if args.debug else logging.ERROR
    logging.basicConfig(stream=sys.stderr, level=level, format='%(levelname)s: %(message)s')
    logging.info("Systemd resource manager started")

    uids, gids = [], []
    if not args.all_users:
        if args.users:
            uids, gids = parse_users(args.users)
        else:
            quit("No users given, either use --all-users or --users")
    elif args.config:
        quit("Configuration file as input not supported yet")

    rules = parse_rules(args.rules)
    manager = UserResourceManager(uids, gids, rules, args.all_users)
    manager.monitor_new_user()
    manager.run()

