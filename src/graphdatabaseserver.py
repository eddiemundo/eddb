import rpyc
from rpyc.utils.server import ThreadedServer
import os, pickle
from graph import Graph

class GraphDatabaseError(Exception):
	"""All purpose exception class for GraphDatabase errors"""
	def __init__(self, error_message):
		self.error_message = error_message
		
	def __str__(self):
		return repr(self.error_message)

class GraphService(rpyc.Service):
	def exposed_graph(self, db_file_location):
		self.location = db_file_location
		if os.path.isfile(self.location):
			with open(self.location, 'rb') as f:
				self.graph = pickle.load(f)
			if not isinstance(self.graph, Graph):
				raise GraphDatabaseError('File is not a Graph.')
		else:
			self.graph = Graph()
		return self.graph
	
	def exposed_save(self):
		with open(self.location, 'wb') as f:
			pickle.dump(self.graph, f)
		
		
if __name__ == '__main__':
	server = ThreadedServer(
						GraphService,
						port=12345,
						protocol_config={
										'allow_exposed_attrs': False,
										'allow_public_attrs': True,
										'allow_all_attrs': True,
										'allow_getattr': True,
										'allow_setattr': True,
										'allow_pickle': True,})
	server.start()