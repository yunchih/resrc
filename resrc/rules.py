import os
from resrc.systemd import UsersResourceManager

class Rule:

    sd_props = [
        "CPUAccounting", "IOAccounting", "BlockIOAccounting",
        "MemoryAccounting", "TasksAccounting", "CPUWeight",
        "CPUQuotaPerSecUSec", "CPUQuota", "StartupCPUWeight",
        "CPUShares", "StartupCPUShares", "CPUQuotaPerSecSec",
        "IOWeight", "StartupIOWeight", "BlockIOWeight",
        "StartupBlockIOWeight", "MemoryLow", "MemoryHigh",
        "MemoryMax", "MemorySwapMax", "MemoryLimit",
        "TasksMax", "DevicePolicy", "Delegate"
    ]

    custom_props = [
        "CPUQuotaOverall"
    ]

    def __init__(self, name="", rules={}):
        self.cpu_cnt = int(os.sysconf('SC_NPROCESSORS_CONF'))
        self.ram_bytes = int(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES'))
        self.rules = rules
        self.name = name
        if self.check_rules(rules):
            raw_rules = [self.translate_rule(n,v) for (n,v) in rules.items()]
            self.rules = UsersResourceManager.dict_to_dbus_properties(raw_rules)
        else:
            pass # won't be here

    @staticmethod
    def percent(pstr):
        return 0.01 * float(pstr.strip("%"))

    def check_rules(self, rules):
        for (n,v) in rules.items():
            if (not n in self.sd_props) and (not n in self.custom_props):
                quit("Property \"{0}\" does not exist in Systemd".format(n))
        return True

    def translate_rule(self, name, v):
        p = self.percent(v)
        if name == "CPUQuota":
            # CPUQuota 1% = CPUQuotaPerSecUSec 10000
            return ("CPUQuotaPerSecUSec", (p * 1000000.0))
        if name == "CPUQuotaOverall":
            return ("CPUQuotaPerSecUSec", int(self.cpu_cnt * p * 1000000.0))
        if "Memory" in name and "%" in v:
            return (name, int(self.ram_bytes * p))
        return (name,v)

    def get(self):
        return self.rules

class RuleEntry:

    def __init__(self, rules, users):
        self.rules = rules
        self.users = users

    def match(self, uid=-1, gid=-1):
        return self.users.match(uid,gid)

    def get_rules(self):
        return self.rules
