from graph import Node, Edge, Graph, GraphError, EdgeList
import unittest

class TestGraph(unittest.TestCase):
	def setUp(self):
		pass
	
	def tearDown(self):
		Node._current_id = 0
		Edge._current_id = 0
	
	def test_graph_init(self):
		g = Graph()
		self.assertEqual(g._nodes, {})
		self.assertEqual(g._edges, {})

	def test_node_init(self):
		self.assertRaises(GraphError, Node, 1)
		self.assertRaises(GraphError, Node, {})
		self.assertRaises(GraphError, Node, object())
		
		g = Graph()
		n1 = Node(g)
		
		n2 = Node(g, type='user', name='joneses')
		self.assertEqual(n2._properties['type'], 'user')
		self.assertEqual(n2._properties['name'], 'joneses')
		self.assertEqual(n2._id, 1)
		self.assertEqual(n1._graph._nodes, {0: n1, 1: n2})
		self.assertEqual(n2._graph._nodes, {0: n1, 1: n2})
		
	def test_node_attributes(self):
		n = Node(Graph(), type='user', name='joneses')
		self.assertEqual(n.type, 'user')
		self.assertEqual(n.name, 'joneses')
		
		n.type = 'replay'
		n.name = 'feeders'
		
		self.assertEqual(n.type, 'replay')
		self.assertEqual(n.name, 'feeders')
		self.assertEqual(n._properties['type'], 'replay')
		self.assertEqual(n._properties['name'], 'feeders')
		
		n.hello = 'jackoff'
		self.assertEqual(n.hello, 'jackoff')
		self.assertEqual(n._properties['hello'], 'jackoff')
	
	def test_edge_init(self):
		n1 = Node(Graph())
		n2 = Node(Graph())
		
		self.assertRaises(GraphError, Edge, 1, 'friend', n2)
		self.assertRaises(GraphError, Edge, n1, 'friend', 2)
		self.assertRaises(GraphError, Edge, n1, 'friend', n2)
		n1._graph = 1
		self.assertRaises(GraphError, Edge, n1, 'friend', n2)
		n1._graph = n2._graph
		e1 = Edge(n1, 'friend', n2, weight=3)
		
		self.assertEqual(e1.label, 'friend')
		self.assertEqual(e1.weight, 3)
		self.assertEqual(e1._properties['weight'], 3)
		self.assertEqual(e1.head, n1)
		self.assertEqual(e1.tail, n2)
		self.assertEqual(e1._id, 0)
		
		e2 = Edge(n1, 'friend', n2, weight=3)
		
		self.assertEqual(e2._id, 1)
		self.assertEqual(n1._incoming_edges, [])
		self.assertEqual(n1._outgoing_edges, [e1, e2])
		self.assertEqual(n2._incoming_edges, [e1, e2])
		self.assertEqual(n2._outgoing_edges, [])
		self.assertEqual(n1._graph._edges, {0: e1, 1: e2})
		self.assertEqual(n2._graph._edges, {0: e1, 1: e2})
	
	def test_node_incoming_edges(self):
		g = Graph()
		n1 = Node(g)
		n2 = Node(g)
		e1 = Edge(n1, 'hates', n2, love='lost')
		e2 = Edge(n1, 'knows', n2)
		self.assertIsInstance(n2.incoming_edges(), EdgeList)
		self.assertEqual(n2.incoming_edges(), EdgeList([e1, e2]))
		self.assertEqual(n2.incoming_edges(love='lost'), EdgeList([e1]))
		self.assertEqual(n2.incoming_edges(love='dead'), EdgeList())
		self.assertEqual(n1.incoming_edges(), EdgeList())
	
	def test_node_outgoing_edges(self):
		g = Graph()
		n1 = Node(g)
		n2 = Node(g)
		e1 = Edge(n1, 'hates', n2, love='lost')
		e2 = Edge(n1, 'knows', n2)
		self.assertIsInstance(n1.outgoing_edges(), EdgeList)
		self.assertEqual(n1.outgoing_edges(), EdgeList([e1, e2]))
		self.assertEqual(n1.outgoing_edges(love='lost'), EdgeList([e1]))
		self.assertEqual(n1.outgoing_edges(love='dead'), EdgeList())
		self.assertEqual(n2.outgoing_edges(), EdgeList())
	
	def test_node_edges(self):
		g = Graph()
		n1 = Node(g)
		n2 = Node(g)
		e1 = Edge(n1, 'hates', n2, love='lost')
		e2 = Edge(n2, 'knows', n1)
		self.assertIsInstance(n1.edges(), EdgeList)
		self.assertEqual(n1.edges(), EdgeList([e1, e2]))
		self.assertEqual(n1.edges(love='lost'), EdgeList([e1]))
		self.assertEqual(n1.edges(love='dead'), EdgeList())
		self.assertEqual(n2.edges(), EdgeList([e2, e1]))
	
if __name__ == '__main__':
	unittest.main()