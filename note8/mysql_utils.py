import pymysql

class MysqlUtils:
    def __init__(self, host='127.0.0.1', user='root', password='123456', database='note123'):
        """Initialize the database connection."""
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.db = None
        self.cursor = None

    def connect(self):
        """Connect to the database."""
        self.db = pymysql.connect(host=self.host, user=self.user, password=self.password, db=self.database)
        self.cursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)

    def disconnect(self):
        """Disconnect from the database."""
        if self.cursor:
            self.cursor.close()
        if self.db:
            self.db.close()

    def insert(self, sql, params=None):
        """Insert data into the database."""
        try:
            self.connect()
            self.cursor.execute(sql, params)
            self.db.commit()
        except Exception as e:
            print(f"Error inserting data: {e}")
            self.db.rollback()
        finally:
            self.disconnect()

    def fetchone(self, sql, params=None):
        """Fetch a single result from the database."""
        result = None
        try:
            self.connect()
            self.cursor.execute(sql, params)
            result = self.cursor.fetchone()
        except Exception as e:
            print(f"Error fetching data: {e}")
        finally:
            self.disconnect()
        return result

    def fetchall(self, sql, params=None):
        """Fetch all results from the database."""
        results = None
        try:
            self.connect()
            self.cursor.execute(sql, params)
            results = self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching data: {e}")
        finally:
            self.disconnect()
        return results

    def delete(self, sql, params=None):
        """Delete data from the database."""
        try:
            self.connect()
            self.cursor.execute(sql, params)
            self.db.commit()
        except Exception as e:
            print(f"Error deleting data: {e}")
            self.db.rollback()
        finally:
            self.disconnect()

    def update(self, sql, params=None):
        """Update data in the database."""
        try:
            self.connect()
            self.cursor.execute(sql, params)
            self.db.commit()
        except Exception as e:
            print(f"Error updating data: {e}")
            self.db.rollback()
        finally:
            self.disconnect()

    def get_user_by_username_and_password(self, username, password):
        """通过用户名和密码从数据库中检索用户。"""
        sql = "SELECT * FROM users WHERE username = %s AND password = %s"
        params = (username, password)
        return self.fetchone(sql, params)

    def get_cursor(self):
        """Return the cursor object."""
        return self.cursor


