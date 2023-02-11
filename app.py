import redis
import json
import os
from dotenv import load_dotenv
from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS

load_dotenv()

redisHost = os.environ.get("redis-host") or 'localhost'
redisPort = os.environ.get("redis-port") or 6379

print("Attempting to connecting to redis host: ", redisHost)

app = Flask(__name__)
CORS(app)
api = Api(app)

redisClient = redis.Redis(host=redisHost, port=redisPort)

templatePreference = {
  'id': 'user:unknown',
  'label': '',
  'recentlyViewed': [],
  'darkMode': False,
  'pinMenu': [],
  'favorites': [],
}

class PreferencesResource(Resource):
  def get(self):
    id = str(request.args.get('id'))

    if not id:
      return "Must supply id", 400

    retrievedPreferenceString = redisClient.get(id)

    if not retrievedPreferenceString:
      return {'preference': {**templatePreference, **{ 'id': id }}}, 200

    retrievedPreference = json.loads(retrievedPreferenceString)
    preference = {**templatePreference, **retrievedPreference}

    return {'preference': preference}, 200
  
  def delete(self):
    id = str(request.args.get('id'))

    if not id:
      return "Must supply id", 400

    redisClient.delete(id)

    return {'message': "Deleted"}, 200

  def patch(self):
    incomingPreference = request.json

    if not incomingPreference:
      return {"error": "Nothing to update"}, 500

    id = incomingPreference.get("id")

    if not id:
      return {"error": "Must supply an id to change"}, 500

    retrievedPreferenceString = redisClient.get(id)

    retrievedPreference = {}

    if retrievedPreferenceString:
      retrievedPreference = json.loads(retrievedPreferenceString)

    preference = {**templatePreference, **retrievedPreference, **incomingPreference}

    redisClient.set(id, json.dumps(preference))

    return {'preference': preference}, 200

class HistoryResource(Resource):
  def get(self):
    id = request.args.get('id')

    if not id:
      return "Must supply id", 400

    retrievedPreferenceString = redisClient.get(id)

    if not retrievedPreferenceString:
      return {'history': []}, 404

    retrievedPreference = json.loads(retrievedPreferenceString)
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

    retrievedPreferenceString = redisClient.get(id)

    if not retrievedPreferenceString:
      return {'history': []}, 404

    preference = json.loads(retrievedPreferenceString)

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