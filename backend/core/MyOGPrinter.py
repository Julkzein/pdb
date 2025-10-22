"""
This file is an external process.

It loads an OrchestrationGraphData object from a pickle file and prints it using matplotlib.
The file has to be named `temp/saveForPrint.pickle`.

One can run either by:
1. clicking on the "Technical Print" button within the Application.

Or, if this results in an error, by
1. clicking on the "Technical Print" button within the Application.
2. running the command `python3 MyOGPrinter.py` from another terminal.

Or, if this results in an error, by
1. Manually saving the OrchestrationGraphData object to a file named `temp/saveForPrint.pickle` using:
    <yourOG>.data.saveAsFile("temp/saveForPrint.pickle")
2. running the command `python3 MyOGPrinter.py` from another terminal.


This is necessary because the matplotlib package conflicts heavily with PyQt
and because both librairies need to be called from the main thread.
"""


import pickle
import os

from OrchestrationGraph import OrchestrationGraphData
import params as p

import matplotlib.pyplot as plt
import matplotlib.patches as patches

def myExternalPrint(OG:OrchestrationGraphData):
    # WARNING: this should not be called from a file or process including a PyQt component
    # The utilisation of matplotlib conflicts with PyQT, see
    # https://stackoverflow.com/questions/36675269/cannot-move-matplotlib-plot-window-and-exit-it-using-red-x-button/36704822#36704822

    fig, ax = plt.subplots(1)
    HAVE_RED_ARROW = False
    HAVE_BLACK_ARROW = False
    
    reached = OG.start
    res = ""
    for iAct in OG.listOfFixedInstancedAct:
        res += str(iAct) + "\n"
        temp_effect = iAct.end.minus(iAct.start)

        if p.PRECISION < reached.distance(iAct.start):
            # draw arrow from reached to act.start

            if p.TRESHOLD < reached.distance_onlyForward(iAct.start):
                HAVE_RED_ARROW = True
                ax.add_patch( patches.FancyArrowPatch(reached.v, iAct.start.v, arrowstyle='->', mutation_scale=10, color='red'))
            else:
                HAVE_BLACK_ARROW = True
                ax.add_patch( patches.FancyArrowPatch(reached.v, iAct.start.v, arrowstyle='->', mutation_scale=10, color='black'))

        ax.add_patch( patches.Rectangle(iAct.start.v,
                    temp_effect.v[0], temp_effect.v[1], fc = 'none', #facecolor
                    color = "black",
                    linewidth = 1, linestyle="-"))
        
        ax.text(iAct.start.v[0] + 0.5*temp_effect.v[0],
                iAct.start.v[1] + 0.5*temp_effect.v[1],
                iAct.actData.name,
            horizontalalignment='center',
            verticalalignment='center',
            fontsize=10, color='gray')

        reached = iAct.end
    

    tempReachedGoal = reached.needToReach(OG.goal)
    if p.PRECISION < reached.distance(tempReachedGoal):
        # draw arrow from reached to the goal (if progression still needed)

        if p.TRESHOLD < reached.distance_onlyForward(tempReachedGoal):
            HAVE_RED_ARROW = True
            ax.add_patch( patches.FancyArrowPatch(reached.v, tempReachedGoal.v, arrowstyle='->', mutation_scale=10, color='red'))
        else:
            HAVE_BLACK_ARROW = True
            ax.add_patch( patches.FancyArrowPatch(reached.v, tempReachedGoal.v, arrowstyle='->', mutation_scale=10, color='black'))
    
    ax.scatter(OG.goal.v[0], OG.goal.v[1], marker='x', label="goal")
    ax.scatter(OG.start.v[0], OG.start.v[1], marker='x', label="start")
    plt.xlabel("fluency")
    plt.ylabel("depth")
    plt.title("Technical representation of the lesson's model")

    # https://stackoverflow.com/questions/13303928/how-to-make-custom-legend
    # Get artists and labels for legend and chose which ones to display
    handles, labels = ax.get_legend_handles_labels()
    display = tuple(range(len(handles)))
    # Latex arrows found thanks to https://stackoverflow.com/questions/22348229/matplotlib-legend-for-an-arrow
    redArrows   = plt.Line2D((0,1),(0,0), linestyle="", color='red', marker=r'$\rightarrow$')
    blackArrows = plt.Line2D((0,1),(0,0), linestyle="", color='black', marker=r'$\longrightarrow$')
    ArrowsHandles = []
    ArrowsLabels = []
    if HAVE_RED_ARROW:
        ArrowsHandles.append(redArrows)
        ArrowsLabels.append('Hard transitions')
    if HAVE_BLACK_ARROW:
        ArrowsHandles.append(blackArrows)
        ArrowsLabels.append('Accepted transitions')
    ax.legend([handle for i,handle in enumerate(handles) if i in display]+ArrowsHandles,
            [label for i,label in enumerate(labels) if i in display]+ArrowsLabels)

    plt.show()


# Get the directory where the current file is located #chatGPT helped for that
script_dir = os.path.dirname(os.path.abspath(__file__))
input_path = os.path.join(script_dir, "temp", "saveForPrint.pickle")

with open(input_path, 'rb') as f:
    OG = pickle.load(f)
    myExternalPrint(OG)

