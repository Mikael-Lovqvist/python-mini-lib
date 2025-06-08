from symbols import NOT_SET

APPLICATION_CONFIGURATION = list()
CONFIG = dict()

def Register_Config(name, title=None, *positional_members, **named_members):
	APPLICATION_CONFIGURATION.append(Config_Group(name, title, *positional_members, **named_members))

class Config_Group:
	def __init__(self, name, title=None, *positional_members, **named_members):
		self.name = name
		self.title = title
		self.positional_members = positional_members
		self.named_members = named_members

class Factory:
	def __init__(self, factory, help=NOT_SET):
		self.factory = factory
		self.help = help


class Settable_Once:
	def __init__(self, default=NOT_SET, help=NOT_SET):
		self.default = default
		self.help = help


def Config_Store(value, dest):
	for piece in dest.split('.'):
		print(piece)

def Config_Push(value, dest):
	pass
