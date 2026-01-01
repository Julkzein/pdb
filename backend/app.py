# -*- coding: utf-8 -*-
"""
Flask REST API for Orchestration Graph Engine
Uses pure Python core modules (no Qt dependencies)
"""

import os
import sys
from datetime import datetime
from flask import Flask, jsonify, request  # type: ignore
from flask_cors import CORS  # type: ignore
from dotenv import load_dotenv  # type: ignore

# Load environment variables from .env file
load_dotenv()

# Add core directory to path
core_dir = os.path.join(os.path.dirname(__file__), 'core')
if core_dir not in sys.path:
    sys.path.insert(0, core_dir)

# Import pure Python modules
from pValues_pure import pVal  # type: ignore
from Activity_pure import Library  # type: ignore
from OrchestrationGraph_pure import OrchestrationGraphData  # type: ignore
from visualizer import generate_state_space_graph  # type: ignore
from llm_service import create_llm_service  # type: ignore

# Create Flask app
app = Flask(__name__)
CORS(app, origins="*")  # Allow all origins for development

# Global state
library = None
current_graph = None
llm_service = None

# Configuration
DEFAULT_TIME_BUDGET = 120
DEFAULT_START = (0.0, 0.0)
DEFAULT_GOAL = (0.9, 0.9)


# ==================== INITIALIZATION ==================== #

def initialize_library():
    """Load activity library from CSV"""
    global library

    csv_path = os.path.join(os.path.dirname(__file__), 'inputData', 'interpolation_2D_library.csv')

    if not os.path.exists(csv_path):
        print(f"ERROR: CSV not found at {csv_path}")
        return False

    try:
        library = Library(csv_path)
        print(f"Loaded {library.getLength()} activities")
        return True
    except Exception as e:
        print(f"Error loading library: {e}")
        return False


def initialize_graph():
    """Create a new orchestration graph"""
    global current_graph

    if library is None:
        print("Cannot initialize graph: library not loaded")
        return False

    try:
        start = pVal(DEFAULT_START)
        goal = pVal(DEFAULT_GOAL)
        current_graph = OrchestrationGraphData(library, DEFAULT_TIME_BUDGET, start, goal)
        print(f"Created new orchestration graph")
        return True
    except Exception as e:
        print(f"Error initializing graph: {e}")
        return False


# Initialize on startup
initialize_library()
initialize_graph()

# Initialize LLM service (will be None if no API key)
try:
    llm_service = create_llm_service(library)
    if llm_service:
        print("✓ LLM service initialized with DeepSeek API (super cheap!)")
    else:
        print("⚠ LLM service not available (no DEEPSEEK_API_KEY configured)")
except Exception as e:
    print(f"⚠ LLM service initialization failed: {e}")
    llm_service = None


# ==================== BASIC ENDPOINTS ==================== #

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Backend is running with pure Python orchestration engine",
        "library_loaded": library is not None,
        "library_size": library.getLength() if library else 0,
        "graph_initialized": current_graph is not None
    })


@app.route('/api/activities', methods=['GET'])
def get_activities():
    """Get all activities from library"""
    if library is None:
        return jsonify({"error": "Library not loaded"}), 500

    activities = []
    for act in library.listeActData():
        act_dict = act.to_dict()
        # Add extra fields not in to_dict()
        act_dict['duration'] = act.defT
        act_dict['minTime'] = act.minT
        act_dict['maxTime'] = act.maxT
        act_dict['planeName'] = act.planeToString(act.defPlane)
        act_dict['planeDescription'] = act.planeDescription(act.defPlane)
        activities.append(act_dict)

    return jsonify(activities)


# ==================== GRAPH STATE ENDPOINTS ==================== #

@app.route('/api/graph/state', methods=['GET'])
def get_graph_state():
    """Get complete orchestration graph state"""
    if current_graph is None:
        return jsonify({"error": "Graph not initialized"}), 400

    return jsonify(current_graph.to_dict())


@app.route('/api/graph/reset', methods=['POST'])
def reset_graph():
    """Reset graph to empty state"""
    if current_graph is None:
        return jsonify({"error": "Graph not initialized"}), 400

    current_graph.reset()

    return jsonify({
        "success": True,
        "message": "Graph reset",
        "state": current_graph.to_dict()
    })


# ==================== ACTIVITY MANIPULATION ENDPOINTS ==================== #

