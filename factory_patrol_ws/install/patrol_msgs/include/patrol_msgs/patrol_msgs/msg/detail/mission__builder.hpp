// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from patrol_msgs:msg/Mission.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "patrol_msgs/msg/mission.hpp"


#ifndef PATROL_MSGS__MSG__DETAIL__MISSION__BUILDER_HPP_
#define PATROL_MSGS__MSG__DETAIL__MISSION__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "patrol_msgs/msg/detail/mission__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace patrol_msgs
{

namespace msg
{

namespace builder
{

class Init_Mission_tasks
{
public:
  explicit Init_Mission_tasks(::patrol_msgs::msg::Mission & msg)
  : msg_(msg)
  {}
  ::patrol_msgs::msg::Mission tasks(::patrol_msgs::msg::Mission::_tasks_type arg)
  {
    msg_.tasks = std::move(arg);
    return std::move(msg_);
  }

private:
  ::patrol_msgs::msg::Mission msg_;
};

class Init_Mission_mission_id
{
public:
  Init_Mission_mission_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Mission_tasks mission_id(::patrol_msgs::msg::Mission::_mission_id_type arg)
  {
    msg_.mission_id = std::move(arg);
    return Init_Mission_tasks(msg_);
  }

private:
  ::patrol_msgs::msg::Mission msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::patrol_msgs::msg::Mission>()
{
  return patrol_msgs::msg::builder::Init_Mission_mission_id();
}

}  // namespace patrol_msgs

#endif  // PATROL_MSGS__MSG__DETAIL__MISSION__BUILDER_HPP_
