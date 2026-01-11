# Architecture & System Design

## System Overview

Multi-agent networking assistant that collects meeting data (voice, images, business cards), extracts information, groups them by priority (P0, P1, P2), and provides conversation summaries. Uses MongoDB Atlas for agent coordination and context management.

**Offline Support:** App works offline - users can record voice, take photos, and capture meeting data without internet. Data is stored locally and automatically synced to backend when internet is available, triggering normal agent workflow.

**End Goal:** Grouped list of people:
- **P0 (Highest Priority):** Names, companies, designations, conversation summaries
- **P1 (Medium Priority):** Names, companies, designations, conversation summaries
- **P2 (Lower Priority):** Names, companies, designations, conversation summaries

---

## Agents (5 Total)

1. **Data Collection Agent** - Processes voice transcriptions, badge photos, business cards
2. **Information Extraction Agent** - Extracts structured data (names, companies, titles, contact info)
3. **Categorization Agent** - Groups contacts into P0, P1, P2 based on user preferences and importance
4. **Summarization Agent** - Creates conversation summaries for each meeting
5. **Orchestrator Agent** - Decides task assignments, coordinates multi-agent workflows, manages agent communication and context sharing

---

## MongoDB Collections

### `agents`
- Agent registry: skills, status, capabilities, current task
- Used for peer discovery and task assignment

### `tasks`
- Task queue: task type, assigned agent, status, input/output data, context references
- Central task management system

### `contexts`
- Conversation contexts with token counts
- Supports compression, chunking, references for token management

### `people`
- Contact profiles: extracted data, categorization scores
- Links to meetings

### `meetings`
- Individual conversations: raw data, summary, priority_group (P0/P1/P2)
- Date, location, person_id

### `user_preferences`
- Use case, structured preferences, extracted preferences from comments
- Custom criteria, value indicators, categorization weights

### `agent_communications`
- Agent-to-agent message logs
- Context sharing records with token counts

---

## Workflows

### Onboarding Flow
```
User fills form (use case + structured fields + comments)
  → API receives data
  → Simple service analyzes comments (not a full agent)
  → Extracts: custom criteria, value indicators, special requirements
  → Updates user_preferences in MongoDB
```

### Meeting Processing Flow
```
User input (voice/image/card)
  → API receives request
  → Orchestrator Agent:
     - Analyzes task requirements
     - Identifies needed agents (Data Collection)
     - Assigns task to Data Collection Agent
  → Data Collection Agent (processes input, creates person/meeting)
     - Completes task, notifies Orchestrator
  → Orchestrator Agent:
     - Identifies next agent (Information Extraction)
     - Shares context (with token management)
     - Assigns task to Information Extraction Agent
  → Information Extraction Agent (extracts structured data)
     - Completes, notifies Orchestrator
  → Orchestrator Agent:
     - Assigns Summarization Agent
  → Summarization Agent
  → Orchestrator Agent:
     - Identifies final agent (Categorization)
     - Coordinates context from all previous agents
     - Assigns Categorization Agent
  → Categorization Agent (groups into P0/P1/P2)
  → Orchestrator Agent completes workflow
```

### End-of-Day Output Format

**API Response Structure:**
```json
{
  "P0": [
    {
      "name": "John Doe",
      "company": "Tech Corp",
      "designation": "CTO",
      "summary": "Discussed AI integration opportunities...",
      "meeting_date": "2024-01-15"
    },
    ...
  ],
  "P1": [
    {
      "name": "Jane Smith",
      "company": "StartupXYZ",
      "designation": "VP Engineering",
      "summary": "Talked about remote work culture...",
      "meeting_date": "2024-01-15"
    },
    ...
  ],
  "P2": [
    ...
  ]
}
```

**Query:** MongoDB aggregation groups meetings by `priority_group` and joins with `people` collection for details.

---

## Offline Functionality

### Offline Mode Support

