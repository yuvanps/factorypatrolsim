// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from patrol_msgs:msg/ExperimentEvent.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "patrol_msgs/msg/experiment_event.hpp"


#ifndef PATROL_MSGS__MSG__DETAIL__EXPERIMENT_EVENT__BUILDER_HPP_
#define PATROL_MSGS__MSG__DETAIL__EXPERIMENT_EVENT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "patrol_msgs/msg/detail/experiment_event__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace patrol_msgs
{

namespace msg
{

namespace builder
{

class Init_ExperimentEvent_data
{
public:
  explicit Init_ExperimentEvent_data(::patrol_msgs::msg::ExperimentEvent & msg)
  : msg_(msg)
  {}
  ::patrol_msgs::msg::ExperimentEvent data(::patrol_msgs::msg::ExperimentEvent::_data_type arg)
  {
    msg_.data = std::move(arg);
    return std::move(msg_);
  }

private:
  ::patrol_msgs::msg::ExperimentEvent msg_;
};

class Init_ExperimentEvent_event_type
{
public:
  explicit Init_ExperimentEvent_event_type(::patrol_msgs::msg::ExperimentEvent & msg)
  : msg_(msg)
  {}
  Init_ExperimentEvent_data event_type(::patrol_msgs::msg::ExperimentEvent::_event_type_type arg)
  {
    msg_.event_type = std::move(arg);
    return Init_ExperimentEvent_data(msg_);
  }

private:
  ::patrol_msgs::msg::ExperimentEvent msg_;
};

class Init_ExperimentEvent_timestamp
{
public:
  Init_ExperimentEvent_timestamp()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ExperimentEvent_event_type timestamp(::patrol_msgs::msg::ExperimentEvent::_timestamp_type arg)
  {
    msg_.timestamp = std::move(arg);
    return Init_ExperimentEvent_event_type(msg_);
  }

private:
  ::patrol_msgs::msg::ExperimentEvent msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::patrol_msgs::msg::ExperimentEvent>()
{
  return patrol_msgs::msg::builder::Init_ExperimentEvent_timestamp();
}

}  // namespace patrol_msgs

#endif  // PATROL_MSGS__MSG__DETAIL__EXPERIMENT_EVENT__BUILDER_HPP_
