# ToVIC Vision & Architecture

## 1. Core Concept (One Sentence)
**Strategic simulation platform where each Discord guild configures a custom world via web editor, plays primarily through Discord bot, with a Python engine as the absolute authority for all game state changes.**

## 2. What Is ToVIC?

### Short Definition
- **Type**: Guild-based strategy game simulator (Victoria II / HOI4 style)
- **Primary Interface**: Discord bot (where players play)
- **Configuration Interface**: Web UI (where editor builds world)
- **Authority**: Python engine (where rules are enforced)
- **Storage**: SQLite database (persistence layer)

### The Dual Architecture
```
CONFIGURATION PHASE (Draft)
    Editor → Web UI → Customize Provinces, Resources, Techs, Buildings, etc.
    ↓
GAMEPLAY PHASE (Running)
    Players → Discord Bot → Play (research, move armies, diplomacy)
    Spectators → Web UI → Public view
```

## 3. The Three Client Types

### 1. **Web UI** (Editor + Viewer)
**Purpose**: Build worlds + spectate games

#### In Draft State
- **Only the editor role** can access `/editor`
- Creates from scratch OR picks template (Victoria2, HOI4)
- Fully editable: Provinces (shape, terrain, resource), Resources, Terrains, Techs, Unit Types, Buildings, Scenarios
- **Provinces are editable in shape**: Draw polygons, adjust borders, assign properties
- **Map can be an image**: Upload background image, auto-slice into provinces or manual mapping
- **Validation** before publish: Check referential integrity
- **Publish**: Locks world (draft → ready)

