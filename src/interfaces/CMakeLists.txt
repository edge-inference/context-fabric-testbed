cmake_minimum_required(VERSION 3.8)
project(interfaces)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/AgentState.msg"
  "msg/DSMUpdate.msg"
  "msg/TaskAssignment.msg"
  "msg/TaskInfo.msg"
  "msg/TaskEvent.msg"
  "srv/TaskService.srv"
  "srv/GetAvailableTasks.srv"
  "srv/ClaimTask.srv"
  "srv/CompleteTask.srv"
  "srv/CreateTask.srv"
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()

