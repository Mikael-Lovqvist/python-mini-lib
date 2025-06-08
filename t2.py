import pathlib

from simple_types import Record, Field
from simple_argparse import Assign_Argument_Type, Register_Argument_Group, Action_Parameter, Argument_Group, Value_Parameter, Parse_Arguments, Register_Description
from simple_config import Register_Config, Factory, Settable_Once

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


# Help argparse backend with types (useful for auto completion)
Assign_Argument_Type(Path, pathlib.Path)
Assign_Argument_Type(Glob, pathlib.Path)


# Application config

Register_Description('Hot reload utility configuration')

Register_Config('main',
	action = Settable_Once(default='run', help='The main action of the application'),
	profile = Settable_Once(default=None, help='Non default profile to operate on'),
)

Register_Config('profile', 'Profile',
	hot_matching_rules = Factory(list, help='Contains the matching rules used when matching the hot files'),
	support_matching_rules = Factory(list, help='Contains the matching rules used when matching the support files'),
	trigger_action_list = Factory(list, help='List of trigger actions to execute upon match'),
	post_trigger_action_list = Factory(list, help='List of post trigger actions to execute after a match has been handled'),
	default_hot_file = Settable_Once(default=None, help='Default hot file'),
)


# Arguments

Register_Argument_Group('Main',
	help = Action_Parameter('--help', '-h', help='Immediate action: Show help and exit', store_key='main.action'),
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
	clear = Action_Parameter('--clear', help='Trigger action: Clear terminal', push_to='profile.trigger_action_list'),
	show_stats = Action_Parameter('--show-stats', help='Post trigger action: Show timing and stats after command', push_to='profile.post_trigger_action_list'),
)



if __name__ == '__main__':
	arguments = Parse_Arguments(['t2.py', '-h', '--profile', 'mah-profile', '--clear', '--cmd', 'ls *', '--include-hot-glob', '*.py', '--save'])

	#from simple_doc import Create_Documentation
	#print('\n'.join(Create_Documentation()))



	#print(arguments)
