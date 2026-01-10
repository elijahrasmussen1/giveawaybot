# Bot Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Discord Platform                        │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │  Admin User  │         │ Player Users │                 │
│  └──────┬───────┘         └──────┬───────┘                 │
│         │                         │                          │
└─────────┼─────────────────────────┼──────────────────────────┘
          │ &setnumber 42          │ Guess: 42
          │                         │
          ▼                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Discord Bot (index.js)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Event Handler: messageCreate                        │  │
│  │  - Checks prefix (&)                                 │  │
│  │  - Routes commands to command handler                │  │
│  │  - Checks for number guesses in game channel         │  │
│  └────────┬──────────────────────────┬──────────────────┘  │
│           │                           │                      │
│           ▼                           ▼                      │
│  ┌─────────────────┐       ┌──────────────────┐           │
│  │ Command Handler │       │  Guess Detector  │           │
│  │  - Loads from   │       │  - Compares to   │           │
│  │    commands/    │       │    target number │           │
│  └────────┬────────┘       └────────┬─────────┘           │
│           │                          │                      │
└───────────┼──────────────────────────┼──────────────────────┘
            │                          │
            ▼                          │
   ┌─────────────────┐                │
   │ setnumber.js    │                │
   │ - Validates     │                │
   │ - Checks perms  │                │
   │ - Updates state │                │
   └────────┬────────┘                │
            │                          │
            ▼                          │
   ┌─────────────────┐                │
   │   state.js      │◄───────────────┘
   │ - targetNumber  │
   │ - get/set/clear │
   └─────────────────┘
```

## Component Responsibilities

### index.js (Main Bot)
- Initialize Discord client with required intents
- Load commands dynamically from commands folder
- Handle message events
- Route commands to appropriate handlers
- Detect number guesses in designated channel
- Announce winners

### state.js (State Management)
- Store the target number
- Provide getter/setter functions
- Maintain game state across different modules
- No circular dependencies

### commands/setnumber.js
- Validate admin permissions
- Parse and validate number input
- Update game state
- Send confirmation to admin
- Announce game activation in game channel

### config.json
- Store bot prefix (`&`)
- Store game channel ID
- Centralized configuration

## Data Flow

### Setting a Number
```
Admin types: &setnumber 42
     ↓
index.js detects command
     ↓
Routes to setnumber.js
     ↓
Checks permissions ✓
     ↓
Validates number ✓
     ↓
state.setTargetNumber(42)
     ↓
Sends embed to admin (confirmation)
     ↓
Sends embed to game channel (announcement)
```

### Guessing Flow
```
Player types: 42
     ↓
index.js detects message in game channel
     ↓
Checks if game is active (targetNumber !== null) ✓
     ↓
Parses message as number
     ↓
Compares to state.getTargetNumber()
     ↓
Match found! ✓
     ↓
Sends winner announcement embed
     ↓
state.clearTargetNumber()
```

## Security Layers

1. **Authentication**: Bot token from .env
2. **Authorization**: Permission checks on admin commands
3. **Input Validation**: All user inputs validated
4. **State Isolation**: State managed in separate module
5. **No Logging of Secrets**: Sensitive data never logged

## Scalability Design

The modular architecture allows easy expansion:

```
commands/
├── setnumber.js      (✅ Implemented)
├── giveaway.js       (Future)
├── gamenight.js      (Future)
├── leaderboard.js    (Future)
└── help.js           (Future)
```

Each command is self-contained and follows the same pattern:
- Name and description
- execute(message, args, client) function
- Permission checks
- Input validation
- Professional embed responses

## Error Handling

```
Try-Catch Wrapper
       ↓
Command Execution
       ↓
   Error? ─── Yes ──→ Log error + Send error embed to user
       │
      No
       ↓
   Success!
```

## Performance Optimizations

1. **Channel Caching**: Check cache before fetching
2. **Event-Driven**: Only processes relevant messages
3. **Minimal State**: Only stores necessary data
4. **Efficient Routing**: Quick prefix check before processing

## Deployment Architecture

```
┌──────────────┐
│  Git Repo    │
└──────┬───────┘
       │
       ├──→ Local Dev (npm start)
       │
       ├──→ Heroku (Procfile + worker)
       │
       ├──→ Railway (Auto deploy)
       │
       └──→ VPS (PM2 + systemd)
```

All deployment options documented in DEPLOYMENT.md

---

This architecture ensures:
- ✅ Clean separation of concerns
- ✅ Easy to test and maintain
- ✅ Scalable for future features
- ✅ Secure by design
- ✅ Professional and reliable
