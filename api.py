import redis
import json
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from redis.commands.json.path import Path

app = Flask(__name__)
api = Api(app)
redisClient = redis.Redis(host='localhost', port=6379)

templatePreference = {
  'id': 'user:unknown',
  'label': '',
  'recentlyViewed': [],
  'darkMode': 'false',
  'pinMenu': [],
  'favorites': [],
}

class PreferencesResource(Resource):
  def get(self):
    id = request.args.get('id')

    if not id:
      return "Must supply id", 400

    retrievedPreference = json.loads(redisClient.get(id))
    preference = {**templatePreference, **retrievedPreference}

    return {'preference': preference}, 200

  def patch(self):
    incomingPreference = request.json

    if not incomingPreference:
      return {"error": "Nothing to update"}, 500

    id = incomingPreference.get("id")

    if not id:
      return {"error": "Must supply an id to change"}, 500

    retrievedPreference = json.loads(redisClient.get(id))
    preference = {**templatePreference, **retrievedPreference, **incomingPreference}

    redisClient.set(id, json.dumps(preference))

    return {'preference': preference}, 200

class HistoryResource(Resource):
  def get(self):
    id = request.args.get('id')

    if not id:
      return "Must supply id", 400

    retrievedPreference = json.loads(redisClient.get(id))

    if not retrievedPreference:
      return "No preference found", 400

    history = retrievedPreference.get("recentlyViewed", [])
    
    return {'history': history}, 200

  def put(self):
    incoming = request.json

    if not incoming:
      return {"error": "Nothing to update"}, 500

    id = incoming.get("id")

    if not id:
      return {"error": "Must supply an id to change"}, 500

    incomingRecentlyViewed = incoming.get("viewed")

    preference = json.loads(redisClient.get(id))

    if not preference:
      preference = templatePreference
      preference["id"] = id

    if preference and incomingRecentlyViewed:
      history = preference['recentlyViewed'] or []
      history = [i for i in history if not (i['id'] == incomingRecentlyViewed["id"])]
      history.insert(0, incomingRecentlyViewed)
      preference['recentlyViewed'] = history[:10]

    redisClient.set(id, json.dumps(preference))

    return {'history': preference}, 200

api.add_resource(PreferencesResource, '/preferences')
api.add_resource(HistoryResource, '/history')

if __name__ == "__main__":
  app.run()