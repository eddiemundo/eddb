"""
Everything to do with Graphs, Nodes, Edges, and how to search them. ALl of
this was made for a graph database.

TODO:
Add a parameter that takes an evaluator function for filtering elements.
Currently can only filter elements by equality of their properties
"""


from collections import defaultdict, deque


class GraphError(Exception):
	"""All purpose exception class for GraphDatabase errors"""
	def __init__(self, error_message):
		self.error_message = error_message
		
	def __str__(self):
		return repr(self.error_message)


def filter(graph_elements, properties=None, **kwargs):
	if properties is None:
		properties = dict(kwargs)
	else:
		properties.update(kwargs)
	
	
	result_list = []
	for element in graph_elements:
		if all(k in element.properties and element.properties[k] == v
				for k, v in properties.items()):
			result_list.append(element)
	return ElementList(result_list)

class ElementList(list):
	def filter_by_property(self, properties=None, **kwargs):
		"""
		Filters graph elements by property
		Keyword arguments:
		properties -- a dict containing properties to filter by
		kwargs -- a dict containing properties to filter by
		"""
		if properties is None:
			properties = {}
		properties.update(kwargs)
		result_list = ElementList()
		for element in self:
			if all(k in element.properties and element.properties[k] == v
					for k, v in properties.items()):
				result_list.append(element)
		return result_list

class Node(object):
	"""
	A node in a graph. Node properties can be accessed like attributes.
	
	Instance variables:
	id -- the unique id of the node in the graph. Do not modify
	properties -- a dict containing the properties of the graph. The keys of
		this dict need to be strings. Key names in the dict must not overlap
		with object/class variable or method names
	_edges -- a default dict containing defaultdicts representing _edges, and
		their direction
		eg. _edges['knows']['outgoing'] == [all outgoing _edges labelled 'knows']
	"""
	_initialized = False
	def __init__(self, id, properties=None, **kwargs):
		self.id = id
		if properties is None:
			self.properties = {}
		else:
			self.properties = properties
		self.properties.update(kwargs)
		# syntax: eg. _edges['knows']['incoming'] == [incoming knows get_edges]
		self._edges = {}
		self._initialized = True
	
	def __setattr__(self, name, value):
		# If this object hasn't finished its __init__ method 
		if not self._initialized:
			object.__setattr__(self, name, value)
		else:
			if name in self.__dict__:
				object.__setattr__(self, name, value)
			else:
				self.properties[name] = value
	
	def __getattr__(self, name):
		"""When python can't find the attribute it comes here"""
		return self.properties[name]
	
	def __getstate__(self): return self.__dict__
	def __setstate__(self, d): self.__dict__.update(d)
		
	
	def edges(self, label=None, direction='any', properties=None, **kwargs):
		"""
		Return a list of get_edges connected to this node (incoming or outgoing)
		with label=label and all the properties in properties and kwargs
		combined
		
		Keyword arguments:
		label -- the label of the get_edges to be returned
		direction -- 'incoming', 'outgoing', or 'both'
		properties -- the properties of the get_edges to be returned
		kwargs -- the properties of the get_edges to be returned
		"""
		if properties is None:
			properties = {}
		result_edges = []
		
		# simple refactoring of duplicate code
		def edges_helper(direction_edge_map):
			if direction == 'incoming' or direction == 'outgoing':
				filtered_edges = filter(direction_edge_map[direction],
										properties,
										**kwargs)
				result_edges.extend(filtered_edges)
			elif direction == 'any':
				for edges in direction_edge_map.values():
					filtered_edges = filter(edges,
											properties,
											**kwargs)
					result_edges.extend(filtered_edges)
			else:
				print("Error: direction isn't a valid direction")
		
		if label is None:
			for direction_edge_map in self._edges.values():
				edges_helper(direction_edge_map)
		elif label in self._edges:
			direction_edge_map = self._edges[label]
			edges_helper(direction_edge_map)
		return ElementList(result_edges)
	
	
			
	def adjacent_nodes(self, label=None, direction="outgoing",
					properties=None, **kwargs):
		"""
		Return a list of adjacent nodes	connected to this node by an edge
		labeled label, with direction == direction. The properties of each
		adjacent node returned will be a subset of properties.update(kwargs).
		
		If label is None then return all adjacent nodes with the above
		qualifications minus label.
		
		Keyword arguments:
		label -- label of the edges connecting the adjacent nodes to be
			returned. Default None.
		direction -- direction of the edges connecting the nodes to be
			returned. Can take values 'incoming', 'outgoing', 'both'.
			Default 'outgoing'
		properties -- dict containing properties that the adjacent nodes must
			have. Default None
		kwargs -- dict containing properties that the adjacent nodes must have
			Default None.
		"""
		if properties is None:
			properties = {}
		result_nodes = ElementList()
		if label is None:
			for direction_edges_map in self._edges.values():
				if direction == 'any':
					for d, edges in direction_edges_map.items():
						if d == 'incoming':
							for edge in edges:
								result_nodes.append(edge.start_node)
						else:
							for edge in edges:
								result_nodes.append(edge.end_node)
				elif direction == 'incoming' or direction == 'outgoing':
					for edge in direction_edges_map[direction]:
						if direction == 'incoming':
							result_nodes.append(edge.start_node)
						else:
							result_nodes.append(edge.end_node)
				else:
					raise GraphError('"{0}" is not valid direction'
									.format(direction))
		else:
			if label in self._edges:
				direction_edges_map = self._edges[label]
				if direction == 'incoming':
					for edge in direction_edges_map[direction]:
						result_nodes.append(edge.start_node)
				elif direction == 'outgoing':
					for edge in direction_edges_map[direction]:
						result_nodes.append(edge.end_node)
				elif direction == 'any':
					for d, edges in direction_edges_map:
						if d == 'incoming':
							for edge in edges:
								result_nodes.append(edge.start_node)
						else:
							for edge in edges:
								result_nodes.append(edge.end_node)
		return result_nodes.filter_by_property(properties, **kwargs)
	
	def adjacent_node(self, label=None, direction="outgoing",
					properties=None, **kwargs):
		"""
		Return an arbitrary adjacent node connected to this node by an edge
		labeled label, with direction == direction. The properties of this
		adjacent node will be a subset of properties.update(kwargs). Otherwise
		return None.
		
		If label is None then return all adjacent nodes with the above
		qualifications minus label.
		
		Keyword arguments:
		label -- label of the edge connecting the adjacent node to be
			returned. Default None.
		direction -- Direction of the edge connecting the adjacent node to be
			returned. Can take values 'incoming', 'outgoing', 'both'. Default
			'outgoing'
		properties -- dict containing properties that the adjacent node must
			have. Default None.
		kwargs -- dict containing properties that the adjacent node must
			have. Default None.
		"""
		nodes = self.adjacent_nodes(label, direction, properties, **kwargs)
		if nodes:
			return nodes[0]
		else:
			return None

