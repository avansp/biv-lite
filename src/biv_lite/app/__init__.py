import typer
import biv_lite.app.measures as bm
import biv_lite.app.plots as bp
import biv_lite.app.ui as ui

app = typer.Typer(add_completion=False,
                  help="Simple tools to load, visualise, and temporal filter biventricular models.")
app.add_typer(bp.app, name="plot")
app.add_typer(bm.app)
app.add_typer(ui.app)

