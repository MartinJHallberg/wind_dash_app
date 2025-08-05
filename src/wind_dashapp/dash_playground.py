from dash import Dash, dcc, html, Output, Input

app = Dash(__name__)

app.layout = html.Div(
    [
        html.H3("Test RangeSlider"),
        dcc.RangeSlider(
            id="my-slider",
            min=0,
            max=30,
            step=1,
            value=[8, 10, 15, 17, 20],
            pushable=2,
            # allowCross=False
        ),
        html.Div(id="slider-output"),
    ]
)


@app.callback(Output("slider-output", "children"), Input("my-slider", "value"))
def update_output(value):
    return f"Selected values: {value}"


if __name__ == "__main__":
    app.run(debug=True)
