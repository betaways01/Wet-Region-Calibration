import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
import pandas as pd
import numpy as np
import base64
from PIL import Image
import io
import plotly.express as px
import datetime

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def split_image(image, rows, cols):
    img = Image.open(image)
    width, height = img.size
    tile_width = width // cols
    tile_height = height // rows

    images = []
    for r in range(rows):
        row_images = []
        for c in range(cols):
            box = (c*tile_width, r*tile_height, (c+1)*tile_width, (r+1)*tile_height)
            row_images.append(img.crop(box))
        images.append(row_images)
    
    return images

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def create_grid_layout(image_slices, rows, cols):
    layout = []
    for r in range(rows):
        row = []
        for c in range(cols):
            img_base64 = image_to_base64(image_slices[r][c])
            img_html = html.Img(src='data:image/png;base64,{}'.format(img_base64), 
                                style={'width': '100%', 'height': '100%'})
            button = dbc.Button(img_html, id=f'button-{r}-{c}', n_clicks=0, style={'padding': '0'})
            row.append(button)
        layout.append(dbc.Row(row))
    return layout

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dcc.Upload(
                id='upload-image',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select an Image')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                multiple=False
            ),
            html.Div(id='output-image-upload'),
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Slider(
                id='rows-slider',
                min=5,
                max=30,
                step=1,
                value=15,
                marks={i: str(i) for i in range(5, 31)},
                tooltip={"placement": "bottom", "always_visible": True},
            ),
            html.Div(id='rows-slider-output')
        ], width=6),
        dbc.Col([
            dcc.Slider(
                id='cols-slider',
                min=5,
                max=30,
                step=1,
                value=15,
                marks={i: str(i) for i in range(5, 31)},
                tooltip={"placement": "bottom", "always_visible": True},
            ),
            html.Div(id='cols-slider-output')
        ], width=6)
    ]),
    html.Div(id='image-grid')
])

@app.callback(
    [Output('rows-slider-output', 'children'),
     Output('cols-slider-output', 'children')],
    [Input('rows-slider', 'value'),
     Input('cols-slider', 'value')]
)
def update_slider_output(rows, cols):
    return f'Rows: {rows}', f'Columns: {cols}'

@app.callback(
    Output('output-image-upload', 'children'),
    [Input('upload-image', 'contents')],
    [State('upload-image', 'filename'),
     State('upload-image', 'last_modified')]
)
def update_output(content, name, date):
    if content is not None:
        return html.Div([
            html.H5(name),
            html.H6(datetime.datetime.fromtimestamp(date)),
            html.Img(src=content, style={'maxWidth': '100%', 'maxHeight': '400px'}),
        ])

@app.callback(
    Output('image-grid', 'children'),
    [Input('upload-image', 'contents'),
     Input('rows-slider', 'value'),
     Input('cols-slider', 'value')]
)
def display_image_grid(contents, rows, cols):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        image = io.BytesIO(decoded)
        image_slices = split_image(image, rows, cols)
        grid_layout = create_grid_layout(image_slices, rows, cols)
        return grid_layout
    return []

if __name__ == '__main__':
    app.run_server(debug=True)
