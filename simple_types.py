from symbols import NOT_SET

class Record_Base:
	def __init__(self, *positional, **named):
		#IMPORTANT TODO - initiate record

		p_list = list(positional)

		for field_name, field in self._st_fields.items():

			#TODO - logic/settings for how to consume positional/named
			# for now assume all is both positional and named
			if p_list:
				value = p_list.pop(-1)
				#TODO - type coercing
				setattr(self, field_name, value)
			elif field.default is NOT_SET:
				raise ValueError





class Field_Descriptor:
	def __init__(self, name, field, shadow):
		self.name = name
		self.field = field
		self.shadow = shadow

	def __get__(self, instance, owner):
		if instance is None:
			return self.field
		else:
			return getattr(instance, self.shadow)

	def __set__(self, instance, value):

		if coerce := self.field.coerce:
			if not isinstance(value, coerce):
				value = coerce(value)

		setattr(instance, self.shadow, value)


class Pending_Record:
	def __init__(self, name, bases, scope):
		self.name = name
		self.bases = bases
		self.scope = scope
		self.fields = {}

	def create(self):
		#IMPORTANT TODO - make use of fields

		for field_name, field in self.fields.items():

			if field.descriptor_type:
				target = field.shadow_pattern.format(field_name)
				self.scope[field_name] = field.descriptor_type(field_name, field, target)
			else:
				target = field_name

			#TODO - support factories
			if field.default is not NOT_SET:
				self.scope[target] = field.default


		self.scope['_st_fields'] = self.fields

		return type(self.name, tuple(self.bases), self.scope)

class Record:
	def __call__(self, cls):
		#IMPORTANT TODO - instantiate bases and scope based on cls - now we silently drop them
		pending = Pending_Record(cls.__name__, [Record_Base], {})

		for field_name, field_def in cls.__annotations__.items():
			field_def.register_field_in_pending_record(pending, field_name)

		return pending.create()


class Field:
	def __init__(self, default=NOT_SET, coerce=None, shadow_pattern='_{}', descriptor_type=Field_Descriptor):
		self.default = default
		self.coerce = coerce
		self.shadow_pattern = shadow_pattern
		self.descriptor_type = descriptor_type

	def register_field_in_pending_record(self, target, name):
		assert name not in target.fields
		target.fields[name] = self