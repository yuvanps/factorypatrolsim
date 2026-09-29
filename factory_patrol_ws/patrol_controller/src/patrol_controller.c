#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>

#include <rcl/rcl.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>
#include <rosidl_runtime_c/string_functions.h>

#include <px4_msgs/msg/offboard_control_mode.h>
#include <px4_msgs/msg/trajectory_setpoint.h>
#include <px4_msgs/msg/vehicle_command.h>
#include <px4_msgs/msg/vehicle_odometry.h>

#include "auction_logic.h"
#include <patrol_msgs/msg/task.h>
#include <patrol_msgs/msg/mission.h>
#include <patrol_msgs/msg/drone_state.h>
#include <patrol_msgs/msg/task_bid.h>
#include <patrol_msgs/msg/task_assignment.h>
#include <patrol_msgs/msg/swarm_status.h>
#include <patrol_msgs/msg/experiment_event.h>
#include <patrol_msgs/msg/movement_command.h>

#define TIMER_PERIOD_MS 100
#define VEHICLE_CMD_DO_SET_MODE            176
#define VEHICLE_CMD_COMPONENT_ARM_DISARM   400
#define WAYPOINT_RADIUS 1.2f

static px4_msgs__msg__VehicleOdometry odometry_msg;
static rcl_subscription_t odometry_sub;

static rcl_publisher_t offboard_control_mode_pub;
static rcl_publisher_t trajectory_setpoint_pub;
static rcl_publisher_t vehicle_command_pub;

static rcl_publisher_t drone_state_pub;
static rcl_publisher_t task_bid_pub;
static rcl_publisher_t task_assignment_pub;
static rcl_publisher_t swarm_status_pub;
static rcl_publisher_t experiment_event_pub; // instrumentation only (metrics), never read by any controller

static rcl_subscription_t mission_sub;
static rcl_subscription_t task_bid_sub;
static rcl_subscription_t task_assignment_sub;
static rcl_subscription_t drone_state_sub;
static rcl_subscription_t movement_cmd_sub;

static patrol_msgs__msg__Mission mission_msg;
static patrol_msgs__msg__TaskBid bid_msg;
static patrol_msgs__msg__TaskAssignment assignment_msg;
static patrol_msgs__msg__DroneState peer_drone_state_msg;
static patrol_msgs__msg__MovementCommand movement_cmd_msg;

static rcl_timer_t timer;
static uint8_t g_drone_id = 0;
static uint8_t g_num_drones = 0; // Number of spawned drones (argv[2]); valid IDs are 0..g_num_drones-1
static uint8_t g_state = DRONE_STATE_IDLE;

static int setpoint_counter = 0;
static bool mission_started = false;

// Factory frame (shared by all drones, tasks and /ground_station/drone_state):
//   x = Gazebo world X (east), y = Gazebo world Y (north), z = -Gazebo world Z (negative = above ground).
// PX4 local NED (VehicleOdometry / TrajectorySetpoint) has its origin at each drone's own spawn point:
//   NED[0] = north = Gazebo Y - spawn_y,  NED[1] = east = Gazebo X - spawn_x,  NED[2] = down.
// So:  factory_x = NED[1] + spawn_x,  factory_y = NED[0] + spawn_y,  factory_z = NED[2].

// Spawn coordinate offsets in global factory frame (Gazebo world X/Y of PX4_GZ_MODEL_POSE)
static float spawn_x = 0.0f;
static float spawn_y = 0.0f;

// Global factory frame coordinates
static float current_x = 0.0f;
static float current_y = 0.0f;
static float current_z = 0.0f;
static bool position_received = false;
static float current_battery = 100.0f;

static bool has_active_task = false;
static float target_x = 0.0f;
static float target_y = 0.0f;
static float target_z = 0.0f; // On ground initially
static uint16_t current_task_id = 0;
static uint32_t hover_timer_ms = 0;
static uint32_t mission_start_tick = 0;
static uint8_t nav_state = 0; // 0: WAIT_STAGGER, 1: ASCEND, 2: TRANSLATE, 3: DESCEND
static uint32_t task_start_tick = 0; // When current task nav was initiated

// Independent zone list — each drone loops its assigned zones forever
#define MAX_MY_ZONES 10
static uint16_t my_zones[MAX_MY_ZONES];
static uint8_t my_zone_count = 0;
static uint8_t my_zone_index = 0;  // Next zone to patrol

// Collision avoidance
#define SAFE_DISTANCE_SQ 6.25f  // 2.5m squared — hold if peer is within this
static bool proximity_hold = false;
static bool initial_takeoff_done = false;

// How long to stagger ascent per drone: drone_id * STAGGER_TICKS
#define STAGGER_TICKS 30  // 3 seconds between each drone's ascent start

