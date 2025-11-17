# Technical Documentation: Orchestration Graph Scheduler

## Architecture Overview

The Orchestration Graph Scheduler is a full-stack web application with a Flask backend (Pure Python) and React TypeScript frontend. The system implements a greedy gap-filling algorithm for educational lesson planning.

### Technology Stack

**Backend:**
- Python 3.8+
- Flask (REST API server)
- Flask-CORS (Cross-Origin Resource Sharing)
- Matplotlib (State-space visualization)
- Pure Python implementation (no Qt dependencies)

**Frontend:**
- React 18
- TypeScript 4.9+
- Zustand (State management)
- React DnD (Drag-and-drop)
- CSS3 (Styling)

### Project Structure

```
pdb/
├── backend/
│   ├── app.py                      # Flask application & REST API
│   ├── visualizer.py               # State-space graph generation
│   ├── requirements.txt            # Python dependencies
│   ├── core/                       # Core business logic
│   │   ├── Activity_pure.py       # Activity templates
│   │   ├── ContextActivity_pure.py # Activity evaluation context
│   │   ├── Efficience_pure.py     # Efficiency scoring algorithms
│   │   ├── InstantiatedAct_pure.py # Activity instances
│   │   ├── Library_pure.py        # Activity library management
│   │   ├── OrchestrationGraph_pure.py # Main orchestration engine
│   │   └── pValues_pure.py        # Parametric values (state vectors)
│   └── inputData/
│       └── interpolation_2D_library.csv # Activity definitions
├── frontend/
│   ├── public/                     # Static assets
│   ├── src/
│   │   ├── App.tsx                # Main application component
│   │   ├── components/
│   │   │   ├── Library/           # Activity library panel
│   │   │   ├── Timeline/          # Timeline visualization
│   │   │   └── Toolbar/           # Toolbar controls
│   │   ├── services/
│   │   │   └── apiService.ts     # Backend API client
│   │   ├── store/
│   │   │   └── orchestrationStore.ts # Zustand state management
│   │   └── types/
│   │       └── domain.ts          # TypeScript type definitions
│   ├── package.json               # Node dependencies
│   └── tsconfig.json              # TypeScript configuration
└── README.md, TECHNICAL.md, DEVELOPMENT_LOG.md
```

---

## Backend Architecture

### Core Concepts

#### 1. Parametric Values (pVal)

**File:** `core/pValues_pure.py`

Represents multi-dimensional student understanding state as a tuple of floats, typically 2D: (fluency, depth).

```python
class pVal:
    v: tuple  # e.g., (0.5, 0.3)

    def distance_onlyForward(self, other) -> float:
        """Calculates distance only in dimensions where progress is needed"""
        som = 0
        for i in range(len(self.v)):
            if self.v[i] < other.v[i]:
                som += (self.v[i] - other.v[i]) ** 2
        return sqrt(som)
```

**Key Methods:**
- `needToReach(other)`: Component-wise maximum (satisfies prerequisites)
- `plus(effect)`: State progression after activity
- `distance_onlyForward(other)`: Forward-only Euclidean distance (used for gap calculation)
- `isPast(other)`: Check if current state >= prerequisite

#### 2. Activity Templates (ActivityData)

**File:** `core/Activity_pure.py`

Defines reusable activity templates loaded from CSV.

**Properties:**
- `pcond: pVal` - Prerequisite state (minimum knowledge to start)
- `peffect: InterPVal` - Time-interpolated effect (how much knowledge gained)
- `defT: int` - Default duration (minutes)
- `maxRepetition: int` - Maximum allowed repetitions
- `defPlane: int` - Default organizational plane (0=Individual, 1=Team, 2=Class)

**CSV Format:**
```
Name,p-condition,min p-effect,min time,max p-effect,max time,def time,max repetitions,def plane
PracticeMemory,(0.2;0.2),(0.2;0.0),10,(0.5;0.0),30,15,2,Indiv.
```

#### 3. Instantiated Activities (InstantiatedActData)

**File:** `core/InstantiatedAct_pure.py`

Represents a specific occurrence of an activity in the timeline.

**Properties:**
- `actData: ActivityData` - Reference to template
- `time: int` - Chosen duration
- `plane: int` - Chosen organizational plane
- `startsAfter: float` - Cumulative start time
- `pValStart: pVal` - State before activity
- `pValEnd: pVal` - State after activity

