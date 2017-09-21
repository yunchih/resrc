import pwd, grp

class Users:

    def __init__(self, users, groups):
        self.uids = self.parse_users(users)
        self.gids = self.parse_groups(groups)

    def parse_groups(self, groups):
        gids = []

        for g in groups:
            if g:
                try:
                    gid = grp.getgrnam(g).gr_gid
                except KeyError as err:
                    quit("Group not found: %s", g)
                if gid > 0: # exclude root user
                    gids.append(gid)

        return gids

    def parse_users(users):
        uids = []
        for u in users:
            if u:
                try:
                    uid = pwd.getpwnam(u).pw_uid
                except KeyError as err:
                    quit("User not found: %s", u)
                if uid > 0: # exclude root user
                    uids.append(uid)
        return uids

    def match(self, uid=-1, gid=-1):
        return uid in self.uids or gid in self.gids
