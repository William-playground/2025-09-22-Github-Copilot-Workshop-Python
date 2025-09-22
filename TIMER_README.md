# 🍅 Pomodoro Timer API

A REST API implementation of the Pomodoro Technique timer with comprehensive state management.

## Features

- **State Machine**: Implements IDLE → FOCUS_RUNNING → PAUSE/RESUME → BREAK_RUNNING → IDLE workflow
- **Auto-transitions**: Automatically moves between focus and break sessions
- **Error Handling**: Proper HTTP status codes for invalid state transitions (409)
- **Logging**: Comprehensive logging of all state changes and API calls
- **Configurable**: Customizable timer durations

## API Endpoints

### Timer Control
- `POST /api/timer/start` - Start a focus session
- `POST /api/timer/pause` - Pause current session
- `POST /api/timer/resume` - Resume paused session
- `POST /api/timer/reset` - Reset timer to idle state

### Information
- `GET /api/timer/state` - Get current timer state
- `GET /api/timer/config` - Get timer configuration
- `GET /health` - Health check endpoint

## Timer States

- `idle` - Timer is not running
- `focus_running` - Focus session in progress
- `focus_paused` - Focus session paused
- `break_running` - Break session in progress
- `break_paused` - Break session paused

## State Transitions

```
IDLE → FOCUS_RUNNING → FOCUS_PAUSED/RESUME → BREAK_RUNNING → IDLE
```

Auto-transitions:
- Focus session completion → Break session
- Break session completion → Idle state

## Configuration

Default timer durations:
- Focus session: 25 minutes
- Short break: 5 minutes
- Long break: 15 minutes
- Cycles before long break: 4

## Usage

### Start the API Server
```bash
python3 timer_api.py
```

### Example API Calls
```bash
# Start a focus session
curl -X POST http://localhost:5000/api/timer/start

# Get current state
curl http://localhost:5000/api/timer/state

# Pause session
curl -X POST http://localhost:5000/api/timer/pause

# Resume session
curl -X POST http://localhost:5000/api/timer/resume

# Reset timer
curl -X POST http://localhost:5000/api/timer/reset
```

## Testing

Run the test suite:
```bash
# Test timer state machine
python3 test_timer.py

# Test API endpoints (requires server running)
python3 test_api.py

# Run interactive demo
python3 demo_timer.py
```

## Error Handling

The API returns appropriate HTTP status codes:
- `200` - Success
- `409` - Invalid state transition
- `422` - Unprocessable entity
- `500` - Internal server error

## Security

- Debug mode is disabled by default in production
- No security vulnerabilities detected by CodeQL analysis
- Uses environment variables for configuration

## Logging

All state changes and API calls are logged with timestamps:
```
2025-09-22 08:01:56,440 - INFO - State transition: idle -> focus_running
2025-09-22 08:01:56,440 - INFO - Started focus session - Duration: 1500s
```