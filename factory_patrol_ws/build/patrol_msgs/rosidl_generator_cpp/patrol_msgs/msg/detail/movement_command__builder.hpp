// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from patrol_msgs:msg/MovementCommand.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "patrol_msgs/msg/movement_command.hpp"


#ifndef PATROL_MSGS__MSG__DETAIL__MOVEMENT_COMMAND__BUILDER_HPP_
#define PATROL_MSGS__MSG__DETAIL__MOVEMENT_COMMAND__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "patrol_msgs/msg/detail/movement_command__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace patrol_msgs
{

namespace msg
{

namespace builder
{

class Init_MovementCommand_velocity_z
{
public:
  explicit Init_MovementCommand_velocity_z(::patrol_msgs::msg::MovementCommand & msg)
  : msg_(msg)
  {}
  ::patrol_msgs::msg::MovementCommand velocity_z(::patrol_msgs::msg::MovementCommand::_velocity_z_type arg)
  {
    msg_.velocity_z = std::move(arg);
    return std::move(msg_);
  }

private:
  ::patrol_msgs::msg::MovementCommand msg_;
};

class Init_MovementCommand_velocity_y
{
public:
  explicit Init_MovementCommand_velocity_y(::patrol_msgs::msg::MovementCommand & msg)
  : msg_(msg)
  {}
  Init_MovementCommand_velocity_z velocity_y(::patrol_msgs::msg::MovementCommand::_velocity_y_type arg)
  {
    msg_.velocity_y = std::move(arg);
    return Init_MovementCommand_velocity_z(msg_);
  }

private:
  ::patrol_msgs::msg::MovementCommand msg_;
};

class Init_MovementCommand_velocity_x
{
public:
  explicit Init_MovementCommand_velocity_x(::patrol_msgs::msg::MovementCommand & msg)
  : msg_(msg)
  {}
  Init_MovementCommand_velocity_y velocity_x(::patrol_msgs::msg::MovementCommand::_velocity_x_type arg)
  {
    msg_.velocity_x = std::move(arg);
    return Init_MovementCommand_velocity_y(msg_);
  }

private:
  ::patrol_msgs::msg::MovementCommand msg_;
};

class Init_MovementCommand_target_z
{
public:
  explicit Init_MovementCommand_target_z(::patrol_msgs::msg::MovementCommand & msg)
  : msg_(msg)
  {}
  Init_MovementCommand_velocity_x target_z(::patrol_msgs::msg::MovementCommand::_target_z_type arg)
  {
    msg_.target_z = std::move(arg);
    return Init_MovementCommand_velocity_x(msg_);
  }

private:
  ::patrol_msgs::msg::MovementCommand msg_;
};

class Init_MovementCommand_target_y
{
public:
  explicit Init_MovementCommand_target_y(::patrol_msgs::msg::MovementCommand & msg)
  : msg_(msg)
  {}
  Init_MovementCommand_target_z target_y(::patrol_msgs::msg::MovementCommand::_target_y_type arg)
  {
    msg_.target_y = std::move(arg);
    return Init_MovementCommand_target_z(msg_);
  }

private:
  ::patrol_msgs::msg::MovementCommand msg_;
};

class Init_MovementCommand_target_x
{
public:
  explicit Init_MovementCommand_target_x(::patrol_msgs::msg::MovementCommand & msg)
  : msg_(msg)
  {}
  Init_MovementCommand_target_y target_x(::patrol_msgs::msg::MovementCommand::_target_x_type arg)
  {
    msg_.target_x = std::move(arg);
    return Init_MovementCommand_target_y(msg_);
  }

private:
  ::patrol_msgs::msg::MovementCommand msg_;
};

class Init_MovementCommand_task_id
{
public:
  explicit Init_MovementCommand_task_id(::patrol_msgs::msg::MovementCommand & msg)
  : msg_(msg)
  {}
  Init_MovementCommand_target_x task_id(::patrol_msgs::msg::MovementCommand::_task_id_type arg)
  {
    msg_.task_id = std::move(arg);
    return Init_MovementCommand_target_x(msg_);
  }

private:
  ::patrol_msgs::msg::MovementCommand msg_;
};

class Init_MovementCommand_drone_id
{
public:
  Init_MovementCommand_drone_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MovementCommand_task_id drone_id(::patrol_msgs::msg::MovementCommand::_drone_id_type arg)
  {
    msg_.drone_id = std::move(arg);
    return Init_MovementCommand_task_id(msg_);
  }

private:
  ::patrol_msgs::msg::MovementCommand msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::patrol_msgs::msg::MovementCommand>()
{
  return patrol_msgs::msg::builder::Init_MovementCommand_drone_id();
}

}  // namespace patrol_msgs

#endif  // PATROL_MSGS__MSG__DETAIL__MOVEMENT_COMMAND__BUILDER_HPP_