class Edge(object):
	"""
	An edge in a graph. Key names of the properties dict are restricted from
	['id', 'label', 'start_node', 'end_node'] and any of the method names
	
	Both Node and Edge share the same _initialized, getattr, setattr,
	properties code
	"""
	_initialized = False
	def __init__(self, id, start_node, label, end_node, properties=None, **kwargs):
		self.id = id
		self.label = label
		self.start_node = start_node
		self.end_node = end_node
		if properties is None:
			self.properties = {}
		else:
			self.properties = properties
		self.properties.update(kwargs)
		# all this code is because I can't pickle defaultdict of defaultdicts
		# and I don't want to mess with __getstate__/__setstate__ right now
		if label not in start_node._edges:
			start_node._edges[label] = {}
			start_node._edges[label]['outgoing'] = []
			start_node._edges[label]['incoming'] = []
		if label not in end_node._edges:
			end_node._edges[label] = {}
			end_node._edges[label]['incoming'] = []
			end_node._edges[label]['outgoing'] = []
		
		start_node._edges[label]['outgoing'].append(self)
		end_node._edges[label]['incoming'].append(self)
		self._initialized = True
		
	def __setattr__(self, name, value):
		# If this object hasn't finished its __init__ method 
		if not self._initialized:
			object.__setattr__(self, name, value)
		else:
			if name in self.__dict__:
				object.__setattr__(self, name, value)
			else:
				self.properties[name] = value
	
	def __getattr__(self, name):
		"""When python can't find the attribute it comes here"""
		return self.properties[name]
	
	def __getstate__(self): return self.__dict__
	def __setstate__(self, d): self.__dict__.update(d)
	

