#!/usr/bin/python3
"""Starts a Flask web application
"""
from flask import Flask
from flask import render_template
from models import storage
from models.state import State

if __name__ == "__main__":
    app = Flask(__name__)


    @app.route("/states_list", strict_slashes=False)
    def states_list():
        """Displays an HTML page with a list of all State objects in DBStorage.
        States are sorted by name.
        """
        states = storage.all(State).values()
        return render_template("7-states_list.html", states=states)


    @app.teardown_appcontext
    def teardown(exc):
        """Remove the current SQLAlchemy session."""
        storage.close()


    app.run(host="0.0.0.0")
