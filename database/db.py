from sqlalchemy.orm import sessionmaker
import sqlalchemy as sq
from database.models import Base
from database.models import User, Status, ViewData, Search
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

    def add_user(self, self_id: int, state: str = None) -> None:
        """
        Добавить пользователя с указанным VK идентификатором.

        Args:
            self_id: Идентификатор пользователя VK.
            state: Состояние пользователя.
        Returns:
            None
        """
        user = self.session.query(User).filter_by(vk_id=self_id).all()
        if not user:
            self.session.add(User(vk_id=self_id, state=state))
            self.session.commit()

    def get_state_user(self, self_id: int) -> str:
        """
        Получить состояние пользователя.

        Args:
            self_id: ID пользователя VK.
        Returns:
            State: Состояние пользователя
        """
        return self.session.query(User).filter_by(vk_id=self_id).first().state

    def set_state_user(self, self_id: int, state: str) -> None:
        """
        Установить состояние пользователя.

        Args:
            self_id: ID пользователя VK.
            state: Состояние пользователя
        Returns:
            None
        """
        (self.session.query(User)
         .filter_by(vk_id=self_id)
         .update({User.state: state}))
        self.session.commit()

    def add_like(self, self_id: int,
                 user_id: int
                 ) -> None:
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
            vk_id=self_id,
            viewed_vk_id=user_id,
            status_id=1,
        )
        )
        self.session.commit()

    def add_dislike(self, self_id: int,
                    user_id: int,
                    ) -> None:
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
            vk_id=self_id,
            viewed_vk_id=user_id,
            status_id=2,
        )
        )
        self.session.commit()

    def change_status(self,
                      self_id: int,
                      user_id: int,
                      new_status_id: int
                      ) -> None:
        """Меняет статус у выбранного пользователя

        Args:
            self_id (int): ID пользователя, который добавляет
            user_id (int): ID пользователя, которого добавляют
            new_status_id (int): ID нового статуса

        Returns:
            None
        """
        obj = self.session.query(ViewData).filter_by(
            vk_id=self_id,
            viewed_vk_id=user_id,
        ).first()
        # Если статус отличается, то меняем, если нет, ничего не делаем
        if obj.status_id != new_status_id:
            obj.status_id = new_status_id
            self.session.commit()

    def request_liked_list(self, self_id: int) -> list:
        """Возвращает список(словарей) лайкнутых пользователей

        Args:
            self_id (int): ID пользователя который добавил
        Returns:
            List: Список словарей, содержащих следующие ключи:

                - 'vk_id': ID пользователя, который добавил лайк
                - 'viewedvkid': ID пользователя, кому был поставлен лайк
                - 'status_id': ID статуса.
        """
        return_list = []
        query = self.session.query(ViewData).filter_by(
            vk_id=self_id,
            status_id=1
        ).all()

        for item in query:
            result_dict = {
                "vk_id": item.vk_id,
                "viewed_vk_id": item.viewed_vk_id,
                "status_id": item.status_id,
            }
            return_list.append(result_dict)

        return return_list

    def request_disliked_list(self, self_id: int) -> list:
        """Возвращает список(словарей) дизлайкнутых пользователей

        Args:
            self_id (int): ID пользователя который добавил
        Returns:
            List: Список словарей, содержащих следующие ключи:

                - 'vk_id': ID пользователя, который добавил дизлайк
                - 'viewedvkid': ID пользователя, кому был поставлен дизлайк
                - 'status_id': ID статуса.
        """
        return_list = []
        query = self.session.query(ViewData).filter_by(
            vk_id=self_id,
            status_id=2
        ).all()
        for item in query:
            result_dict = {
                "vk_id": item.vk_id,
                "viewed_vk_id": item.viewed_vk_id,
                "status_id": item.status_id,
            }
            return_list.append(result_dict)

        return return_list

    def is_viewed(self, self_id: int, user_id: int) -> bool:
        """Проверяет был ли пользователь предложен ранее

        Args:
            self_id (int): ID пользователя, который добавляет
            user_id (int): ID пользователя, которого добавляют
        Returns:
            bool: "True" если пользователь был просмотрен ранее, иначе "False"
        """
        query = self.session.query(ViewData).filter_by(
            vk_id=self_id,
            viewed_vk_id=user_id,
        ).first()

        return bool(query)

    def set_search(self, self_id: int,
                   sex: str = None,
                   city: str = None,
                   age_from: int = None,
                   age_to: int = None
                   ) -> None:
        """
        Записать параметры поиска.

        Args:
            self_id: ID пользователя.
            sex: Пол.
            city: Город.
            age_from: Нижняя граница возраста.
            age_to: Верхняя граница возраста.
        Returns:
            None
        """
        user = self.session.query(Search).filter_by(vk_id=self_id).first()
        if not user:
            self.session.add(Search(
                vk_id=self_id,
                sex=sex,
                city=city,
                age_from=age_from,
                age_to=age_to,
            ))
        else:
            if sex is not None:
                user.sex = sex
            if city is not None:
                user.city = city
            if age_from is not None:
                user.age_from = age_from
            if age_to is not None:
                user.age_to = age_to

        self.session.commit()

    def get_search(self, self_id: int) -> dict:
        """
        Получить параметры поиска.

        Args:
            self_id: ID пользователя.
        Returns:
            dict: Словарь параметров поиска

                - 'sex': Пол.
                - 'city': Город.
                - 'age_from': Нижняя граница возраста.
                - 'age_to': Верхняя граница возраста.

        """
        query = self.session.query(Search).filter_by(
            vk_id=self_id,
        ).first()

        if query is None:
            return {}

        result_dict = {
            "sex": query.sex,
            "city": query.city,
            "age_from": query.age_from,
            "age_to": query.age_to,
        }
        return result_dict
