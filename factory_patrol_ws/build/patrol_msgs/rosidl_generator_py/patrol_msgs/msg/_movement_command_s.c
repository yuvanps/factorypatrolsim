// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from patrol_msgs:msg/MovementCommand.idl
// generated code does not contain a copyright notice
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <stdbool.h>
#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-function"
#endif
#include "numpy/ndarrayobject.h"
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif
#include "rosidl_runtime_c/visibility_control.h"
#include "patrol_msgs/msg/detail/movement_command__struct.h"
#include "patrol_msgs/msg/detail/movement_command__functions.h"


ROSIDL_GENERATOR_C_EXPORT
bool patrol_msgs__msg__movement_command__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[50];
    {
      char * class_name = NULL;
      char * module_name = NULL;
      {
        PyObject * class_attr = PyObject_GetAttrString(_pymsg, "__class__");
        if (class_attr) {
          PyObject * name_attr = PyObject_GetAttrString(class_attr, "__name__");
          if (name_attr) {
            class_name = (char *)PyUnicode_1BYTE_DATA(name_attr);
            Py_DECREF(name_attr);
          }
          PyObject * module_attr = PyObject_GetAttrString(class_attr, "__module__");
          if (module_attr) {
            module_name = (char *)PyUnicode_1BYTE_DATA(module_attr);
            Py_DECREF(module_attr);
          }
          Py_DECREF(class_attr);
        }
      }
      if (!class_name || !module_name) {
        return false;
      }
      snprintf(full_classname_dest, sizeof(full_classname_dest), "%s.%s", module_name, class_name);
    }
    assert(strncmp("patrol_msgs.msg._movement_command.MovementCommand", full_classname_dest, 49) == 0);
  }
  patrol_msgs__msg__MovementCommand * ros_message = _ros_message;
  {  // drone_id
    PyObject * field = PyObject_GetAttrString(_pymsg, "drone_id");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->drone_id = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // task_id
    PyObject * field = PyObject_GetAttrString(_pymsg, "task_id");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->task_id = (uint16_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // target_x
    PyObject * field = PyObject_GetAttrString(_pymsg, "target_x");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->target_x = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // target_y
    PyObject * field = PyObject_GetAttrString(_pymsg, "target_y");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->target_y = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // target_z
    PyObject * field = PyObject_GetAttrString(_pymsg, "target_z");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->target_z = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // velocity_x
    PyObject * field = PyObject_GetAttrString(_pymsg, "velocity_x");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->velocity_x = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // velocity_y
    PyObject * field = PyObject_GetAttrString(_pymsg, "velocity_y");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->velocity_y = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // velocity_z
    PyObject * field = PyObject_GetAttrString(_pymsg, "velocity_z");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->velocity_z = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * patrol_msgs__msg__movement_command__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of MovementCommand */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("patrol_msgs.msg._movement_command");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "MovementCommand");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  patrol_msgs__msg__MovementCommand * ros_message = (patrol_msgs__msg__MovementCommand *)raw_ros_message;
  {  // drone_id
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->drone_id);
    {
      int rc = PyObject_SetAttrString(_pymessage, "drone_id", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // task_id
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->task_id);
    {
      int rc = PyObject_SetAttrString(_pymessage, "task_id", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // target_x
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->target_x);
    {
      int rc = PyObject_SetAttrString(_pymessage, "target_x", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // target_y
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->target_y);
    {
      int rc = PyObject_SetAttrString(_pymessage, "target_y", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // target_z
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->target_z);
    {
      int rc = PyObject_SetAttrString(_pymessage, "target_z", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // velocity_x
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->velocity_x);
    {
      int rc = PyObject_SetAttrString(_pymessage, "velocity_x", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // velocity_y
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->velocity_y);
    {
      int rc = PyObject_SetAttrString(_pymessage, "velocity_y", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // velocity_z
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->velocity_z);
    {
      int rc = PyObject_SetAttrString(_pymessage, "velocity_z", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