// Navigation mode (argv[3]):
//   internal (default) - built-in transit: per-drone altitude layers, centre-corridor routing,
//                        proximity hold. Used by the auction baseline.
//   external           - after a vertical takeoff, transit is driven by MovementCommands on
//                        /swarm/movement_command (reactive algorithms, e.g. APF). Task allocation,
//                        zone looping, arrival check (WAYPOINT_RADIUS), inspection hover,
//                        low-battery return and failure handling are unchanged.
static bool g_nav_external = false;
#define NAV_EXTERNAL_FOLLOW 5            // nav_state used only in external mode
#define MOVEMENT_CMD_TIMEOUT_US 500000ULL // stale command -> keep last setpoint (bounded hold)
static bool external_airborne = false;    // external mode: initial vertical takeoff completed
static bool movement_cmd_valid = false;
static uint16_t movement_cmd_task_id = 0;
static float movement_cmd_x = 0.0f, movement_cmd_y = 0.0f, movement_cmd_z = 0.0f;
static uint64_t movement_cmd_rx_us = 0;

static uint64_t timestamp_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return ((uint64_t)ts.tv_sec * 1000000ULL) + ((uint64_t)ts.tv_nsec / 1000ULL);
}

static void publish_offboard_control_mode(void) {
    px4_msgs__msg__OffboardControlMode msg;
    px4_msgs__msg__OffboardControlMode__init(&msg);
    msg.timestamp = timestamp_us();
    msg.position = true;
    msg.velocity = false;
    msg.acceleration = false;
    msg.attitude = false;
    msg.body_rate = false;
    msg.thrust_and_torque = false;
    msg.direct_actuator = false;
    (void)rcl_publish(&offboard_control_mode_pub, &msg, NULL);
}

static void publish_trajectory_setpoint(void) {
    px4_msgs__msg__TrajectorySetpoint msg;
    px4_msgs__msg__TrajectorySetpoint__init(&msg);
    msg.timestamp = timestamp_us();

    // Safety: clamp factory-frame targets within wall bounds (3m margin)
    float safe_x = target_x;
    float safe_y = target_y;
    if (safe_x > 12.0f) safe_x = 12.0f;
    if (safe_x < -12.0f) safe_x = -12.0f;
    if (safe_y > 7.0f) safe_y = 7.0f;
    if (safe_y < -7.0f) safe_y = -7.0f;

    // Transform clamped global factory target to PX4 local NED frame (north, east, down):
    msg.position[0] = safe_y - spawn_y;
    msg.position[1] = safe_x - spawn_x;
    msg.position[2] = target_z;
    msg.velocity[0] = NAN; msg.velocity[1] = NAN; msg.velocity[2] = NAN;
    msg.acceleration[0] = NAN; msg.acceleration[1] = NAN; msg.acceleration[2] = NAN;
    msg.jerk[0] = NAN; msg.jerk[1] = NAN; msg.jerk[2] = NAN;
    msg.yaw = 0.0f;
    msg.yawspeed = NAN;
    (void)rcl_publish(&trajectory_setpoint_pub, &msg, NULL);
}

static void publish_vehicle_command(uint16_t command, float param1, float param2) {
    px4_msgs__msg__VehicleCommand msg;
    px4_msgs__msg__VehicleCommand__init(&msg);
    msg.timestamp = timestamp_us();
    msg.param1 = param1;
    msg.param2 = param2;
    msg.command = command;
    msg.target_system = g_drone_id + 1; // Target this drone's specific PX4 instance
    msg.target_component = 1;
    msg.source_system = 1;
    msg.source_component = 1;
    msg.from_external = true;
    (void)rcl_publish(&vehicle_command_pub, &msg, NULL);
}

static void odometry_callback(const void * msgin) {
    const px4_msgs__msg__VehicleOdometry * msg = (const px4_msgs__msg__VehicleOdometry *)msgin;
    // Transform PX4 local NED odometry (origin = this drone's spawn) to global factory frame:
    current_x = msg->position[1] + spawn_x; // east  -> factory x
    current_y = msg->position[0] + spawn_y; // north -> factory y
    current_z = msg->position[2];
    position_received = true;
    auction_update_drone_state(g_drone_id, current_x, current_y, current_z, current_battery, g_state, timestamp_us());
}

static void peer_drone_state_callback(const void * msgin) {
    const patrol_msgs__msg__DroneState * msg = (const patrol_msgs__msg__DroneState *)msgin;
    if (msg->drone_id != g_drone_id && msg->drone_id < g_num_drones && msg->battery_level > 0.0f) {
        auction_update_drone_state(msg->drone_id, msg->x, msg->y, msg->z, msg->battery_level, msg->state, timestamp_us());
    }
}

static void movement_command_callback(const void * msgin) {
    const patrol_msgs__msg__MovementCommand * msg = (const patrol_msgs__msg__MovementCommand *)msgin;
    if (msg->drone_id != g_drone_id) return;
    // Reject malformed commands outright (defence in depth; the algorithm already guarantees finite values)
    if (!isfinite(msg->target_x) || !isfinite(msg->target_y) || !isfinite(msg->target_z)) return;
    movement_cmd_task_id = msg->task_id;
    movement_cmd_x = msg->target_x;
    movement_cmd_y = msg->target_y;
    movement_cmd_z = msg->target_z;
    movement_cmd_rx_us = timestamp_us();
    movement_cmd_valid = true;
}

