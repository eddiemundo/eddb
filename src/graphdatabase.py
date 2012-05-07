import rpyc
import pickle
from graph import Graph
class GraphDatabase(object):
	def __init__(self, host, port, db_file_location):
		self.location = db_file_location
		self.conn = rpyc.connect(host, port,
									config = {
											'allow_exposed_attrs': False,
											'allow_pickle': True,
											'allow_public_attrs': True,
											'allow_all_attrs': True,
											'allow_getattr': True,
											'allow_setattr': True,})
		self.graph = self.conn.root.graph(db_file_location)
	
	
	def save(self):
		self.conn.root.save()

loc = 'C:/Users/Shenra/git/LoLReplaySite/LoLReplaySite/lolreplaysite/databases/lolreplaysite.gd'
def db():
	return GraphDatabase('localhost', 12345, loc)

gd = db()
g = gd.graph
print(g)