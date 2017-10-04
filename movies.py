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

def save_ratings(tx, user_id, genre, ratings):
    """ Merge the User node by User ID
    """
    tx.run("MERGE (u:User {userId: $user_id})", user_id=user_id)

    """ Save each rating
    """
    for movieId, rating in ratings.items():
        tx.run("MATCH (u:User {userId: $user_id}) "
               "MATCH (m:Movie {imdbId: $movie_id}) "
               "MERGE (u)-[r:RATED]->(m) "
               "SET r.rating = $rating ", user_id=user_id, movie_id=movieId, rating=rating)

def get_recommendation(tx, user_id, genre):
    """ Get a recommendation
    """
    record = tx.run("MATCH (g:Genre {name: $genre}) "
                    "MATCH (u:User {userId: $user_id})-[x:RATED]->()<-[y:RATED]-(other) "
                    "WITH g, u, other, COUNT(*) AS numbermovies, SUM(x.rating * y.rating) AS xyDotProduct, "
                    "SQRT(REDUCE(xDot = 0.0, a IN COLLECT(x.rating) | xDot + a^2)) AS xLength, "
                    "SQRT(REDUCE(yDot = 0.0, b IN COLLECT(y.rating) | yDot + b^2)) AS yLength "
                    "WITH g, u, other, xyDotProduct / (xLength * yLength) AS sim "
                    "ORDER BY sim DESC LIMIT 10 "
                    "MATCH (other)-[r:RATED]->(recommendation)-[:IN_GENRE]->(g) "
                    "WHERE r.rating >= 4 AND NOT (u)-[:RATED]->(recommendation) "
                    "RETURN g, recommendation, count(*) as occurrences "
                    "ORDER BY occurrences DESC LIMIT 1", user_id=user_id, genre=genre).single()

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

@app.route("/recommend/<genre>/next")
def get_next_movie(genre):
    with driver.session() as session:
        ignore = request.args.get("rated", "").split(",")
        genre, movie = session.read_transaction(match_random_movie, genre, ignore)
        return jsonify(movie)

@app.route("/recommend/<genre>/results")
def get_results(genre):
    with driver.session() as session:
        user_id = str(uuid.uuid4())
        param = request.args.get("ratings", "")
        ratings = json.loads(param)

        session.write_transaction(save_ratings, user_id, genre, ratings)

        genre, movie = session.read_transaction(get_recommendation, user_id, genre)

        return render_template("result.html", genre=genre, movie=movie)