@app.route('/api/graph/insert', methods=['POST'])
def insert_activity():
    """
    Insert an activity at a specific position

    Body:
        actIdx: activity index in library
        position: insertion position (0 = before first)
        plane: optional plane (0=Indiv, 1=Team, 2=Class)
        time: optional custom duration
    """
    if current_graph is None:
        return jsonify({"error": "Graph not initialized"}), 400

    data = request.get_json()

    actIdx = data.get('actIdx')
    position = data.get('position', 0)
    plane = data.get('plane')  # None = use default
    time = data.get('time')  # None = use default

    if actIdx is None:
        return jsonify({"error": "actIdx required"}), 400

    success = current_graph.insert(actIdx, position, plane, time)

    if success:
        return jsonify({
            "success": True,
            "message": f"Inserted activity at position {position}",
            "state": current_graph.to_dict()
        })
    else:
        return jsonify({"error": "Failed to insert activity"}), 400


@app.route('/api/graph/remove', methods=['POST'])
def remove_activity():
    """
    Remove activity at position

    Body:
        position: position to remove
    """
    if current_graph is None:
        return jsonify({"error": "Graph not initialized"}), 400

    data = request.get_json()
    position = data.get('position')

    if position is None:
        return jsonify({"error": "position required"}), 400

    success = current_graph.remove(position)

    if success:
        return jsonify({
            "success": True,
            "message": f"Removed activity at position {position}",
            "state": current_graph.to_dict()
        })
    else:
        return jsonify({"error": "Failed to remove activity"}), 400


@app.route('/api/graph/change-plane', methods=['POST'])
def change_plane():
    """
    Change the plane of an activity at a given position

    Body:
        position: position of activity to modify
        plane: new plane (0=Indiv, 1=Team, 2=Class)
    """
    if current_graph is None:
        return jsonify({"error": "Graph not initialized"}), 400

    data = request.get_json()
    position = data.get('position')
    new_plane = data.get('plane')

    if position is None or new_plane is None:
        return jsonify({"error": "position and plane required"}), 400

    # Validate position
    if position < 0 or position >= len(current_graph.listOfFixedInstancedAct):
        return jsonify({"error": "Invalid position"}), 400

    # Validate plane
    if new_plane not in [0, 1, 2]:
        return jsonify({"error": "Invalid plane (must be 0, 1, or 2)"}), 400

    # Update the plane
    inst = current_graph.listOfFixedInstancedAct[position]
    old_plane = inst.plane
    inst.plane = new_plane

    print(f"Changed plane for {inst.actData.name} at position {position}: {old_plane} → {new_plane}")

    return jsonify({
        "success": True,
        "message": f"Changed plane from {old_plane} to {new_plane}",
        "state": current_graph.to_dict()
    })


@app.route('/api/graph/exchange', methods=['POST'])
def exchange_activities():
    """
    Swap two activities

    Body:
        posA: first position
        posB: second position
    """
    if current_graph is None:
        return jsonify({"error": "Graph not initialized"}), 400

    data = request.get_json()
    posA = data.get('posA')
    posB = data.get('posB')

    if posA is None or posB is None:
        return jsonify({"error": "posA and posB required"}), 400

    success = current_graph.exchange(posA, posB)

    if success:
        return jsonify({
            "success": True,
            "message": f"Exchanged positions {posA} and {posB}",
            "state": current_graph.to_dict()
        })
    else:
        return jsonify({"error": "Failed to exchange activities"}), 400


# ==================== GAP & RECOMMENDATION ENDPOINTS ==================== #

@app.route('/api/graph/gaps', methods=['GET'])
def get_gaps():
    """Get list of hard gaps"""
    if current_graph is None:
        return jsonify({"error": "Graph not initialized"}), 400

    return jsonify({
        "hardGapsList": current_graph.hardGapsList,
        "hardGapsCount": current_graph.hardGapsCount,
        "remainingGapsDistance": current_graph.remainingGapsDistance
    })


@app.route('/api/graph/gap/focus', methods=['POST'])
def set_gap_focus():
    """
    Set focus on a specific gap

    Body:
        gapIndex: gap position to focus on (-1 to clear)
    """
    if current_graph is None:
        return jsonify({"error": "Graph not initialized"}), 400

    data = request.get_json()
    gapIndex = data.get('gapIndex', -1)

    current_graph.setGapFocus(gapIndex)

    # Get recommendations
    recommendations = []
    for ctx in current_graph.currentListForSelectedGap:
        recommendations.append(ctx.to_dict())

    return jsonify({
        "gapIndex": gapIndex,
        "recommendations": recommendations,
        "isHardGap": gapIndex in current_graph.hardGapsList if gapIndex >= 0 else False
    })


