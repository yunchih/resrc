import logging
from lib.users import Users
from lib.systemd import UsersResourceManager
from lib.rules import Rule, RuleEntry
from lib.users import User

def parse_cmd(users=[], groups=[], rules=""):
    if users or groups:
        _users = Users(users,groups)
        _rules = parse_rules(rules)
        return [RuleEntry(_rules, _users)]
    else:
        return []

def parse_rules(rules):
    _rules = {}
    rules = rules.split(",")
    for r in rules:
        try:
            k, v = r.split("=")
            if not k or not v:
                raise ValueError
        except ValueError:
            quit("Invalid rule: %s", r)

        _rules[k] = v

    return _rules

def parse_config(f):
    try:
        cfg = yaml.load(f)
    except yaml.YAMLError as exc:
        if hasattr(exc, 'problem_mark'):
            mark = exc.problem_mark
            print ("Error position: (%s:%s)" % (mark.line+1, mark.column+1))
            quit()

    rules = cfg["rules"]
    binded_rules = []
    for entry in users:
        glist = [] if "groups" in entry else entry["groups"]
        ulist = [] if "users" in entry else entry["users"]
        r = Rule(entry["name"],entry["rules"])
        u = Users(ulist, glist)
        binded_rules.append(RuleEntry(r, u))

    return binded_rules
