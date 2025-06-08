class Symbol:
	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return f'sym:{self.name}'

class Local_Symbol:
	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return f'ls:{self.name}'


