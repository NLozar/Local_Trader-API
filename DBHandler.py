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

# MAIN (testing only)
if __name__ == "__main__":
    db = DBHandler("root", config("MYSQL_PW"), "localhost", 13306, "local_trader")
    db.get_all_items()