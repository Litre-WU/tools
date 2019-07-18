import sqlite3
import pymysql
import psycopg2


class S2S:
	def __init__(self):
		self.db = ''
		self.table = ''
		self.cursor = ''
	
	def conn_db(self, db):
		self.db = sqlite3.connect(db)
		self.cursor = self.db.cursor()
	
	def crete_table(self, db, table, fields):
		self.conn_db(db)
		self.table = table
		insert_fields = ", ".join([x[0] + " " + x[1] for x in fields.items()])
		sql = f"CREATE TABLE IF NOT EXISTS {table}(id integer(20) NOT NULL PRIMARY KEY auto_increment, {insert_fields})"
		self.cursor.execute(sql)
		self.close_db()
	
	def insert_into(self, db, table, data):
		
		self.conn_db(db)
		
		fields_name = ",".join([k for k in data.keys()])
		fields_values = ''
		for x in data.values():
			try:
				float(x)
				fields_values += str(x) + ", "
			except:
				fields_values += "'" + x + "', "
		fields_values = fields_values.strip(", ")
		
		sql = f"INSERT INTO {table}({fields_name})VALUES({fields_values})"
		self.cursor.execute(sql)
		self.close_db()
	
	def update_db(self, db, table, data):
		
		self.conn_db(db)
		updata_fields = ''
		for x in data["SET"].keys():
			updata_fields += x + "='" + data["SET"][x] + "',"
		updata_fields = updata_fields.strip(',')
		key = str(data["WHERE"]).strip("{'").strip("}").replace("':", "=")
		sql = f"UPDATE {table} SET {updata_fields} WHERE {key};"
		self.cursor.execute(sql)
		self.close_db()
	
	def close_db(self):
		self.db.commit()
		self.cursor.close()
		self.db.close()


class S2M(S2S):
	
	def conn_db(self, db):
		self.db = pymysql.connect("localhost", "root", "123456", db)
		self.cursor = self.db.cursor()
	

class S2P(S2S):
	
	def conn_db(self, db):
		self.db = psycopg2.connect(host="localhost", port=5432, user="postgres", password="123456", dbname=db)
		self.cursor = self.db.cursor()
	
	def crete_table(self, db, table, fields):
		self.conn_db(db)
		self.table = table
		insert_fields = ", ".join([x[0] + " " + x[1] for x in fields.items()])
		sql = f"CREATE TABLE IF NOT EXISTS {table} (id SERIAL PRIMARY KEY,{insert_fields})"
		self.cursor.execute(sql)
		self.close_db()


if __name__ == '__main__':
	s = S2P()
	fields = {
		"name": "varchar(20)",
		"age": "integer",
		"data": "text"
	}
	# s.crete_table('test', 'test2', fields)
	data = {
		"name": "小明",
		"age": "10",
		"data": "测试"
	}
	# s.insert_into('test', 'test2', data)
	up_data = {
		"SET": {
			"name": "小名",
			"age": "10",
			"data": "测试"
		},
		"WHERE": {
			"id": 1
		}
	}
	s.update_db('test', 'test', up_data)
