import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from scipy.interpolate import griddata

# Read the specified range from the Excel file (B6:P20)
def read_excel_data(file_path, sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    messwerte_data = df.iloc[5:20, 1:16]
    messwerte_data = messwerte_data.apply(pd.to_numeric, errors='coerce')
    return messwerte_data

# Interpolation and smoothing function
def interpolate_data(data):
    points = np.array([(x, y) for y in range(data.shape[0]) for x in range(data.shape[1]) if not np.isnan(data.iloc[y, x])])
    values = np.array([data.iloc[y, x] for y in range(data.shape[0]) for x in range(data.shape[1]) if not np.isnan(data.iloc[y, x])])
    grid_x, grid_y = np.mgrid[0:data.shape[1]:50j, 0:data.shape[0]:50j]  # Milder interpolation
    grid_z = griddata(points, values, (grid_x, grid_y), method='linear')
    return grid_x, grid_y, grid_z

# Plot original data
def plot_original_data(data, title):
    fig, ax = plt.subplots(figsize=(10, 8))

    levels = [0, 9, 16, 20, 25]
    colors = ['yellow', 'limegreen', 'green', 'darkgreen']
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)

    heatmap = ax.imshow(data, cmap=cmap, norm=norm, interpolation='none', aspect='auto', origin='upper')

    cbar = fig.colorbar(heatmap, ax=ax, ticks=levels)
    cbar.ax.set_yticklabels([str(level) for level in levels])
    cbar.set_label('% Vol. Wassergehalt', fontsize=8)
    cbar.ax.tick_params(labelsize=8)

    ax.set_title(title)
    ax.axis('off')
    plt.show()

# Plot smooth heatmap
def plot_smooth_heatmap(data, title):
    fig, ax = plt.subplots(figsize=(10, 8))

    grid_x, grid_y, grid_z = interpolate_data(data)

    levels = [0, 9, 16, 20, 25]
    colors = ['yellow', 'limegreen', 'green', 'darkgreen']
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)

    heatmap = ax.contourf(grid_x, grid_y, grid_z, levels=levels, cmap=cmap, norm=norm, extend='both')

    cbar = fig.colorbar(heatmap, ax=ax, ticks=levels)
    cbar.ax.set_yticklabels([str(level) for level in levels])
    cbar.set_label('% Vol. Wassergehalt', fontsize=8)
    cbar.ax.tick_params(labelsize=8)

    # Center the plot within the figure
    ax.set_xlim(0, data.shape[1] - 1)
    ax.set_ylim(data.shape[0] - 1, 0)

    ax.set_title(title)
    ax.axis('off')
    plt.show()

# File path to the Excel data
file_path = 'Distribution_Uniformity.xlsx'

# Read and plot data for Example 1, Example 2, and Example 3
for sheet_name in ['Example 1', 'Example 2', 'Example 3']:
    data = read_excel_data(file_path, sheet_name)
    plot_original_data(data, f"Original Data - {sheet_name}")
    plot_smooth_heatmap(data, f"Heatmap of % Vol. Wassergehalt - {sheet_name}")
