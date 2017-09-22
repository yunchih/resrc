import pwd, grp

class Users:

    @staticmethod
    def get_user_gid(uid):
        return pwd.getpwuid(uid).pw_gid

    @staticmethod
    def gname_to_gid(g):
        return grp.getgrnam(g).gr_gid

    @staticmethod
    def uname_to_uid(u):
        return pwd.getpwnam(u).pw_uid

    def __init__(self, users, groups):
        self.uids = self.parse_users(users)
        self.gids = self.parse_groups(groups)

    def parse_groups(self, groups):
        gids = []

        for g in groups:
            if g:
                try:
                    gid = self.gname_to_gid(g)
                except KeyError as err:
                    quit("Group not found: %s", g)
                if gid > 0: # exclude root user
                    gids.append(gid)

        return gids

    def parse_users(self, users):
        uids = []
        for u in users:
            if u:
                try:
                    uid = self.uname_to_uid(u)
                except KeyError as err:
                    quit("User not found: %s", u)
                if uid > 0: # exclude root user
                    uids.append(uid)
        return uids

    def match(self, uid=-1, gid=-1):
        return uid in self.uids or gid in self.gids
