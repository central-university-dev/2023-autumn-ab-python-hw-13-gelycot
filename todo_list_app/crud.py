from todo_list_app.database import get_session, TaskList, Task, User


def create_user_db(username, password_hash, salt):
    with get_session() as session:
        new_user = User(
            username=username, password_hash=password_hash, salt=salt
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user


def get_task_list_by_id_db(task_list_id):
    with get_session() as session:
        task_list = (
            session.query(TaskList).filter(TaskList.id == task_list_id).first()
        )
        return task_list


def get_tasks_by_list_id_db(list_id):
    with get_session() as session:
        tasks_query = session.query(Task.id).filter(Task.list_id == list_id)
        task_ids = [result.id for result in tasks_query.all()]

        return task_ids


def create_task_list_db(user_id, name):
    new_task_list = TaskList(user_id=user_id, name=name)
    with get_session() as session:
        session.add(new_task_list)
        session.commit()
        session.refresh(new_task_list)
        return new_task_list


def create_task_db(list_id, name):
    new_task = Task(list_id=list_id, name=name)
    with get_session() as session:
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        return new_task


def update_task_list_db(task_list_id, new_name):
    with get_session() as session:
        task_list = (
            session.query(TaskList).filter(TaskList.id == task_list_id).first()
        )

        task_list.name = new_name
        session.commit()
        session.refresh(task_list)
        return task_list


def delete_task_list_db(task_list_id: int):
    with get_session() as session:
        task_list = (
            session.query(TaskList).filter(TaskList.id == task_list_id).first()
        )

        session.delete(task_list)
        session.commit()


def delete_task_db(task_id: int):
    with get_session() as session:
        task = session.query(Task).filter(Task.id == task_id).first()

        session.delete(task)
        session.commit()


def get_task_by_id_db(task_id: int):
    with get_session() as session:
        return session.query(Task).filter(Task.id == task_id).first()


def update_task_db(task_id: int, name: str):
    with get_session() as session:
        task = session.query(Task).filter(Task.id == task_id).first()
        task.name = name
        session.commit()
        session.refresh(task)
        return task
