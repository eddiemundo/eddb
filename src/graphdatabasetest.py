import os
import unittest
from graphdatabase import GraphDatabase

class TestGraphDatabase(unittest.TestCase):
	def setUp(self):
		self.location = 'test.gd'
		if os.path.isfile(self.location):
			os.remove(self.location)
		self.gd = GraphDatabase('localhost', 12345, self.location)
	
	def test_gd(self):
		g = self.gd.graph
		a = g.add_node()
		b = g.add_node()
		c = g.add_node()
		d = g.add_node()
		e = g.add_node()
		f = g.add_node()
		
		g.add_edge(a, 'contains', b)
		g.add_edge(a, 'contains', c)
		g.add_edge(a, 'contains', d)
		g.add_edge(b, 'contains', e)
		g.add_edge(c, 'contains', e)
		g.add_edge(e, 'contains', f)
		g.add_edge(f, 'contains', a)
		
		iterator = g.find_reachable_nodes_from(a)
		
		self.assertEquals([b,c,d,e,f], list(iterator))
		
		iterator = g.find_reachable_nodes_from(a, contains='outgoing')
		self.assertEquals([b,c,d,e,f], list(iterator))
		iterator = g.find_reachable_nodes_from(a, contains='incoming')
		self.assertEquals([f,e,b,c], list(iterator))
		
		replay = g.add_node(type='replay')
		comment = g.add_node(type='comment', name='Jon Salamander', comment="Son, don't fuck around.")
		g.add_edge(replay, 'owns', comment)
		