static void mission_callback(const void * msgin) {
    const patrol_msgs__msg__Mission * msg = (const patrol_msgs__msg__Mission *)msgin;
    printf("[Drone %d] Mission %d received with %zu tasks. ARMING & STARTING PATROL!\n", g_drone_id, msg->mission_id, msg->tasks.size);
    mission_started = true;
    mission_start_tick = setpoint_counter;

    // Reset battery to full for the new mission run
    current_battery = 100.0f;

    auction_init(g_num_drones, timestamp_us());

    // Force-register self as healthy at 100% so stale peer messages can't poison our own slot
    auction_update_drone_state(g_drone_id, current_x, current_y, current_z, current_battery, DRONE_STATE_IDLE, timestamp_us());
    
    for (size_t i = 0; i < msg->tasks.size; i++) {
        patrol_msgs__msg__Task *t = &msg->tasks.data[i];
        auction_add_task(t->task_id, t->x, t->y, t->z, t->priority, t->inspection_type, t->hover_duration);
        float cost = auction_calculate_cost(g_drone_id, t->task_id);
        
        auction_record_bid(t->task_id, g_drone_id, cost);

        patrol_msgs__msg__TaskBid bid;
        patrol_msgs__msg__TaskBid__init(&bid);
        bid.task_id = t->task_id;
        bid.drone_id = g_drone_id;
        bid.cost = cost;
        (void)rcl_publish(&task_bid_pub, &bid, NULL);
    }
}

static void task_bid_callback(const void * msgin) {
    const patrol_msgs__msg__TaskBid * msg = (const patrol_msgs__msg__TaskBid *)msgin;
    auction_record_bid(msg->task_id, msg->drone_id, msg->cost);
}

static float get_patrol_altitude(uint8_t drone_id) {
    // Formulaic: each drone gets its own patrol hover layer
    // Drone 0: -2.5, Drone 1: -3.5, Drone 2: -4.5, Drone 3: -5.5, ...
    return -2.5f - (drone_id * 1.0f);
}

// Each drone has a UNIQUE transit altitude above the tallest machines (~4m).
// All transit routes meet at the centre corridor (0,0), so layers are 1.25m apart
// (0.5m layering produced ~1.4m near-misses there; PX4 altitude tracking uses ~0.3m of
// the gap). Layers are compressed only if needed to keep the top layer at or below 10m
// (factory ceiling barrier is at 12m).
// <=5 drones: Drone 0: -5.0m, Drone 1: -6.25m, Drone 2: -7.5m, ... Drone 4: -10.0m.  10 drones: 0.56m.
#define TRANSIT_BASE_ALT   -5.0f
#define TRANSIT_TOP_ALT   -10.0f
#define TRANSIT_LAYER_SEP   1.25f
static float get_transit_altitude(uint8_t drone_id) {
    float sep = TRANSIT_LAYER_SEP;
    if (g_num_drones > 1) {
        float max_sep = (TRANSIT_BASE_ALT - TRANSIT_TOP_ALT) / (float)(g_num_drones - 1);
        if (max_sep < sep) sep = max_sep;
    }
    return TRANSIT_BASE_ALT - (drone_id * sep);
}

// Returns true if any peer drone is within SAFE_DISTANCE_SQ of this drone's target.
// If so, the drone should hold position (not move toward target).
// Priority rule: lower drone ID has right-of-way and keeps moving.
static bool check_peer_proximity(void) {
    // Peer positions come from /ground_station/drone_state (factory frame), stored by the auction module
    for (uint8_t d = 0; d < g_num_drones; d++) {
        if (d == g_drone_id) continue;
        if (!auction_is_drone_healthy(d)) continue;
        
        // Get peer position from the auction system
        float px, py, pz;
        auction_get_drone_position(d, &px, &py, &pz);
        
        float dx = px - target_x;
        float dy = py - target_y;
        float dz = pz - target_z;
        float dist_sq = dx*dx + dy*dy + dz*dz;
        
        if (dist_sq < SAFE_DISTANCE_SQ && d < g_drone_id) {
            // A higher-priority drone is near our target — hold
            if (!proximity_hold) {
                printf("[Drone %d] HOLD — Drone %d within safe distance. Waiting.\n", g_drone_id, d);
                proximity_hold = true;
            }
            return true;
        }
    }
    
    if (proximity_hold) {
        printf("[Drone %d] RESUME — Path is clear.\n", g_drone_id);
        proximity_hold = false;
    }
    return false;
}

