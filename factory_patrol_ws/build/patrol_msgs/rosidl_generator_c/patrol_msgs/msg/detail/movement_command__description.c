// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from patrol_msgs:msg/MovementCommand.idl
// generated code does not contain a copyright notice

#include "patrol_msgs/msg/detail/movement_command__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_patrol_msgs
const rosidl_type_hash_t *
patrol_msgs__msg__MovementCommand__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xc3, 0xb6, 0x7f, 0x29, 0x26, 0x97, 0x80, 0x68,
      0x4d, 0x03, 0x72, 0x35, 0xc2, 0x74, 0xb1, 0xb2,
      0xdc, 0xb5, 0xb0, 0x90, 0xdb, 0x17, 0xf7, 0x1d,
      0x94, 0x28, 0x28, 0xfc, 0x0d, 0xfa, 0x39, 0x17,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char patrol_msgs__msg__MovementCommand__TYPE_NAME[] = "patrol_msgs/msg/MovementCommand";

// Define type names, field names, and default values
static char patrol_msgs__msg__MovementCommand__FIELD_NAME__drone_id[] = "drone_id";
static char patrol_msgs__msg__MovementCommand__FIELD_NAME__task_id[] = "task_id";
static char patrol_msgs__msg__MovementCommand__FIELD_NAME__target_x[] = "target_x";
static char patrol_msgs__msg__MovementCommand__FIELD_NAME__target_y[] = "target_y";
static char patrol_msgs__msg__MovementCommand__FIELD_NAME__target_z[] = "target_z";
static char patrol_msgs__msg__MovementCommand__FIELD_NAME__velocity_x[] = "velocity_x";
static char patrol_msgs__msg__MovementCommand__FIELD_NAME__velocity_y[] = "velocity_y";
static char patrol_msgs__msg__MovementCommand__FIELD_NAME__velocity_z[] = "velocity_z";

static rosidl_runtime_c__type_description__Field patrol_msgs__msg__MovementCommand__FIELDS[] = {
  {
    {patrol_msgs__msg__MovementCommand__FIELD_NAME__drone_id, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__MovementCommand__FIELD_NAME__task_id, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT16,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__MovementCommand__FIELD_NAME__target_x, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__MovementCommand__FIELD_NAME__target_y, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__MovementCommand__FIELD_NAME__target_z, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__MovementCommand__FIELD_NAME__velocity_x, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__MovementCommand__FIELD_NAME__velocity_y, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__MovementCommand__FIELD_NAME__velocity_z, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
patrol_msgs__msg__MovementCommand__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {patrol_msgs__msg__MovementCommand__TYPE_NAME, 31, 31},
      {patrol_msgs__msg__MovementCommand__FIELDS, 8, 8},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# Movement command from a reactive coordination algorithm (e.g. APF) to one patrol controller.\n"
  "# All positions/velocities are in the common factory frame used by DroneState and Task:\n"
  "#   x = Gazebo X (east), y = Gazebo Y (north), z = -height (negative = above ground).\n"
  "uint8 drone_id\n"
  "uint16 task_id      # goal this command steers toward; controllers ignore commands for any other task\n"
  "float32 target_x    # position setpoint the controller should track\n"
  "float32 target_y\n"
  "float32 target_z\n"
  "float32 velocity_x  # commanded velocity that produced the target (informational / diagnostics)\n"
  "float32 velocity_y\n"
  "float32 velocity_z";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
patrol_msgs__msg__MovementCommand__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {patrol_msgs__msg__MovementCommand__TYPE_NAME, 31, 31},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 622, 622},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
patrol_msgs__msg__MovementCommand__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *patrol_msgs__msg__MovementCommand__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
