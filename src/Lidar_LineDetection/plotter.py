import sys
# import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d

from read_json import read_json

# Read JSON
data = read_json()

# Get X, Y, Z & I
X, Y, Z, I = [points.get('x') for points in data], [points.get('y') for points in data], [points.get('z') for points in data], [points.get('i') for points in data]

# Plot X,Y,Z
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_trisurf(X, Y, Z, color='white', edgecolors='grey', alpha=0.5)
ax.scatter(X, Y, Z, c='red')
plt.show()
