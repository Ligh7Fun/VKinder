

from database.db import DataBase

db = DataBase()

db.drop_tables()
db.create_tables()
db.add_status(status="Like")
db.add_status(status="Dislike")
db.add_user(self_id=1)
db.add_user(self_id=99999999)

db.add_like(self_id=1, user_id=77777)
db.add_like(self_id=1, user_id=8888)
db.add_like(self_id=99999999, user_id=77777)
db.add_like(self_id=99999999, user_id=99999)
db.add_dislike(self_id=1, user_id=77773333)
db.add_dislike(self_id=99999999, user_id=33337777)
db.change_status(self_id=1, user_id=77777, new_status_id=1)
db.change_status(self_id=1, user_id=77777, new_status_id=2)
