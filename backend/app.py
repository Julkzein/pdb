# Fixed backend/app.py
# Cleaned import flow, fixed try/except nesting, consistent fallbacks,
# and small robustness improvements (CSV parsing, OG_AVAILABLE flag).

import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

# Add core directory to path so imports like `from core.X import Y` work
core_dir = os.path.join(os.path.dirname(__file__), 'core')
if core_dir not in sys.path:
    sys.path.append(core_dir)

# Feature-availability flag
OG_AVAILABLE = False

# Try to import orchestration-related classes from your repo; provide
# sensible fallbacks when they are missing so the backend still runs.
InstantiatedActivity = None
Activity = None
OrchestrationGraph = None

# Attempt to load cleaned classes first, then fall back to originals.
try:
    try:
        # Prefer cleaned versions if they exist
        from InstantiatedAct_cleaned import InstantiatedActivity, InstantiatedActData
        from Activity_cleaned import Activity, ActivityData
        OG_AVAILABLE = True
        print("✅ Imported cleaned InstantiatedAct and Activity classes")
    except Exception:
        # Try original module names (common case)
        try:
            from InstantiatedAct import InstantiatedActData as InstantiatedActivity
            from Activity import ActivityData as Activity
            OG_AVAILABLE = True
            print("✅ Imported original InstantiatedAct and Activity modules")
        except Exception:
            # Leave OG_AVAILABLE False; we'll provide basic fallbacks below
            print("⚠️  Could not import InstantiatedAct/Activity modules; using simple fallbacks")

    # Optional params module
    try:
        import params
        print("✅ Imported params")
    except Exception:
        # params is optional; continue without it
        pass

except Exception as e:
    # This outer try/except is defensive and should not usually trigger,
    # but if it does, we will continue in limited mode.
    print(f"⚠️  Unexpected import error: {e}")

# Now import OrchestrationGraph with preference for cleaned, then original.
try:
    try:
        from OrchestrationGraph_cleaned import OrchestrationGraph
        print("✅ Using cleaned OrchestrationGraph (no Qt dependencies)")
    except Exception:
        try:
            # Original OrchestrationGraph may depend on Qt; try to mock Qt if needed
            import qt_compat  # this may be a local shim; if missing, this will fail
            from OrchestrationGraph import OrchestrationGraph
            print("⚠️ Using original OrchestrationGraph with qt_compat shim")
        except Exception:
            # Final fallback: lightweight dummy implementation
            print("❌ Could not import OrchestrationGraph; using dummy fallback implementation")
            class OrchestrationGraph:
                def __init__(self, *args, **kwargs):
                    self.activities = []

                def add_activity(self, activity):
                    self.activities.append(activity)

                def to_dict(self):
                    # Try to serialize activities cleanly
                    serialized = []
                    for a in self.activities:
                        try:
                            # If activity has to_dict, use it
                            serialized.append(a.to_dict())
                        except Exception:
                            serialized.append(a)
                    return {"activities": serialized}

except Exception as e:
    # Extremely defensive fallback (shouldn't be reached)
    print(f"⚠️  Unexpected error while setting up OrchestrationGraph fallback: {e}")
    class OrchestrationGraph:
        def __init__(self):
            self.activities = []
        def add_activity(self, activity):
            self.activities.append(activity)
        def to_dict(self):
            return {"activities": self.activities}

# If InstantiatedActivity wasn't imported from your modules, provide a simple class
if InstantiatedActivity is None:
    class InstantiatedActivity:
        def __init__(self, name: str, duration: int):
            self.name = name
            self.duration = duration
            # Keep 'time' for compatibility with earlier code
            self.time = duration

        def to_dict(self):
            return {"name": self.name, "duration": self.duration, "time": self.time}

# Flask app setup
app = Flask(__name__)
CORS(app, origins="*")  # Allow all origins for development only

# Global variable to store the current orchestration graph
current_graph = None