static void task_assignment_callback(const void * msgin) {
    const patrol_msgs__msg__TaskAssignment * msg = (const patrol_msgs__msg__TaskAssignment *)msgin;
    AuctionTask* t = auction_get_task(msg->task_id);
    if (t) {
        t->assigned_drone = msg->drone_id;
        t->active = true;
        t->completed = false;

        // Always accumulate zones assigned to this drone into my_zones[]
        if (msg->drone_id == g_drone_id) {
            bool already_have = false;
            for (uint8_t zi = 0; zi < my_zone_count; zi++) {
                if (my_zones[zi] == msg->task_id) { already_have = true; break; }
            }
            if (!already_have && my_zone_count < MAX_MY_ZONES) {
                my_zones[my_zone_count++] = msg->task_id;
                printf("[Drone %d] Zone %d registered (%d total zones).\n",
                       g_drone_id, msg->task_id, my_zone_count);
            }
        }

        if (msg->drone_id == g_drone_id && !has_active_task && g_state != DRONE_STATE_RETURNING) {
            has_active_task = true;
            nav_state = 0; // Reset navigation state machine
            task_start_tick = setpoint_counter;
            current_task_id = t->task_id;
            g_state = DRONE_STATE_PATROLLING;
            hover_timer_ms = 0;
            printf("[Drone %d] Assigned to Task %d. Commencing safe transit.\n", g_drone_id, msg->task_id);
        }
    }
}

static void start_next_zone(void) {
    if (my_zone_count == 0) { has_active_task = false; g_state = DRONE_STATE_IDLE; return; }
    uint8_t idx = my_zone_index % my_zone_count;
    my_zone_index = (idx + 1) % my_zone_count;
    current_task_id = my_zones[idx];
    AuctionTask* t = auction_get_task(current_task_id);
    if (t) {
        t->active = true;
        t->completed = false;
        has_active_task = true;
        nav_state = initial_takeoff_done ? 1 : 0; // Skip stagger if already airborne
        task_start_tick = setpoint_counter;
        g_state = DRONE_STATE_PATROLLING;
        hover_timer_ms = 0;
        printf("[Drone %d] Zone loop -> Task %d (%.1f,%.1f)\n", g_drone_id, current_task_id, t->x, t->y);
    } else {
        has_active_task = false;
        g_state = DRONE_STATE_IDLE;
    }
}

// External-mode transit (nav_state 1 -> NAV_EXTERNAL_FOLLOW -> 4). nav_state 0 (stagger) and
// 4 (hold at the task point + inspection hover) are shared with internal mode.
static void update_external_navigation(const AuctionTask *t, float task_z) {
    if (nav_state == 1) {
        // Initial TAKEOFF only: climb vertically above the spawn point to the task altitude,
        // then hand transit over to the external algorithm. Later zones start airborne.
        if (!external_airborne) {
            target_z = task_z;
            uint32_t ascend_elapsed = setpoint_counter - task_start_tick;
            // 0.3 m: hand over at the inspection altitude, not at rack/partition-top height
            if (fabsf(current_z - task_z) >= 0.3f && ascend_elapsed <= 150) return;
            external_airborne = true;
            printf("[Drone %d] Takeoff complete (z=%.1f). Following external movement commands.\n",
                   g_drone_id, current_z);
        }
        nav_state = NAV_EXTERNAL_FOLLOW;
    }

    // FOLLOW: track the latest command for THIS task. If it is missing, stale or for another
    // task, keep the previous setpoint (at most one short command horizon away) until a new one arrives.
    if (movement_cmd_valid && movement_cmd_task_id == current_task_id &&
        timestamp_us() - movement_cmd_rx_us < MOVEMENT_CMD_TIMEOUT_US) {
        target_x = movement_cmd_x;
        target_y = movement_cmd_y;
        target_z = movement_cmd_z;
    }

    // Arrival uses the same criterion as internal mode; from here the controller holds the
    // exact task point (nav_state 4), so residual repulsion cannot make the drone oscillate.
    float dx = t->x - current_x, dy = t->y - current_y, dz = task_z - current_z;
    if (sqrtf(dx*dx + dy*dy + dz*dz) < WAYPOINT_RADIUS) {
        nav_state = 4;
        target_x = t->x; target_y = t->y; target_z = task_z;
        printf("[Drone %d] Reached task %d. Inspecting.\n", g_drone_id, current_task_id);
    }
}

// Instrumentation: announce a task completion (the moment t->completed is set) on
// /experiment/events so the metrics collector counts exactly what the mission logic
// completed. Publish-only; it does not influence navigation or allocation.
static void publish_task_completed(uint16_t task_id, float hover_s) {
    patrol_msgs__msg__ExperimentEvent ev;
    patrol_msgs__msg__ExperimentEvent__init(&ev);
    ev.timestamp = timestamp_us() * 1000ULL; // ns, same clock as the other experiment events
    char data[96];
    snprintf(data, sizeof(data), "{\"drone_id\": %d, \"task_id\": %d, \"hover_s\": %.2f}",
             g_drone_id, task_id, hover_s);
    rosidl_runtime_c__String__assign(&ev.event_type, "task_completed");
    rosidl_runtime_c__String__assign(&ev.data, data);
    (void)rcl_publish(&experiment_event_pub, &ev, NULL);
    patrol_msgs__msg__ExperimentEvent__fini(&ev);
}

