#!/usr/bin/env python
# coding: utf-8
import json
import uuid
from flask import Flask, abort, render_template, request, jsonify
from neo4j.v1 import GraphDatabase

app = Flask(__name__)

# Set up a driver for the recommendation graph database.
uri = "bolt://54.173.14.47:32973"
username = "neo4j"
password = "rounds-discontinuances-remedy"

driver = GraphDatabase.driver(uri, auth=(username, password))

def match_genres(tx):
    return tx.run("MATCH (genre:Genre) "
                  "RETURN genre.name AS name "
                  "ORDER BY genre.name").data()
@app.route("/")
def get_index():
    """ Show the index page.
    """
    with driver.session() as session:
        return render_template("index.html", genres=session.read_transaction(match_genres))
