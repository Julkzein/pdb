"""
State-space visualization generator
Creates 2D matplotlib graphs showing pValue transitions
"""

import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO
import base64


def generate_state_space_graph(graph_data):
    """
    Generate 2D state-space visualization showing activity transitions.

    Args:
        graph_data: OrchestrationGraphData instance

    Returns:
        str: Base64-encoded PNG image
    """
    fig, ax = plt.subplots(1, figsize=(10, 10))

    # Set up axes
    plt.xlabel("fluency", fontsize=14)
    plt.ylabel("depth", fontsize=14)
    plt.title("Technical representation of the lesson's model", fontsize=16)
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)

    # Plot start and goal points
    ax.scatter(graph_data.start.v[0], graph_data.start.v[1],
               marker='x', s=200, c='orange', label="start", linewidths=3, zorder=10)
    ax.scatter(graph_data.goal.v[0], graph_data.goal.v[1],
               marker='x', s=200, c='blue', label="goal", linewidths=3, zorder=10)

    # Draw each activity as a rectangle
    current_state = graph_data.start

    for i, inst_act in enumerate(graph_data.listOfFixedInstancedAct):
        # Get activity start and effect
        start_point = inst_act.pValStart
        effect = inst_act.actData.peffect.get(inst_act.time)

        # Draw rectangle showing the activity transition
        rect = patches.Rectangle(
            (start_point.v[0], start_point.v[1]),  # Bottom-left corner
            effect.v[0],  # Width (fluency effect)
            effect.v[1],  # Height (depth effect)
            fc='none',  # No fill
            edgecolor='black',
            linewidth=1,
            linestyle='-'
        )
        ax.add_patch(rect)

        # Add activity name label at the center of the rectangle
        center_x = start_point.v[0] + effect.v[0] / 2
        center_y = start_point.v[1] + effect.v[1] / 2
        ax.text(center_x, center_y, inst_act.actData.name,
                ha='center', va='center', fontsize=9, color='gray')

        # Draw arrow from previous state to this activity's start
        if i == 0:
            # First activity - arrow from start point
            arrow_start = (graph_data.start.v[0], graph_data.start.v[1])
        else:
            # Arrow from previous activity's end
            arrow_start = (current_state.v[0], current_state.v[1])

        arrow_end = (start_point.v[0], start_point.v[1])

        # Check if this is a hard gap (transition distance > threshold)
        distance = current_state.distance_onlyForward(start_point)
        THRESHOLD = 0.05
        is_hard_gap = distance > THRESHOLD

        # Draw arrow (red for hard gaps, black for accepted transitions)
        if arrow_start != arrow_end:  # Only draw if there's movement
            arrow = patches.FancyArrowPatch(
                arrow_start, arrow_end,
                arrowstyle='->',
                mutation_scale=15,
                color='red' if is_hard_gap else 'black',
                linewidth=2 if is_hard_gap else 1,
                zorder=5
            )
            ax.add_patch(arrow)

        # Update current state to end of this activity
        current_state = inst_act.pValEnd

    # Draw final arrow to goal if not reached
    if not graph_data.reached.isPast(graph_data.goal):
        final_arrow = patches.FancyArrowPatch(
            (current_state.v[0], current_state.v[1]),
            (graph_data.goal.v[0], graph_data.goal.v[1]),
            arrowstyle='->',
            mutation_scale=15,
            color='red',
            linewidth=2,
            linestyle='--',
            zorder=5
        )
        ax.add_patch(final_arrow)

    # Create legend with arrow symbols
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='x', color='w', markerfacecolor='blue',
               markersize=10, label='goal'),
        Line2D([0], [0], marker='x', color='w', markerfacecolor='orange',
               markersize=10, label='start'),
        Line2D([0], [0], color='black', linewidth=1, label='Accepted transitions'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=10)

    # Save to BytesIO buffer
    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    plt.close(fig)

    # Encode as base64
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    return image_base64
