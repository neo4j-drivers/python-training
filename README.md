# Building Real-time Web Apps with Neo4j using Python

To install requirements:
```bash
pip install -r requirements.txt
```

To run:
```bash
FLASK_APP=movies.py flask run
```
Or run in debug mode for live updates.
```bash
 FLASK_APP=movies.py FLASK_DEBUG=1 flask run
```
To view, browse to http://localhost:5000/


## Branches
- `01-getting-started` - Connecting to Neo4j
- `02-read-queries` - Run a basic read query inside a read transaction
- `03-query-parameters`- Use query parameter to find a random movie related to a movie
- `04-write-transactions`- Save the User's ratings into the graph using a write transaction, then provide a recommendation based on the similarity in taste to other users
