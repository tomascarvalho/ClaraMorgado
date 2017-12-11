from sqlalchemy import Column, String, Integer, Sequence, Text
from sqlalchemy.ext.declarative import declarative_base
from config.config import engine
from werkzeug.security import generate_password_hash, \
     check_password_hash
from flask_login import UserMixin

Base = declarative_base()

class Painting(Base):
    __tablename__ = 'paintings'
    id = Column(Integer, Sequence('painting_id_seq'), primary_key = True)
    name = Column(String(128))
    style = Column(String(512))
    price = Column(Integer)
    date = Column(Integer)
    size = Column(String(128))
    observations = Column(String(512))
    image = Column(Text)

    def __repr__(self):
        return "<Paiting(painting_id='%s' name='%s' style='%s image='%s')>" % (self.id, self.name, self.style, self.image)

class Administrator(Base, UserMixin):
    __tablename__ = 'admins'
    id = Column(Integer, Sequence('admin_id_seq'), primary_key = True)
    email = Column(String(128))
    pw_hash = Column(String(512))
    session_token = Column(String(128, convert_unicode=True))

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

Base.metadata.create_all(engine)