static void update_task_execution(void) {
    if (!position_received || !mission_started) return;

    // ---- LOW BATTERY: Return to base via center corridor ----
    if (g_state == DRONE_STATE_RETURNING) {
        float transit_z = get_transit_altitude(g_drone_id);
        if (nav_state == 0) {
            // Ascend to transit altitude
            target_z = transit_z;
            if (fabsf(current_z - transit_z) < 0.5f) nav_state = 1;
        } else if (nav_state == 1) {
            // Fly to factory center corridor first
            target_x = 0.0f; target_y = 0.0f; target_z = transit_z;
            float dx = target_x - current_x; float dy = target_y - current_y;
            if (sqrtf(dx*dx + dy*dy) < 1.5f) nav_state = 2;
        } else if (nav_state == 2) {
            // Fly from center to spawn XY at transit altitude
            target_x = spawn_x; target_y = spawn_y; target_z = transit_z;
            float dx = target_x - current_x; float dy = target_y - current_y;
            if (sqrtf(dx*dx + dy*dy) < 0.5f) nav_state = 3;
        } else if (nav_state == 3) {
            // Descend at spawn
            target_x = spawn_x; target_y = spawn_y;
            target_z = get_patrol_altitude(g_drone_id);
        }
        return;
    }

    // ---- NO TASK: Get initial assignment or loop zones ----
    if (!has_active_task) {
        if (my_zone_count > 0) {
            start_next_zone();
        } else {
            // Still waiting for zone assignments from Drone 0
            target_z = get_patrol_altitude(g_drone_id);
            return;
        }
        if (!has_active_task) {
            target_z = get_patrol_altitude(g_drone_id); // Hover and wait
            return;
        }
    }

    AuctionTask* t = auction_get_task(current_task_id);
    if (!t) { has_active_task = false; return; }

    float transit_z = get_transit_altitude(g_drone_id);
    float task_z = (t->z < -1.0f) ? t->z : get_patrol_altitude(g_drone_id);
    uint32_t stagger_delay = (uint32_t)g_drone_id * STAGGER_TICKS;

    if (nav_state == 0) {
        // WAIT_STAGGER: Hold on ground until stagger window opens
        if ((uint32_t)(setpoint_counter - task_start_tick) >= stagger_delay) {
            nav_state = 1;
            initial_takeoff_done = true;
            printf("[Drone %d] Ascending to transit %.1fm\n", g_drone_id, -transit_z);
        }
        return; // Stay grounded during stagger wait
    } else if (g_nav_external && nav_state != 4) {
        update_external_navigation(t, task_z);
    } else if (nav_state == 1) {
        // ASCEND: Go up to transit altitude while holding horizontal position.
        // DO NOT track current_x/current_y — that follows drift and prevents
        // PX4 position hold. Leave target_x/target_y from the previous state
        // (spawn position for initial takeoff, or last task position for zone loops).
        target_z = transit_z;
        // Transition to TRANSIT_CENTER when near transit altitude, OR after 15s timeout
        uint32_t ascend_elapsed = setpoint_counter - task_start_tick;
        if (fabsf(current_z - transit_z) < 1.2f || ascend_elapsed > 150) {
            nav_state = 2;
            printf("[Drone %d] Transit altitude reached (z=%.1f, target=%.1f). Translating.\n",
                   g_drone_id, current_z, transit_z);
        }
    } else if (nav_state == 2) {
        // TRANSIT_CENTER: Fly to factory center corridor (0,0) at transit altitude
        // This avoids long diagonal flights near walls where PX4 overshoot causes collisions
        if (check_peer_proximity()) {
            target_z = transit_z;
            return;
        }
        target_x = 0.0f; target_y = 0.0f; target_z = transit_z;
        float h_dx = target_x - current_x; float h_dy = target_y - current_y;
        if (sqrtf(h_dx*h_dx + h_dy*h_dy) < 1.5f) {
            nav_state = 3;
            printf("[Drone %d] Reached center corridor. Heading to task %d at (%.1f,%.1f)\n",
                   g_drone_id, current_task_id, t->x, t->y);
        }
    } else if (nav_state == 3) {
        // TRANSIT_TARGET: Fly from center corridor to task XY at transit altitude
        if (check_peer_proximity()) {
            target_z = transit_z;
            return;
        }
        target_x = t->x; target_y = t->y; target_z = transit_z;
        float h_dx = target_x - current_x; float h_dy = target_y - current_y;
        if (sqrtf(h_dx*h_dx + h_dy*h_dy) < 0.5f) {
            nav_state = 4;
            // Switch to the inspection point now, so the arrival check below measures distance
            // to the task (not to the transit-altitude point we are already at).
            target_z = task_z;
            printf("[Drone %d] Above task %d. Descending to %.1fm\n",
                   g_drone_id, current_task_id, -task_z);
        }
    } else if (nav_state == 4) {
        // DESCEND: Drop to inspection point
        target_x = t->x; target_y = t->y; target_z = task_z;
    }

    float dx = target_x - current_x;
    float dy = target_y - current_y;
    float dz = target_z - current_z;
    float distance = sqrtf(dx*dx + dy*dy + dz*dz);

    if (distance < WAYPOINT_RADIUS && nav_state == 4) {
        g_state = DRONE_STATE_INSPECTING;
        hover_timer_ms += TIMER_PERIOD_MS;
        float req_hover = t->hover_duration > 0.1f ? t->hover_duration : 3.0f;
        if (hover_timer_ms >= (uint32_t)(req_hover * 1000.0f)) {
            printf("[Drone %d] Inspection done at Task %d (%.1fs). Cycling zones.\n",
                   g_drone_id, current_task_id, req_hover);
            t->active = false; t->completed = true;
            publish_task_completed(current_task_id, req_hover);
            has_active_task = false; hover_timer_ms = 0;
            g_state = DRONE_STATE_IDLE;
            start_next_zone(); // Immediately begin next zone — no waiting for Drone 0
        }
    }
}