**Frontend Offline Capabilities:**
- User can record voice, take photos, upload business cards without internet
- All data stored locally (IndexedDB for files, localStorage for metadata)
- Queue system stores pending uploads
- UI shows offline indicator

**When Offline:**
1. User records voice / takes photos
2. Frontend stores files in IndexedDB
3. Frontend stores meeting metadata in localStorage queue
4. Shows "Offline - Data will sync when online" message
5. User can continue adding more meetings

**When Internet Returns:**
1. Frontend detects online status (navigator.onLine or network event)
2. Sync service automatically triggers
3. Processes queue: uploads files + metadata to backend
4. Backend receives data and triggers normal workflow:
   - Orchestrator Agent coordinates
   - Agents process in sequence
   - Results stored in MongoDB
5. Frontend shows sync progress
6. Once synced, user can view results

### Offline Storage Structure

**IndexedDB (for files):**
```
meeting_files/
  - meeting_001/
    - voice_recording.mp3
    - badge_photo.jpg
    - business_card.jpg
  - meeting_002/
    - ...
```

**localStorage (for metadata queue):**
```json
{
  "pending_meetings": [
    {
      "local_id": "local_meeting_001",
      "timestamp": "2024-01-15T10:30:00",
      "files": {
        "voice": "meeting_001/voice_recording.mp3",
        "images": ["meeting_001/badge_photo.jpg"],
        "business_cards": ["meeting_001/business_card.jpg"]
      },
      "metadata": {
        "location": "Tech Conference",
        "date": "2024-01-15"
      },
      "synced": false
    }
  ]
}
```

### Sync Workflow

```
Frontend detects online
  ↓
Sync Service starts
  ↓
For each pending meeting in queue:
  ↓
1. Read files from IndexedDB
  ↓
2. Create FormData with files + metadata
  ↓
3. POST /api/meetings (with retry logic)
  ↓
4. On success:
   - Mark as synced in localStorage
   - Remove files from IndexedDB
   - Update queue status
  ↓
5. On failure:
   - Keep in queue
   - Retry on next sync
  ↓
All synced? Show success message
```

### Backend Handling

**Backend receives synced data:**
- Normal workflow starts (same as online)
- Orchestrator Agent coordinates
- Agents process sequentially
- Results stored in MongoDB
- Frontend can fetch results once processing completes

**API Endpoint:**
- `POST /api/meetings` - Accepts FormData (works same for online/offline)
- Returns: `{ meeting_id, status: "processing" }`
- Frontend can poll status if needed

### Frontend Components for Offline

**offlineStorage.js:**
- Manages IndexedDB for file storage
- Manages localStorage for metadata queue
- Functions: `storeMeeting()`, `getPendingMeetings()`, `markAsSynced()`, `clearSynced()`

**syncService.js:**
- Detects online/offline status
- Processes pending queue when online
- Handles retry logic for failed syncs
- Functions: `startSync()`, `syncPendingMeetings()`, `retryFailedSyncs()`

**networkDetector.js:**
- Monitors network status
- Triggers sync when coming online
- Functions: `isOnline()`, `onOnline()`, `onOffline()`

**useOffline.js (React Hook):**
- Provides offline state to components
- Handles online/offline events
- Returns: `{ isOffline, pendingCount, syncStatus }`

**OfflineIndicator.js:**
- UI component showing offline status
- Shows pending sync count
- Shows sync progress when syncing

### Meeting Input Component (Offline-Aware)

**When offline:**
```javascript
// MeetingInput.js
const handleSubmit = async (formData) => {
  if (navigator.onLine) {
    // Online: Submit directly
    await api.submitMeeting(formData);
  } else {
    // Offline: Store locally
    await offlineStorage.storeMeeting({
      files: formData,
      metadata: {...},
      timestamp: new Date()
    });
    // Show "Saved offline" message
  }
};
```

**When online:**
- Normal API call
- If fails, falls back to offline storage

---

## Use Case Customization

