import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
class Mongo:
    _instance = None

    def __new__(cls, app=None):
        if not cls._instance:
            cls._instance = super(Mongo, cls).__new__(cls)
            if app:
                cls._instance.init_app(app)
        return cls._instance

    def init_app(self, app):
        mongo_uri = os.environ.get("MONGO_URI")
        if not mongo_uri:
            raise ValueError("MONGO_URI çevre değişkeni tanımlı değil!")
        self.client = MongoClient(mongo_uri)
        database_name = mongo_uri.split("/")[-1].split("?")[0]
        self.db = self.client[database_name]

    def get_db(self):
        return self.db