static void timer_callback(rcl_timer_t *timer_handle, int64_t last_call_time) {
    (void)timer_handle; (void)last_call_time;

    // Drone 0 orchestrates continuous patrol cycle and peer health
    // Wait 50 ticks (5 seconds) so all drones have received the mission and published bids
    if (g_drone_id == 0 && mission_started && (setpoint_counter - mission_start_tick > 50)) {
        auction_check_peer_timeouts(timestamp_us(), 5000000ULL); // 5 sec timeout
        auction_recycle_tasks_if_all_completed(); // Loop patrol continuously

        // Allocate ALL unassigned tasks in one timer tick (not just one per tick)
        uint16_t out_t;
        uint8_t out_d;
        bool any_allocated = false;
        while (auction_run_allocation(&out_t, &out_d)) {
            any_allocated = true;
            patrol_msgs__msg__TaskAssignment assign;
            patrol_msgs__msg__TaskAssignment__init(&assign);
            assign.task_id = out_t;
            assign.drone_id = out_d;
            (void)rcl_publish(&task_assignment_pub, &assign, NULL);

            // Drone 0 must also collect its own zones here (callback may not fire for self)
            if (out_d == 0) {
                bool already_have = false;
                for (uint8_t zi = 0; zi < my_zone_count; zi++) {
                    if (my_zones[zi] == out_t) { already_have = true; break; }
                }
                if (!already_have && my_zone_count < MAX_MY_ZONES) {
                    my_zones[my_zone_count++] = out_t;
                    printf("[Drone 0] Zone %d registered (%d total zones).\n", out_t, my_zone_count);
                }
            }

            if (out_d == 0 && !has_active_task && g_state != DRONE_STATE_RETURNING) {
                AuctionTask* t = auction_get_task(out_t);
                if (t) {
                    has_active_task = true;
                    nav_state = 0; // Reset navigation state machine
                    task_start_tick = setpoint_counter;
                    current_task_id = t->task_id;
                    g_state = DRONE_STATE_PATROLLING;
                    hover_timer_ms = 0;
                    printf("[Drone 0] Assigned to Task %d. Commencing safe transit.\n", t->task_id);
                }
            }
        }

        // Check if tasks remain but NO healthy drones are available — alert ground station
        static bool no_drones_reported = false;
        uint8_t count = 0;
        AuctionTask* task_list = auction_get_tasks(&count);
        bool any_unassigned = false;
        for (int i = 0; i < count; i++) {
            if (task_list[i].active && task_list[i].assigned_drone == 255) {
                any_unassigned = true;
                break;
            }
        }

        if (!any_allocated && any_unassigned && auction_count_healthy_drones() == 0) {
            if (!no_drones_reported) {
                no_drones_reported = true;
                printf("\n!!! [Swarm] NO HEALTHY DRONES AVAILABLE — tasks cannot be assigned. Alerting ground station.\n\n");
                patrol_msgs__msg__SwarmStatus status_msg;
                patrol_msgs__msg__SwarmStatus__init(&status_msg);
                status_msg.status = patrol_msgs__msg__SwarmStatus__STATUS_NO_DRONES_AVAILABLE;
                rosidl_runtime_c__String__assign(&status_msg.reason,
                    "All drones are unavailable (low battery or failed). Patrol suspended.");
                (void)rcl_publish(&swarm_status_pub, &status_msg, NULL);
                patrol_msgs__msg__SwarmStatus__fini(&status_msg);
            }
        } else {
            no_drones_reported = false; // Reset so we can alert again if it happens again
        }
    }

    publish_offboard_control_mode();

    // Always send ARM + OFFBOARD commands every 10 ticks so PX4 satisfies its
    // 10-setpoint requirement and drones are ready to fly the moment a mission arrives.
    if (setpoint_counter % 10 == 0) {
        publish_vehicle_command(VEHICLE_CMD_DO_SET_MODE, 1.0f, 6.0f);
        publish_vehicle_command(VEHICLE_CMD_COMPONENT_ARM_DISARM, 1.0f, 0.0f);
    }

    if (mission_started) {
        // Battery simulation during active mission
        if (setpoint_counter > 50 && current_battery > 0.0f) {
            current_battery -= 0.01f;
            if (current_battery < 20.0f && g_state != DRONE_STATE_RETURNING) {
                g_state = DRONE_STATE_RETURNING;
                has_active_task = false;
                nav_state = 0; // Initialize state machine for safe return
                printf("\n>>> [Drone %d] WARNING: BATTERY LOW (%.1f%%)! Returning to home base! <<<\n\n", g_drone_id, current_battery);
                auction_update_drone_state(g_drone_id, current_x, current_y, current_z, current_battery, g_state, timestamp_us());
            }
        }

        update_task_execution();
        publish_trajectory_setpoint();

        setpoint_counter++;
    } else {
        // Stay stationary on the ground disarmed until ground station dispatches mission
        target_x = spawn_x;
        target_y = spawn_y;
        target_z = 0.0f;
        publish_trajectory_setpoint();
        setpoint_counter++;
    }
    
    // Publish drone state
    patrol_msgs__msg__DroneState ds;
    patrol_msgs__msg__DroneState__init(&ds);
    ds.drone_id = g_drone_id;
    ds.x = current_x;
    ds.y = current_y;
    ds.z = current_z;
    ds.battery_level = current_battery;
    ds.state = g_state;
    ds.current_task_id = has_active_task ? current_task_id : 0;
    (void)rcl_publish(&drone_state_pub, &ds, NULL);
}