### Frontend Onboarding Form
- **Step 1:** Use case selection (lead gen, sales, job hunting, etc.)
- **Step 2:** Structured fields (industries, company sizes, job titles, geographic focus)
- **Step 3:** Free-form comments (what user wants, priorities, special requirements)

### Comment Processing
**Preference Analysis Agent extracts:**
- Additional industries/companies mentioned
- Custom criteria (e.g., "Series A or later", "remote-first culture")
- Value indicators (what makes contacts valuable)
- Special requirements (geographic, cultural, etc.)
- Exclusion criteria (what to avoid)

### How Agents Use Comments

**Categorization Agent:**
- Applies custom criteria from comments
- Groups contacts into P0/P1/P2 based on:
  - Match with user preferences (industry, company size, job title)
  - Custom criteria from comments (e.g., "Series A or later")
  - Value indicators (what makes contacts valuable to user)
  - Conversation quality and depth
- P0 = Highest match, P1 = Medium match, P2 = Lower match

**Summarization Agent:**
- Creates concise conversation summaries
- Emphasizes comment-relevant topics if applicable

---

## Orchestrator Agent - Multi-Agent Coordination

### How Agents Convey Their Skills

**Agent Registration (on startup):**
- Each agent registers itself in `agents` MongoDB collection
- Stores skills array: `["voice_processing", "entity_extraction", "summarization", "categorization"]`
- Stores capabilities: input types, output types, max context tokens
- Updates status: "idle", "busy", "error"
- Periodically updates status and current_task_id

**Example agent document:**
```json
{
  "agent_id": "extraction_agent_001",
  "agent_type": "extraction",
  "skills": ["entity_extraction", "nlp", "data_normalization"],
  "capabilities": {
    "input_types": ["text", "structured_data"],
    "output_types": ["person_profile", "extracted_entities"],
    "max_context_tokens": 4000
  },
  "status": "idle",
  "current_task_id": null
}
```

### Core Responsibilities

**1. Skill Discovery & Agent Registry**
- Queries `agents` collection to discover available agents
- Maintains real-time view of agent capabilities, status, and workload
- Uses MongoDB queries to filter agents by skills, status, capabilities

**2. Peer Identification for Sub-tasks**
- When task arrives, Orchestrator analyzes requirements
- Uses MongoDB queries on `agents` collection to find suitable peers:
  ```python
  # Example query
  agents = db.agents.find({
    "skills": {"$in": ["entity_extraction"]},
    "status": {"$in": ["idle", "active"]},
    "capabilities.output_types": "person_profile"
  })
  ```
- Filters by required skills, status, and capabilities
- Considers current workload (agents with fewer active tasks preferred)
- Selects best match based on skill overlap and availability
- Example: Task needs "entity_extraction" → finds Information Extraction Agent

**3. Context Sharing with Token Limits (MongoDB-organized)**
- Before assigning task, Orchestrator checks context size
- Uses Token Management Service to:
  - Count tokens in context
  - Compress if exceeds limits (using summarization)
  - Chunk large contexts into manageable pieces
  - Store full context in `contexts` MongoDB collection with token counts
  - Create reference IDs for large data
- Shares optimized context or reference IDs with receiving agent via `tasks` collection
- Logs all context sharing in `agent_communications` MongoDB collection:
  ```json
  {
    "from_agent_id": "extraction_agent",
    "to_agent_id": "summarization_agent",
    "context_refs": ["context_id_123"],
    "token_count": 3500,
    "compressed": true
  }
  ```
- Uses MongoDB to organize and oversee all contexts

**4. Task Assignment & Workflow Coordination**
- Creates tasks in `tasks` collection with:
  - Task type, requirements, input data
  - Context references (if large)
  - Priority and dependencies
- Assigns tasks to identified agents
- Monitors task completion
- Coordinates sequential and parallel workflows
- Handles errors and retries

