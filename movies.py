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

@app.route("/")
def get_index():
    """ Read-only queries should be run within a read_transaction
    """
    return "Hello, world!"
