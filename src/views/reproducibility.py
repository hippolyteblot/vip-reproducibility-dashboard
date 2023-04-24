from dash import html, callback, Input, Output, dcc, ctx
import dash_bootstrap_components as dbc
import plotly.express as px
from skimage import io
import os

folder_1 = "src/assets/images/image1/"
folder_2 = "src/assets/images/image2/"
img_1 = io.imread(folder_1 + "frame0.png")
fig_img_1 = px.imshow(img_1)
img_2 = io.imread(folder_1 + "frame0.png")
fig_img_2 = px.imshow(img_2)


def layout():
    return html.Div(
        children=[

            html.Div(
                children=[
                    html.Div(
                        children=[
                            html.Div(
                                children=dcc.Graph(
                                    id="image1-chart",
                                    figure=fig_img_1,
                                    config={"displayModeBar": False},
                                ),
                                className="card row-graph",
                            ),
                            html.Div(
                                children=dcc.Graph(
                                    id="image2-chart",
                                    figure=fig_img_2,
                                    config={"displayModeBar": False},
                                ),
                                className="card row-graph",
                            ),
                        ],
                        style={"width": "100%", "display": "flex", "justifyContent": "space-between"},
                    ),

                    html.Div(
                        children=[
                            html.Div(
                                children=[
                                    html.Button(
                                        children="<-",
                                        id="previous-image",
                                        className="button",
                                    ),
                                    html.Div(
                                        children="0/" + str(len(os.listdir(folder_1))),
                                        id="image-index",
                                        className="button",
                                    ),

                                    html.Button(
                                        children="->",
                                        id="next-image",
                                        className="button",
                                    ),

                                    html.Div(
                                        children=[
                                            html.P("Similarity ratio :"),
                                            html.P(
                                                children="0.0",
                                                id="similarity-ratio"
                                            ),
                                        ],
                                        style={'display': 'flex', 'gap': '10px'}
                                    ),

                                ],
                                style={"width": "100%", "display": "flex", "gap": "10px"},
                            ),
                        ],
                    ),
                    html.Div(
                        children=[
                            html.Div(
                                children=[
                                    html.P(
                                        children=(
                                            "The yellow part of the next image represents the difference between the "
                                            "two input images."
                                        ),
                                    ),
                                    dcc.Graph(
                                        id="difference-subimage",
                                        figure=fig_img_1,
                                        config={"displayModeBar": False},

                                    ),
                                ],
                                className="wrapper",
                            ),
                        ],

                    ),
                ],
                className="wrapper",
            ),
        ]
    )


@callback(
    Output("image1-chart", "figure"),
    Output("image2-chart", "figure"),
    Output("previous-image", "n_clicks"),
    Output("next-image", "n_clicks"),
    Output("image-index", "children"),
    Output("difference-subimage", "figure"),
    Output("similarity-ratio", "children"),
    Output("similarity-ratio", "style"),
    Input("previous-image", "n_clicks"),
    Input("next-image", "n_clicks"),
    Input("image1-chart", "figure"),
    Input("image2-chart", "figure"),
)
def update_charts(previous, next, fig_img_1, fig_img_2):
    layout_id = ctx.triggered_id if not None else 'No clicks yet'

    if previous is None:
        previous = 0
    if next is None:
        next = 0
    index = next - previous

    # get the length of the folder
    length = len(os.listdir(folder_1))

    if index < 0:
        index = 0
        previous = 0
        next = 0
    elif index >= length:
        index = length - 1
        previous = 0
        next = length - 1

    img_1 = io.imread(folder_1 + f"frame{index}.png")
    img_2 = io.imread(folder_2 + f"frame{index}.png")

    # get equivalence ratio
    ratio = get_equivalence_ratio(img_1, img_2)

    # round the ratio to 3 decimals
    ratio = round(ratio, 3)
    ratio_color = "green"
    if ratio != 100:
        ratio_color = "red"

    diff_image = get_diff_image(img_1, img_2)
    diff_fig = px.imshow(diff_image)

    fig_img_1 = px.imshow(img_1)
    fig_img_2 = px.imshow(img_2)

    return fig_img_1, fig_img_2, previous, next, f"{index + 1}/{length}", diff_fig, f"{ratio}%", {"color": ratio_color}


def get_equivalence_ratio(img_1, img_2):
    different_pixels = 0
    img1_array = img_1.flatten()
    img2_array = img_2.flatten()
    for i in range(len(img1_array)):
        if img1_array[i] != img2_array[i]:
            different_pixels += 1

    return (1 - (different_pixels / len(img1_array))) * 100


def get_diff_image(img_1, img_2):
    # return an image where the different pixels are colored in red
    new_img = img_1.copy()
    for i in range(len(new_img)):
        for j in range(len(new_img[i])):
            red = new_img[i][j][0]
            green = new_img[i][j][1]
            blue = new_img[i][j][2]
            if red != img_2[i][j][0] or green != img_2[i][j][1] or blue != img_2[i][j][2]:
                new_img[i][j][0] = 255
                new_img[i][j][1] = 255
                new_img[i][j][2] = 0

    return new_img
