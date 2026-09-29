// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from patrol_msgs:msg/ExperimentEvent.idl
// generated code does not contain a copyright notice

#include "patrol_msgs/msg/detail/experiment_event__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_patrol_msgs
const rosidl_type_hash_t *
patrol_msgs__msg__ExperimentEvent__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x69, 0xaf, 0x8c, 0x67, 0x5e, 0x6c, 0x07, 0xfe,
      0x1b, 0x68, 0x8a, 0xe0, 0x38, 0xf4, 0x70, 0xeb,
      0xd7, 0xbf, 0x9e, 0x9c, 0x9d, 0xf3, 0x5c, 0x0e,
      0xb8, 0x51, 0x21, 0xc6, 0x45, 0xae, 0x48, 0x54,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char patrol_msgs__msg__ExperimentEvent__TYPE_NAME[] = "patrol_msgs/msg/ExperimentEvent";

// Define type names, field names, and default values
static char patrol_msgs__msg__ExperimentEvent__FIELD_NAME__timestamp[] = "timestamp";
static char patrol_msgs__msg__ExperimentEvent__FIELD_NAME__event_type[] = "event_type";
static char patrol_msgs__msg__ExperimentEvent__FIELD_NAME__data[] = "data";

static rosidl_runtime_c__type_description__Field patrol_msgs__msg__ExperimentEvent__FIELDS[] = {
  {
    {patrol_msgs__msg__ExperimentEvent__FIELD_NAME__timestamp, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT64,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__ExperimentEvent__FIELD_NAME__event_type, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__ExperimentEvent__FIELD_NAME__data, 4, 4},
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
patrol_msgs__msg__ExperimentEvent__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {patrol_msgs__msg__ExperimentEvent__TYPE_NAME, 31, 31},
      {patrol_msgs__msg__ExperimentEvent__FIELDS, 3, 3},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint64 timestamp\n"
  "string event_type\n"
  "string data";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
patrol_msgs__msg__ExperimentEvent__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {patrol_msgs__msg__ExperimentEvent__TYPE_NAME, 31, 31},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 47, 47},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
patrol_msgs__msg__ExperimentEvent__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *patrol_msgs__msg__ExperimentEvent__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
