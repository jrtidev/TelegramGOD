import sqlite3

#init db and creates db connection
class DBHelper:
	def __init__(self, dbname='god.sqlite'):
		self.dbname = dbname
		self.conn = sqlite3.connect(dbname)
#creates a new table with one column
	def setup(self):
		tblstmt = "CREATE TABLE IF NOT EXISTS items (description text, owner text)"
		itemidx = "CREATE INDEX IF NOT EXISTS itemIndex ON items (description ASC)" 
		ownidx = "CREATE INDEX IF NOT EXISTS ownIndex ON items (owner ASC)"
		self.conn.execute(tblstmt)
		self.conn.execute(itemidx)
		self.conn.execute(ownidx)
		self.conn.commit()
#add item by inserting it to the table
	def add_item(self, item_text, owner):
		stmt = 'INSERT INTO items (description, owner)  VALUES (?, ?)'
		args = (item_text, owner)
		self.conn.execute(stmt, args)
		self.conn.commit()
#takes text of an item and removes it from db
	def delete_item(self, item_text, owner):
		stmt = "DELETE FROM items WHERE description = (?) AND owner = (?)"
		args = (item_text, owner)
		self.conn.execute(stmt, args)
		self.conn.commit()
#return list of items
	def get_items(self, owner):
		stmt = 'SELECT description FROM items WHERE owner = (?)'
		args = (owner, )
		return [x[0] for x in self.conn.execute(stmt, args)]

