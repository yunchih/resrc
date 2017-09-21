import os
from lib.systemd import dict_to_dbus_properties

class Rule:

    sd_props = [
        "CPUAccounting", "IOAccounting", "BlockIOAccounting",
        "MemoryAccounting", "TasksAccounting", "CPUWeight",
        "StartupCPUWeight", "CPUShares", "StartupCPUShares",
        "CPUQuotaPerSecSec", "IOWeight", "StartupIOWeight",
        "BlockIOWeight", "StartupBlockIOWeight", "MemoryLow",
        "MemoryHigh", "MemoryMax", "MemorySwapMax", "MemoryLimit",
        "TasksMax", "DevicePolicy", "Delegate"
    ]

    def __init__(self, name, rules):
        self.cpu_cnt = int(os.sysconf('SC_NPROCESSORS_CONF'))
        self.ram_bytes = int(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES'))

        if self.check_rules(rules):
            self.name = name
            self.rules = dict_to_dbus_properties([self.translate_rule(n,v) for n,v in rules])

    def percent(self, pstr):
        return 0.01 * float(pstr.strip("%"))

    def check_rules(self, rules):
        for n,v in rules:
            if not n in sd_props:
                quit("Property \"${0}\" does not exist in SystemD".formatn(n))
        return true

    def translate_rule(self, name, v):
        if name is "CPUQuota":
            # CPUQuota 1% = CPUQuotaPerSecUSec 10000
            return ("CPUQuotaPerSecUSec", (percent(v) * 1000000.0))
        if name is "CPUQuotaOverall":
            return ("CPUQuotaPerSecUSec", int(self.cpu_cnt * percent(v) * 1000000.0))
        if "Memory" in name and "%" in v:
            return (name, int(self.ram_bytes * percent(v)))
        return (name,v)

class RuleEntry:

    def __init__(self, rules, users):
        self.rules = rules
        self.users = users

    def match(self, uid=-1, gid=-1):
        return self.users.match(uid,gid)

    def get(self):
        return self.rules
