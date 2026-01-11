# Multi-Agent System Implementation

## Overview

The system has been converted from a sequential workflow to a **true multi-agent system** that uses MongoDB as the coordination layer. Agents now communicate and coordinate through a task queue system rather than direct method calls.

## Key Changes

### 1. Task Queue System

All agent coordination now happens through MongoDB's `tasks` collection:

- **Task Creation**: Orchestrator creates tasks with dependencies
- **Task Assignment**: Agents claim tasks from the queue
- **Task Dependencies**: Tasks can depend on other tasks completing
- **Task Status**: Tasks track status (pending → assigned → completed/failed)

### 2. Agent Autonomy

Each agent now has a `process_task(task_id)` method that:
- Reads task data from MongoDB
- Processes the task independently
- Updates task status and output
- Can be called by orchestrator OR polled autonomously

### 3. Workflow Coordination

The Orchestrator now:
- Creates tasks instead of directly calling agents
- Sets up task dependencies (e.g., categorization depends on extraction + summarization)
- Monitors task completion
- Coordinates the workflow through the task queue

## Architecture

```
User Request
    ↓
Orchestrator Agent
    ↓
Creates Task 1: data_collection (priority 10, no deps)
    ↓
Data Collection Agent claims & processes task
    ↓
Orchestrator creates:
  - Task 2: extraction (depends on Task 1)
  - Task 3: summarization (depends on Task 1)
    ↓
Extraction Agent & Summarization Agent process in parallel
    ↓
Orchestrator creates:
  - Task 4: categorization (depends on Task 2 & Task 3)
    ↓
Categorization Agent processes task
    ↓
Workflow Complete
```

## Task Dependencies

Tasks use a `depends_on` field to ensure proper execution order:

- **Data Collection**: No dependencies (starts workflow)
- **Extraction**: Depends on Data Collection
- **Summarization**: Depends on Data Collection  
- **Categorization**: Depends on Extraction AND Summarization

## Agent Methods

### BaseAgent (Enhanced)

- `create_task()` - Create a new task in the queue
- `get_available_task()` - Find tasks this agent can handle
- `claim_task()` - Atomically claim a task for processing
- `update_task()` - Update task status and output
- `process_task()` - Process a task from the queue (implemented by each agent)

### Each Agent Implements

- `process_task(task_id)` - Main entry point for task processing
- Original methods (e.g., `extract()`, `summarize()`) still work but are called internally

## MongoDB Collections Used

### `tasks`
- Task queue with status, dependencies, input/output data
- Agents query this to find work
- Orchestrator creates tasks here

### `agents`
- Agent registry with skills, status, capabilities
- Used for peer discovery (future enhancement)

### `temporary_files` (new)
- Stores file references for agents to access
- Used for audio/photo files that can't be passed through task queue directly

## Current Implementation Status

✅ **Task Queue System**: Fully implemented
✅ **Task Dependencies**: Working
✅ **Agent Task Processing**: All agents have `process_task()` methods
✅ **Orchestrator Coordination**: Creates tasks and monitors completion

🔄 **Hybrid Mode**: Currently, Orchestrator still triggers agents synchronously, but they process through the task queue. This ensures reliability while maintaining the multi-agent architecture.

## Future Enhancements

### Fully Autonomous Agents

To make agents fully autonomous (running independently):

1. **Background Workers**: Run agents as separate processes/threads that poll for tasks
2. **Event-Driven**: Use MongoDB change streams to notify agents of new tasks
3. **Load Balancing**: Multiple instances of same agent type can process tasks in parallel
4. **Peer Discovery**: Agents query MongoDB to find other agents for collaboration

### Example: Autonomous Agent Worker

```python
def agent_worker(agent):
    """Background worker that continuously polls for tasks"""
    while True:
        task = agent.get_available_task(agent.agent_type)
        if task:
            if agent.claim_task(task["task_id"]):
                agent.process_task(task["task_id"])
        time.sleep(1)  # Poll interval
```

## Benefits of This Architecture

1. **Scalability**: Multiple agent instances can process tasks in parallel
2. **Reliability**: Tasks are persisted in MongoDB, can be retried on failure
3. **Observability**: All tasks and agent status tracked in MongoDB
4. **Flexibility**: Easy to add new agents or modify workflows
5. **Decoupling**: Agents don't need to know about each other directly

## Testing the Multi-Agent System

1. Submit a meeting through the API
2. Check MongoDB `tasks` collection - you'll see tasks being created
3. Watch task status change: pending → assigned → completed
4. Verify task dependencies are respected
5. Check agent status in `agents` collection

## Migration Notes

- Old direct method calls still work (backward compatible)
- New `process_task()` methods use the task queue
- Orchestrator uses task queue for coordination
- All agent-to-agent communication goes through MongoDB