class Graph(object):
	def __init__(self):
		self._nextid = 0
		self._nodes = {}
		self._edges = {}
	
	def node(self, id=None, properties=None, **kwargs):
		"""
		Returns a node with id==id and all the properties in properties and
		kwargs combined. If id==None, returns an arbitrary node with all the
		properties in properties and kwargs combined. Property keys in kwargs
		will overwrite property keys in properties if they match.
		
		Keyword arguments:
		id -- the id of the node to return
		properties -- a dict containing properties of the node to return 
		kwargs -- a dict containing properties of the node to return
		"""
		if properties is None:
			properties = {}
		if id is None:
			nodes = filter(self._nodes.values(), properties, **kwargs)
			if not nodes:
				return None
			else:
				return nodes[0]
		else:
			if id in self._nodes:
				result_node = self._nodes[id]
				properties.update(kwargs)
				for key, value in properties.items():
					if key not in result_node.properties:
						return None
					if result_node.properties[key] != value:
						return None
				return result_node
			else:
				return None
	
	def nodes(self, properties=None, **kwargs):
		"""
		Returns a list containing nodes with all the properties in
		properties_dict and properties combined. If both are empty, returns
		all the nodes in the graph.
		
		Keyword arguments:
		properties_dict -- a dict containing properties of the nodes to return
		properties -- a dict containing properties of the nodes to return
		"""
		if properties is None:
			properties = {}
		return filter(self._nodes.values(), properties, **kwargs)
	
	def edge(self, id=None, label=None, properties=None, **kwargs):
		"""
		Returns the edge with id=id or returns an arbitrary edge with label=
		label, and properties=properties
		
		Keyword arguments:
		id -- the id of the edge to return
		label -- the label of the edge to return
		properties_dict -- a dict containing properties of the edge to return
		properties -- a dict containing properties of the edge to return
		"""
		if properties is None:
			properties = {}
		if id is None:
			# real sloppy but works
			results = []
			edges = filter(self._edges.values(), properties, **kwargs)
			if label is None:
				results = edges
			else:
				for edge in edges:
					if edge.label == label:
						results.append(edge)
			if not results:
				return None
			else:
				return results[0]
		else:
			return self._edges[id]
		
	def edges(self, label=None, properties=None, **kwargs):
		"""
		Returns a list of get_edges with label=label, and the properties of
		properties_dict and properties combined
		
		Keyword arguments:
		label -- the label of the get_edges to return
		properties_dict -- a dict containing properties of the get_edges to return
		properties -- a dict containing properties of the get_edges to return
		"""
		if properties is None:
			properties = {}
		if label is None:
			return filter(self._edges.values(), properties, **kwargs)
		else:
			results = []
			for edge in self._edges.values():
				if label == edge.label:
					results.append(edge)
			return filter(results, properties, **kwargs)
	
	def add_node(self, properties=None, **kwargs):
		"""
		Adds a node to the graph, and returns it. Arguments properties and
		kwargs cannot have "id" as a key as it's reserved.
		
		Keyword arguments:
		properties -- a dict containing the properties of the node
		kwargs -- a dict containing the properties of the node
		"""
		if properties is None:
			properties={}
		# may change method sig of Node since we can always combine arguments
		# here
		node = Node(self._nextid, properties, **kwargs)
		self._nodes[self._nextid] = node
		self._nextid += 1
		return node
	
	def remove_node(self, id):
		"""
		Removes node from the graph by id. See also, node.remove()
		
		Keyword arguments:
		id -- the id of the node to remove
		"""
		if id in self._nodes:
			node = self._nodes[id]
			edges = node.edges()
			# ugly can maybe fix it up with sets
			for edge in edges:
				label = edge.label
				del edge.start_node._edges[label]
				del edge.end_node._edges[label]
				del self._edges[edge.id]
			del self._nodes[id]
		else:
			# return a real exception someday
			print('Error: Cannot remove node since id does not exist')
	
	def remove_nodes(self, properties, **kwargs):
		"""
		Remove all nodes with any of the properties in properties or kwargs
		
		Keyword arguments:
		properties -- a dict containing properties of nodes to be removed
		kwargs -- a dict containing properties of nodes to be removed
		"""
		raise NotImplementedError
	
	def add_edge(self, start_node, label, end_node, properties=None, **kwargs):
		"""
		Connect two nodes with an edge
		
		Keyword arguments:
		start_node -- the node the edge starts from
		label -- the label of the edge
		end_node -- the node the edge ends at
		properties -- a dict containing properties of the edge
		kwargs -- a dict containing properties of the edge
		"""
		if properties is None:
			properties = {}
		edge = Edge(self._nextid, start_node, label, end_node, properties, **kwargs)
		self._edges[self._nextid] = edge
		self._nextid += 1
		return edge
	
	def remove_edge(self, id):
		"""
		Remove an edge from the graph by id. See also, node.remove_edge(), and
		edge.remove()
		
		Keyword arguments:
		id -- id of the edge to remove
		"""
		edge = self._edges[id]
		label = edge.label
		del edge.start_node._edges[label]
		del edge.end_node._edges[label]
		del self._edges[id]
		
	def remove_edges(self, ids, properties, **kwargs):
		"""
		Remove all get_edges from the graph with any of the properties in
		properties or kwargs
		
		Keyword arguments:
		ids -- list of ids of edges to remove
		properties -- a dict containing the properties of nodes to be removed
		kwargs -- a dict containing properties of nodes to be removed
		"""
		raise NotImplementedError
	
	def find_reachable_nodes_from(self, start_node, **kwargs):
		"""
		Returns an iterator of all nodes reachable from start_node through
		get_edges labeled with edge_labels. If edge_labels is None then all nodes
		reachable from start_node through any outgoing edge is returned.
		
		Keyword arguments:
		start_node -- the node to start the search from
		kwargs -- a dict whose only keys are edge labels and whose
		values are a direction 'incoming', 'outgoing', 'any'
			eg. {'knows': 'incoming', 'hates':'any'}
		"""
		return BreadthFirstTraverser(start_node, **kwargs)
	
