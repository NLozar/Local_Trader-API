import mysql.connector
from decouple import config

class DBHandler:
    def __init__(self, user, pw, host, port, db):
        self.db = mysql.connector.connect(
            user=user,
            password=pw,
            host=host,
            port=port,
            database=db
        )
        self.cursor = self.db.cursor()
    
    def get_all_items(self):
        self.cursor.execute("select * from items;")
        items = []
        for row in self.cursor:
            items.append({
                "title": row[1],
                "descr": row[3],
                "price": row[4],
                "uuid": row[6]
            })
        return items

    def get_item_details(self, uuid):
        query = "select * from items where uuid=%s"
        val = (uuid,)
        self.cursor.execute(query, val)
        res = self.cursor.fetchone()
        if not res:
            return None
        keys = ["title", "seller", "descr", "price", "contact", "uuid"]
        OFFSET = 1
        item_details = {}
        for i, key in enumerate(keys):
            item_details[key] = res[i+OFFSET]
        return item_details
    
    def register_user(self, username, pw, uuid):
        sql = "insert into users (username, pw, uuid) values (%s, %s, %s)"
        val = (username, pw, uuid)
        self.cursor.execute(sql, val)
        self.db.commit()

    def get_all_usernames(self):
        self.cursor.execute("select username from users;")
        usernames = []
        for i in self.cursor:
            usernames.append(i)
        usernames = [i for ii in usernames for i in ii]
        return usernames

    def get_user_details(self, username):
        query = "select * from users where username=%s"
        val = (username,)
        self.cursor.execute(query, val)
        for row in self.cursor:   # looks stupid, but trust me, this works
            return {
                "hashed_pw": row[2],
                "uuid": row[3]
            }
    
    def update_user_info(self, uuid, username=None, password=None):
        if password:
            sql = "update users set password=%s where uuid=%s"
            val = (password, uuid)
        elif username:
            sql = "update users set username=%s where uuid=%s"
            val = (username, uuid)
        elif username and password:
            sql = "update users set username=%s, password=%s where uuid=%s"
            val = (username, password, uuid)
        self.cursor.execute(sql, val)
        self.db.commit()
    
    def post_item(self, title, seller_name, uuid, seller_uuid, descr, price, contact):
        sql = "insert into items (title, seller_name, descr, price, contact, uuid, seller_uuid) values (%s, %s, %s, %s, %s, %s, %s)"
        val = (title, seller_name, descr, price, contact, uuid, seller_uuid)
        self.cursor.execute(sql, val)
        self.db.commit()

# MAIN (testing only)
if __name__ == "__main__":
    db = DBHandler("root", config("MYSQL_PW"), "localhost", 13306, "local_trader")