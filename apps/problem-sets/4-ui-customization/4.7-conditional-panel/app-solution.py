from shiny import ui, render, reactive, App
import pandas as pd
from pathlib import Path
from plots import temp_distirbution, daily_error

infile = Path(__file__).parent / "weather.csv"
weather = pd.read_csv(infile)
weather["error"] = weather["observed_temp"] - weather["forecast_temp"]

data_tab = ui.nav("Data", ui.output_data_frame("data"))
error_tab = ui.nav(
    "Error",
    ui.row(
        ui.column(
            4, ui.value_box("Hotter than forecast", ui.output_text("hot_days"))
        ),
        ui.column(
            4, ui.value_box("Colder than forecast", ui.output_text("cold_days"))
        ),
        ui.column(4, ui.value_box("Mean Error", ui.output_text("mean_error"))),
    ),
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
                "states",
                "Select States",
                weather["state"].unique().tolist(),
                selected="CO",
                multiple=True,
            ),
            ui.output_ui("cities_ui"),
            ui.panel_conditional(
                "input.tabs === 'Data'",
                ui.input_selectize(
                    "columns",
                    "Display Columns",
                    choices=weather.columns.tolist(),
                    selected=weather.columns.tolist(),
                    multiple=True,
                ),
            ),
            width=3,
        ),
        ui.panel_main(ui.navset_tab(error_tab, data_tab, id="tabs")),
    ),
)


def server(input, output, session):
    @render.ui
    def cities_ui():
        df = weather.copy()
        df = df[df["state"].isin(input.states())]
        city_options = df["city"].unique().tolist()
        return ui.input_selectize(
            "cities",
            "Select Cities",
            choices=city_options,
            selected=city_options[0],
            multiple=True,
        )

    @reactive.Calc
    def filtered_data() -> pd.DataFrame:
        df = weather.copy()
        df = df[df["city"].isin(input.cities())]
        df["date"] = pd.to_datetime(df["date"])
        dates = pd.to_datetime(input.dates())
        df = df[(df["date"] > dates[0]) & (df["date"] <= dates[1])]
        return df

    @render.plot
    def error_distribution():
        return temp_distirbution(filtered_data())

    @render.plot
    def error_by_day():
        return daily_error(filtered_data(), input.alpha())

    @render.data_frame
    def data():
        return filtered_data().loc[:, input.columns()]

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


app = App(app_ui, server)
