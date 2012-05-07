from graph import Node, Edge, Graph, ElementList
import unittest

class TestGraph(unittest.TestCase):
	def setUp(self):
		pass
	
	def test_Node_init(self):
		n = Node(0)
		self.assertEqual(n.id, 0)
		self.assertEqual(n.properties, {})
		n = Node(1)
		self.assertEqual(n.id, 1)
		self.assertEqual(n.properties, {})
		n = Node(2, {'type': 'user', 'username': 'N7Shepard'})
		self.assertEqual(n.id, 2)
		self.assertEqual(n.properties, {'type': 'user', 'username': 'N7Shepard'})
		self.assertEqual(n.type, 'user')
		self.assertEqual(n.username, 'N7Shepard')
		
	def test_Node(self):
		n = Node(0)
		n.name = 'jack'
		self.assertEqual(n.properties['name'], 'jack')
		n.gender = 'sexy'
		self.assertEqual(n.properties['gender'], 'sexy')
	
	def test_Node_edges(self):
		jack = Node(0, {'age': 21}, name='jack')
		jill = Node(1, {'age': 21}, name='jill')
		jon = Node(2, {'age': 22}, name='jon')
		e0 = Edge(0, jack, 'loves', jill, intensity=100, ferocity=100)
		e1 = Edge(1, jack, 'loves', jon)
		e2 = Edge(2, jon, 'loves', jack)
		e3 = Edge(3, jill, 'bangs', jack)
		e4 = Edge(4, jill, 'hates', jon)
		eall_set = set((e0, e1, e2, e3))
		eloves_set = set((e0,e1,e2))
		self.assertTrue(eall_set == set(jack.edges()))
		self.assertTrue(e4 not in jack.edges())
		self.assertTrue(eloves_set == set(jack.edges('loves')))
		self.assertTrue(set([e2])==set(jack.edges('loves', 'incoming')))
		self.assertTrue(set([e0]) == set(jack.edges('loves', intensity=100)))
		self.assertTrue(set([]) == set(jack.edges('loves', properties={'ferocity':99}, intensity=100)))
	
	def test_Edge_init(self):
		jack = Node(0)
		jill = Node(1)
		e = Edge(0, jack, 'loves', jill)
		self.assertEqual(e.id, 0)
		self.assertEqual(e.label, 'loves')
		self.assertEqual(e.start_node, jack)
		self.assertEqual(e.end_node, jill)
		self.assertEqual(e.properties, {})
		e = Edge(0, jack, 'loves', jill, {'intensity': 100, 'blindness': 100})
		self.assertEqual(e.intensity, 100)
		self.assertEqual(e.blindness, 100)
		
	def test_Edge(self):
		jack = Node(0)
		jill = Node(1)
		e = Edge(0, jack, 'loves', jill)
		e.label = 'hates'
		e.intensity = 99
		self.assertEqual(e.label, 'hates')
		self.assertTrue('label' not in e.properties)
		self.assertTrue(e.properties['intensity'] == 99)
		
	def test_ElementList(self):
		jack = Node(0, {'age': 21}, name='jack')
		jill = Node(1, {'age': 21}, name='jill')
		jon = Node(2, {'age': 22}, name='jon')
		e0 = Edge(0, jack, 'loves', jill, intensity=100, ferocity=100)
		e1 = Edge(1, jack, 'loves', jon)
		e2 = Edge(2, jon, 'loves', jack)
		e3 = Edge(3, jill, 'bangs', jack)
		e4 = Edge(4, jill, 'hates', jon)
		self.assertTrue(set([e0]) == set(jack.edges().filter_by_property({'ferocity':100},intensity=100)))
		
	def test_Graph_init(self):
		g = Graph()
		
	def test_Graph_add_node(self):
		g = Graph()
		g.add_node({'type': 'user', 'username': 'Shepard'}, emailaddress='shepard@normandy.com',summonername='N7Shepard')
		self.assertTrue(g._nodes[0].type == 'user')
		self.assertTrue(g._nodes[0].username == 'Shepard')
		self.assertTrue(g._nodes[0].emailaddress == 'shepard@normandy.com')
		self.assertTrue(g._nodes[0].summonername == 'N7Shepard')
		self.assertTrue(g._nodes[0].id == 0)
		self.assertTrue(len(g._nodes) == 1)
		g.add_node()
		self.assertTrue(len(g._nodes) == 2)
		self.assertTrue(1 in g._nodes)
		self.assertTrue(g.add_node(name='Geronimo').name == 'Geronimo')
		jack = g.add_node(name='jack')
		self.assertEqual(jack.name, 'jack')
		
	def test_Graph_add_edge(self):
		g = Graph()
		jack = g.add_node()
		jill = g.add_node()
		g.add_edge(jack, 'loves', jill)
		e = g.add_edge(jack, 'kills', jill)
		self.assertTrue(len(g._edges) == 2)
		self.assertTrue(g._edges[2].label=='loves')
		self.assertTrue(g._edges[3].label=='kills')
		self.assertEqual(e, g._edges[3])
	
	def test_Graph_remove_edge(self):
		g = Graph()
		jack = g.add_node()
		jill = g.add_node()
		g.add_edge(jack, 'loves', jill)
		g.remove_edge(2)
		self.assertTrue(len(jack.edges()) == 0)
		self.assertTrue(len(jill.edges()) == 0)
		self.assertTrue(len(g._edges) == 0)
	
	def test_Graph_remove_node(self):
		g = Graph()
		jack = g.add_node()
		jill = g.add_node()
		g.add_edge(jack, 'loves', jill)
		g.add_edge(jack, 'kills', jill)
		g.remove_node(0)
		self.assertTrue(len(g._nodes) == 1)
		self.assertTrue(len(g._edges) == 0)
		self.assertEqual(jill, g._nodes[1])
	
	def test_Graph_find_reachable_by(self):
		g = Graph()
		
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
		
		self.assertEqual([b,c,d,e,f], list(iterator))
		
		iterator = g.find_reachable_nodes_from(a, contains='outgoing')
		self.assertEqual([b,c,d,e,f], list(iterator))
		iterator = g.find_reachable_nodes_from(a, contains='incoming')
		self.assertEqual([f,e,b,c], list(iterator))
		
	def test_Graph_node(self):
		g = Graph()
		a = g.add_node()
		b = g.add_node()
		self.assertEqual(g.node(), a)
		self.assertEqual(g.node(name='jack'), None)
		self.assertEqual(g.node(1), b)
		
	def test_Graph_nodes(self):
		g = Graph()
		self.assertEqual(g.nodes(), ElementList([]))
		a = g.add_node(name='jack')
		b = g.add_node()
		self.assertEqual(g.nodes(), ElementList([a, b]))
		self.assertEqual(g.nodes(name='jack'), ElementList([a]))
	
	def test_Graph_edge(self):
		g = Graph()
		jack = g.add_node()
		jill = g.add_node()
		loves = g.add_edge(jack, 'loves', jill)
		kills = g.add_edge(jack, 'kills', jill)
		self.assertEqual(g.edge(label='loves'), loves)
		self.assertEqual(g.edge(label='deads'), None)
		self.assertEqual(g.edge(2), loves)
	
	def test_Graph_edges(self):
		g = Graph()
		jack = g.add_node()
		jill = g.add_node()
		self.assertEqual(g.edges(), ElementList())
		loves = g.add_edge(jack, 'loves', jill, intensity=100)
		kills = g.add_edge(jack, 'kills', jill)
		self.assertEqual(g.edges(), ElementList([loves, kills]))
		self.assertEqual(g.edges('loves'), ElementList([loves]))
		self.assertEqual(g.edges('dead'), ElementList())
		self.assertEqual(g.edges(intensity=100), ElementList([loves]))
		
	def test_Node_adjacent_nodes(self):
		g = Graph()
		jack = g.add_node()
		jill = g.add_node(name='jill')
		g.add_edge(jack, 'loves', jill)
		self.assertEqual(jack.adjacent_nodes(name="jill")[0], jill)
		self.assertEqual(jack.adjacent_node(name="jill"), jill)
		

		
if __name__ == '__main__':
	unittest.main()