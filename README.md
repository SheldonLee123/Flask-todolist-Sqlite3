# Flask-todolist-Sqlite3
Later versions will use the MySQL database

virtualenv venv
source venv/bin/activate

pip install -r requirement.txt

python
from app import db
db.create_all()

python app.py
