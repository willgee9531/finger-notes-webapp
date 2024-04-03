from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    school_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    country = db.Column(db.String(100), nullable=False)
    # password = db.Column()

    def __repr__(self):
        return f'<{self.id}: {self.school_name} - {self.email} - {self.country}>'



# class Upload(db.Model):
#     pass