**State Calculation:**
```python
def adjust(self, newStartsAfter, newPValStart):
    self.startsAfter = newStartsAfter
    self.pValStart = newPValStart.needToReach(self.actData.pcond)
    effect = self.actData.peffect.get(self.time)
    self.pValEnd = self.pValStart.plus(effect)
```

#### 4. Orchestration Graph (OrchestrationGraphData)

**File:** `core/OrchestrationGraph_pure.py`

The main engine that manages the lesson plan as a sequence of instantiated activities.

**Core Data Structures:**
- `listOfFixedInstancedAct: List[InstantiatedActData]` - Ordered activity sequence
- `quantities: List[int]` - Track activity usage counts
- `hardGapsList: List[int]` - Positions with significant learning gaps
- `start: pVal` - Initial student knowledge
- `goal: pVal` - Target knowledge level
- `tBudget: int` - Time budget (minutes)

**Key Algorithms:**

##### Gap Evaluation

```python
def evaluate_gaps(self):
    gaps = []
    totalDistance = 0.0

    # Check gap before first activity
    if len(self.listOfFixedInstancedAct) > 0:
        distance = self.start.distance_onlyForward(
            self.listOfFixedInstancedAct[0].actData.pcond)
        if distance > THRESHOLD:
            gaps.append(0)
            totalDistance += distance

    # Check gaps between activities
    for i in range(len(self.listOfFixedInstancedAct) - 1):
        currentEnd = self.listOfFixedInstancedAct[i].pValEnd
        nextPrecond = self.listOfFixedInstancedAct[i + 1].actData.pcond
        distance = currentEnd.distance_onlyForward(nextPrecond)
        if distance > THRESHOLD:
            gaps.append(i + 1)
            totalDistance += distance

    # Check gap to goal
    if len(self.listOfFixedInstancedAct) > 0:
        lastEnd = self.listOfFixedInstancedAct[-1].pValEnd
        distance = lastEnd.distance_onlyForward(self.goal)
        if distance > THRESHOLD:
            gaps.append(len(self.listOfFixedInstancedAct))
            totalDistance += distance

    self.hardGapsList = gaps
    self.remainingGapsDistance = totalDistance
```

##### Activity Recommendation

```python
def evaluateFor(self, actIdx, position):
    actData = self.lib.getActData(actIdx)

    # Get current state at position
    if position == 0:
        currentState = self.start
    else:
        currentState = self.listOfFixedInstancedAct[position - 1].pValEnd

    # Get next prerequisite
    if position < len(self.listOfFixedInstancedAct):
        nextPrecond = self.listOfFixedInstancedAct[position].actData.pcond
    else:
        nextPrecond = self.goal

    # Calculate state after activity
    stateAfterPrereqs = currentState.needToReach(actData.pcond)
    effect = actData.peffect.default()
    stateAfterActivity = stateAfterPrereqs.plus(effect)

    # Calculate efficiency score
    distToNext = currentState.distance_onlyForward(nextPrecond)
    distToStart = currentState.distance_onlyForward(stateAfterPrereqs)
    distEndToNext = stateAfterActivity.distance_onlyForward(nextPrecond)

    score = getEff(
        fromStartToGoal=distToNext,
        fromStartToWouldStart=distToStart,
        fromWouldEndToGoal=distEndToNext,
        actTime=actData.defT,
        remTime=self.tBudget - self.totTime,
        totalRemDistance=self.remainingGapsDistance
    )

    return ContextActivity(actData, score=score, flags=flags)
```

#### 5. Efficiency Scoring

**File:** `core/Efficience_pure.py`

The core recommendation algorithm uses **distance removed per unit time**:

```python
def getEff(fromStartToGoal, fromStartToWouldStart, fromWouldEndToGoal,
           actTime, remTime, totalRemDistance):
    distRemoved = (fromStartToGoal - fromStartToWouldStart - fromWouldEndToGoal)
    return distRemoved / actTime  # Progress per minute
```

**Rationale:** Maximizes learning progress while respecting time constraints.

**Selection Priority:**
1. Must make progress (`distRemoved > 0`)
2. Respect constraints (not exhausted, not too long)
3. Highest efficiency score

##### Critical Bug Fix (2025-10-23)

The distance calculation was corrected to use `distance_onlyForward()` instead of `distance()`:

**Before (Incorrect):**
```python
distToNext = currentState.distance(nextPrecond)  # Wrong: counts backward dimensions
```

**After (Correct):**
```python
distToNext = currentState.distance_onlyForward(nextPrecond)  # Only forward progress
```

