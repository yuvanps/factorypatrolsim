// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from patrol_msgs:msg/ExperimentEvent.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "patrol_msgs/msg/experiment_event.hpp"


#ifndef PATROL_MSGS__MSG__DETAIL__EXPERIMENT_EVENT__TRAITS_HPP_
#define PATROL_MSGS__MSG__DETAIL__EXPERIMENT_EVENT__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "patrol_msgs/msg/detail/experiment_event__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace patrol_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const ExperimentEvent & msg,
  std::ostream & out)
{
  out << "{";
  // member: timestamp
  {
    out << "timestamp: ";
    rosidl_generator_traits::value_to_yaml(msg.timestamp, out);
    out << ", ";
  }

  // member: event_type
  {
    out << "event_type: ";
    rosidl_generator_traits::value_to_yaml(msg.event_type, out);
    out << ", ";
  }

  // member: data
  {
    out << "data: ";
    rosidl_generator_traits::value_to_yaml(msg.data, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ExperimentEvent & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: timestamp
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "timestamp: ";
    rosidl_generator_traits::value_to_yaml(msg.timestamp, out);
    out << "\n";
  }

  // member: event_type
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "event_type: ";
    rosidl_generator_traits::value_to_yaml(msg.event_type, out);
    out << "\n";
  }

  // member: data
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "data: ";
    rosidl_generator_traits::value_to_yaml(msg.data, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ExperimentEvent & msg, bool use_flow_style = false)
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
  const patrol_msgs::msg::ExperimentEvent & msg,
  std::ostream & out, size_t indentation = 0)
{
  patrol_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use patrol_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const patrol_msgs::msg::ExperimentEvent & msg)
{
  return patrol_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<patrol_msgs::msg::ExperimentEvent>()
{
  return "patrol_msgs::msg::ExperimentEvent";
}

template<>
inline const char * name<patrol_msgs::msg::ExperimentEvent>()
{
  return "patrol_msgs/msg/ExperimentEvent";
}

template<>
struct has_fixed_size<patrol_msgs::msg::ExperimentEvent>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<patrol_msgs::msg::ExperimentEvent>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<patrol_msgs::msg::ExperimentEvent>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // PATROL_MSGS__MSG__DETAIL__EXPERIMENT_EVENT__TRAITS_HPP_
