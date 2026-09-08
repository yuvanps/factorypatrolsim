// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from patrol_msgs:msg/Mission.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "patrol_msgs/msg/detail/mission__rosidl_typesupport_introspection_c.h"
#include "patrol_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "patrol_msgs/msg/detail/mission__functions.h"
#include "patrol_msgs/msg/detail/mission__struct.h"


// Include directives for member types
// Member `tasks`
#include "patrol_msgs/msg/task.h"
// Member `tasks`
#include "patrol_msgs/msg/detail/task__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__Mission_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  patrol_msgs__msg__Mission__init(message_memory);
}

void patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__Mission_fini_function(void * message_memory)
{
  patrol_msgs__msg__Mission__fini(message_memory);
}

size_t patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__size_function__Mission__tasks(
  const void * untyped_member)
{
  const patrol_msgs__msg__Task__Sequence * member =
    (const patrol_msgs__msg__Task__Sequence *)(untyped_member);
  return member->size;
}

const void * patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__get_const_function__Mission__tasks(
  const void * untyped_member, size_t index)
{
  const patrol_msgs__msg__Task__Sequence * member =
    (const patrol_msgs__msg__Task__Sequence *)(untyped_member);
  return &member->data[index];
}

void * patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__get_function__Mission__tasks(
  void * untyped_member, size_t index)
{
  patrol_msgs__msg__Task__Sequence * member =
    (patrol_msgs__msg__Task__Sequence *)(untyped_member);
  return &member->data[index];
}

void patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__fetch_function__Mission__tasks(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const patrol_msgs__msg__Task * item =
    ((const patrol_msgs__msg__Task *)
    patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__get_const_function__Mission__tasks(untyped_member, index));
  patrol_msgs__msg__Task * value =
    (patrol_msgs__msg__Task *)(untyped_value);
  *value = *item;
}

void patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__assign_function__Mission__tasks(
  void * untyped_member, size_t index, const void * untyped_value)
{
  patrol_msgs__msg__Task * item =
    ((patrol_msgs__msg__Task *)
    patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__get_function__Mission__tasks(untyped_member, index));
  const patrol_msgs__msg__Task * value =
    (const patrol_msgs__msg__Task *)(untyped_value);
  *item = *value;
}

bool patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__resize_function__Mission__tasks(
  void * untyped_member, size_t size)
{
  patrol_msgs__msg__Task__Sequence * member =
    (patrol_msgs__msg__Task__Sequence *)(untyped_member);
  patrol_msgs__msg__Task__Sequence__fini(member);
  return patrol_msgs__msg__Task__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__Mission_message_member_array[2] = {
  {
    "mission_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT16,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(patrol_msgs__msg__Mission, mission_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "tasks",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(patrol_msgs__msg__Mission, tasks),  // bytes offset in struct
    NULL,  // default value
    patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__size_function__Mission__tasks,  // size() function pointer
    patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__get_const_function__Mission__tasks,  // get_const(index) function pointer
    patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__get_function__Mission__tasks,  // get(index) function pointer
    patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__fetch_function__Mission__tasks,  // fetch(index, &value) function pointer
    patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__assign_function__Mission__tasks,  // assign(index, value) function pointer
    patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__resize_function__Mission__tasks  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__Mission_message_members = {
  "patrol_msgs__msg",  // message namespace
  "Mission",  // message name
  2,  // number of fields
  sizeof(patrol_msgs__msg__Mission),
  false,  // has_any_key_member_
  patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__Mission_message_member_array,  // message members
  patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__Mission_init_function,  // function to initialize message memory (memory has to be allocated)
  patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__Mission_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__Mission_message_type_support_handle = {
  0,
  &patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__Mission_message_members,
  get_message_typesupport_handle_function,
  &patrol_msgs__msg__Mission__get_type_hash,
  &patrol_msgs__msg__Mission__get_type_description,
  &patrol_msgs__msg__Mission__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_patrol_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, patrol_msgs, msg, Mission)() {
  patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__Mission_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, patrol_msgs, msg, Task)();
  if (!patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__Mission_message_type_support_handle.typesupport_identifier) {
    patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__Mission_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &patrol_msgs__msg__Mission__rosidl_typesupport_introspection_c__Mission_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
