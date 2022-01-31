# Requirements

- database goes up with *docker-compose -f ./db.yaml up*
- database credentials are in *db.yaml*
- request headers must have *Content-Type: application/json* and *Api-Key: qwerty*
- api-key is stored in *secret.py* (for demo purposes)
- POST requests only accepted by the root endpoint (http://127.0.0.1:5000)