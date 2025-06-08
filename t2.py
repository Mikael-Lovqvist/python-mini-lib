import pathlib

from simple_types import Record, Field
from simple_argparse import Assign_Argument_Type, Register_Argument_Group, Action_Parameter, Argument_Group, Value_Parameter, Parse_Arguments
from simple_config import Register_Config, Factory, Settable_Once, Assign_Config_Format, Register_Config_Description, Read_Config

# Local types

@Record()
class Path:
	value: Field(coerce=pathlib.Path)

@Record()
class Glob:
	pattern: Field(coerce=str)

@Record()
class Name:
	value: Field(coerce=str)

@Record()
class Command:
	value: Field(coerce=str)

@Record()
class Critical_Command:
	value: Field(coerce=str)


# Help argparse backend with types (useful for auto completion)
Assign_Argument_Type(Path, pathlib.Path)
Assign_Argument_Type(Glob, pathlib.Path)

Assign_Config_Format(Name, lambda item: item.value)
Assign_Config_Format(Path, lambda item: item.value)
Assign_Config_Format(Glob, lambda item: item.pattern)
Assign_Config_Format(Command, lambda item: repr(f'execute: {item.value}'))
Assign_Config_Format(Critical_Command, lambda item: repr(f'critical execute: {item.value}'))


# Application config

Register_Config_Description('Hot reload utility configuration')

Register_Config('main',
	action = Settable_Once(default='run', help='The main action of the application'),
	config_file = Settable_Once(default='.pot-watcher.conf', help='Configuration filename'),
	use_config_file = Settable_Once(default=True, help='Whether to use config or not'),
	profile = Settable_Once(default=None, help='Non default profile to operate on'),
)

Register_Config('profile', 'Profile',
	hot_matching_rules = Factory(list, help='Contains the matching rules used when matching the hot files'),
	support_matching_rules = Factory(list, help='Contains the matching rules used when matching the support files'),
	trigger_action_list = Factory(list, help=(
		'List of trigger actions to execute upon match\n'
		'Valid triggers are as follows\n'
		'  critical execute: command    | Executes a command and aborts if return code is non zero\n'
		'  execute: command             | Executes a command\n'
		'  clear                        | Clears the screen'
	)),
	post_trigger_action_list = Factory(list, help='List of post trigger actions to execute after a match has been handled'),
	default_hot_file = Settable_Once(default=None, help='Default hot file'),
)


# Arguments

Register_Argument_Group('Main',
	help = Action_Parameter('--help', '-h', help='Immediate action: Show help and exit', store_key='main.action'),
	config_file = Value_Parameter('--config-file', type=Path, help='Alternate configuration file', store_key='main.config_file'),
	no_config = Action_Parameter('--no-config', help='Do not load any configuration', store_key='main.use_config_file', store_value=False),
)


Register_Argument_Group('File matching',
	Argument_Group('Hot files',
		include_hot_glob = Value_Parameter('--include-hot-glob', type=Glob, help='Glob for hot files', push_to='profile.hot_matching_rules'),
		exclude_hot_glob = Value_Parameter('--exclude-hot-glob', type=Glob, help='Glob to exclude from hot files', push_to='profile.hot_matching_rules'),
		default_hot_file = Value_Parameter('--default-hot-file', type=Path, help='Path to default hot file', store_key='profile.default_hot_file'),
	),
	Argument_Group('Support files',
		include_support_glob = Value_Parameter('--include-support-glob', type=Glob, help='Glob for support files', push_to='profile.support_matching_rules'),
		exclude_support_glob = Value_Parameter('--exclude-support-glob', type=Glob, help='Glob to exclude from support files', push_to='profile.support_matching_rules'),
	),
)

Register_Argument_Group('Profile',
	profile = Value_Parameter('--profile', type=Name, help='Profile name to use or modify', store_key='main.profile'),
	save_profile = Action_Parameter('--save', help='Immediate action: Save current configuration to profile and exit', store_key='main.action'),
)

Register_Argument_Group('Trigger action',
	command = Value_Parameter('--cmd', type=Command, help='Trigger action: Run command', push_to='profile.trigger_action_list'),
	critical_command = Value_Parameter('--critical-cmd', type=Critical_Command, help='Trigger action: Run command and stop chain if exit status is not 0', push_to='profile.trigger_action_list'),
	clear = Action_Parameter('--clear', help='Trigger action: Clear terminal', push_to='profile.trigger_action_list'),
	show_stats = Action_Parameter('--show-stats', help='Post trigger action: Show timing and stats after command', push_to='profile.post_trigger_action_list'),
)



if __name__ == '__main__':

	from simple_config import CONFIG_TREE, CONFIG, Update_Config, Format_Value
	#print(APPLICATION_CONFIGURATION)
	#arguments = Parse_Arguments(['t2.py', '--default-hot-file', 'blargh', '--save', '--include-hot-glob', '*.js', '--critical-cmd', 'make stuff', '--clear', '--cmd', 'make test'])
	arguments = Parse_Arguments(['t2.py'])
	#arguments = Parse_Arguments(['t2.py', '-h', '--profile', 'mah-profile', '--clear', '--cmd', 'ls *', '--include-hot-glob', '*.py', '--save'])


	if CONFIG.main.action == 'save_profile':
		if CONFIG.main.profile is None:
			Update_Config(CONFIG.main.config_file, {'default profile': [CONFIG_TREE.profile, CONFIG.profile]})
		else:
			Update_Config(CONFIG.main.config_file, {f'profile: {Format_Value(CONFIG.main.profile)}': [CONFIG_TREE.profile, CONFIG.profile]})

	elif CONFIG.main.action == 'run':
		if CONFIG.main.use_config_file:
			#Here we must load the profile from the config file

			if CONFIG.main.profile is None:
				config = Read_Config(CONFIG.main.config_file, {'default profile': [CONFIG_TREE.profile, CONFIG.profile]})
			else:
				config = Read_Config(CONFIG.main.config_file, {f'profile: {Format_Value(CONFIG.main.profile)}': [CONFIG_TREE.profile, CONFIG.profile]})

			print(config)



	else:
		raise Exception()

	#TODO - make sure Create_Documentation works after fixing config stuff
	#from simple_doc import Create_Documentation
	#print('\n'.join(Create_Documentation()))



	#print(arguments)
