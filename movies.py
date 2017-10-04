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

def match_random_movie(tx, genre, ignore):
    cypher = "MATCH (g:Genre)<-[:IN_GENRE]-(m:Movie) WHERE g.name = $genre "

    if ignore:
        cypher += " AND NOT m.imdbId IN $ignore "

    cypher += "RETURN g, m  ORDER BY RAND() LIMIT 1"

    record = tx.run(cypher, genre=genre, ignore=ignore).single()
    return dict(record[0]), dict(record[1]) if record else None

@app.route("/")
def get_index():
    """ Show the index page.
    """
    with driver.session() as session:
        return render_template("index.html", genres=session.read_transaction(match_genres))

@app.route("/recommend/<genre>")
def start_recommendation(genre):
    """ Get a movie within this genre at random
    """
    with driver.session() as session:
        genre, movie = session.read_transaction(match_random_movie, genre, [])
        return render_template("rate.html", genre=genre, movie=movie)
