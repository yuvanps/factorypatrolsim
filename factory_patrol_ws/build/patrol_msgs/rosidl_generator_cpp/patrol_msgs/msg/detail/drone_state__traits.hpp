// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from patrol_msgs:msg/DroneState.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "patrol_msgs/msg/drone_state.hpp"


#ifndef PATROL_MSGS__MSG__DETAIL__DRONE_STATE__TRAITS_HPP_
#define PATROL_MSGS__MSG__DETAIL__DRONE_STATE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "patrol_msgs/msg/detail/drone_state__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace patrol_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const DroneState & msg,
  std::ostream & out)
{
  out << "{";
  // member: drone_id
  {
    out << "drone_id: ";
    rosidl_generator_traits::value_to_yaml(msg.drone_id, out);
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

  // member: battery_level
  {
    out << "battery_level: ";
    rosidl_generator_traits::value_to_yaml(msg.battery_level, out);
    out << ", ";
  }

  // member: state
  {
    out << "state: ";
    rosidl_generator_traits::value_to_yaml(msg.state, out);
    out << ", ";
  }

  // member: current_task_id
  {
    out << "current_task_id: ";
    rosidl_generator_traits::value_to_yaml(msg.current_task_id, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const DroneState & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: drone_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "drone_id: ";
    rosidl_generator_traits::value_to_yaml(msg.drone_id, out);
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

  // member: battery_level
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "battery_level: ";
    rosidl_generator_traits::value_to_yaml(msg.battery_level, out);
    out << "\n";
  }

  // member: state
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "state: ";
    rosidl_generator_traits::value_to_yaml(msg.state, out);
    out << "\n";
  }

  // member: current_task_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "current_task_id: ";
    rosidl_generator_traits::value_to_yaml(msg.current_task_id, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const DroneState & msg, bool use_flow_style = false)
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
  const patrol_msgs::msg::DroneState & msg,
  std::ostream & out, size_t indentation = 0)
{
  patrol_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use patrol_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const patrol_msgs::msg::DroneState & msg)
{
  return patrol_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<patrol_msgs::msg::DroneState>()
{
  return "patrol_msgs::msg::DroneState";
}

template<>
inline const char * name<patrol_msgs::msg::DroneState>()
{
  return "patrol_msgs/msg/DroneState";
}

template<>
struct has_fixed_size<patrol_msgs::msg::DroneState>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<patrol_msgs::msg::DroneState>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<patrol_msgs::msg::DroneState>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // PATROL_MSGS__MSG__DETAIL__DRONE_STATE__TRAITS_HPP_
