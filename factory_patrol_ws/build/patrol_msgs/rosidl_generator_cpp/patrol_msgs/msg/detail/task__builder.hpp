// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from patrol_msgs:msg/Task.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "patrol_msgs/msg/task.hpp"


#ifndef PATROL_MSGS__MSG__DETAIL__TASK__BUILDER_HPP_
#define PATROL_MSGS__MSG__DETAIL__TASK__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "patrol_msgs/msg/detail/task__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace patrol_msgs
{

namespace msg
{

namespace builder
{

class Init_Task_hover_duration
{
public:
  explicit Init_Task_hover_duration(::patrol_msgs::msg::Task & msg)
  : msg_(msg)
  {}
  ::patrol_msgs::msg::Task hover_duration(::patrol_msgs::msg::Task::_hover_duration_type arg)
  {
    msg_.hover_duration = std::move(arg);
    return std::move(msg_);
  }

private:
  ::patrol_msgs::msg::Task msg_;
};

class Init_Task_inspection_type
{
public:
  explicit Init_Task_inspection_type(::patrol_msgs::msg::Task & msg)
  : msg_(msg)
  {}
  Init_Task_hover_duration inspection_type(::patrol_msgs::msg::Task::_inspection_type_type arg)
  {
    msg_.inspection_type = std::move(arg);
    return Init_Task_hover_duration(msg_);
  }

private:
  ::patrol_msgs::msg::Task msg_;
};

class Init_Task_priority
{
public:
  explicit Init_Task_priority(::patrol_msgs::msg::Task & msg)
  : msg_(msg)
  {}
  Init_Task_inspection_type priority(::patrol_msgs::msg::Task::_priority_type arg)
  {
    msg_.priority = std::move(arg);
    return Init_Task_inspection_type(msg_);
  }

private:
  ::patrol_msgs::msg::Task msg_;
};

class Init_Task_z
{
public:
  explicit Init_Task_z(::patrol_msgs::msg::Task & msg)
  : msg_(msg)
  {}
  Init_Task_priority z(::patrol_msgs::msg::Task::_z_type arg)
  {
    msg_.z = std::move(arg);
    return Init_Task_priority(msg_);
  }

private:
  ::patrol_msgs::msg::Task msg_;
};

class Init_Task_y
{
public:
  explicit Init_Task_y(::patrol_msgs::msg::Task & msg)
  : msg_(msg)
  {}
  Init_Task_z y(::patrol_msgs::msg::Task::_y_type arg)
  {
    msg_.y = std::move(arg);
    return Init_Task_z(msg_);
  }

private:
  ::patrol_msgs::msg::Task msg_;
};

class Init_Task_x
{
public:
  explicit Init_Task_x(::patrol_msgs::msg::Task & msg)
  : msg_(msg)
  {}
  Init_Task_y x(::patrol_msgs::msg::Task::_x_type arg)
  {
    msg_.x = std::move(arg);
    return Init_Task_y(msg_);
  }

private:
  ::patrol_msgs::msg::Task msg_;
};

class Init_Task_task_id
{
public:
  Init_Task_task_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Task_x task_id(::patrol_msgs::msg::Task::_task_id_type arg)
  {
    msg_.task_id = std::move(arg);
    return Init_Task_x(msg_);
  }

private:
  ::patrol_msgs::msg::Task msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::patrol_msgs::msg::Task>()
{
  return patrol_msgs::msg::builder::Init_Task_task_id();
}

}  // namespace patrol_msgs

#endif  // PATROL_MSGS__MSG__DETAIL__TASK__BUILDER_HPP_
