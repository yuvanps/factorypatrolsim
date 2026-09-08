// generated from rosidl_typesupport_c/resource/idl__type_support.cpp.em
// with input from patrol_msgs:msg/SwarmStatus.idl
// generated code does not contain a copyright notice

#include "cstddef"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "patrol_msgs/msg/detail/swarm_status__struct.h"
#include "patrol_msgs/msg/detail/swarm_status__type_support.h"
#include "patrol_msgs/msg/detail/swarm_status__functions.h"
#include "rosidl_typesupport_c/identifier.h"
#include "rosidl_typesupport_c/message_type_support_dispatch.h"
#include "rosidl_typesupport_c/type_support_map.h"
#include "rosidl_typesupport_c/visibility_control.h"
#include "rosidl_typesupport_interface/macros.h"

namespace patrol_msgs
{

namespace msg
{

namespace rosidl_typesupport_c
{

typedef struct _SwarmStatus_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _SwarmStatus_type_support_ids_t;

static const _SwarmStatus_type_support_ids_t _SwarmStatus_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _SwarmStatus_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _SwarmStatus_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _SwarmStatus_type_support_symbol_names_t _SwarmStatus_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, patrol_msgs, msg, SwarmStatus)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, patrol_msgs, msg, SwarmStatus)),
  }
};

typedef struct _SwarmStatus_type_support_data_t
{
  void * data[2];
} _SwarmStatus_type_support_data_t;

static _SwarmStatus_type_support_data_t _SwarmStatus_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _SwarmStatus_message_typesupport_map = {
  2,
  "patrol_msgs",
  &_SwarmStatus_message_typesupport_ids.typesupport_identifier[0],
  &_SwarmStatus_message_typesupport_symbol_names.symbol_name[0],
  &_SwarmStatus_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t SwarmStatus_message_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_SwarmStatus_message_typesupport_map),
  rosidl_typesupport_c__get_message_typesupport_handle_function,
  &patrol_msgs__msg__SwarmStatus__get_type_hash,
  &patrol_msgs__msg__SwarmStatus__get_type_description,
  &patrol_msgs__msg__SwarmStatus__get_type_description_sources,
};

}  // namespace rosidl_typesupport_c

}  // namespace msg

}  // namespace patrol_msgs

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_c, patrol_msgs, msg, SwarmStatus)() {
  return &::patrol_msgs::msg::rosidl_typesupport_c::SwarmStatus_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
