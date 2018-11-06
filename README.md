# Flask-todolist-Sqlite3
Later versions will use the MySQL database

virtualenv env
source env/bin/activate

python
from app import db
db.create_all()

python app.run
