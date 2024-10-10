import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from matplotlib.colors import ListedColormap, BoundaryNorm
from PIL import Image, ImageDraw
from scipy.spatial import ConvexHull, QhullError

# Function to create an empty grid
def create_empty_grid(rows, cols):
    return pd.DataFrame(np.nan, index=np.arange(rows), columns=np.arange(cols))

# Function to calculate summary statistics
def calculate_summary_statistics(data):
    # Flatten the data and remove NaN values
    values = data.values.flatten()
    values = values[~np.isnan(values)]
    
    summary = {
        'sum_all_boxes': np.sum(values),
        'count_boxes_with_data': len(values),
        'average_all_samples': np.mean(values),
        'no_of_cups_lowest_quarter': np.sum(values <= np.percentile(values, 25)),
        'sum_values_lowest_quarter': np.sum(values[values <= np.percentile(values, 25)]),
        'count_boxes_lowest_quarter': np.sum(values <= np.percentile(values, 25)),
        'average_lowest_quarter': np.mean(values[values <= np.percentile(values, 25)]),
        'distribution_uniformity': (np.mean(values[values <= np.percentile(values, 25)]) / np.mean(values)) * 100
    }
    
    return summary

# Function to plot heatmap
def plot_heatmap(data, title, image):
    values = data.values.flatten()
    grid_size = data.shape

    points = [(i % grid_size[1], i // grid_size[1]) for i, value in enumerate(values) if not np.isnan(value)]
    values_list = [value for value in values if not np.isnan(value)]

    if len(points) < 4:
        st.error("Not enough points to generate the heatmap. Select at least 4 grids.")
        return

    grid_x, grid_y = np.mgrid[0:grid_size[1]:100j, 0:grid_size[0]:100j]
    try:
        grid_z = griddata(points, values_list, (grid_x, grid_y), method='cubic')
    except ValueError:
        st.error("Invalid number of dimensions in xi. Ensure there are values in the selected grids.")
        return

    levels = [0, 9, 16, 20, 25]
    colors = ['yellow', 'limegreen', 'green', 'darkgreen']
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(image, extent=[0, grid_size[1], grid_size[0], 0])
    contourf = ax.contourf(grid_x, grid_y, grid_z, levels=levels, cmap=cmap, norm=norm, alpha=0.9, extend='both')

    # Create a new axis for the color bar
    cbar_ax = fig.add_axes([0.95, 0.52, 0.01, 0.25])  # Adjust the position and size of the color bar
    cbar = fig.colorbar(contourf, cax=cbar_ax, ticks=levels)
    cbar.ax.set_yticklabels([str(level) for level in levels])
    cbar.set_label('% Vol. Wassergehalt', fontsize=8)
    cbar.ax.tick_params(labelsize=8)

    # Calculate summary statistics
    summary = calculate_summary_statistics(data)
    summary_text = '\n'.join([
        f"Sum: {summary['sum_all_boxes']}",
        f"Count: {summary['count_boxes_with_data']}",
        f"Avg: {summary['average_all_samples']:.2f}",
        f"Low Qtr Cups: {summary['no_of_cups_lowest_quarter']}",
        f"Low Qtr Sum: {summary['sum_values_lowest_quarter']}",
        f"Low Qtr Count: {summary['count_boxes_lowest_quarter']}",
        f"Low Qtr Avg: {summary['average_lowest_quarter']:.2f}",
        f"DUlq: {summary['distribution_uniformity']:.2f}%"
    ])
    fig.text(0.92, 0.8, summary_text, fontsize=8, bbox=dict(facecolor='white', alpha=0.5), ha='left')

    # Add cell position labels outside the image
    for i in range(grid_size[1]):
        ax.text(i + 0.5, grid_size[0] + 0.5, f'{i}', ha='center', va='center', fontsize=8, color='black')
    for j in range(grid_size[0]):
        ax.text(-0.5, j + 0.5, f'{j}', ha='center', va='center', fontsize=8, color='black')

    ax.set_title(title)
    ax.set_xlim([-1, grid_size[1]])
    ax.set_ylim([grid_size[0], -1])
    ax.axis('off')
    plt.subplots_adjust(left=0.1, right=0.9, top=0.95, bottom=0.1)  # Adjust to make room for the summary text and colorbar
    st.pyplot(fig)

# Function to draw grid on image
def draw_grid(image, rows, cols):
    img = image.copy()
    draw = ImageDraw.Draw(img)
    width, height = img.size

    for i in range(1, cols):
        x = i * width // cols
        draw.line([(x, 0), (x, height)], fill=(0, 0, 0), width=1)

    for i in range(1, rows):
        y = i * height // rows
        draw.line([(0, y), (width, y)], fill=(0, 0, 0), width=1)

    return img

# Streamlit app
st.title("Interactive Heatmap Generator")

# User uploads image
uploaded_file = st.file_uploader("Upload Land Image", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Land Image", use_column_width=True)
    
    # User selects the number of rows and columns for the grid
    st.write("### Adjust Grid Size")
    rows = st.slider("Number of rows", min_value=5, max_value=30, value=15)
    cols = st.slider("Number of columns", min_value=5, max_value=30, value=15)
    
    # Create grid and display it
    grid_image = draw_grid(image, rows, cols)
    st.image(grid_image, caption="Grid Overlay", use_column_width=True)

    # Create an empty grid
    grid = create_empty_grid(rows, cols)

    # User input for entering values
    st.write("### Enter Values for Selected Cells")
    edited_grid = st.data_editor(grid, use_container_width=True)

    # Generate heatmap
    if st.button("Generate Heatmap"):
        plot_heatmap(edited_grid, "Heatmap of % Volumetrischer Wassergehalt", image)