@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple endpoint to test if backend is running"""
    return jsonify({
        "status": "healthy",
        "message": "Backend is running!",
        "orchestration_available": OG_AVAILABLE
    })


@app.route('/api/activities', methods=['GET'])
def get_activities():
    """Load and return activities from CSV or use defaults"""
    try:
        csv_path = os.path.join(os.path.dirname(__file__), 'inputData', 'interpolation_2D_library.csv')
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            activities = []

            # Prefer explicit 'name' column if present
            if 'name' in df.columns:
                for index, row in df.iterrows():
                    try:
                        duration = int(row.get('duration', 30)) if not pd.isna(row.get('duration', 30)) else 30
                    except Exception:
                        duration = 30

                    activity = {
                        'id': str(index),
                        'name': row['name'],
                        'type': row.get('type', 'general'),
                        'duration': duration,
                        'color': row.get('color', '#4CAF50'),
                        'description': row.get('description', '')
                    }
                    activities.append(activity)
            else:
                # Heuristic parsing if CSV is in a custom format
                for index, row in df.iterrows():
                    # Use first column as name when possible
                    name = row.iloc[0] if len(row) > 0 and not pd.isna(row.iloc[0]) else f'Activity {index}'
                    try:
                        defT = int(row.iloc[6]) if len(row) > 6 and not pd.isna(row.iloc[6]) else 30
                    except Exception:
                        defT = 30

                    activity = {
                        'id': str(index),
                        'name': name,
                        'type': 'general',
                        'duration': defT,
                        'color': '#4CAF50' if index % 2 == 0 else '#2196F3',
                        'description': 'Activity from library'
                    }
                    activities.append(activity)

            print(f"✅ Loaded {len(activities)} activities from CSV")
            return jsonify(activities)
        else:
            print(f"⚠️  CSV not found at {csv_path}, using default activities")

    except Exception as e:
        print(f"⚠️  Error loading CSV: {e}")

    # Default fallback activities
    default_activities = [
        {'id': '1', 'name': 'Introduction', 'type': 'general', 'duration': 15, 'color': '#4CAF50'},
        {'id': '2', 'name': 'Lecture', 'type': 'general', 'duration': 30, 'color': '#2196F3'},
        {'id': '3', 'name': 'Group Work', 'type': 'general', 'duration': 25, 'color': '#FF9800'},
        {'id': '4', 'name': 'Discussion', 'type': 'general', 'duration': 20, 'color': '#9C27B0'},
        {'id': '5', 'name': 'Break', 'type': 'general', 'duration': 10, 'color': '#607D8B'},
        {'id': '6', 'name': 'Conclusion', 'type': 'general', 'duration': 15, 'color': '#E91E63'},
    ]
    return jsonify(default_activities)


@app.route('/api/orchestration/create', methods=['POST'])
def create_orchestration():
    """Create a new orchestration graph"""
    global current_graph
    try:
        data = request.get_json(force=True) or {}

        # Create new orchestration graph
        current_graph = OrchestrationGraph()

        # Add activities if provided
        for activity_data in data.get('activities', []):
            if OG_AVAILABLE and isinstance(activity_data, dict):
                # Try to instantiate your domain class if available
                try:
                    activity = InstantiatedActivity(
                        name=activity_data.get('name'),
                        duration=activity_data.get('duration', 30)
                    )
                    current_graph.add_activity(activity)
                except Exception:
                    # If instantiation fails, store the raw dict
                    current_graph.add_activity(activity_data)
            else:
                # Simple mode: store the dict or provided object
                current_graph.add_activity(activity_data)

        return jsonify({
            "success": True,
            "message": "Graph created",
            "graph_id": id(current_graph)
        })
    except Exception as e:
        print(f"Error creating orchestration: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/orchestration/validate', methods=['POST'])
def validate_orchestration():
    """Validate the current orchestration"""
    global current_graph
    try:
        if current_graph is None:
            return jsonify({"valid": False, "errors": ["No graph created yet"]})

        # Placeholder validation; replace with real validators when available
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }

        return jsonify(validation_result)
    except Exception as e:
        print(f"Error validating orchestration: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/orchestration/export', methods=['GET'])
def export_orchestration():
    """Export the current orchestration"""
    global current_graph
    try:
        if current_graph is None:
            return jsonify({"error": "No graph to export"}), 400

        if hasattr(current_graph, 'to_dict'):
            export_data = current_graph.to_dict()
        else:
            export_data = {
                "activities": getattr(current_graph, 'activities', []),
                "connections": [],
            }

        return jsonify(export_data)
    except Exception as e:
        print(f"Error exporting orchestration: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/orchestration/recommend', methods=['POST'])
def recommend_activity():
    """Get recommended activities for a gap"""
    global current_graph
    try:
        data = request.json
        gap_index = data.get('gapIndex', 0)
        
        # In limited mode, return a simple recommendation
        if not OG_AVAILABLE or current_graph is None:
            return jsonify({
                "recommended": {
                    "id": "0",
                    "name": "Introduction",
                    "reason": "Good starting activity"
                }
            })
        
        # If full orchestration is available, use the actual recommendation logic
        if hasattr(current_graph, 'setGapFocus'):
            current_graph.setGapFocus(gap_index)
            # Get recommendations from the evaluateFor method
            if hasattr(current_graph, 'data'):
                recommendations = current_graph.data.currentListForSelectedGap
                # Find the best one
                for rec in recommendations:
                    if hasattr(rec, 'isBest') and rec.isBest:
                        return jsonify({
                            "recommended": {
                                "id": str(rec.myActData.idx),
                                "name": rec.myActData.name,
                                "score": rec.myScore
                            }
                        })
        
        return jsonify({"recommended": None})
    except Exception as e:
        print(f"Error getting recommendation: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/orchestration/save', methods=['POST'])
def save_orchestration():
    """Save orchestration to file"""
    global current_graph
    try:
        data = request.json
        filename = data.get('filename', 'orchestration.json')
        
        # Get the export data
        export_data = {
            "activities": [],
            "connections": [],
            "metadata": {
                "created": str(datetime.now()),
                "version": "1.0"
            }
        }
        
        if current_graph and hasattr(current_graph, 'to_dict'):
            export_data = current_graph.to_dict()
        
        # Save to file
        save_path = os.path.join('saved_orchestrations', filename)
        os.makedirs('saved_orchestrations', exist_ok=True)
        
        with open(save_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return jsonify({
            "success": True,
            "filename": filename,
            "message": f"Saved to {filename}"
        })
    except Exception as e:
        print(f"Error saving: {e}")
        return jsonify({"error": str(e)}), 500

# Add these routes to backend/app.py

@app.route('/api/orchestration/auto-add', methods=['POST'])
def auto_add_activity():
    """Automatically add the best activity to fill the largest gap"""
    global current_graph
    try:
        if not OG_AVAILABLE or current_graph is None:
            # Fallback for limited mode
            return jsonify({
                "success": False,
                "message": "Orchestration engine not available"
            })
        
        # Find the largest gap and add the best activity
        if hasattr(current_graph, 'autoAdd'):
            current_graph.autoAdd()
            
            # Return the updated graph
            return jsonify({
                "success": True,
                "graph": current_graph.to_dict(),
                "message": "Added recommended activity"
            })
        
        return jsonify({"success": False, "message": "Method not available"})
    except Exception as e:
        print(f"Error in auto-add: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/orchestration/evaluate-gaps', methods=['POST'])
def evaluate_gaps():
    """Evaluate all gaps in the current orchestration"""
    global current_graph
    try:
        if not OG_AVAILABLE or current_graph is None:
            return jsonify({"gaps": []})
        
        if hasattr(current_graph, 'data'):
            gaps = current_graph.data.evaluate_gaps()
            return jsonify({
                "gaps": [{"distance": d, "index": i} for d, i in gaps],
                "hardGapsCount": current_graph.data.hardGapsCount
            })
        
        return jsonify({"gaps": []})
    except Exception as e:
        print(f"Error evaluating gaps: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/orchestration/activities-for-gap', methods=['POST'])
def get_activities_for_gap():
    """Get recommended activities for a specific gap"""
    global current_graph
    try:
        data = request.json
        gap_index = data.get('gapIndex', 0)
        
        if not OG_AVAILABLE or current_graph is None:
            return jsonify({"activities": []})
        
        if hasattr(current_graph, 'setGapFocus'):
            current_graph.setGapFocus(gap_index)
            
            # Get the evaluated activities for this gap
            if hasattr(current_graph, 'data'):
                activities = []
                for ctx_act in current_graph.data.currentListForSelectedGap:
                    act_dict = {
                        "name": ctx_act.myActData.name,
                        "score": ctx_act.myScore,
                        "isBest": ctx_act.isBest,
                        "flags": {
                            "exhausted": ctx_act.myFlags.exhausted,
                            "tooLong": ctx_act.myFlags.tooLong,
                            "noProgress": ctx_act.myFlags.noProgress
                        }
                    }
                    activities.append(act_dict)
                
                # Sort by score (best first)
                activities.sort(key=lambda x: x['score'] if x['score'] else -999, reverse=True)
                return jsonify({"activities": activities})
        
        return jsonify({"activities": []})
    except Exception as e:
        print(f"Error getting activities for gap: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/orchestration/load', methods=['POST'])
def load_orchestration():
    """Load orchestration from file"""
    global current_graph
    try:
        data = request.json
        filename = data.get('filename', 'orchestration.json')
        
        save_path = os.path.join('saved_orchestrations', filename)
        
        if not os.path.exists(save_path):
            return jsonify({"error": "File not found"}), 404
        
        with open(save_path, 'r') as f:
            loaded_data = json.load(f)
        
        # Recreate the graph from loaded data
        # This is simplified - you'd need to properly reconstruct the graph
        current_graph = OrchestrationGraph()
        
        return jsonify({
            "success": True,
            "data": loaded_data,
            "message": f"Loaded from {filename}"
        })
    except Exception as e:
        print(f"Error loading: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/orchestration/state', methods=['GET'])
def get_orchestration_state():
    """Get current orchestration state"""
    global current_graph
    try:
        if current_graph and hasattr(current_graph, 'data'):
            return jsonify({
                "nodes": [
                    {
                        "id": f"node-{i}",
                        "name": act.actData.name if hasattr(act, 'actData') else 'Activity',
                        "time": act.time if hasattr(act, 'time') else 30,
                        "startsAfter": act.startsAfter if hasattr(act, 'startsAfter') else 0
                    }
                    for i, act in enumerate(current_graph.data.listOfFixedInstancedAct)
                ],
                "totalTime": current_graph.data.totTime,
                "timeBudget": current_graph.data.tBudget,
                "hardGapsCount": current_graph.data.hardGapsCount,
                "hardGapsList": current_graph.data.hardGapsList,
                "remainingGapsDistance": current_graph.data.remainingGapsDistance
            })
        return jsonify({
            "nodes": [],
            "totalTime": 0,
            "timeBudget": 120,
            "hardGapsCount": 0,
            "hardGapsList": [],
            "remainingGapsDistance": 0
        })
    except Exception as e:
        print(f"Error getting state: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/orchestration/set-gap-focus', methods=['POST'])
def set_gap_focus():
    """Set focus on a specific gap and get recommendations for it"""
    global current_graph
    try:
        data = request.json
        gap_index = data.get('gapIndex', -1)
        
        if not OG_AVAILABLE or current_graph is None:
            # Fallback mode
            return jsonify({
                "recommendations": [],
                "isHardGap": False
            })
        
        if hasattr(current_graph, 'setGapFocus'):
            current_graph.setGapFocus(gap_index)
            
            recommendations = []
            if hasattr(current_graph, 'data') and current_graph.data.currentListForSelectedGap:
                for ctx_act in current_graph.data.currentListForSelectedGap:
                    rec = {
                        "idx": ctx_act.myActData.idx,
                        "name": ctx_act.myActData.name,
                        "score": ctx_act.myScore,
                        "isBest": ctx_act.isBest,
                        "flags": {
                            "exhausted": ctx_act.myFlags.exhausted,
                            "tooLong": ctx_act.myFlags.tooLong,
                            "noProgress": ctx_act.myFlags.noProgress
                        },
                        "okeyToTake": ctx_act.okeyToTake()
                    }
                    recommendations.append(rec)
                
                # Sort by best first
                recommendations.sort(key=lambda x: (
                    not x['isBest'],  # Best first
                    not x['okeyToTake'],  # Okay activities before not okay
                    -x['score'] if x['score'] is not None else 999
                ))
            
            is_hard_gap = gap_index in current_graph.data.hardGapsList if gap_index >= 0 else False
            
            return jsonify({
                "recommendations": recommendations,
                "isHardGap": is_hard_gap,
                "gapIndex": gap_index
            })
        
        return jsonify({"recommendations": [], "isHardGap": False})
    except Exception as e:
        print(f"Error setting gap focus: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/orchestration/auto-add-from-gap', methods=['POST'])
def auto_add_from_gap():
    """Auto-add the best activity for the selected gap"""
    global current_graph
    try:
        if not OG_AVAILABLE or current_graph is None:
            return jsonify({"success": False, "message": "Not available"})
        
        if hasattr(current_graph, 'autoAddFromSelectedGap'):
            current_graph.autoAddFromSelectedGap()
            
            # Return updated state
            return get_orchestration_state()
        
        return jsonify({"success": False})
    except Exception as e:
        print(f"Error auto-adding: {e}")
        return jsonify({"error": str(e)}), 500
    
# backend/app.py - Add this endpoint
@app.route('/api/orchestration/technical-graph', methods=['GET'])
def get_technical_graph():
    """Generate the technical graph representation"""
    global current_graph
    
    if not OG_AVAILABLE or current_graph is None:
        return jsonify({"error": "Orchestration not available"}), 400
    
    try:
        import matplotlib.pyplot as plt
        import io
        import base64
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Plot activities as rectangles
        current_pos = (0.0, 0.0)
        positions = [current_pos]
        
        for act in current_graph.data.listOfFixedInstancedAct:
            # Draw activity box
            next_pos = (act.end.p[0], act.end.p[1])
            
            # Draw box
            rect = plt.Rectangle(
                (current_pos[0], current_pos[1]),
                next_pos[0] - current_pos[0],
                next_pos[1] - current_pos[1],
                fill=False,
                edgecolor='black'
            )
            ax.add_patch(rect)
            
            # Add label
            ax.text(
                (current_pos[0] + next_pos[0]) / 2,
                (current_pos[1] + next_pos[1]) / 2,
                act.actData.name,
                ha='center',
                va='center'
            )
            
            positions.append(next_pos)
            current_pos = next_pos
        
        # Draw hard transitions
        for gap_idx in current_graph.data.hardGapsList:
            if gap_idx < len(positions) - 1:
                ax.arrow(
                    positions[gap_idx][0], positions[gap_idx][1],
                    positions[gap_idx + 1][0] - positions[gap_idx][0],
                    positions[gap_idx + 1][1] - positions[gap_idx][1],
                    color='red', width=0.002, head_width=0.02
                )
        
        # Mark start and goal
        ax.plot(0, 0, 'go', markersize=10, label='start')
        ax.plot(0.9, 0.9, 'bx', markersize=10, label='goal')
        
        ax.set_xlim(-0.1, 1.0)
        ax.set_ylim(-0.1, 1.0)
        ax.set_xlabel('fluency')
        ax.set_ylabel('depth')
        ax.set_title("Technical representation of the lesson's model")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return jsonify({"image": f"data:image/png;base64,{image_base64}"})
        
    except Exception as e:
        print(f"Error generating graph: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/orchestration/print', methods=['GET'])
def print_orchestration():
    """Generate printable version"""
    global current_graph
    try:
        if current_graph is None:
            return jsonify({"error": "No graph to print"}), 400
        
        # Generate a simple text representation
        output = "ORCHESTRATION GRAPH LESSON PLAN\n"
        output += "=" * 40 + "\n\n"
        
        if hasattr(current_graph, 'data'):
            output += f"Total Time: {current_graph.data.totTime} min\n"
            output += f"Budget: {current_graph.data.tBudget} min\n"
            output += f"Gaps: {current_graph.data.hardGapsCount}\n\n"
            output += "Activities:\n"
            output += "-" * 20 + "\n"
            
            if hasattr(current_graph.data, 'listOfFixedInstancedAct'):
                for i, act in enumerate(current_graph.data.listOfFixedInstancedAct):
                    if hasattr(act, 'actData'):
                        output += f"{i+1}. {act.actData.name} ({act.time} min)\n"
                    else:
                        output += f"{i+1}. Activity ({getattr(act, 'time', 30)} min)\n"
        
        return jsonify({
            "content": output,
            "format": "text"
        })
    except Exception as e:
        print(f"Error printing: {e}")
        return jsonify({"error": str(e)}), 500
    
    
if __name__ == '__main__':
    print("=" * 50)
    print(" Starting Orchestration Graph Backend...")
    print("=" * 50)
    print(f"=Orchestration modules available: {OG_AVAILABLE}")
    print(" Backend running at http://127.0.0.1:5000")
    print(" Test API at: http://127.0.0.1:5000/api/health")
    print("=" * 50)
    app.run(debug=True, port=5000, host='0.0.0.0')
