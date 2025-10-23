# Orchestration Graph Scheduler

A React TypeScript application for designing optimized educational lesson plans through activity orchestration. Build sequential timelines of learning activities across individual, team, and class organizational planes.

## Overview

The Orchestration Graph Scheduler helps educators create structured lesson plans by:
- Organizing activities across three organizational levels (Individual, Team, Class)
- Automatically recommending activities to fill learning gaps
- Visualizing lesson progression through state-space graphs
- Ensuring pedagogical constraints are met (time budgets, prerequisites, repetition limits)

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Installation

1. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Frontend Setup**
```bash
cd frontend
npm install
```

### Running the Application

1. **Start the Backend** (from `backend/` directory):
```bash
source venv/bin/activate
python app.py
```
The backend will start on `http://localhost:5000`

2. **Start the Frontend** (from `frontend/` directory):
```bash
npm start
```
The application will open in your browser at `http://localhost:3000`

## Using the Application

### Building a Lesson

1. **Drag and Drop**: Drag activities from the library panel (right side) onto the timeline
2. **Three Organizational Lanes**:
   - **Individual**: Activities students perform alone
   - **Team**: Collaborative team-based activities
   - **Class**: Whole-class instruction and activities

3. **Sequential Timeline**: Activities are positioned left-to-right by time. The x-axis represents lesson time in minutes.

### Automatic Recommendations

Click "Add Recommended" to automatically add the best activity for the largest learning gap. The system uses an efficiency algorithm to select activities that maximize learning progress per minute.

### Activity Information

Hover over any activity (in the library or timeline) to view:
- Activity description
- Duration and organizational plane
- Time range (for timeline activities)

### Changing Activity Placement

- **Move Between Lanes**: Drag an activity from one lane to another to change its organizational plane
- **Remove Activity**: Hover over an activity and click the × button

### Visualization

Click "Print" to generate a 2D state-space visualization showing:
- Start point (current knowledge level)
- Goal point (target knowledge level)
- Learning trajectory through activities
- Progress along fluency and depth dimensions

### Saving and Loading

- **Save**: Click "Save" to save your orchestration graph
- **Load**: Click "Load" to restore a previously saved orchestration

### Reset

Click "Reset" to clear the timeline and start fresh.

## Activity Library

The system includes 10 educational activity types:

- **TellTheClass**: Direct instruction to the entire class
- **DesirableDifficultyProblem**: Challenging problems for retention
- **PracticeMemory**: Memorization and recall exercises
- **PracticeApplication**: Practical problem-solving
- **PracticeAnalyse**: Analysis and breakdown of concepts
- **PracticeEvaluate**: Evaluation of ideas and solutions
- **PracticeCreate**: Creative synthesis demonstrating mastery
- **AdvancedOrganiser**: Overview to organize new information
- **Introduction**: Lesson introduction and topic presentation
- **ExplainClass**: Concept explanation with discussion

## Learning Model

The system models student understanding across two dimensions:
- **Fluency**: Ability to quickly recall and apply knowledge
- **Depth**: Understanding of underlying concepts and relationships

Activities move students through this 2D space from a starting knowledge level to a learning goal.

## Support

For issues or questions, please refer to the technical documentation (TECHNICAL.md) or the development history (DEVELOPMENT_LOG.md).
