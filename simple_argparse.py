from symbols import NOT_SET
from simple_data import predicate_dict
from simple_config import Config_Store, Config_Push
import sys

APPLICATION_ARGUMENT_TYPE_LUT = dict()
APPLICATION_ARGUMENT_GROUPS = list()
APPLICATION_DESCRIPTION = None

def Register_Description(description):
	global APPLICATION_DESCRIPTION
	assert APPLICATION_DESCRIPTION is None
	APPLICATION_DESCRIPTION = description

class Action_Parameter:
	def __init__(self, argument, *aliases, help=NOT_SET, store_key=None, store_value=NOT_SET, push_to=None):
		self.argument = argument
		self.aliases = aliases
		self.help = help
		self.store_key = store_key
		self.store_value = store_value
		self.push_to = push_to

	def process_values(self, name):
		if self.store_value is NOT_SET:
			value = name or self
		else:
			value = self.store_value

		if self.store_key:
			Config_Store(value, self.store_key)

		elif self.push_to:
			Config_Push(value, self.push_to)



class Value_Parameter:
	def __init__(self, argument, *aliases, type=NOT_SET, help=NOT_SET, store_key=None, store_value=NOT_SET, push_to=None):
		self.argument = argument
		self.aliases = aliases
		self.type = type
		self.help = help
		self.store_key = store_key
		self.store_value = store_value
		self.push_to = push_to

	def process_values(self, name, value):

		if self.store_value is not NOT_SET:
			value = self.store_value

		if self.store_key:
			Config_Store(value, self.store_key)

		elif self.push_to:
			Config_Push(value, self.push_to)

class Argument_Group:
	def __init__(self, title, *positional_members, **named_members):
		self.title = title
		self.positional_members = positional_members
		self.named_members = named_members


def Assign_Argument_Type(application_type, argparse_type):
	assert application_type not in APPLICATION_ARGUMENT_TYPE_LUT
	APPLICATION_ARGUMENT_TYPE_LUT[application_type] = argparse_type


def Register_Argument_Group(title, *positional_members, **named_members):
	APPLICATION_ARGUMENT_GROUPS.append(Argument_Group(title, *positional_members, **named_members))



#TODO - maybe move argparse backend to separate module


import argparse
class Push_Token:
	class _Action(argparse.Action):
		def __init__(self, token_pusher, *pos, **named):
			super().__init__(*pos, **named)
			self.token_pusher = token_pusher

		def __call__(self, parser, namespace, values, option_string=None):
			if self.token_pusher.argument:
				self.token_pusher.push((self.token_pusher.argument, values))
			else:
				self.token_pusher.push((self.dest, values))

	def __init__(self, target, argument=None):
		self.target = target
		self.argument = argument

	def push(self, item):
		self.target.append(item)

	def __call__(self, *pos, **named):
		return self._Action(self, *pos, **named)


PENDING_ARGUMENTS = list()

def Configure_Argparse_Parser(parser, source, name=None):
	match source:
		case list() | tuple():
			for sub_item in source:
				Configure_Argparse_Parser(parser, sub_item)

		case dict():
			for name, sub_item in source.items():
				Configure_Argparse_Parser(parser, sub_item, name=name)

		case Argument_Group():
			Configure_Argparse_Parser(parser, source.positional_members)
			Configure_Argparse_Parser(parser, source.named_members)

		#TODO - typing for helping argparse/argcomplete
		case Action_Parameter(argument=argument, aliases=aliases):
			parser.add_argument(argument, *aliases, nargs=0, action=Push_Token(PENDING_ARGUMENTS, (name, source)))

		case Value_Parameter(argument=argument, aliases=aliases):
			parser.add_argument(argument, *aliases, nargs=1, action=Push_Token(PENDING_ARGUMENTS, (name, source)))

		case unhandled:
			raise ValueError(unhandled)


def Parse_Arguments(arguments=None):
	import argparse
	if arguments is None:
		arguments = sys.argv

	parser = argparse.ArgumentParser(add_help=False)

	Configure_Argparse_Parser(parser, APPLICATION_ARGUMENT_GROUPS)

	#parser.add_argument('--save', nargs=0, action=Push_Token(target), help="Immediate action: Save current configuration to profile")

	result, unparsed = parser.parse_known_args(arguments[1:])

	assert not unparsed, f'Could not parse arguments: {unparsed}'

	for [field_name, field], values in PENDING_ARGUMENTS:
		field.process_values(field_name, *values)