#### During Gameplay (Ready/Running)
- **All roles** can access `/game/{guild_id}`
- **Guild Admin**: Full state view, pause/resume controls, can start/stop game
- **Players**: Own country view (money, tech, armies, diplomacy)
- **Observers**: Spectator mode - sees world generically
  - YES: Terrain types, resource distribution, wars (who's fighting), population aggregates, country colors, general map state
  - NO: Specific troop counts, fort levels, detailed diplomatic secrets, private stockpiles
  - Like watching a live match without inside knowledge
- **Real-time updates** via WebSocket

#### Discovery
- `/worlds` - List public games
- Anyone can see active guilds' worlds if public

### 2. **Discord Bot** (Gameplay Interface)
**Purpose**: Players issue commands during game

#### Commands (Only when world is running/paused)
- `/research {tech_id}` - Queue tech
- `/build {building} {province}` - Construction order
- `/army-move {army_id} {to_province}` - Army movement
- `/diplomacy {action} {target_country}` - War/peace/trade
- `/game info` - Current world status
- `/country status` - Own country status
- `/armies` - List own armies

#### Bot's Job
1. Format command from Discord
2. Get user ID → look up country assignment
3. Call API: `POST /api/v1/guilds/{guild_id}/commands`
4. Engine validates & executes
5. Announce result to Discord

#### The Shareable Link
- When editor publishes world (draft → ready → running)
- Bot generates: `https://tovic.example.com/join/{guild_id}/{token}`
- **Link is public**: Anyone can click it
- Takes to `/game/{guild_id}` in web
- New players see world, can request to join (awaiting guild_admin approval)
- Once assigned country, can use bot commands

### 3. **Python Engine** (The Authority)
**Purpose**: Validate rules, execute decisions, emit events

#### Responsibilities
- ✅ Validate every action (is it legal?)
- ✅ Execute if valid (modify state)
- ✅ Emit event (broadcast what happened)
- ✅ Persist result (write to DB via API)
- ✅ Make each tick reproducible (deterministic)

#### What It Does NOT Do
- ❌ Accept direct modifications
- ❌ Trust client inputs
- ❌ Write to database directly (routes through API)
- ❌ Expose internals to clients

## 4. The Golden Rule
### "Client Requests, Engine Decides"

```
Web sends: "Add resource coal to province 5"
  ↓
API validates authorization (is editor? is draft mode?)
  ↓
Engine receives: "Add resource with ID 'coal' to province 5"
  ↓
Engine checks: Does coal resource exist? Is province valid?
  ↓
Engine decides: YES → Modify world definition, emit event, write to DB
              NO → Reject with reason, return error to web
  ↓
Web shows: ✅ or ❌
```

## 5. World States (Lifecycle)

```
1. DRAFT
   - Editing mode
   - Only editor role can modify world definitions
   - State: definition tables (provinces, resources, techs) are mutable
   - Game: No gameplay possible
   - Web editors: Only editor can view/edit
   - Bot: Cannot issue game commands
   
2. READY
   - Validated
   - Definitions locked permanently (no more editing EVER)
   - Waiting for guild_admin to start game
   - Web viewers: All roles can view (no edit mode)
   - Bot: Cannot issue commands yet
   
3. RUNNING / PAUSED
   - Gameplay active
   - Definitions frozen (read-only forever)
   - Players issue commands via bot/web
   - Engine processes ticks
   - State evolves (provinces change owner, countries research, etc.)
   - **No editing allowed** (world configuration is locked)
   
4. FINISHED
   - Game ended (victor declared or timeout)
   - Definitions & state frozen
   - Visible for replay/stats
   - No more commands processed
   
5. ARCHIVED
   - Moved to history
   - No longer appears in active list
   - Available for full replay (from snapshot)
```

## 6. User Roles & Permissions

| Role | Can Edit World | Can Play | Can See Full Map | Can Access Game | Notes |
|------|---|---|---|---|---|
| **superadmin** | Yes | Yes | Yes | Yes | Platform owner, all guilds |
| **guild_admin** | No | Yes | Yes | Yes | Discord server owner, starts game, assigns roles |
| **editor** | Yes | Maybe | Yes | Yes (after) | Designated world builder (only 1 per guild, only in draft) |
| **player** | No | Yes | Own country | Yes | Assigned by guild_admin, can issue game commands |
| **observer** | No | No | Partial* | Yes | Assigned by guild_admin, spectator mode only |

*Observer: Sees terrain, resources, wars, population. NOT troops, forts, secret data.

## 7. Data Models

### Definitions (Static, per Guild)
- **Provinces**: ID, name, shape (polygon), terrain, resource, buildings
- **Resources**: ID, type, price, icon
- **Terrains**: ID, supply limit, defense bonus
- **Technologies**: ID, branch, requirements, effects
- **Unit Types**: ID, attack, defense, cost
- **Buildings**: Factory, fort, farm, infrastructure
- **Scenarios**: Initial country states, armies, distributions

### State (Mutable, Live)
- **Game State**: Current tick, world_state
- **Province State**: Owner, population, fort_level
- **Country State**: Money, population, stockpile, relations
- **Armies**: Location, units, morale, organization

### Tables (Database)
- **Per-guild definitions**: `guild_provinces`, `guild_resources`, `guild_techs`, etc.
- **Live state**: `game_province_states`, `game_country_states`
- **Game metadata**: `guilds` (with world_state), `guild_players` (with roles)
- **Audit**: `command_log`, `game_events`

## 8. Customization Scope

### Everything Is Customizable
- **Provinces**: Create custom map, define shapes
  - Can upload image and auto-slice or manual mapping
  - Can edit shape (polygon) in editor
- **Resources**: Define any resource (not just "coal", "iron" — add custom ones)
- **Terrains**: Custom terrain types with custom defense/supply bonuses
- **Technologies**: Build entire tech tree from scratch
- **Unit Types**: Create custom military units
- **Buildings**: Define factory, fort, farm, infrastructure, custom buildings
- **Scenarios**: Set initial state (which countries exist, armies, distributions)
- **Map**: Visual representation (image-based or procedural)

### OR Use Templates
- Pick Victoria2 template → Get pre-built world (1836 provinces, techs, etc.)
- Pick HOI4 template → Get different world (1939 setup)
- Customize from template (change a tech, add province, etc.)

## 9. The Playflow

### Before Game Starts
```
1. Guild admin creates new game (discord → bot command)
2. Editor opens web → `/editor`
3. Picks template or starts blank
4. Builds world: Draws provinces, defines res (definitions locked FOREVER)
7. Guild admin clicks "Start Game" → Ready → Running (engine begins)
8. Bot generates join link for this guild
9. Initial players assigned to countries (world started with these players)
10. Game begins, **no editing possible**, **hot-join not available at start**
```

**Note on Hot-Join**: Can be added later as optional feature (guild_admin toggles), but for MVP, players list is fixed at game start. Implementation TBD if enabled.Players click link → See world in web
10. Guild admin assigns countries to players
```

### During Gameplay
```
1. Player in Discord: /research coal_power
2. Bot checks: Is user assigned a country? Is world running?
3. API call: POST /commands {command:"research", country:"ENG", tech:"coal_power"}
4. Engine: Validates (does tech exist? did player start with enough points?)
5. Engine: YES → Deduct points, queue research, schedule completion tick
6. Engine: Event emission → "United Kingdom researching Coal Power"
7. Bot announces: 🔬 **TECH RESEARCH** | United Kingdom (ETA: 50 ticks)
8. Web updates real-time (WebSocket): Progress bar updates
9. At completion tick: Engine emits event → Bot announces → Web updates
```

### During Spectating
```
1. Enters Spectator Mode
4. Sees: Terrain map, resource distribution, wars (who's warring), 
         population numbers per country, overall state
5. Does NOT see: Troop counts, fort detail, secret diplomacy
6. Live updates via WebSocket (like watching 24/7 sports broadcast)
7. Cannot command, cannot see strategic military secrets
5. Sees events log (wars, techs, important events)
6. Cannot command, cannot see strategic data
```

## 10. Architecture Diagram

```
PLAYER INPUT
  ↓
Web Editor (Draft)    OR    Discord Bot (Game)    OR    Web Viewer (Spectate)
  ↓                            ↓                            ↓
API Layer (Validation)   API Layer (Validation)    API Layer (Validation)
  ↓                            ↓                            ↓
───────────────────────────────────────────────────────────────
                    PYTHON ENGINE (Authority)
                    - Validate rules
                    - Execute changes
                    - Emit events
                    - Make reproducible
───────────────────────────────────────────────────────────────
  ↓
SQLite Database
  - Guild configs (world_state, editor, etc.)
  - Definitions (provinces, resources, techs, customs per guild)
  - Live state (provinces, countries, armies, current values)
  - Logs (commands, events, audit trail)
  ↓
STATE PERSISTENCE
  
REAL-TIME UPDATES
  ↓
WebSocket broadcast (tick completed, war declared, tech researched)
  ↓
Web updates + Bot announces
```

## 11. Development Rules (Golden Rules)

1. **All logic in engine**: No client-side validation of game rules
2. **No client writes DB**: All persistence through engine
3. **Every action = validatable order**: Client asks, engine checks
4. **Separate definitions from state**: Provinces (what exists) ≠ ProvinceState (current owner)
5. **Reproducible ticks**: Each tick deterministic, same seed = same result
6. **LoSnapshots & Replay System

### Snapshot Strategy
- Engine saves **full state snapshots** at periodic intervals (every N ticks or every game day/month/year)
- Each snapshot includes:
  - World definition snapshot (provinces, resources, techs — all static once game starts)
  - Current game state (all provinces, countries, armies, relations at that tick)
  - Tick number & game date
  - Event log up to that point
  - Template info (for world archival)

### Replay File Format
- **Single file per finished guild game**: `{guild_id}_{world_name}_{end_date}.tovic`
- Contains:
  - Initial world definition (from READY state)
  - All snapshots (every N ticks)
  - Command log (every command issued)
  - Event log (outcome of every command)
  - Final state & victor info
  - Metadata (players, duration, statistics)
  
### Replay Capability
- Viewers can load `.tovic` file and:
  - Play forward tick-by-tick
  - Jump to any snapshot instant
  - Filter events (show only wars, show only techs, etc.)
  - Analyze player decisions in hindsight
  - Export statistics

### Database Persistence
- Live game snapshots stored in `game_snapshots` table (for fast recovery if engine crashes)
- Final replay file exported to storage (S3 or local file) when game finishes
- Player can download `/game/{guild_id}/replay.tovic` after game endse, DB — no shortcuts |
| Starting too big | MVP scope: provinces, resources, techs, basic economy |
| Bad order flow | Clear request → validate → execute → persist pipeline |
| Ambiguous authority | Engine ALWAYS has final say, not clients |
| Lost context | Every module documented before changes |

## 13. Success Criteria (MVP)

✅ **Players can**:
- Click join link & see their guild's world
- Issue `/research`, `/build`, `/move-army` commands via bot
- See results update in real-time on web

✅ **Editors can**:
- Build custom world (provinces, resources, techs, units)
- Upload custom map image
- Adjust anything before publishing

**ANSWERED:**
- ✅ Observer visibility: See terrain, resources, wars, population — like spectator mode
- ✅ Edit after ready: NO, definitions locked forever once game starts
- ✅ Initial player list: Fixed at game start
- ✅ Max 1 editor: Yes, enforced at app level
- ✅ Multi-guild: Yes, same person can have different roles in different guilds
- ✅ World archive: Snapshot file exportable for replay after game finishes
- ✅ **Snapshot interval**: Every game day (~365 snapshots/year) = balanced file size + sufficient granularity for replay
- ✅ **Hot-join implementation**: YES, but ONLY for vassal nations (freed vassals only). New players can take over liberated nations or request new role if game allows dynamically adding nations
- ✅ **Max game duration**: NO timeout. Games run until guild_admin manually ends them (infinite duration possible)
- ✅ **Victory condition**: HYBRID. Automatic when only 1 nation remains undefeated, OR guild_admin can manually declare end
- ✅ **Player role changes mid-game**: YES, guild_admin can demote PLAYER→OBSERVER anytime. SPECIAL RULE: If a country becomes empty (player leaves), game cannot resume tick processing until someone new is assigned that country

**IMPLICATIONS:**

### Snapshot System Impact
- **Every game day means ~365 snapshots per year** of game time
- **Replay granularity**: Players can jump to any day in history (fine-grained analysis)
- **File size**: Manageable (~50-100 MB per full year, depending on world size)
- **Engine responsibility**: Mark current game date based on ticks. Define tick→date conversion (e.g., 1 tick = 1 day, or 10 ticks = 1 day)
- **Database**: Snapshot trigger when game_date increments (not every tick)

### Hot-Join (Vassal Liberation) Impact
- **When vassal is freed**: Becomes an available nation for hot-join
- **Hot-join player**: Takes over the vassal nation at that moment
- **Implementation**: 
  - Engine tracks "vassal_freed_on_tick"
  - API exposes `GET /api/v1/guilds/{guild_id}/available-nations` 
  - Web shows "Available Nations to Join" if game is running & player clicks join link late
  - Bot can announce: "⚔️ **VASSAL FREED** - {nation} is now available for join!"
- **No new nations spawned**: Only liberated vassals can be joined

### Game Duration Impact
- **No automatic timeout**: Games persist indefinitely (guild_admin must end manually)
- **Implication for DB**: Snapshots accumulate over time (months/years of gameplay = many snapshots)
- **Archive strategy**: When guild_admin ends game, transition to FINISHED, then allow ARCHIVE later
- **Storage**: Consider cleanup policy for very old snapshots (keep most recent 100 or compress)

### Victory Condition Impact (Auto✅ + Manual✅)
- **Automatic victory**: Engine emits "victory_reached" event when `alive_nations.count == 1`
  - API notifies guild_admin (optional auto-finish, or wait for confirmation)
  - Web shows banner: "🏆 {nation} has won! Game can be ended by admin."
  - Bot announces: "🏆 **VICTORY** {nation} stands alone!"
- **Manual end**: Guild_admin can always click "End Game" button to force FINISHED state
  - Gets final stats/victor selection screen
- **State transition**: RUNNING → FINISHED (snapshot taken at final state)

### Player Role Change Impact (YES, with Empty-Nation Rule)
- **Mid-game demotion**: Guild_admin can demote PLAYER→OBSERVER in `/game/{guild_id}/settings/players`
  - Web UI shows warning: "This player will lose command access"
  - Player becomes observer immediately (can still view, can't command)
  - Country assignment stays the same (will be orphaned if was only player for that nation)
- **Special rule - Empty nation recovery**:
  - **If a nation has no PLAYER assigned** (after player demoted/left):
    - Engine **halts tick processing** (game enters "PAUSED" state automatically)
    - Bot announces: "⚠️ **GAME PAUSED** - {nation} has no commander. Guild admin must reassign!"
    - Guild_admin must reassign a new PLAYER to that nation before game resumes
    - Once reassigned → Game resumes automatically (ticks resume)
  - **Implication for API**: 
    - `PUT /api/v1/guilds/{guild_id}/players/{user_id}/role` triggers validation
    - If removing last PLAYER from a nation → Pause game
    - `PUT /api/v1/guilds/{guild_id}/players/{user_id}/country` triggers auto-resume if paused
  - **Implication for Engine**: 
    - After each tick, check: Does every active nation have ≥1 PLAYER assigned?
    - If not → Emit "nations_need_players" event → API pauses game

## How This Changes the Agents

### Discord Bot
- **New responsibility**: Monitor "nations_need_players" WebSocket event
  - Announce when a nation is leadership-less
  - Notify guild_admin to reassign
- **Hot-join feature**: Already announced via "VASSAL FREED" event (no new code needed, just existing event broadcast)
- **Victory detection**: Listen for "victory_reached" event, announce winners

### Web Dashboard
- **Settings/Players page**: Add warning when demoting to observer ("Country will be orphaned")
- **Game status**: Show "⏸️ PAUSED (MISSING COMMANDER)" if a nation is empty
- **Country reassignment**: Auto-trigger game resume after assignment
- **Discovery in Settings**: Show list of available nations for reassignment

### FastAPI
- **New validation endpoint**:
  ```
  PUT /api/v1/guilds/{guild_id}/players/{user_id}/role
    - If removing last PLAYER from nation → Call Engine.pause_game()
    - Return 200 with warning
  ```
- **Auto-resume logic**:
  ```
  PUT /api/v1/guilds/{guild_id}/players/{user_id}/country
    - If game is PAUSED (due to missing commander) → Call Engine.resume_game()
    - Return 200 OK
  ```
- **Available nations endpoint**:
  ```
  GET /api/v1/guilds/{guild_id}/available-nations
    - Return list of freed vassals (or unassigned home nations)
    - For hot-join discovery
  ```

### Engine
- **New check each tick**:
  ```python
  def process_tick():
      # ... normal tick logic ...
      
      # Check: Does every nation have a PLAYER assigned?
      orphaned = [nation for nation in active_nations 
                  if not get_player_for_nation(nation)]
      if orphaned:
          emit("nations_need_players", {"orphaned_nations": orphaned})
          return False  # Don't advance tick, stay paused
      return True  # Tick succeeded, advance
  ```

- **Victory check each tick**:
  ```python
  def check_victory():
      if alive_nations == 1:
          emit("victory_reached", {"winner": last_nation})
  ```
- Guild definitions (custom per guild)
- Live state (provinces, countries)
- Audit trail (commands, events)

---

## How I Understand This

1. **This is NOT a generic game platform** — it's a Discord-guild-first simulator
2. **Web builds worlds, bot plays them** — clear separation of concerns
3. **Engine is law** — all validation, all decisions happen there
4. **Customization is core** — players build their own worlds, not locked to templates
5. **Privacy matters** — observers see public, players see strategic, admins see all
6. **One link per guild** — simple social mechanic for inviting players
7. **Simple → Scale** — start with basic mechanics, add complexity later

---

## Questions I'd Ask to Double-Check

- ❓ Is the observer visibility correct? (No troops, forts, diplomacy details?)
- ❓ Should guild_admin be able to edit world after it's ready, or locked forever?
- ❓ Can players change roles mid-game, or assigned once?
- ❓ Max 1 editor per guild — enforced at database/app level?
- ❓ When world finishes, auto-archive or manual?
- ❓ Can same person run multiple guilds?