**5. Multi-Agent Collaboration (MongoDB-coordinated)**
- Identifies when multiple agents need to collaborate
- Uses MongoDB `tasks` collection to coordinate:
  - Creates dependent tasks (task B depends on task A)
  - Links tasks via `context_refs` pointing to previous task outputs
  - Enables parallel processing by creating independent tasks
- Coordinates context sharing between agents via `contexts` collection
- Manages dependencies: Agent B reads Agent A's output from `tasks` collection
- Combines results from multiple agents stored in MongoDB
- All coordination happens through MongoDB collections, not direct agent-to-agent communication

### Orchestrator Decision-Making Process

```
1. Receive task/request
2. Analyze requirements → Identify needed skills
3. Query agents collection → Find agents with matching skills
4. Check agent availability → Filter by status: "idle"
5. Evaluate context size → Use Token Management if needed
6. Assign task → Update tasks collection, agent status
7. Monitor progress → Check task status
8. Coordinate next step → Identify next agent or parallel tasks
9. Combine results → Aggregate outputs from multiple agents
10. Complete workflow → Finalize and return results
```

### Agent Communication via Orchestrator

**Agents don't communicate directly** - Orchestrator facilitates:
- Agent A completes task → Notifies Orchestrator
- Orchestrator identifies Agent B needs Agent A's output
- Orchestrator manages context sharing (token limits)
- Orchestrator assigns task to Agent B with context
- Agent B processes and notifies Orchestrator
- Orchestrator coordinates next step

---

## Token Management (Utility Service)

**Token Management Service (used by Orchestrator):**
- Utility functions for token counting
- Context compression when needed
- Context chunking for large data
- Reference creation (store full context, share IDs)

Orchestrator Agent uses this service before sharing contexts between agents.

---

## Task Assignment Flow

1. **Task Creation:** API/Orchestrator creates task in `tasks` collection (status: "pending")
2. **Orchestrator Analysis:** Analyzes task, identifies required skills
3. **Peer Discovery:** Orchestrator queries `agents` collection for suitable agents
4. **Context Management:** Orchestrator checks token limits, compresses/chunks if needed
5. **Assignment:** Orchestrator updates task (assigned_agent_id, status: "assigned"), updates agent (status: "busy")
6. **Execution:** Agent processes, stores results in task output_data, updates status: "completed"
7. **Orchestration:** Orchestrator identifies next agent or parallel tasks, coordinates workflow
8. **Completion:** Agent status → "idle", Orchestrator continues workflow or completes

---

## Key Design Decisions

- **5 Core Agents:** Specialized agents + Orchestrator for coordination
- **MongoDB-based communication:** Centralized, persistent, queryable
- **Orchestrator-driven coordination:** Centralized decision-making for task assignment and agent communication
- **Skill-based peer discovery:** Agents advertise skills, Orchestrator identifies suitable peers
- **Token-aware context sharing:** Orchestrator manages context sharing within token limits
- **Priority Groups (P0/P1/P2):** Clear categorization output
- **Comment-driven personalization:** Agents adapt to user's natural language input

---

## Tech Stack

- **Backend:** Python (FastAPI)
- **Database:** MongoDB Atlas
- **AI:** OpenAI GPT-4/Claude, Whisper API, Vision API
- **OCR:** Tesseract/EasyOCR
- **APIs:** LinkedIn, Company databases

---

## MVP Implementation Priority

1. MongoDB Atlas setup + schema
2. Agent registry system (agents collection)
3. Token Management Service
4. Orchestrator Agent (core coordination logic)
5. Data Collection Agent
6. Information Extraction Agent
7. Basic Summarization Agent
8. Categorization Agent (groups into P0/P1/P2)
9. Onboarding service (comment analysis)
11. API endpoints (submit meeting, get grouped results)
12. **Offline support (frontend):**
    - IndexedDB setup for file storage
    - localStorage queue for pending meetings
    - Network detection
    - Sync service
    - Offline indicator UI
