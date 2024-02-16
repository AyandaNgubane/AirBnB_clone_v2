#!/usr/bin/python3
"""Starts a Flask web application
"""
from flask import Flask
from flask import render_template
from models import storage
from models.state import State

if __name__ == '__main__':
    app = Flask(__name__)


    @app.route('/states_list', strict_slashes=False)
    def states_list():
        """Display a HTML page of the States
        """
        states = storage.all(State).values()
        return render_template('7-states_list.html', states=states)

    @app.teardown_appcontext
    def teardown_db(error):
        """Closes the database again at the end of the request.
        """
        storage.close()
