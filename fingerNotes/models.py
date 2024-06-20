from datetime import datetime
from fingerNotes import db, login_manager
from flask_login import UserMixin


"""
platform = User(school_name="Platform", email="platform@email.com", country="Nigeria", password="123")
phidel = User(school_name="Phidel", email="phidel@email.com", country="Nigeria", password="123")

upload1 = UploadInfo(session="2023/2024", term="Third term", grade="Grade 7", user_id=phidel.id)
upload2 = UploadInfo(session="2023/2024", term="Third term", grade="Grade 8", user_id=phidel.id)

db.session.add(upload1)
db.session.add(upload2)
db.session.commit()

file1 = File(ppsx_file="thisIsAPowerPointSlide", upload_id=upload1.id)
file2 = File(ppsx_file="thisIsAPowerPointSlide2", upload_id=upload1.id)

db.session.add(file1)
db.session.add(file2)
db.session.commit()

---------------------------------------------------

uploads = UploadInfo.query.all()
for upload in uploads:
    for file in upload.files:
        print(f"{upload.session} - {upload.term} - {upload.grade}")   
        print(f"slide {file.id} - {file.ppsx_file}")
    print("-" *10)

"""

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    school_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    country = db.Column(db.String(100), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    password = db.Column(db.String(60), nullable=False)
    telephone_no = db.Column(db.String(14))
    school_address = db.Column(db.String(255))
    school_website = db.Column(db.String(255))
    upload_infos = db.relationship('UploadInfo', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.id}: {self.school_name} - {self.email} - {self.country}>'
    

class UploadInfo(db.Model):
    __tablename__ = 'uploads'
    id = db.Column(db.Integer, primary_key=True)
    session = db.Column(db.String(20), nullable=False)
    term = db.Column(db.String(20), nullable=False)
    grade = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='pending')
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_upload_user'), nullable=False)
    files = db.relationship('File', backref='upload_info', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<UploadInfo: {self.session} - {self.term} - {self.grade}>'
    

class File(db.Model):
    __tablename__ = 'file'
    id = db.Column(db.Integer, primary_key=True)
    ppsx_file = db.Column(db.String(20), nullable=False)
    upload_id = db.Column(db.Integer, db.ForeignKey('uploads.id', name='fk_file_upload'), nullable=False)

    def __repr__(self):
        return f'<ppsx - {self.ppsx_file}>'
    

class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f'<admin {self.id}: {self.password}>'
    