class BreadthFirstTraverser(object):
	"""
	An iterator that returns nodes that can be found from start_node through
	the edge labels/directions specified by kwargs to the constructor
	
	Instance variables:
	self.current_node -- the node that will be returned on the next iteration.
		If there is no next node its value will be None
	self.depth -- the depth of the node that will be returned on the next
		iteration. If there is no next node its value will be -1
	"""
	def __init__(self, start_node, **kwargs):
		"""
		Initializes the instance variables for the iterator.
		
		Keyword arguments:
		start_node -- the node obj to start the search from
		kwargs -- dictionary containing 2 keys 'incoming' and 'outgoing'.
			The dictionary values for both keys are iterables containing\
			Relation objects 
			
			eg.
			kwargs[edge_label] = edge_direction
			kwargs['knows'] = 'any'
			kwargs['hates'] = 'incoming'
			kwargs['creator'] = 'outgoing'
		"""
		self._next = deque(((start_node, 0),))
		self._visited = set()
		self.kwargs = kwargs
		# peek at the node, and its depth that will be returned next
		self.current_node, self.depth = self._next[0]
		
	def __iter__(self):
		return self
	
	def __next__(self):
		if not self._next:
			raise StopIteration
		
		current_node, current_depth = self._next.popleft()
		self._visited.add(current_node)
		
		# needs refactoring, also not efficient
		if self.kwargs:
			for label, direction in self.kwargs.items():
				edges = current_node.edges(label, direction)
				for edge in edges:
					node = None
					if edge.start_node == current_node:
						node = edge.end_node
					else:
						node = edge.start_node
					next_nodes = [n for n, _ in self._next]
					if node not in self._visited and node not in next_nodes:
						self._next.append((node, current_depth + 1))
		else:
			edges = current_node.edges(direction='outgoing')
			for edge in edges:
				node = None
				if edge.start_node == current_node:
					node = edge.end_node
				else:
					node = edge.start_node
				next_nodes = [n for n, _ in self._next]
				if node not in self._visited and node not in next_nodes:
					self._next.append((node, current_depth + 1))
		if self._next:
			self.current_node, self.depth = self._next[0]
		else:
			self.current_node = None
			self.depth = -1
		if len(self._visited) == 1:
			return self.__next__()
		else:
			return current_node
			
			
			
		
		
		
		
		