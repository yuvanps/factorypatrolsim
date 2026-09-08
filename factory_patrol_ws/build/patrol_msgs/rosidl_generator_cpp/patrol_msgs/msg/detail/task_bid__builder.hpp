// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from patrol_msgs:msg/TaskBid.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "patrol_msgs/msg/task_bid.hpp"


#ifndef PATROL_MSGS__MSG__DETAIL__TASK_BID__BUILDER_HPP_
#define PATROL_MSGS__MSG__DETAIL__TASK_BID__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "patrol_msgs/msg/detail/task_bid__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace patrol_msgs
{

namespace msg
{

namespace builder
{

class Init_TaskBid_cost
{
public:
  explicit Init_TaskBid_cost(::patrol_msgs::msg::TaskBid & msg)
  : msg_(msg)
  {}
  ::patrol_msgs::msg::TaskBid cost(::patrol_msgs::msg::TaskBid::_cost_type arg)
  {
    msg_.cost = std::move(arg);
    return std::move(msg_);
  }

private:
  ::patrol_msgs::msg::TaskBid msg_;
};

class Init_TaskBid_task_id
{
public:
  explicit Init_TaskBid_task_id(::patrol_msgs::msg::TaskBid & msg)
  : msg_(msg)
  {}
  Init_TaskBid_cost task_id(::patrol_msgs::msg::TaskBid::_task_id_type arg)
  {
    msg_.task_id = std::move(arg);
    return Init_TaskBid_cost(msg_);
  }

private:
  ::patrol_msgs::msg::TaskBid msg_;
};

class Init_TaskBid_drone_id
{
public:
  Init_TaskBid_drone_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_TaskBid_task_id drone_id(::patrol_msgs::msg::TaskBid::_drone_id_type arg)
  {
    msg_.drone_id = std::move(arg);
    return Init_TaskBid_task_id(msg_);
  }

private:
  ::patrol_msgs::msg::TaskBid msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::patrol_msgs::msg::TaskBid>()
{
  return patrol_msgs::msg::builder::Init_TaskBid_drone_id();
}

}  // namespace patrol_msgs

#endif  // PATROL_MSGS__MSG__DETAIL__TASK_BID__BUILDER_HPP_
