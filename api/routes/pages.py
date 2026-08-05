"""Marketing / informational pages."""

from flask import render_template


def register(app):
    @app.route("/")
    def index():
        return render_template("home.html")

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/contact")
    def contact():
        return render_template("contact.html")
