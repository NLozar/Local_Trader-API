import mysql.connector
from decouple import config

class DBHandler:
    def __init__(self, user, pw, host, port, db):
        self.user = user
        self.pw = pw
        self.host = host
        self.port = port
        self.db = db
    
    def returnDbConn(self):
        return mysql.connector.connect(
            user=self.user,
            password=self.pw,
            host=self.host,
            port=self.port,
            database=self.db
        )
    
    def get_all_items(self):
        db = self.returnDbConn()
        cursor = db.cursor()
        cursor.execute("select * from items;")
        items = []
        for row in cursor.fetchall():
            items.append({
                "title": row[1],
                "descr": row[3],
                "price": row[4],
                "uuid": row[6]
            })
        cursor.close()
        db.close()
        return items

    def get_item_details(self, uuid):
        query = "select * from items where uuid=%s"
        val = (uuid,)
        db = self.returnDbConn()
        cursor = db.cursor()
        cursor.execute(query, val)
        res = cursor.fetchone()
        cursor.close()
        db.close()
        if not res:
            return None
        keys = ["title", "seller", "descr", "price", "contact", "uuid"]
        OFFSET = 1
        item_details = {}
        for i, key in enumerate(keys):
            item_details[key] = res[i+OFFSET]
        return item_details
    
    def get_seller_uuid_of_item(self, item_uuid):
        query = "select seller_uuid from items where uuid=%s"
        val = (item_uuid,)
        db = self.returnDbConn()
        cursor = db.cursor()
        cursor.execute(query, val)
        res = cursor.fetchone()
        cursor.close()
        db.close()
        if res:
            return res[0]
        return None
    
    def register_user(self, username, pw, uuid):
        sql = "insert into users (username, pw, uuid) values (%s, %s, %s)"
        val = (username, pw, uuid)
        db = self.returnDbConn()
        cursor = db.cursor()
        cursor.execute(sql, val)
        cursor.close()
        db.commit()
        db.close()

    def get_all_usernames(self):
        db = self.returnDbConn()
        cursor = db.cursor()
        cursor.execute("select username from users;")
        usernames = []
        for i in cursor:
            usernames.append(i)
        usernames = [i for ii in usernames for i in ii]
        cursor.close()
        db.close()
        return usernames

    def get_user_details(self, username):
        query = "select * from users where username=%s"
        val = (username,)
        db = self.returnDbConn()
        cursor = db.cursor()
        cursor.execute(query, val)
        for row in cursor:   # looks stupid, but trust me, this works
            cursor.close()
            db.close()
            return {
                "hashed_pw": row[2],
                "uuid": row[3]
            }
    
    def update_user_info(self, uuid, username=None, password=None):
        db = self.returnDbConn()
        cursor = db.cursor()
        if username and password:
            sql = "update users set username=%s, password=%s where uuid=%s"
            val = (username, password, uuid)
            cursor.execute(sql, val)
            sql = "update items set seller_name=%s where seller_uuid=%s"
            val = (username, uuid)
            cursor.execute(sql, val)
        elif password:
            sql = "update users set password=%s where uuid=%s"
            val = (password, uuid)
            cursor.execute(sql, val)
        elif username:
            sql = "update users set username=%s where uuid=%s"
            val = (username, uuid)
            cursor.execute(sql, val)
            sql = "update items set seller_name=%s where seller_uuid=%s"
            val = (username, uuid)
            cursor.execute(sql, val)
        cursor.close()
        db.commit()
        db.close()
    
    def post_item(self, title, seller_name, uuid, seller_uuid, descr, price, contact):
        sql = "insert into items (title, seller_name, descr, price, contact, uuid, seller_uuid) values (%s, %s, %s, %s, %s, %s, %s)"
        val = (title, seller_name, descr, price, contact, uuid, seller_uuid)
        db = self.returnDbConn()
        cursor = db.cursor()
        cursor.execute(sql, val)
        cursor.close()
        db.commit()
        db.close()
    
    def delete_item(self, uuid):
        sql = "delete from items where uuid=%s"
        val = (uuid,)
        db = self.returnDbConn()
        cursor = db.cursor()
        cursor.execute(sql, val)
        cursor.close()
        db.commit()
        db.close()

# MAIN (testing only)
if __name__ == "__main__":
    db = DBHandler("root", config("MYSQL_PW"), "localhost", 13306, "local_trader")