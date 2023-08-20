from flask import Flask
from db.mongo.config.mongo import Mongo
from routes.payment.payment import payment
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

mongo = Mongo(app)

app.register_blueprint(payment, url_prefix='/payment')