@app.route('/api/graph/gap/recommendations', methods=['POST'])
def get_gap_recommendations():
    """
    Get recommendations for a specific gap (same as focus but doesn't change state)

    Body:
        gapIndex: gap position
    """
    if current_graph is None:
        return jsonify({"error": "Graph not initialized"}), 400

    data = request.get_json()
    gapIndex = data.get('gapIndex', 0)

    # Temporarily evaluate this gap
    evaluations = []
    for actIdx in range(library.getLength()):
        ctx = current_graph.evaluateFor(actIdx, gapIndex)
        if ctx is not None:
            evaluations.append(ctx.to_dict())

    return jsonify({
        "gapIndex": gapIndex,
        "recommendations": evaluations
    })


# ==================== AUTO-ADD ENDPOINTS ==================== #

@app.route('/api/graph/auto-add', methods=['POST'])
def auto_add():
    """Automatically add best activity to worst gap"""
    if current_graph is None:
        return jsonify({"error": "Graph not initialized"}), 400

    success = current_graph.autoAdd()

    if success:
        return jsonify({
            "success": True,
            "message": "Added recommended activity",
            "state": current_graph.to_dict()
        })
    else:
        return jsonify({
            "success": False,
            "message": "No valid activities to add"
        }), 400


@app.route('/api/graph/auto-add-from-gap', methods=['POST'])
def auto_add_from_gap():
    """Add best activity to currently selected gap"""
    if current_graph is None:
        return jsonify({"error": "Graph not initialized"}), 400

    success = current_graph.autoAddFromSelectedGap()

    if success:
        return jsonify({
            "success": True,
            "message": "Added activity to selected gap",
            "state": current_graph.to_dict()
        })
    else:
        return jsonify({
            "success": False,
            "message": "No valid activities to add or no gap selected"
        }), 400


@app.route('/api/graph/auto-complete', methods=['POST'])
def auto_complete():
    """Automatically add activities until goal is reached"""
    if current_graph is None:
        return jsonify({"error": "Graph not initialized"}), 400

    activities_added = 0
    max_iterations = 100  # Safety limit to prevent infinite loops

    # Keep adding activities until goal is reached or we hit the limit
    while activities_added < max_iterations:
        # Check if goal is already reached
        graph_dict = current_graph.to_dict()
        if graph_dict.get('goalReached', False):
            break

        # Try to add an activity
        success = current_graph.autoAdd()

        if success:
            activities_added += 1
        else:
            # Can't add more activities
            break

    # Get final state
    final_state = current_graph.to_dict()
    goal_reached = final_state.get('goalReached', False)

    return jsonify({
        "success": True,
        "message": f"Added {activities_added} activities. Goal {'reached' if goal_reached else 'not yet reached'}.",
        "activitiesAdded": activities_added,
        "goalReached": goal_reached,
        "state": final_state
    })


# ==================== SAVE/LOAD ENDPOINTS ==================== #

@app.route('/api/graph/save', methods=['POST'])
def save_graph():
    """
    Save graph to pickle file

    Body:
        filename: filename (optional, defaults to timestamp)
    """
    if current_graph is None:
        return jsonify({"error": "Graph not initialized"}), 400

    data = request.get_json()
    filename = data.get('filename')

    if not filename:
        filename = f"orchestration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pickle"

    # Create saves directory
    save_dir = os.path.join(os.path.dirname(__file__), 'saved_orchestrations')
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, filename)

    try:
        current_graph.saveAsFile(save_path)
        return jsonify({
            "success": True,
            "filename": filename,
            "path": save_path,
            "message": f"Saved to {filename}"
        })
    except Exception as e:
        return jsonify({"error": f"Failed to save: {str(e)}"}), 500


@app.route('/api/graph/load', methods=['POST'])
def load_graph():
    """
    Load graph from pickle file

    Body:
        filename: filename to load
    """
    global current_graph

    if library is None:
        return jsonify({"error": "Library not loaded"}), 400

    data = request.get_json()
    filename = data.get('filename')

    if not filename:
        return jsonify({"error": "filename required"}), 400

    save_dir = os.path.join(os.path.dirname(__file__), 'saved_orchestrations')
    load_path = os.path.join(save_dir, filename)

    if not os.path.exists(load_path):
        return jsonify({"error": f"File not found: {filename}"}), 404

    try:
        current_graph = OrchestrationGraphData.loadFromFile(load_path, library)
        return jsonify({
            "success": True,
            "filename": filename,
            "message": f"Loaded from {filename}",
            "state": current_graph.to_dict()
        })
    except Exception as e:
        return jsonify({"error": f"Failed to load: {str(e)}"}), 500


