import sqlalchemy as sq
from sqlalchemy.orm import declarative_base


# Создание базового класса для моделей SQLAlchemy
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, unique=True)
    state = sq.Column(sq.Text, default=None)


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
