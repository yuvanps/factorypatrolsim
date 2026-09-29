// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from patrol_msgs:msg/DroneState.idl
// generated code does not contain a copyright notice

#include "patrol_msgs/msg/detail/drone_state__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_patrol_msgs
const rosidl_type_hash_t *
patrol_msgs__msg__DroneState__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x7d, 0x4f, 0x24, 0x73, 0x93, 0xc6, 0x26, 0xf2,
      0xb5, 0x3b, 0x8b, 0xda, 0x21, 0xed, 0x73, 0x5a,
      0x7a, 0xe7, 0x14, 0xc0, 0x53, 0xdd, 0x1f, 0x21,
      0xe0, 0xde, 0xe0, 0x83, 0x3a, 0x67, 0xbd, 0x08,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char patrol_msgs__msg__DroneState__TYPE_NAME[] = "patrol_msgs/msg/DroneState";

// Define type names, field names, and default values
static char patrol_msgs__msg__DroneState__FIELD_NAME__drone_id[] = "drone_id";
static char patrol_msgs__msg__DroneState__FIELD_NAME__x[] = "x";
static char patrol_msgs__msg__DroneState__FIELD_NAME__y[] = "y";
static char patrol_msgs__msg__DroneState__FIELD_NAME__z[] = "z";
static char patrol_msgs__msg__DroneState__FIELD_NAME__battery_level[] = "battery_level";
static char patrol_msgs__msg__DroneState__FIELD_NAME__state[] = "state";
static char patrol_msgs__msg__DroneState__FIELD_NAME__current_task_id[] = "current_task_id";

static rosidl_runtime_c__type_description__Field patrol_msgs__msg__DroneState__FIELDS[] = {
  {
    {patrol_msgs__msg__DroneState__FIELD_NAME__drone_id, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__DroneState__FIELD_NAME__x, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__DroneState__FIELD_NAME__y, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__DroneState__FIELD_NAME__z, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__DroneState__FIELD_NAME__battery_level, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__DroneState__FIELD_NAME__state, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__DroneState__FIELD_NAME__current_task_id, 15, 15},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT16,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
patrol_msgs__msg__DroneState__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {patrol_msgs__msg__DroneState__TYPE_NAME, 26, 26},
      {patrol_msgs__msg__DroneState__FIELDS, 7, 7},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint8 drone_id\n"
  "float32 x\n"
  "float32 y\n"
  "float32 z\n"
  "float32 battery_level\n"
  "uint8 state\n"
  "uint16 current_task_id  # task the drone is currently flying to / inspecting (0 = none)";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
patrol_msgs__msg__DroneState__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {patrol_msgs__msg__DroneState__TYPE_NAME, 26, 26},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 167, 167},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
patrol_msgs__msg__DroneState__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *patrol_msgs__msg__DroneState__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