This ensures efficiency scores only consider dimensions where progress is needed.

#### 6. Visualization

**File:** `visualizer.py`

Generates 2D state-space graphs using Matplotlib:

```python
def generate_state_space_graph(graph_data):
    fig, ax = plt.subplots(1, figsize=(10, 10))
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.set_xlabel("fluency", fontsize=14)
    ax.set_ylabel("depth", fontsize=14)

    # Plot start (orange X) and goal (blue X)
    ax.scatter(start[0], start[1], marker='x', s=200, c='orange')
    ax.scatter(goal[0], goal[1], marker='x', s=200, c='blue')

    # Draw activity rectangles and transition arrows
    # ...

    # Return base64-encoded PNG
    return base64.b64encode(buf.getvalue()).decode('utf-8')
```

### REST API Endpoints

**Base URL:** `http://localhost:5000/api`

#### Graph State
- `GET /graph/state` - Get current orchestration state
- `POST /graph/reset` - Reset to empty graph

#### Activity Management
- `POST /graph/insert` - Insert activity at position
  - Body: `{actIdx, position, plane?, time?}`
- `POST /graph/remove` - Remove activity
  - Body: `{position}`
- `POST /graph/change-plane` - Change activity plane
  - Body: `{position, plane}`

#### Recommendations
- `POST /graph/gap/focus` - Set focus on gap
  - Body: `{gapIndex}`
- `POST /graph/gap/recommendations` - Get recommendations for gap
  - Body: `{gapIndex}`
- `POST /graph/auto-add` - Automatically add best activity to worst gap

#### Persistence
- `POST /graph/save` - Save orchestration
  - Body: `{filename?}`
- `POST /graph/load` - Load orchestration
  - Body: `{filename}`
- `GET /graph/saved-files` - List saved files

#### Visualization
- `GET /graph/visualize` - Generate state-space PNG
  - Returns: `{success, image: base64, format: "png"}`

---

## Frontend Architecture

### State Management (Zustand)

**File:** `store/orchestrationStore.ts`

Centralized state using Zustand:

```typescript
interface OrchestrationStore {
  // State
  graphState: OrchestrationGraphState | null;
  isLoading: boolean;
  error: string | null;
  selectedGap: number | null;
  showRecommendations: boolean;

  // Actions
  initialize: () => Promise<void>;
  insertActivity: (actIdx: number, position: number, plane: number) => Promise<void>;
  removeActivity: (position: number) => Promise<void>;
  changePlane: (position: number, plane: number) => Promise<void>;
  autoAdd: () => Promise<void>;
  resetGraph: () => Promise<void>;
  saveGraph: (filename?: string) => Promise<string>;
  loadGraph: (filename: string) => Promise<void>;
}
```

**State Flow:**
1. User interaction triggers action
2. Action calls API service
3. Backend processes request
4. Response updates Zustand store
5. React components re-render

### Component Hierarchy

```
App
├── Header (connection status)
├── ToolbarPanel
│   ├── Reset button
│   ├── Load/Save dialogs
│   ├── Print/Visualize
│   └── Add Recommended
├── Timeline Area
│   └── OrchestrationTimeline
│       ├── Stats Panel (time/goal status)
│       ├── Lane Labels
│       ├── TimelineLane (×3)
│       │   ├── Time grid
│       │   ├── ActivityBlock (drag source)
│       │   └── DropZone (drop target)
│       └── Activity Info Panel
└── Library Area
    └── ActivityLibraryPanel
        └── DraggableActivity (×10)
```

### Drag-and-Drop System

**Library:** React DnD with HTML5Backend

**Item Types:**
1. `LIBRARY_ACTIVITY` - Activities from library to timeline
2. `TIMELINE_ACTIVITY` - Activities within/between lanes

**Drop Zones:**
- **DropZone Component**: Positioned between activities, accepts LIBRARY_ACTIVITY
- **TimelineLane Component**: Entire lane surface, accepts TIMELINE_ACTIVITY (for plane switching)

**Flow:**
```
User drags activity from library
  → useDrag hook creates drag source
  → DropZone detects hover (visual feedback)
  → User drops
  → onDrop callback fires
  → insertActivity action called
  → Backend inserts and recalculates
  → State updates, UI re-renders
```

### Timeline Rendering

**Key Algorithm:** Activities positioned by `startsAfter` time (sequential, no overlap).

```typescript
const leftPosition = activity.startsAfter * pixelsPerMinute;  // X position
const width = activity.time * pixelsPerMinute;                // Width
```

