import sqlalchemy as sq
from sqlalchemy.orm import declarative_base


# Создание базового класса для моделей SQLAlchemy
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, unique=True)
    state = sq.Column(sq.Text, default=None)
    current_state = sq.Column(sq.Text, default=None)  

class Favorites(Base):
    __tablename__ = 'favorites'

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user.id'))
    profile_id = sq.Column(sq.Integer)
    status = sq.Column(sq.String(255)) 


class Search(Base):
    __tablename__ = 'search'

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, sq.ForeignKey('user.vk_id'))
    age_from = sq.Column(sq.Integer, default=None)
    age_to = sq.Column(sq.Integer, default=None)
    sex = sq.Column(sq.Text, default=None)
    city = sq.Column(sq.Text, default=None)
    results = sq.Column(sq.JSON, default=None)
    results_index = sq.Column(sq.Integer, default=0) 
    



class Status(Base):
    __tablename__ = 'status'

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=10), unique=True)


class ViewData(Base):
    __tablename__ = 'viewdata'

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, sq.ForeignKey('user.vk_id'))
    viewed_vk_id = sq.Column(sq.Integer)
    status_id = sq.Column(sq.Integer, sq.ForeignKey('status.id'))

