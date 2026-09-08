#ifndef AUCTION_LOGIC_H
#define AUCTION_LOGIC_H

#include <stdint.h>
#include <stdbool.h>

#define MAX_TASKS 20
#define MAX_DRONES 3

#define DRONE_STATE_IDLE 0
#define DRONE_STATE_PATROLLING 1
#define DRONE_STATE_INSPECTING 2
#define DRONE_STATE_RETURNING 3
#define DRONE_STATE_FAILED 4

typedef struct {
    uint16_t task_id;
    float x;
    float y;
    float z;
    uint8_t priority;
    uint8_t inspection_type;
    float hover_duration;
    bool active;
    bool completed;
    uint8_t assigned_drone; // 255 if unassigned
} AuctionTask;

typedef struct {
    float x;
    float y;
    float z;
    float battery_level;
    uint8_t state;
    bool is_healthy;
    uint64_t last_seen_us;
} DroneStateInfo;

void auction_init(void);
void auction_add_task(uint16_t id, float x, float y, float z, uint8_t priority, uint8_t type, float hover);
void auction_update_drone_state(uint8_t drone_id, float x, float y, float z, float battery, uint8_t state, uint64_t timestamp);
void auction_record_bid(uint16_t task_id, uint8_t drone_id, float cost);

bool auction_run_allocation(uint16_t *out_task_id, uint8_t *out_drone_id);
float auction_calculate_cost(uint8_t drone_id, uint16_t task_id);

void auction_recycle_tasks_if_all_completed(void);
void auction_handle_drone_failure(uint8_t failed_drone_id);
void auction_check_peer_timeouts(uint64_t current_time_us, uint64_t timeout_us);

AuctionTask* auction_get_task(uint16_t task_id);
AuctionTask* auction_get_tasks(uint8_t *count);
uint8_t auction_get_assigned_task_count(uint8_t drone_id);
bool auction_is_drone_healthy(uint8_t drone_id);
uint8_t auction_count_healthy_drones(void);
void auction_get_drone_position(uint8_t drone_id, float *x, float *y, float *z);

#endif
