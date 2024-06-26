from shiny import Inputs, Outputs, Session, App, reactive, render, req, ui

app_ui = ui.page_fluid(
    ui.column(
        3,
        ui.card(
            ui.card_header("Slider card"),
            ui.input_slider("n", "N", 0, 100, 20),
            ui.output_text_verbatim("txt"),
            fill=False,
        ),
    )
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def txt():
        return f"n*2 is {input.n() * 2}"


app = App(app_ui, server)
