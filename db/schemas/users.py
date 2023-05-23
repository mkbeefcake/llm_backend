
class UsersSchema:
    
    def __init__(self, id: str, username: str, passwd: str, email: str):
        self.id = id
        self.username = username
        self.passwd = passwd
        self.email = email