from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast
import redis
import json
from redis.commands.json.path import Path

redisClient = redis.Redis(host='localhost', port=6379)

def seed():
  users = [{
      'id': 'user:1',
      'label': 'User 1',
      'recentlyViewed': [],
      'darkMode': 'false',
      'pinMenu': [],
      'favorites': [],
    },
    {
      'id': 'user:2',
      'label': 'User 2',
      'recentlyViewed': [],
      'darkMode': 'false',
      'pinMenu': [],
      'favorites': [],
    }
  ]

  for user in users:
    redisClient.set(user['id'], json.dumps(user))

if __name__ == "__main__":
  seed()