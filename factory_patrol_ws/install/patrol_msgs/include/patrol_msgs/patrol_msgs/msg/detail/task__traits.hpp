// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from patrol_msgs:msg/Task.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "patrol_msgs/msg/task.hpp"


#ifndef PATROL_MSGS__MSG__DETAIL__TASK__TRAITS_HPP_
#define PATROL_MSGS__MSG__DETAIL__TASK__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "patrol_msgs/msg/detail/task__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace patrol_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const Task & msg,
  std::ostream & out)
{
  out << "{";
  // member: task_id
  {
    out << "task_id: ";
    rosidl_generator_traits::value_to_yaml(msg.task_id, out);
    out << ", ";
  }

  // member: x
  {
    out << "x: ";
    rosidl_generator_traits::value_to_yaml(msg.x, out);
    out << ", ";
  }

  // member: y
  {
    out << "y: ";
    rosidl_generator_traits::value_to_yaml(msg.y, out);
    out << ", ";
  }

  // member: z
  {
    out << "z: ";
    rosidl_generator_traits::value_to_yaml(msg.z, out);
    out << ", ";
  }

  // member: priority
  {
    out << "priority: ";
    rosidl_generator_traits::value_to_yaml(msg.priority, out);
    out << ", ";
  }

  // member: inspection_type
  {
    out << "inspection_type: ";
    rosidl_generator_traits::value_to_yaml(msg.inspection_type, out);
    out << ", ";
  }

  // member: hover_duration
  {
    out << "hover_duration: ";
    rosidl_generator_traits::value_to_yaml(msg.hover_duration, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Task & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: task_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "task_id: ";
    rosidl_generator_traits::value_to_yaml(msg.task_id, out);
    out << "\n";
  }

  // member: x
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "x: ";
    rosidl_generator_traits::value_to_yaml(msg.x, out);
    out << "\n";
  }

  // member: y
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "y: ";
    rosidl_generator_traits::value_to_yaml(msg.y, out);
    out << "\n";
  }

  // member: z
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "z: ";
    rosidl_generator_traits::value_to_yaml(msg.z, out);
    out << "\n";
  }

  // member: priority
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "priority: ";
    rosidl_generator_traits::value_to_yaml(msg.priority, out);
    out << "\n";
  }

  // member: inspection_type
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "inspection_type: ";
    rosidl_generator_traits::value_to_yaml(msg.inspection_type, out);
    out << "\n";
  }

  // member: hover_duration
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "hover_duration: ";
    rosidl_generator_traits::value_to_yaml(msg.hover_duration, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Task & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace patrol_msgs

namespace rosidl_generator_traits
{

[[deprecated("use patrol_msgs::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const patrol_msgs::msg::Task & msg,
  std::ostream & out, size_t indentation = 0)
{
  patrol_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use patrol_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const patrol_msgs::msg::Task & msg)
{
  return patrol_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<patrol_msgs::msg::Task>()
{
  return "patrol_msgs::msg::Task";
}

template<>
inline const char * name<patrol_msgs::msg::Task>()
{
  return "patrol_msgs/msg/Task";
}

template<>
struct has_fixed_size<patrol_msgs::msg::Task>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<patrol_msgs::msg::Task>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<patrol_msgs::msg::Task>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // PATROL_MSGS__MSG__DETAIL__TASK__TRAITS_HPP_
