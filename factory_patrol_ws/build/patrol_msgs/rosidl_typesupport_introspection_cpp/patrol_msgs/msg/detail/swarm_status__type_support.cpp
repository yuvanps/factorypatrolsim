// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from patrol_msgs:msg/SwarmStatus.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "patrol_msgs/msg/detail/swarm_status__functions.h"
#include "patrol_msgs/msg/detail/swarm_status__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace patrol_msgs
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void SwarmStatus_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) patrol_msgs::msg::SwarmStatus(_init);
}

void SwarmStatus_fini_function(void * message_memory)
{
  auto typed_message = static_cast<patrol_msgs::msg::SwarmStatus *>(message_memory);
  typed_message->~SwarmStatus();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember SwarmStatus_message_member_array[2] = {
  {
    "status",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(patrol_msgs::msg::SwarmStatus, status),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "reason",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(patrol_msgs::msg::SwarmStatus, reason),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers SwarmStatus_message_members = {
  "patrol_msgs::msg",  // message namespace
  "SwarmStatus",  // message name
  2,  // number of fields
  sizeof(patrol_msgs::msg::SwarmStatus),
  false,  // has_any_key_member_
  SwarmStatus_message_member_array,  // message members
  SwarmStatus_init_function,  // function to initialize message memory (memory has to be allocated)
  SwarmStatus_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t SwarmStatus_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &SwarmStatus_message_members,
  get_message_typesupport_handle_function,
  &patrol_msgs__msg__SwarmStatus__get_type_hash,
  &patrol_msgs__msg__SwarmStatus__get_type_description,
  &patrol_msgs__msg__SwarmStatus__get_type_description_sources,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace patrol_msgs


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<patrol_msgs::msg::SwarmStatus>()
{
  return &::patrol_msgs::msg::rosidl_typesupport_introspection_cpp::SwarmStatus_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, patrol_msgs, msg, SwarmStatus)() {
  return &::patrol_msgs::msg::rosidl_typesupport_introspection_cpp::SwarmStatus_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
