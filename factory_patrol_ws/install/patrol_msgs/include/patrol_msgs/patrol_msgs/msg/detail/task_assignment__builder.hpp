// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from patrol_msgs:msg/TaskAssignment.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "patrol_msgs/msg/task_assignment.hpp"


#ifndef PATROL_MSGS__MSG__DETAIL__TASK_ASSIGNMENT__BUILDER_HPP_
#define PATROL_MSGS__MSG__DETAIL__TASK_ASSIGNMENT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "patrol_msgs/msg/detail/task_assignment__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace patrol_msgs
{

namespace msg
{

namespace builder
{

class Init_TaskAssignment_drone_id
{
public:
  explicit Init_TaskAssignment_drone_id(::patrol_msgs::msg::TaskAssignment & msg)
  : msg_(msg)
  {}
  ::patrol_msgs::msg::TaskAssignment drone_id(::patrol_msgs::msg::TaskAssignment::_drone_id_type arg)
  {
    msg_.drone_id = std::move(arg);
    return std::move(msg_);
  }

private:
  ::patrol_msgs::msg::TaskAssignment msg_;
};

class Init_TaskAssignment_task_id
{
public:
  Init_TaskAssignment_task_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_TaskAssignment_drone_id task_id(::patrol_msgs::msg::TaskAssignment::_task_id_type arg)
  {
    msg_.task_id = std::move(arg);
    return Init_TaskAssignment_drone_id(msg_);
  }

private:
  ::patrol_msgs::msg::TaskAssignment msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::patrol_msgs::msg::TaskAssignment>()
{
  return patrol_msgs::msg::builder::Init_TaskAssignment_task_id();
}

}  // namespace patrol_msgs

#endif  // PATROL_MSGS__MSG__DETAIL__TASK_ASSIGNMENT__BUILDER_HPP_