@app.route('/api/graph/saved-files', methods=['GET'])
def get_saved_files():
    """Get list of saved orchestration files"""
    save_dir = os.path.join(os.path.dirname(__file__), 'saved_orchestrations')

    if not os.path.exists(save_dir):
        return jsonify([])

    files = []
    for filename in os.listdir(save_dir):
        if filename.endswith('.pickle'):
            filepath = os.path.join(save_dir, filename)
            stat = os.stat(filepath)
            files.append({
                'filename': filename,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })

    # Sort by modification time (newest first)
    files.sort(key=lambda x: x['modified'], reverse=True)

    return jsonify(files)


# ==================== PRINT/EXPORT ENDPOINTS ==================== #

@app.route('/api/graph/export-json', methods=['GET'])
def export_json():
    """Export graph as JSON"""
    if current_graph is None:
        return jsonify({"error": "Graph not initialized"}), 400

    return jsonify(current_graph.to_dict())


@app.route('/api/graph/print-text', methods=['GET'])
def print_text():
    """Get text representation of graph"""
    if current_graph is None:
        return jsonify({"error": "Graph not initialized"}), 400

    text = str(current_graph)

    return jsonify({
        "content": text,
        "format": "text"
    })


# ==================== CONFIGURATION ENDPOINTS ==================== #

@app.route('/api/config/planes', methods=['GET'])
def get_planes():
    """Get plane names and descriptions"""
    return jsonify({
        "planes": [
            {"index": 0, "name": "Indiv.", "description": "individually"},
            {"index": 1, "name": "Team", "description": "in teams"},
            {"index": 2, "name": "Class", "description": "as a class"}
        ]
    })


@app.route('/api/config/params', methods=['GET'])
def get_params():
    """Get configuration parameters"""
    return jsonify({
        "timeBudget": DEFAULT_TIME_BUDGET,
        "start": list(DEFAULT_START),
        "goal": list(DEFAULT_GOAL),
        "threshold": 0.05,
        "precision": 0.01
    })


# ==================== ACTIVITY MANAGEMENT ENDPOINTS ==================== #

@app.route('/api/activities/create', methods=['POST'])
def create_activity():
    """
    Create a new activity (append to library)

    Body:
        name: str
        description: str
        pcond: [float, float]
        canChangeTime: bool
        minT: int (if canChangeTime)
        maxT: int (if canChangeTime)
        defT: int
        minEffect: [float, float] (if canChangeTime)
        maxEffect: [float, float]
        maxRepetition: int
        defPlane: int (0=Indiv, 1=Team, 2=Class)
    """
    if library is None:
        return jsonify({"error": "Library not loaded"}), 500

    try:
        data = request.get_json()

        # Validate required fields
        required = ['name', 'description', 'pcond', 'maxEffect', 'defT', 'maxRepetition', 'defPlane']
        for field in required:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Validate name uniqueness
        for act in library.listeActData():
            if act.name == data['name']:
                return jsonify({"error": f"Activity name '{data['name']}' already exists"}), 400

        # Build CSV line for new activity
        name = data['name']
        description = data['description']
        pcond = f"({data['pcond'][0]};{data['pcond'][1]})"

        canChangeTime = data.get('canChangeTime', False)
        defPlane = data['defPlane']
        maxRepetition = data['maxRepetition']

        if canChangeTime:
            minEffect = f"({data['minEffect'][0]};{data['minEffect'][1]})"
            maxEffect = f"({data['maxEffect'][0]};{data['maxEffect'][1]})"
            minT = data['minT']
            maxT = data['maxT']
            defT = data['defT']
            csv_line = f"{name},{description},{pcond},{minEffect},{minT},{maxEffect},{maxT},{defT},{maxRepetition},{['Indiv.', 'Team', 'Class'][defPlane]}"
        else:
            maxEffect = f"({data['maxEffect'][0]};{data['maxEffect'][1]})"
            defT = data['defT']
            csv_line = f"{name},{description},{pcond},,,{maxEffect},{defT},,{maxRepetition},{['Indiv.', 'Team', 'Class'][defPlane]}"

        # Create ActivityData from CSV line
        from Activity_pure import ActivityData
        newIdx = library.getLength()
        new_activity = ActivityData(csv_line, newIdx)

        # Add to library
        library.addActivity(new_activity)

        # Save to CSV with backup
        library.saveToCSV(backup=True)

        # Reinitialize the graph with the updated library
        global current_graph
        start = pVal(DEFAULT_START)
        goal = pVal(DEFAULT_GOAL)
        current_graph = OrchestrationGraphData(library, DEFAULT_TIME_BUDGET, start, goal)
        print(f"Reinitialized graph with {library.getLength()} activities")

        return jsonify({
            "success": True,
            "message": f"Created activity '{name}'",
            "activity": new_activity.to_dict()
        })

    except Exception as e:
        return jsonify({"error": f"Failed to create activity: {str(e)}"}), 500


