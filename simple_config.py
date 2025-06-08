from types import SimpleNamespace
from symbols import NOT_SET
import os, re


CONFIG_TREE = SimpleNamespace()
CONFIG = SimpleNamespace()
CONFIG_SETTABLE_ONCE_SET = set()

CONFIG_FORMAT = dict()

CONFIG_DESCRIPTION = None

def Register_Config_Description(description):
	global CONFIG_DESCRIPTION
	assert CONFIG_DESCRIPTION is None
	CONFIG_DESCRIPTION = description

def Assign_Config_Format(type, formatter):
	CONFIG_FORMAT[type] = formatter

def Register_Config(name, title=None, *positional_members, **named_members):
	def process(config_tree, value_tree, item_name, item_value):
		match item_value:
			case Config_Group():
				config_tree_node = SimpleNamespace()
				value_tree_node = SimpleNamespace()
				setattr(config_tree, item_name, config_tree_node)
				setattr(value_tree, item_name, value_tree_node)
				for positional in item_value.positional_members:
					raise NotImplementedError()	#TODO - implement

				for sub_item_name, sub_item_value in item_value.named_members.items():
					process(config_tree_node, value_tree_node, sub_item_name, sub_item_value)

			case Settable_Once():
				setattr(config_tree, item_name, item_value)
				if item_value.default is not NOT_SET:
					setattr(value_tree, item_name, item_value.default)

			case Factory():
				setattr(config_tree, item_name, item_value)
				setattr(value_tree, item_name, item_value.factory())

			case unhandled:
				raise ValueError(unhandled)

	process(CONFIG_TREE, CONFIG, name, Config_Group(name, title, *positional_members, **named_members))



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


# def Config_Finalize():
# 	global CONFIG_TREE
# 	print('Finalize')

# 	CONFIG_TREE = Config_Group(None)

# 	for config in APPLICATION_CONFIGURATION:
# 		ptr = CONFIG_TREE

# 		if '.' in config.name or config.positional_members:
# 			raise NotImplementedError

# 		# pieces = config.name.split('.')
# 		# for piece in pieces[:-1]:	#All but one
# 		# 	pending_ptr = ptr.named_members.get(piece)
# 		# 	if pending_ptr is None:
# 		# 		print('Should transfer config')
# 		# 	else:
# 		# 		ptr = pending_ptr

# 		# if config.positional_members:

# 		#TODO - implement and test proper tree handling above - for now let's just cheat (we may alter actually do the proper handling when creating the Config_Group instead
# 		ptr.named_members[config.name] = config


def Config_Resolve(path):
	parent_value_ptr = None
	config_ptr, value_ptr = CONFIG_TREE, CONFIG
	for piece in path.split('.'):
		config_ptr = getattr(config_ptr, piece)
		if value_ptr is not NOT_SET:
			parent_value_ptr = value_ptr
			value_ptr = getattr(value_ptr, piece, NOT_SET)
		else:
			raise Exception	#This probably means we didn't properly initialize all values

	return config_ptr, parent_value_ptr, piece, value_ptr


def Config_Store(value, dest):
	config_ptr, parent_value_ptr, value_name, value_ptr = Config_Resolve(dest)

	if config_ptr in CONFIG_SETTABLE_ONCE_SET:
		raise Exception(f'Tried to set "{dest}" more than once')

	CONFIG_SETTABLE_ONCE_SET.add(config_ptr)

	#TODO - type coercion support?
	#if config_ptr.coerce:
	#	value = config_ptr.coerce(value)

	setattr(parent_value_ptr, value_name, value)

def Config_Push(value, dest):
	config_ptr, parent_value_ptr, value_name, value_ptr = Config_Resolve(dest)

	#TODO - type coercion support?
	#if config_ptr.coerce:
	#	value = config_ptr.coerce(value)

	value_ptr.append(value)

def Walk_Config(config_tree, value_tree, path=None):

	match config_tree:
		case SimpleNamespace():
			for sub_key, sub_value in config_tree.__dict__.items():
				yield from Walk_Config(sub_value, getattr(value_tree, sub_key), f'{path}.{sub_key}' if path else sub_key)

		case Factory():
			yield path, config_tree, value_tree

		case Settable_Once():
			yield path, config_tree, value_tree

		case unhandled:
			raise ValueError(unhandled)


def Format_Value(value):
	if formatter := CONFIG_FORMAT.get(type(value)):
		return formatter(value)

	else:
		match value:
			case list():
				return f'[{", ".join(map(Format_Value, value))}]'

			case str() | float() | int():
				return repr(value)

			case unhandled:
				raise TypeError(unhandled)




def Read_Config(path, section_map, include_help=True):

	section_regex = re.compile(r'\[(.*)\]')

	lines_to_keep = list()
	keep_section = True


	with open(path, 'r', encoding='utf-8') as infile:
		for line in map(str.rstrip, infile):
			if section_match := section_regex.fullmatch(line):
				[section_name] = section_match.groups()
				keep_section = section_name not in section_map

			if keep_section:
				lines_to_keep.append(line)



def Update_Config(path, section_map, include_help=True):
	#TODO - we need to rethink the whole config thing and make things better coupled (but still making it flexible)

	new_file = not os.path.exists(path)

	if not new_file:

		section_regex = re.compile(r'\[(.*)\]')

		lines_to_keep = list()
		keep_section = True


		with open(path, 'r', encoding='utf-8') as infile:
			for line in map(str.rstrip, infile):
				if section_match := section_regex.fullmatch(line):
					[section_name] = section_match.groups()
					keep_section = section_name not in section_map

				if keep_section:
					lines_to_keep.append(line)

	with open(path, 'w', encoding='utf-8') as outfile:
		if new_file and CONFIG_DESCRIPTION:
			for line in CONFIG_DESCRIPTION.splitlines():
				print(f'# {line}', file=outfile)

		for line in lines_to_keep:
			print(line, file=outfile)


		for section_name, [section_config, section_value] in section_map.items():
			print(f'[{section_name}]', file=outfile)

			for path, config, value in Walk_Config(section_config, section_value):
				if include_help and config.help:
					print(file=outfile)

					first_line, *remaining_lines = config.help.splitlines()
					print(f'# {path} -=- {first_line}', file=outfile)
					for line in remaining_lines:
						print(f'# {line}', file=outfile)

				print(f'{path} = {Format_Value(value)}', file=outfile)


