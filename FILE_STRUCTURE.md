# File Structure

```
mongodb-hack-networking-assistant/
│
├── README.md
├── .gitignore
│
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── mongodb_config.py
│   │   └── agent_config.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   ├── schemas.py
│   │   └── indexes.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   │
│   │   ├── data_collection/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   ├── voice_processor.py
│   │   │   ├── image_processor.py
│   │   │   └── business_card_parser.py
│   │   │
│   │   ├── extraction/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   ├── entity_extractor.py
│   │   │   └── normalizer.py
│   │   │
│   │   ├── categorization/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   └── scorer.py
│   │   │
│   │   └── summarization/
│   │       ├── __init__.py
│   │       ├── agent.py
│   │       └── summarizer.py
│   │
│   └── orchestrator/
│       ├── __init__.py
│       ├── agent.py
│       ├── task_coordinator.py
│       └── peer_discovery.py
│
│   ├── services/
│   │   ├── __init__.py
│   │   ├── agent_registry.py
│   │   ├── task_queue.py
│   │   ├── context_manager.py
│   │   ├── preference_analysis.py
│   │   └── token_management.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── task.py
│   │   ├── context.py
│   │   ├── person.py
│   │   ├── meeting.py
│   │   └── user_preferences.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   ├── exceptions.py
│   │   ├── token_utils.py
│   │   └── helpers.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── meetings.py
│   │   │   ├── groups.py
│   │   │   ├── agents.py
│   │   │   └── onboarding.py
│   │   └── schemas/
│   │       ├── __init__.py
│   │       ├── request_schemas.py
│   │       └── response_schemas.py
│   │
│   ├── external/
│   │   ├── __init__.py
│   │   ├── openai_client.py
│   │   ├── whisper_client.py
│   │   ├── vision_client.py
│   │   └── linkedin_client.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── unit/
│   │   └── integration/
│   │
│   └── scripts/
│       ├── setup_database.py
│       └── start_agents.py
│
└── frontend/
    ├── package.json
    ├── .env
    ├── public/
    │   └── index.html
    │
    └── src/
        ├── App.js
        ├── index.js
        ├── components/
        │   ├── OnboardingForm.js
        │   ├── MeetingInput.js
        │   ├── GroupsView.js
        │   ├── PersonCard.js
        │   └── OfflineIndicator.js
        ├── services/
        │   ├── api.js
        │   ├── offlineStorage.js
        │   └── syncService.js
        ├── utils/
        │   ├── constants.js
        │   └── networkDetector.js
        └── hooks/
            └── useOffline.js
```
