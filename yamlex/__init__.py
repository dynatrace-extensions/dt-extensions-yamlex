import typer    

from yamlex.cli import app, join, split


app.command(name="j", hidden=True)(join)
app.command(name="s", hidden=True)(split)


if __name__ == "__main__":
    app()
