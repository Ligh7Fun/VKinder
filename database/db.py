from sqlalchemy.orm import sessionmaker
import sqlalchemy as sq
from database.models import Base
from database.models import User, Status, ViewData
from dotenv import load_dotenv
import os

load_dotenv()


class DataBase:

    def __init__(self):
        # Базовый класс для моделей SQLAlchemy
        self.Base = Base
        # Создание объекта Engine для взаимодействия с базой данных
        self.engine = sq.create_engine(os.getenv('DSN'))
        # Создание класса сессии для работы с базой данных
        self.Session = sessionmaker(bind=self.engine)
        # Создание объекта сессии, для работы с данными в базе
        self.session = self.Session()

    def create_tables(self):
        """
        Создать таблицы в базе.

        Args:
            None.

        Returns:
            None
        """
        self.Base.metadata.create_all(self.engine)

    def drop_tables(self) -> None:
        """
        Удалить все таблицы из базы.

        Args:
            None.

        Returns:
            None.
        """
        self.Base.metadata.drop_all(self.engine)

    def add_status(self, status: str) -> None:
        """
        Добавить новый статус в базу.

        Args:
            status (str): Название добавляемого статуса.

        Returns:
            None
        """
        self.session.add(Status(name=status))
        self.session.commit()

    def add_user(self, self_id: int) -> None:
        """
        Добавить пользователя с указанным VK идентификатором.

        Args:
            vk_id: Идентификатор пользователя VK.

        Returns:
            None
        """
        user = self.session.query(User).filter_by(vk_id=self_id).all()
        if not user:
            self.session.add(User(vk_id=self_id))
            self.session.commit()

    def add_like(self, self_id: int, user_id: int) -> None:
        """
        Добавить предложенного пользователя в список
        со статусом "лайк"(избранное).

        Args:
            self_id (int): ID пользователя, который добавляет
            user_id (int): ID пользователя, которого добавляют

        Returns:
            None.
        """
        self.session.add(ViewData(
            vk_id=self_id, viewed_vk_id=user_id, status_id=1))
        self.session.commit()

    def add_dislike(self, self_id: int, user_id: int) -> None:
        """
        Добавить предложенного пользователя в список
        со статусом "дизлайк"(черный список).

        Args:
            self_id (int): ID пользователя, который добавляет
            user_id (int): ID полтзователя, которого добавляют

        Returns:
            None.
        """
        self.session.add(ViewData(
            vk_id=self_id, viewed_vk_id=user_id, status_id=2))
        self.session.commit()

    def change_status(self,
                      self_id: int,
                      user_id: int,
                      new_status_id: int
                      ) -> None:
        """Меняет статус у выбранного пользователя

        Args:
            self_id (int): ID пользователя, который добавляет
            user_id (int): ID полтзователя, которого добавляют
            new_status_id (int): ID нового статуса

        Returns:
            None
        """
        obj = self.session.query(ViewData).filter_by(
            vk_id=self_id,
            viewed_vk_id=user_id).first()
        # Если статус отличается, то меняем, если нет, ничего не делаем
        if obj.status_id != new_status_id:
            obj.status_id = new_status_id
            self.session.commit()
