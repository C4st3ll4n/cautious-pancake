from flask import Flask
from flask_migrate import Migrate

from models import db, init_app
from routes import order_blueprint

app = Flask(__name__)

app.config["SECRET_KEY"] = "7wFGaxYX93QChF22dLikkw"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./database/order.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

init_app(app)

migrate = Migrate(app, db)

app.register_blueprint(order_blueprint)
if __name__ == '__main__':
    app.run(debug=True, port=5003)
