// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from patrol_msgs:msg/SwarmStatus.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "patrol_msgs/msg/swarm_status.hpp"


#ifndef PATROL_MSGS__MSG__DETAIL__SWARM_STATUS__BUILDER_HPP_
#define PATROL_MSGS__MSG__DETAIL__SWARM_STATUS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "patrol_msgs/msg/detail/swarm_status__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace patrol_msgs
{

namespace msg
{

namespace builder
{

class Init_SwarmStatus_reason
{
public:
  explicit Init_SwarmStatus_reason(::patrol_msgs::msg::SwarmStatus & msg)
  : msg_(msg)
  {}
  ::patrol_msgs::msg::SwarmStatus reason(::patrol_msgs::msg::SwarmStatus::_reason_type arg)
  {
    msg_.reason = std::move(arg);
    return std::move(msg_);
  }

private:
  ::patrol_msgs::msg::SwarmStatus msg_;
};

class Init_SwarmStatus_status
{
public:
  Init_SwarmStatus_status()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_SwarmStatus_reason status(::patrol_msgs::msg::SwarmStatus::_status_type arg)
  {
    msg_.status = std::move(arg);
    return Init_SwarmStatus_reason(msg_);
  }

private:
  ::patrol_msgs::msg::SwarmStatus msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::patrol_msgs::msg::SwarmStatus>()
{
  return patrol_msgs::msg::builder::Init_SwarmStatus_status();
}

}  // namespace patrol_msgs

#endif  // PATROL_MSGS__MSG__DETAIL__SWARM_STATUS__BUILDER_HPP_
