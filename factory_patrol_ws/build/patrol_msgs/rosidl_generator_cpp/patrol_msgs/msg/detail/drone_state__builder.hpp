// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from patrol_msgs:msg/DroneState.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "patrol_msgs/msg/drone_state.hpp"


#ifndef PATROL_MSGS__MSG__DETAIL__DRONE_STATE__BUILDER_HPP_
#define PATROL_MSGS__MSG__DETAIL__DRONE_STATE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "patrol_msgs/msg/detail/drone_state__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace patrol_msgs
{

namespace msg
{

namespace builder
{

class Init_DroneState_current_task_id
{
public:
  explicit Init_DroneState_current_task_id(::patrol_msgs::msg::DroneState & msg)
  : msg_(msg)
  {}
  ::patrol_msgs::msg::DroneState current_task_id(::patrol_msgs::msg::DroneState::_current_task_id_type arg)
  {
    msg_.current_task_id = std::move(arg);
    return std::move(msg_);
  }

private:
  ::patrol_msgs::msg::DroneState msg_;
};

class Init_DroneState_state
{
public:
  explicit Init_DroneState_state(::patrol_msgs::msg::DroneState & msg)
  : msg_(msg)
  {}
  Init_DroneState_current_task_id state(::patrol_msgs::msg::DroneState::_state_type arg)
  {
    msg_.state = std::move(arg);
    return Init_DroneState_current_task_id(msg_);
  }

private:
  ::patrol_msgs::msg::DroneState msg_;
};

class Init_DroneState_battery_level
{
public:
  explicit Init_DroneState_battery_level(::patrol_msgs::msg::DroneState & msg)
  : msg_(msg)
  {}
  Init_DroneState_state battery_level(::patrol_msgs::msg::DroneState::_battery_level_type arg)
  {
    msg_.battery_level = std::move(arg);
    return Init_DroneState_state(msg_);
  }

private:
  ::patrol_msgs::msg::DroneState msg_;
};

class Init_DroneState_z
{
public:
  explicit Init_DroneState_z(::patrol_msgs::msg::DroneState & msg)
  : msg_(msg)
  {}
  Init_DroneState_battery_level z(::patrol_msgs::msg::DroneState::_z_type arg)
  {
    msg_.z = std::move(arg);
    return Init_DroneState_battery_level(msg_);
  }

private:
  ::patrol_msgs::msg::DroneState msg_;
};

class Init_DroneState_y
{
public:
  explicit Init_DroneState_y(::patrol_msgs::msg::DroneState & msg)
  : msg_(msg)
  {}
  Init_DroneState_z y(::patrol_msgs::msg::DroneState::_y_type arg)
  {
    msg_.y = std::move(arg);
    return Init_DroneState_z(msg_);
  }

private:
  ::patrol_msgs::msg::DroneState msg_;
};

class Init_DroneState_x
{
public:
  explicit Init_DroneState_x(::patrol_msgs::msg::DroneState & msg)
  : msg_(msg)
  {}
  Init_DroneState_y x(::patrol_msgs::msg::DroneState::_x_type arg)
  {
    msg_.x = std::move(arg);
    return Init_DroneState_y(msg_);
  }

private:
  ::patrol_msgs::msg::DroneState msg_;
};

class Init_DroneState_drone_id
{
public:
  Init_DroneState_drone_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_DroneState_x drone_id(::patrol_msgs::msg::DroneState::_drone_id_type arg)
  {
    msg_.drone_id = std::move(arg);
    return Init_DroneState_x(msg_);
  }

private:
  ::patrol_msgs::msg::DroneState msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::patrol_msgs::msg::DroneState>()
{
  return patrol_msgs::msg::builder::Init_DroneState_drone_id();
}

}  // namespace patrol_msgs

#endif  // PATROL_MSGS__MSG__DETAIL__DRONE_STATE__BUILDER_HPP_
