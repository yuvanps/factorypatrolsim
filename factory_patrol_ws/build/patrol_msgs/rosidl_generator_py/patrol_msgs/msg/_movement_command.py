# generated from rosidl_generator_py/resource/_idl.py.em
# with input from patrol_msgs:msg/MovementCommand.idl
# generated code does not contain a copyright notice

# This is being done at the module level and not on the instance level to avoid looking
# for the same variable multiple times on each instance. This variable is not supposed to
# change during runtime so it makes sense to only look for it once.
from os import getenv

ros_python_check_fields = getenv('ROS_PYTHON_CHECK_FIELDS', default='')


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_MovementCommand(type):
    """Metaclass of message 'MovementCommand'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('patrol_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'patrol_msgs.msg.MovementCommand')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__movement_command
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__movement_command
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__movement_command
            cls._TYPE_SUPPORT = module.type_support_msg__msg__movement_command
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__movement_command

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class MovementCommand(metaclass=Metaclass_MovementCommand):
    """Message class 'MovementCommand'."""

    __slots__ = [
        '_drone_id',
        '_task_id',
        '_target_x',
        '_target_y',
        '_target_z',
        '_velocity_x',
        '_velocity_y',
        '_velocity_z',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'drone_id': 'uint8',
        'task_id': 'uint16',
        'target_x': 'float',
        'target_y': 'float',
        'target_z': 'float',
        'velocity_x': 'float',
        'velocity_y': 'float',
        'velocity_z': 'float',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint16'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        if 'check_fields' in kwargs:
            self._check_fields = kwargs['check_fields']
        else:
            self._check_fields = ros_python_check_fields == '1'
        if self._check_fields:
            assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
                'Invalid arguments passed to constructor: %s' % \
                ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.drone_id = kwargs.get('drone_id', int())
        self.task_id = kwargs.get('task_id', int())
        self.target_x = kwargs.get('target_x', float())
        self.target_y = kwargs.get('target_y', float())
        self.target_z = kwargs.get('target_z', float())
        self.velocity_x = kwargs.get('velocity_x', float())
        self.velocity_y = kwargs.get('velocity_y', float())
        self.velocity_z = kwargs.get('velocity_z', float())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.get_fields_and_field_types().keys(), self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    if self._check_fields:
                        assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.drone_id != other.drone_id:
            return False
        if self.task_id != other.task_id:
            return False
        if self.target_x != other.target_x:
            return False
        if self.target_y != other.target_y:
            return False
        if self.target_z != other.target_z:
            return False
        if self.velocity_x != other.velocity_x:
            return False
        if self.velocity_y != other.velocity_y:
            return False
        if self.velocity_z != other.velocity_z:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def drone_id(self):
        """Message field 'drone_id'."""
        return self._drone_id

    @drone_id.setter
    def drone_id(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'drone_id' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'drone_id' field must be an unsigned integer in [0, 255]"
        self._drone_id = value

    @builtins.property
    def task_id(self):
        """Message field 'task_id'."""
        return self._task_id

    @task_id.setter
    def task_id(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'task_id' field must be of type 'int'"
            assert value >= 0 and value < 65536, \
                "The 'task_id' field must be an unsigned integer in [0, 65535]"
        self._task_id = value

    @builtins.property
    def target_x(self):
        """Message field 'target_x'."""
        return self._target_x

    @target_x.setter
    def target_x(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'target_x' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'target_x' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._target_x = value

    @builtins.property
    def target_y(self):
        """Message field 'target_y'."""
        return self._target_y

    @target_y.setter
    def target_y(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'target_y' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'target_y' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._target_y = value

    @builtins.property
    def target_z(self):
        """Message field 'target_z'."""
        return self._target_z

    @target_z.setter
    def target_z(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'target_z' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'target_z' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._target_z = value

    @builtins.property
    def velocity_x(self):
        """Message field 'velocity_x'."""
        return self._velocity_x

    @velocity_x.setter
    def velocity_x(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'velocity_x' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'velocity_x' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._velocity_x = value

    @builtins.property
    def velocity_y(self):
        """Message field 'velocity_y'."""
        return self._velocity_y

    @velocity_y.setter
    def velocity_y(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'velocity_y' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'velocity_y' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._velocity_y = value

    @builtins.property
    def velocity_z(self):
        """Message field 'velocity_z'."""
        return self._velocity_z

    @velocity_z.setter
    def velocity_z(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'velocity_z' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'velocity_z' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._velocity_z = value
