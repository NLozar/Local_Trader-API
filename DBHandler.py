import mysql.connector
from decouple import config
import bcrypt

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
        #self.cursor.execute(f"use {db};")
    
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
        self.cursor.execute(f"select * from items where uuid='{uuid}'")
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

# MAIN (testing only)
if __name__ == "__main__":
    db = DBHandler("root", config("MYSQL_PW"), "localhost", 13306, "local_trader")
    print("pajdo" in db.get_all_usernames())