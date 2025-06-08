

def predicate_dict(source):
	result = dict()
	for key, [condition, value] in source.items():
		if condition(value):
			result[key] = value

	return result