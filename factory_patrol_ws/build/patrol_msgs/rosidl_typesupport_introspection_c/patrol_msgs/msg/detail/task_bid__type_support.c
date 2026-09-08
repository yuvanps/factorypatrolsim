// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from patrol_msgs:msg/TaskBid.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "patrol_msgs/msg/detail/task_bid__rosidl_typesupport_introspection_c.h"
#include "patrol_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "patrol_msgs/msg/detail/task_bid__functions.h"
#include "patrol_msgs/msg/detail/task_bid__struct.h"


#ifdef __cplusplus
extern "C"
{
#endif

void patrol_msgs__msg__TaskBid__rosidl_typesupport_introspection_c__TaskBid_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  patrol_msgs__msg__TaskBid__init(message_memory);
}

void patrol_msgs__msg__TaskBid__rosidl_typesupport_introspection_c__TaskBid_fini_function(void * message_memory)
{
  patrol_msgs__msg__TaskBid__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember patrol_msgs__msg__TaskBid__rosidl_typesupport_introspection_c__TaskBid_message_member_array[3] = {
  {
    "drone_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(patrol_msgs__msg__TaskBid, drone_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "task_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT16,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(patrol_msgs__msg__TaskBid, task_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "cost",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(patrol_msgs__msg__TaskBid, cost),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers patrol_msgs__msg__TaskBid__rosidl_typesupport_introspection_c__TaskBid_message_members = {
  "patrol_msgs__msg",  // message namespace
  "TaskBid",  // message name
  3,  // number of fields
  sizeof(patrol_msgs__msg__TaskBid),
  false,  // has_any_key_member_
  patrol_msgs__msg__TaskBid__rosidl_typesupport_introspection_c__TaskBid_message_member_array,  // message members
  patrol_msgs__msg__TaskBid__rosidl_typesupport_introspection_c__TaskBid_init_function,  // function to initialize message memory (memory has to be allocated)
  patrol_msgs__msg__TaskBid__rosidl_typesupport_introspection_c__TaskBid_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t patrol_msgs__msg__TaskBid__rosidl_typesupport_introspection_c__TaskBid_message_type_support_handle = {
  0,
  &patrol_msgs__msg__TaskBid__rosidl_typesupport_introspection_c__TaskBid_message_members,
  get_message_typesupport_handle_function,
  &patrol_msgs__msg__TaskBid__get_type_hash,
  &patrol_msgs__msg__TaskBid__get_type_description,
  &patrol_msgs__msg__TaskBid__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_patrol_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, patrol_msgs, msg, TaskBid)() {
  if (!patrol_msgs__msg__TaskBid__rosidl_typesupport_introspection_c__TaskBid_message_type_support_handle.typesupport_identifier) {
    patrol_msgs__msg__TaskBid__rosidl_typesupport_introspection_c__TaskBid_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &patrol_msgs__msg__TaskBid__rosidl_typesupport_introspection_c__TaskBid_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
