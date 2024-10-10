import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from matplotlib.colors import ListedColormap, BoundaryNorm
from scipy.spatial import ConvexHull

# Function to create an empty grid
def create_empty_grid(rows, cols):
    return pd.DataFrame(np.nan, index=np.arange(rows), columns=np.arange(cols))

# Function to draw a convex hull around selected points
def draw_convex_hull(points, ax):
    if len(points) > 2:
        hull = ConvexHull(points)
        for simplex in hull.simplices:
            ax.plot([points[simplex[0]][0], points[simplex[1]][0]], 
                    [points[simplex[0]][1], points[simplex[1]][1]], 'r-', linewidth=0.5)

# Function to plot heatmap
def plot_heatmap(data, title):
    values = data.values.flatten()
    grid_size = data.shape

    points = [(i % grid_size[1], i // grid_size[1]) for i, value in enumerate(values) if not np.isnan(value)]
    values_list = [value for value in values if not np.isnan(value)]

    grid_x, grid_y = np.mgrid[0:grid_size[1]:100j, 0:grid_size[0]:100j]
    grid_z = griddata(points, values_list, (grid_x, grid_y), method='cubic')

    levels = [0, 9, 16, 20, 25]
    colors = ['yellow', 'limegreen', 'green', 'darkgreen']
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)

    fig, ax = plt.subplots(figsize=(10, 8))
    contourf = ax.contourf(grid_x, grid_y, grid_z, levels=levels, cmap=cmap, norm=norm, extend='both')
    cbar = fig.colorbar(contourf, ticks=levels, pad=0.1)
    cbar.ax.set_yticklabels([str(level) for level in levels])
    cbar.set_label('% Vol. Wassergehalt', fontsize=8)
    cbar.ax.tick_params(labelsize=8)

    draw_convex_hull(points, ax)

    ax.set_title(title)
    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Y Coordinate")
    ax.invert_yaxis()
    fig.subplots_adjust(right=0.8)
    st.pyplot(fig)

# Streamlit app
st.title("Interactive Heatmap Generator")

# Create an empty grid
grid_size = (15, 15)  # Same size as B6:P20
grid = create_empty_grid(*grid_size)

# User input for selecting boxes
st.write("### Select Boxes")
selected_cells = st.experimental_data_editor(grid, use_container_width=True)

# User input for entering values
st.write("### Enter Values for Selected Boxes")
input_data = selected_cells.copy()
for row in input_data.index:
    for col in input_data.columns:
        if pd.notna(selected_cells.loc[row, col]):
            input_data.loc[row, col] = st.number_input(f"Value for cell ({row}, {col})", min_value=0.0, step=1.0)

# Generate heatmap
if st.button("Generate Heatmap"):
    plot_heatmap(input_data, "Heatmap of % Volumetrischer Wassergehalt")
