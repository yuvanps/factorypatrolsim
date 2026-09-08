// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from patrol_msgs:msg/TaskAssignment.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "patrol_msgs/msg/task_assignment.hpp"


#ifndef PATROL_MSGS__MSG__DETAIL__TASK_ASSIGNMENT__TRAITS_HPP_
#define PATROL_MSGS__MSG__DETAIL__TASK_ASSIGNMENT__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "patrol_msgs/msg/detail/task_assignment__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace patrol_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const TaskAssignment & msg,
  std::ostream & out)
{
  out << "{";
  // member: task_id
  {
    out << "task_id: ";
    rosidl_generator_traits::value_to_yaml(msg.task_id, out);
    out << ", ";
  }

  // member: drone_id
  {
    out << "drone_id: ";
    rosidl_generator_traits::value_to_yaml(msg.drone_id, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const TaskAssignment & msg,
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

  // member: drone_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "drone_id: ";
    rosidl_generator_traits::value_to_yaml(msg.drone_id, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const TaskAssignment & msg, bool use_flow_style = false)
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
  const patrol_msgs::msg::TaskAssignment & msg,
  std::ostream & out, size_t indentation = 0)
{
  patrol_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use patrol_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const patrol_msgs::msg::TaskAssignment & msg)
{
  return patrol_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<patrol_msgs::msg::TaskAssignment>()
{
  return "patrol_msgs::msg::TaskAssignment";
}

template<>
inline const char * name<patrol_msgs::msg::TaskAssignment>()
{
  return "patrol_msgs/msg/TaskAssignment";
}

template<>
struct has_fixed_size<patrol_msgs::msg::TaskAssignment>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<patrol_msgs::msg::TaskAssignment>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<patrol_msgs::msg::TaskAssignment>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // PATROL_MSGS__MSG__DETAIL__TASK_ASSIGNMENT__TRAITS_HPP_
