from shiny import ui, render, reactive, App
import pandas as pd
from pathlib import Path
from plots import temp_distirbution, daily_error

infile = Path(__file__).parent / "weather.csv"
weather = pd.read_csv(infile)
weather["error"] = weather["observed_temp"] - weather["forecast_temp"]


def val_box_col(id, n_boxes):
    width = 12 // n_boxes
    card_title = id.replace("_", " ").title()
    return ui.column(width, ui.value_box(card_title, ui.output_text(id)))


boxes = ["hot_days", "cold_days", "mean_error"]

data_tab = ui.nav("Data", ui.output_data_frame("data"))
error_tab = ui.nav(
    "Error",
    ui.row([val_box_col(box, len(boxes)) for box in boxes]),
    ui.row(
        ui.column(
            6,
            ui.card(
                ui.card_header("Distribution"),
                ui.output_plot("error_distribution"),
            ),
        ),
        ui.column(
            6,
            ui.card(
                ui.card_header("Error by day"),
                ui.output_plot("error_by_day"),
                ui.input_slider("alpha", "Plot Alpha", value=0.5, min=0, max=1),
            ),
        ),
    ),
)

app_ui = ui.page_fluid(
    ui.panel_title("Weather error"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_date_range("dates", "Date", start="2022-01-01", end="2022-01-30"),
            ui.input_selectize(
                "cities",
                "Select Cities",
                weather["city"].unique().tolist(),
                selected="BUFFALO",
                multiple=True,
            ),
            width=3,
        ),
        ui.panel_main(
            ui.navset_tab(
                error_tab,
                data_tab,
            )
        ),
    ),
)


def server(input, output, session):
    @reactive.Calc
    def filtered_data() -> pd.DataFrame:
        return filter_weather(weather, input.cities(), input.dates())

    @render.plot
    def error_distribution():
        return temp_distirbution(filtered_data())

    @render.plot
    def error_by_day():
        return daily_error(filtered_data(), input.alpha())

    @render.data_frame
    def data():
        return filtered_data()

    @render.text
    def mean_error():
        mean_error = filtered_data()["error"].mean()
        return round(mean_error, 2)

    @render.text
    def hot_days():
        hot_days = filtered_data()["error"] > 0
        return sum(hot_days)

    @render.text
    def cold_days():
        hot_days = filtered_data()["error"] < 0
        return sum(hot_days)


def filter_weather(data, cities, dates):
    df = data.copy()
    df = df[df["city"].isin(cities)]
    df["date"] = pd.to_datetime(df["date"])
    dates = pd.to_datetime(dates)
    df = df[(df["date"] > dates[0]) & (df["date"] <= dates[1])]
    return df


app = App(app_ui, server)
