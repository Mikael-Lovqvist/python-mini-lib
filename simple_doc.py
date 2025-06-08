import simple_argparse as SA
import simple_config as SC

BASE_INDENT = '  '

#TODO - we could add some type hints and other stuff to integrate into documentation but this is a start
#TODO - document aliases

def Create_Configuration_Documentation(config, level=0):
	result = Title(config.title, level)
	indent = BASE_INDENT * level

	for item in config.positional_members:
		match item:
			case unhandled:
				raise ValueError(unhandled)

	for item_name, item in config.named_members.items():
		match item:
			case SC.Factory():
				result.append(f'{indent}{item_name}')
				if item.help:
					result += [f'{BASE_INDENT * (level + 1)}{line}' for line in item.help.splitlines()] + ['']

			case SC.Settable_Once():
				result.append(f'{indent}{item_name}')
				if item.help:
					result += [f'{BASE_INDENT * (level + 1)}{line}' for line in item.help.splitlines()] + ['']

			case unhandled:
				raise ValueError(unhandled)



	return result

def Create_Group_Documentation(group, level=0):
	result = Title(group.title, level)
	indent = BASE_INDENT * level

	for item in group.positional_members:
		match item:
			case SA.Argument_Group():
				result += Create_Group_Documentation(item, level+1)

			case unhandled:
				raise ValueError(unhandled)

	for item_name, item in group.named_members.items():
		match item:
			case SA.Action_Parameter():
				result.append(f'{indent}{item.argument}')
				if item.help:
					result += [f'{BASE_INDENT * (level + 1)}{line}' for line in item.help.splitlines()] + ['']

			case SA.Value_Parameter():
				result.append(f'{indent}{item.argument} {item_name.upper()}')
				if item.help:
					result += [f'{BASE_INDENT * (level + 1)}{line}' for line in item.help.splitlines()] + ['']

			case unhandled:
				raise ValueError(unhandled)


	return result




def Title(title, level=0):
	under_lines = '━═─'
	indent = BASE_INDENT * level
	under_line = under_lines[level] if level < len(under_lines) else None

	if under_line:
		return [
			f'{indent}{title}',
			f'{indent}{len(title) * under_line}',
		]
	else:
		return [
			f'{indent}{title}',
		]



def Create_Documentation():
	from simple_argparse import APPLICATION_ARGUMENT_GROUPS
	from simple_config import APPLICATION_CONFIGURATION
	#TODO - modularize better for supporting different formatters
	result = list()

	result += Title('Command line arguments')
	for group in APPLICATION_ARGUMENT_GROUPS:
		result += Create_Group_Documentation(group, 1)

	if any(config.title for config in APPLICATION_CONFIGURATION):
		result += Title('Configuration')
		for config in APPLICATION_CONFIGURATION:
			if config.title:
				result += Create_Configuration_Documentation(config, 1)



	return result