int main(int argc, char const * const * argv) {
    if (argc < 3) {
        fprintf(stderr, "Usage: patrol_controller <drone_id> <num_drones> [internal|external]\n");
        return 1;
    }
    if (argc >= 4 && argv[3][0] != '-') {
        if (strcmp(argv[3], "external") == 0) {
            g_nav_external = true;
        } else if (strcmp(argv[3], "internal") != 0) {
            fprintf(stderr, "Invalid navigation mode '%s' (expected internal|external)\n", argv[3]);
            return 1;
        }
    }
    int arg_id = atoi(argv[1]);
    int arg_num = atoi(argv[2]);
    if (arg_num < 1 || arg_num > MAX_DRONES || arg_id < 0 || arg_id >= arg_num) {
        fprintf(stderr, "Invalid arguments: drone_id=%d num_drones=%d (need 1 <= num_drones <= %d, 0 <= drone_id < num_drones)\n",
                arg_id, arg_num, MAX_DRONES);
        return 1;
    }
    g_drone_id = (uint8_t)arg_id;
    g_num_drones = (uint8_t)arg_num;

    // Set spawn offset matching start_swarm.sh coordinates
    // Drones spawn in north area (y=7), spaced 4m apart along X starting at x=-8
    // Clearances: north wall 2.85m, loading dock 4m, partition 1m north
    spawn_x = (g_drone_id * 4.0f) - 8.0f;
    spawn_y = 7.0f;
    
    target_x = spawn_x;
    target_y = spawn_y;
    target_z = 0.0f; // Rest on ground
    
    char namespace[32];
    sprintf(namespace, "/px4_%d", g_drone_id);

    rcl_allocator_t allocator = rcl_get_default_allocator();
    rclc_support_t support;
    rcl_node_t node;
    rclc_executor_t executor;

    printf("====================================\n");
    printf("     FACTORY PATROL CONTROLLER      \n");
    printf("     DRONE ID: %d / %d               \n", g_drone_id, g_num_drones);
    printf("     SPAWN: (%.1f, %.1f)             \n", spawn_x, spawn_y);
    printf("     NAV MODE: %s                   \n", g_nav_external ? "external" : "internal");
    printf("     STATUS: Grounded (Ready)       \n");
    printf("====================================\n");

    rclc_support_init(&support, argc, (char const * const * )argv, &allocator);
    rclc_node_init_default(&node, "patrol_controller", namespace, &support);

    rmw_qos_profile_t qos_profile = rmw_qos_profile_sensor_data;
    rmw_qos_profile_t rel_qos_profile = rmw_qos_profile_default;

    rclc_publisher_init(&offboard_control_mode_pub, &node, ROSIDL_GET_MSG_TYPE_SUPPORT(px4_msgs, msg, OffboardControlMode), "fmu/in/offboard_control_mode", &qos_profile);
    rclc_publisher_init(&trajectory_setpoint_pub, &node, ROSIDL_GET_MSG_TYPE_SUPPORT(px4_msgs, msg, TrajectorySetpoint), "fmu/in/trajectory_setpoint", &qos_profile);
    rclc_publisher_init(&vehicle_command_pub, &node, ROSIDL_GET_MSG_TYPE_SUPPORT(px4_msgs, msg, VehicleCommand), "fmu/in/vehicle_command", &qos_profile);
    
    rclc_publisher_init(&drone_state_pub, &node, ROSIDL_GET_MSG_TYPE_SUPPORT(patrol_msgs, msg, DroneState), "/ground_station/drone_state", &rel_qos_profile);
    rclc_publisher_init(&task_bid_pub, &node, ROSIDL_GET_MSG_TYPE_SUPPORT(patrol_msgs, msg, TaskBid), "/swarm/task_bid", &rel_qos_profile);
    rclc_publisher_init(&task_assignment_pub, &node, ROSIDL_GET_MSG_TYPE_SUPPORT(patrol_msgs, msg, TaskAssignment), "/swarm/task_assignment", &rel_qos_profile);
    rclc_publisher_init(&swarm_status_pub, &node, ROSIDL_GET_MSG_TYPE_SUPPORT(patrol_msgs, msg, SwarmStatus), "/ground_station/swarm_status", &rel_qos_profile);
    rclc_publisher_init(&experiment_event_pub, &node, ROSIDL_GET_MSG_TYPE_SUPPORT(patrol_msgs, msg, ExperimentEvent), "/experiment/events", &rel_qos_profile);

    rclc_timer_init_default(&timer, &support, RCL_MS_TO_NS(TIMER_PERIOD_MS), timer_callback);
    
    rclc_subscription_init(&odometry_sub, &node, ROSIDL_GET_MSG_TYPE_SUPPORT(px4_msgs, msg, VehicleOdometry), "fmu/out/vehicle_odometry", &qos_profile);
    rclc_subscription_init(&mission_sub, &node, ROSIDL_GET_MSG_TYPE_SUPPORT(patrol_msgs, msg, Mission), "/ground_station/mission", &rel_qos_profile);
    rclc_subscription_init(&task_bid_sub, &node, ROSIDL_GET_MSG_TYPE_SUPPORT(patrol_msgs, msg, TaskBid), "/swarm/task_bid", &rel_qos_profile);
    rclc_subscription_init(&task_assignment_sub, &node, ROSIDL_GET_MSG_TYPE_SUPPORT(patrol_msgs, msg, TaskAssignment), "/swarm/task_assignment", &rel_qos_profile);
    rclc_subscription_init(&drone_state_sub, &node, ROSIDL_GET_MSG_TYPE_SUPPORT(patrol_msgs, msg, DroneState), "/ground_station/drone_state", &rel_qos_profile);
    if (g_nav_external) {
        rclc_subscription_init(&movement_cmd_sub, &node, ROSIDL_GET_MSG_TYPE_SUPPORT(patrol_msgs, msg, MovementCommand), "/swarm/movement_command", &rel_qos_profile);
    }

    rclc_executor_init(&executor, &support.context, 7, &allocator);
    rclc_executor_add_timer(&executor, &timer);
    
    px4_msgs__msg__VehicleOdometry__init(&odometry_msg);
    rclc_executor_add_subscription(&executor, &odometry_sub, &odometry_msg, &odometry_callback, ON_NEW_DATA);
    
    patrol_msgs__msg__Mission__init(&mission_msg);
    patrol_msgs__msg__Task__Sequence__init(&mission_msg.tasks, 20);
    rclc_executor_add_subscription(&executor, &mission_sub, &mission_msg, &mission_callback, ON_NEW_DATA);
    
    patrol_msgs__msg__TaskBid__init(&bid_msg);
    rclc_executor_add_subscription(&executor, &task_bid_sub, &bid_msg, &task_bid_callback, ON_NEW_DATA);
    
    patrol_msgs__msg__TaskAssignment__init(&assignment_msg);
    rclc_executor_add_subscription(&executor, &task_assignment_sub, &assignment_msg, &task_assignment_callback, ON_NEW_DATA);

    patrol_msgs__msg__DroneState__init(&peer_drone_state_msg);
    rclc_executor_add_subscription(&executor, &drone_state_sub, &peer_drone_state_msg, &peer_drone_state_callback, ON_NEW_DATA);

    if (g_nav_external) {
        patrol_msgs__msg__MovementCommand__init(&movement_cmd_msg);
        rclc_executor_add_subscription(&executor, &movement_cmd_sub, &movement_cmd_msg, &movement_command_callback, ON_NEW_DATA);
    }

    auction_init(g_num_drones, timestamp_us());

    while (rcl_context_is_valid(&support.context)) {
        rclc_executor_spin_some(&executor, RCL_MS_TO_NS(100));
    }

    rclc_executor_fini(&executor);
    (void)rcl_node_fini(&node);
    (void)rcl_shutdown(&support.context);
    rclc_support_fini(&support);
    return 0;
}