**Lane Structure:**
- 3 horizontal lanes (Individual, Team, Class)
- Time axis horizontal (left-to-right)
- Grid lines every 10 minutes
- Activities absolutely positioned within lanes

### Type System

**File:** `types/domain.ts`

```typescript
interface PValue {
  v: number[];  // [fluency, depth]
}

interface ActivityData {
  idx: number;
  name: string;
  description: string;
  pcond: PValue;
  peffect: InterPValue;
  defT: number;
  maxRepetition: number;
  defPlane: number;
}

interface InstantiatedActivity {
  activityIdx: number;
  activityName: string;
  activityDescription: string;
  time: number;
  plane: number;
  startsAfter: number;
  endsAfter: number;
  pValStart: PValue;
  pValEnd: PValue;
}

interface OrchestrationGraphState {
  activities: InstantiatedActivity[];
  tBudget: number;
  totTime: number;
  hardGapsCount: number;
  hardGapsList: number[];
  goalReached: boolean;
  start: PValue;
  goal: PValue;
  reached: PValue;
}
```

---

## Key Features Implementation

### 1. Activity Hover Information

**Components:** `App.tsx`, `OrchestrationTimeline.tsx`, `ActivityLibraryPanel.tsx`

State lifted to App level to share hover state:
```typescript
const [hoveredActivity, setHoveredActivity] = useState<{
  name: string;
  description: string;
  time: number;
  plane: number;
  startsAfter?: number;
  endsAfter?: number;
} | null>(null);
```

Info panel positioned directly under timeline lanes.

### 2. Plane Switching (Drag-and-Drop)

**Backend Endpoint:** `POST /api/graph/change-plane`

Simply updates `inst.plane` without repositioning:
```python
inst = current_graph.listOfFixedInstancedAct[position]
inst.plane = new_plane
```

**Frontend:** TimelineLane uses `useDrop` to accept dragged activities.

### 3. Recommendation Algorithm

**Process:**
1. Evaluate all gaps (distance_onlyForward)
2. Sort by distance (largest first)
3. For worst gap, evaluate all activities
4. Score using `distRemoved / actTime`
5. Select activity with highest score
6. Insert activity
7. Recalculate state progression

### 4. State-Space Visualization

**Matplotlib Generation:**
- 2D plot: x=fluency, y=depth
- Orange X: start point
- Blue X: goal point
- Rectangles: activity effects
- Arrows: state transitions
- Base64-encoded PNG returned to frontend
- Displayed in modal (not popup window)

---


## Configuration

### Backend (`backend/core/pValues_pure.py`)
```python
THRESHOLD = 0.05  # Gap detection threshold
```

### Frontend (`frontend/src/components/Timeline/OrchestrationTimeline.tsx`)
```typescript
const pixelsPerMinute = 6;       // Timeline scaling
const minTimelineWidth = 1200;   // Minimum width
```

---

## Dependencies

### Backend (`requirements.txt`)
```
Flask==3.0.0
Flask-CORS==4.0.0
matplotlib==3.8.0
```

### Frontend (`package.json`)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-dnd": "^16.0.1",
    "react-dnd-html5-backend": "^16.0.1",
    "zustand": "^4.4.0",
    "axios": "^1.6.0",
    "typescript": "^4.9.5"
  }
}
```

---

## Error Handling

### Backend
- Validation errors → 400 Bad Request
- Graph not initialized → 400
- File operations → Try/catch with error messages

### Frontend
- API errors caught in Zustand actions
- Error state displayed in toast (if connected) or error screen (if disconnected)
- User-friendly alerts for operation failures

---

## Testing

### Manual Testing Checklist
- [ ] Drag activity from library to timeline
- [ ] Remove activity from timeline
- [ ] Drag activity between lanes (plane switching)
- [ ] Click "Add Recommended" (check gap filling)
- [ ] Hover over activities (check info panel)
- [ ] Save orchestration
- [ ] Load orchestration
- [ ] Print visualization
- [ ] Reset graph

### Backend Testing
```bash
python -m pytest tests/
```

### Frontend Testing
```bash
npm test
```

---

## References

- Original Qt/QML implementation: https://github.com/Katokoda/OG_QML
- Flask documentation: https://flask.palletsprojects.com/
- React documentation: https://react.dev/
- Zustand documentation: https://github.com/pmndrs/zustand
- React DnD documentation: https://react-dnd.github.io/react-dnd/
