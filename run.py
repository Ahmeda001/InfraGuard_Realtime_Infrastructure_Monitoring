from app import create_app
from app.extensions import db
from config import Config

app = create_app(Config)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
