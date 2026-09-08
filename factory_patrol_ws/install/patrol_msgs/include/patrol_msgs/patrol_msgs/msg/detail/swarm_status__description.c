// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from patrol_msgs:msg/SwarmStatus.idl
// generated code does not contain a copyright notice

#include "patrol_msgs/msg/detail/swarm_status__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_patrol_msgs
const rosidl_type_hash_t *
patrol_msgs__msg__SwarmStatus__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x2d, 0x1d, 0xa6, 0xbd, 0x3c, 0x9a, 0xa9, 0xf9,
      0xf0, 0x4b, 0x0e, 0x0a, 0x7f, 0x90, 0x16, 0x00,
      0xa5, 0xf9, 0x78, 0x99, 0x4b, 0x63, 0x48, 0x2e,
      0x77, 0xdb, 0x16, 0x3c, 0xb2, 0xb7, 0x4f, 0x3c,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char patrol_msgs__msg__SwarmStatus__TYPE_NAME[] = "patrol_msgs/msg/SwarmStatus";

// Define type names, field names, and default values
static char patrol_msgs__msg__SwarmStatus__FIELD_NAME__status[] = "status";
static char patrol_msgs__msg__SwarmStatus__FIELD_NAME__reason[] = "reason";

static rosidl_runtime_c__type_description__Field patrol_msgs__msg__SwarmStatus__FIELDS[] = {
  {
    {patrol_msgs__msg__SwarmStatus__FIELD_NAME__status, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__SwarmStatus__FIELD_NAME__reason, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
patrol_msgs__msg__SwarmStatus__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {patrol_msgs__msg__SwarmStatus__TYPE_NAME, 27, 27},
      {patrol_msgs__msg__SwarmStatus__FIELDS, 2, 2},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint8 STATUS_OK=0\n"
  "uint8 STATUS_NO_DRONES_AVAILABLE=1\n"
  "uint8 STATUS_ALL_DRONES_LOW_BATTERY=2\n"
  "uint8 STATUS_PATROL_CYCLE_COMPLETE=3\n"
  "\n"
  "uint8 status\n"
  "string reason";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
patrol_msgs__msg__SwarmStatus__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {patrol_msgs__msg__SwarmStatus__TYPE_NAME, 27, 27},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 156, 156},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
patrol_msgs__msg__SwarmStatus__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *patrol_msgs__msg__SwarmStatus__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
