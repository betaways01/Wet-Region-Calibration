from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from matplotlib.colors import ListedColormap, BoundaryNorm
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

@app.route('/')
def home():
    return "Heatmap API is running."

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    file = request.files['image']
    image = Image.open(file)
    rows = int(request.form.get('rows', 15))
    cols = int(request.form.get('cols', 15))
    grid_image = draw_grid(image, rows, cols)
    buf = io.BytesIO()
    grid_image.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/generate_heatmap', methods=['POST'])
def generate_heatmap():
    data = request.json.get('data')
    rows = int(request.json.get('rows'))
    cols = int(request.json.get('cols'))
    file = request.files['image']
    image = Image.open(file)
    grid = pd.DataFrame(data).reindex(index=np.arange(rows), columns=np.arange(cols))
    heatmap = plot_heatmap(grid, "Heatmap of % Volumetrischer Wassergehalt", image)
    return send_file(heatmap, mimetype='image/png')


def create_empty_grid(rows, cols):
    return pd.DataFrame(np.nan, index=np.arange(rows), columns=np.arange(cols))

def calculate_summary_statistics(data):
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

def plot_heatmap(data, title, image):
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
    ax.imshow(image, extent=[0, grid_size[1], grid_size[0], 0])
    contourf = ax.contourf(grid_x, grid_y, grid_z, levels=levels, cmap=cmap, norm=norm, alpha=0.9, extend='both')

    cbar_ax = fig.add_axes([0.95, 0.52, 0.01, 0.25])
    cbar = fig.colorbar(contourf, cax=cbar_ax, ticks=levels)
    cbar.ax.set_yticklabels([str(level) for level in levels])
    cbar.set_label('% Vol. Wassergehalt', fontsize=8)
    cbar.ax.tick_params(labelsize=8)

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

    ax.set_title(title)
    ax.set_xlim([0, grid_size[1]])
    ax.set_ylim([grid_size[0], 0])
    ax.axis('off')
    plt.subplots_adjust(left=0.05, right=0.9, top=0.95, bottom=0.05)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf

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

    font = ImageFont.truetype("arial.ttf", 10)  # Ensure arial.ttf is available in your environment
    for i in range(cols):
        draw.text((i * width // cols + width // (2 * cols), 0), f'{i}', fill=(0, 0, 0), font=font)
    for j in range(rows):
        draw.text((0, j * height // rows + height // (2 * rows)), f'{j}', fill=(0, 0, 0), font=font)

    return img

if __name__ == '__main__':
    app.run(debug=True)
