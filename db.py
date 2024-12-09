from app import db
from app import app
from sqlalchemy import inspect

with app.app_context():
    db.session.execute('DROP TABLE IF EXISTS event')
    db.session.commit()

    db.create_all()
    inspector=inspect(db.engine)
    print(inspector.get_table_names())