from typing import Dict, Any

from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
import sqlalchemy as sq

from database.models import Base
from database.models import (User,
                             Status,
                             ViewData,
                             Search,
                             )

load_dotenv()


class Database:

    def __init__(self, dsn: str) -> None:
        # Базовый класс для моделей SQLAlchemy
        self.Base = Base
        # Создание объекта Engine для взаимодействия с базой данных
        self.engine = sq.create_engine(dsn)
        # Создание класса сессии для работы с базой данных
        self.Session = sessionmaker(bind=self.engine)
        # Создание объекта сессии, для работы с данными в базе
        self.session = self.Session()

    def create_tables(self) -> None:
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
        status_ = self.session.query(Status).filter_by(name=status).first()
        if not status_:
            self.session.add(Status(name=status))
            self.session.commit()

    def add_user(self, self_id: int, state: str = None) -> None:
        """
        Добавить пользователя с указанным VK идентификатором.

        Args:
            self_id (int): Идентификатор пользователя VK.
            state (str): Состояние пользователя.
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
            self_id (int): ID пользователя VK.
        Returns:
            State: Состояние пользователя
        """
        return self.session.query(User).filter_by(vk_id=self_id).first().state

    def set_state_user(self, self_id: int, state: str) -> None:
        """
        Установить состояние пользователя.

        Args:
            self_id (int): ID пользователя VK.
            state (str): Состояние пользователя
        Returns:
            None
        """
        (self.session.query(User)
         .filter_by(vk_id=self_id)
         .update({User.state: state}))
        self.session.commit()

    def add_like(self, self_id: int,
                 user_id: int,
                 first_name: str,
                 last_name: str,
                 ) -> None:
        """
        Добавить предложенного пользователя в список
        со статусом "лайк"(избранное).

        Args:
            self_id (int): ID пользователя, который добавляет
            user_id (int): ID пользователя, которого добавляют
            first_name (str): Имя пользователя
            last_name (str): Фамилия пользователя
        Returns:
            None.
        """
        self.session.add(ViewData(
                vk_id=self_id,
                viewed_vk_id=user_id,
                status_id=1,
                first_name=first_name,
                last_name=last_name,
        )
        )
        self.session.commit()

    def add_dislike(self, self_id: int,
                    user_id: int,
                    first_name: str,
                    last_name: str,
                    ) -> None:
        """
        Добавить предложенного пользователя в список
        со статусом "дизлайк"(черный список).

        Args:
            self_id (int): ID пользователя, который добавляет
            user_id (int): ID пользователя, которого добавляют
            first_name (str): Имя пользователя
            last_name (str): Фамилия пользователя
        Returns:
            None.
        """
        self.session.add(ViewData(
                vk_id=self_id,
                viewed_vk_id=user_id,
                status_id=2,
                first_name=first_name,
                last_name=last_name,
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
                - 'viewed_vk_id': ID пользователя, кому был поставлен лайк
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
                "first_name": item.first_name,
                "last_name": item.last_name,
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
                - 'viewed_vk_id': ID пользователя, кому был поставлен дизлайк
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
                "first_name": item.first_name,
                "last_name": item.last_name,
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
                   age_to: int = None,
                   results: Dict[str, Any] = None,
                   results_index: int = 0,
                   ) -> None:
        """
        Записать параметры поиска.

        Args:
            self_id (int): ID пользователя.
            sex (str): Пол.
            city (str): Город.
            age_from (int): Нижняя граница возраста.
            age_to (int): Верхняя граница возраста.
            results (Dict[str, Any]): Результаты поиска.
            results_index (int): Индекс поиска.
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
                    results=results,
                    results_index=results_index,
            )
            )
        else:
            if sex is not None:
                user.sex = sex
            if city is not None:
                user.city = city
            if age_from is not None:
                user.age_from = age_from
            if age_to is not None:
                user.age_to = age_to
            if results is not None:
                user.results = results
            if results_index is not None:
                user.results_index = results_index

        self.session.commit()

    def get_search(self, self_id: int) -> dict:
        """
        Получить параметры поиска.

        Args:
            self_id (int): ID пользователя.
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

    def get_search_index(self, self_id: int) -> int:
        """
        Получить индекс поиска.

        Args:
            self_id (int): ID пользователя.

        Returns:
            int: Индекс поиска.
        """
        query = self.session.query(Search.results_index).filter_by(
                vk_id=self_id,
        ).scalar()

        return query or 0

    def set_search_index(self, self_id: int, new_index: int) -> None:
        """
        Изменить индекс поиска для пользователя.

        Args:
            self_id (int): ID пользователя.
            new_index (int): Новый индекс для пользователя.

        Returns:
            None.
        """
        query = self.session.query(Search).filter_by(
                vk_id=self_id,
        ).first()

        if query:
            query.results_index = new_index
            self.session.commit()

    def get_search_results(self, self_id: int) -> dict:
        """
        Получить результаты поиска.

        Args:
            self_id (int): ID пользователя.

        Returns:
            dict: Словарь результатов поиска.
        """
        query = self.session.query(Search.results).filter_by(
                vk_id=self_id,
        ).scalar()

        return query or {}
