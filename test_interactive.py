import matplotlib.pyplot as plt
from easygui import *
from matplotlib.widgets import Button
from matplotlib.patches import Circle, Wedge, Polygon
import clustering as cl
from matplotlib.collections import PatchCollection

# MainWindow
pts = []
circles = []
fig = plt.figure()
plt.subplots_adjust(bottom=0.2)
ax = fig.add_subplot(111)
def clear_ax():
    global ax, circles, fig, pts
    pts = []
    ax.clear()
    ax.set_xlim([0, 10])
    ax.set_ylim([0, 10])
    for c in circles:
        ax.add_artist(c)
    fig.canvas.draw()
clear_ax()

# Add a button for parameters
k = 3
z = 3
m = 5
clust = None
def start_clust():
    global k,z,m, clust, circles
    clust = cl.ParallelStreamingClustering(k,z,cl.DEFAULT_ALPHA,cl.DEFAULT_BETA,cl.DEFAULT_ETA,m)
    circles = []
    for _ in range(k):
        circles.append(plt.Circle((0, 0), 0.0, color='r', alpha=0.0))
    clear_ax()
    
start_clust()
def set_params(event):
    global k,z,m
    msg = "Enter parameters for the clustering algorithm"
    title = "Parameters"
    fieldNames = ["Number of clusters (k)","Number of outliers (z)","Number of instances (m)"]
    fieldValues = [str(k),str(z),str(m)]
    fieldValues = multenterbox(msg, title, fieldNames, fieldValues)
    while True:
        if fieldValues == None: break # Cancel button
        errmsg = ""
        for i in range(len(fieldNames)):
            if fieldValues[i] == None or fieldValues[i].strip() == "":
                errmsg = errmsg + ('"%s" is a required field.\n\n' % fieldNames[i])
        if errmsg == "": break
        fieldValues = multenterbox(errmsg, title, fieldNames, fieldValues)
    k = int(fieldValues[0])
    z = int(fieldValues[1])
    m = int(fieldValues[2])
    start_clust()

axparam = plt.axes([0.75, 0.05, 0.2, 0.075])
bparam = Button(axparam, 'Parameters')
bparam.on_clicked(set_params)

# Add a button to clear all the points
def clear_all_points(event):
    start_clust()
axclear = plt.axes([0.55, 0.05, 0.15, 0.075])
bclear = Button(axclear, 'Clear')
bclear.on_clicked(clear_all_points)

# Add a button to "compute clusters"
def show_clusters(offline):
    global circles, clust, fig, k, z, pts
    if offline:
        (clusters,r) = cl.robust_clustering(pts, k, len(pts)-z, False)
    else:
        (clusters,r) = clust.get_clusters()
    n = len(clusters)
    for i in range(len(circles)):
        if i >= n:
            circles[i].set_alpha(0.0)
        else:
            circles[i].set_alpha(0.3)
            circles[i].set_center(clusters[i])
            circles[i].set_radius(r)
    fig.canvas.draw()

def compute(event):
    try:
        clust.end_batch_now()
    except cl.Not_initialized:
        print("Can't end batch during initialization step.")
    show_clusters(False)
axcompute = plt.axes([0.3, 0.05, 0.2, 0.075])
bcompute = Button(axcompute, 'Force batch end')
bcompute.on_clicked(compute)

# Add button to use offline algorithm
def show_offline(event):
    show_clusters(True)
axoffline = plt.axes([0.05, 0.05, 0.2, 0.075])
boffline = Button(axoffline, 'Compute offline')
boffline.on_clicked(show_offline)

# Add points on click
def onclick(event):
    global clust, ax, fig
    if event.inaxes in [ax]:
        ax.scatter(event.xdata, event.ydata, s=12)
        clust.next((event.xdata, event.ydata))
        pts.append((event.xdata, event.ydata))
        fig.canvas.draw()
        show_clusters(False)

cid = fig.canvas.mpl_connect('button_press_event', onclick)

# Show MainWindow
plt.sca(ax)
plt.show()