@app.route('/api/library/reload', methods=['POST'])
def reload_library():
    """Manually reload library from CSV"""
    global library

    if library is None:
        return jsonify({"error": "Library not loaded"}), 500

    try:
        library.reload()

        return jsonify({
            "success": True,
            "message": "Library reloaded",
            "activity_count": library.getLength()
        })
    except Exception as e:
        return jsonify({"error": f"Failed to reload library: {str(e)}"}), 500


# ==================== LLM ENHANCEMENT ENDPOINT ==================== #

@app.route('/api/enhance-orchestration', methods=['POST'])
def enhance_orchestration():
    """
    Enhance orchestration with LLM-generated teaching resources

    Body:
        orchestration: full graph state dict
        ageGroup: string (e.g., "12-13 years old")
        subject: string (e.g., "Photosynthesis")
    """
    if llm_service is None:
        return jsonify({
            "error": "LLM service not available",
            "message": "DEEPSEEK_API_KEY not configured"
        }), 503

    try:
        data = request.get_json()

        orchestration = data.get('orchestration')
        age_group = data.get('ageGroup')
        subject = data.get('subject')

        if not orchestration or not age_group or not subject:
            return jsonify({
                "error": "Missing required fields",
                "required": ["orchestration", "ageGroup", "subject"]
            }), 400

        print(f"\n[API] Enhancement request: {subject} for {age_group}")
        print(f"[API] Activities in orchestration: {len(orchestration.get('activities', []))}")

        # Call LLM service
        result = llm_service.enhance_orchestration(orchestration, age_group, subject)

        print(f"[API] ✓ Enhancement completed successfully")

        return jsonify({
            "success": True,
            "enhancements": result["enhancements"],
            "metadata": result["metadata"]
        })

    except Exception as e:
        error_message = str(e)
        print(f"[API] ✗ Enhancement failed: {error_message}")

        # Determine appropriate HTTP status code
        if "timeout" in error_message.lower():
            status_code = 504  # Gateway Timeout
        elif "connection" in error_message.lower():
            status_code = 503  # Service Unavailable
        else:
            status_code = 500  # Internal Server Error

        return jsonify({
            "error": "Enhancement failed",
            "message": error_message
        }), status_code


# ==================== ERROR HANDLERS ==================== #

@app.route('/api/graph/visualize', methods=['GET'])
def visualize_graph():
    """
    Generate 2D state-space visualization of the current graph.

    Returns:
        JSON with base64-encoded PNG image
    """
    if current_graph is None:
        return jsonify({"error": "Graph not initialized"}), 400

    try:
        image_base64 = generate_state_space_graph(current_graph)
        return jsonify({
            "success": True,
            "image": image_base64,
            "format": "png"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(_):
    return jsonify({"error": "Internal server error"}), 500


# ==================== MAIN ==================== #

if __name__ == '__main__':
    print("=" * 60)
    print("Orchestration Graph Backend (Pure Python)")
    print("=" * 60)
    print(f" Library loaded: {library is not None}")
    if library:
        print(f" Activities available: {library.getLength()}")
    print(f" Graph initialized: {current_graph is not None}")
    print("-" * 60)
    print(" Running at: http://127.0.0.1:5000")
    print(" API docs: http://127.0.0.1:5000/api/health")
    print("=" * 60)
    print()

    # Use debug mode but disable auto-reloader to prevent crashes
    # Set use_reloader=True only during active development
    app.run(debug=True, port=5000, host='0.0.0.0', use_reloader=False)
