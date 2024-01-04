.PHONY: update test lint security_checks

make_migration:
	alembic -c ./todo_list_app/alembic.ini revision --autogenerate -m '$(message)'

apply_migration:
	 alembic -c ./todo_list_app/alembic.ini upgrade '$(hash)'

apply_all_migrations:
	alembic -c ./todo_list_app/alembic.ini upgrade head

test:
	pytest -v --cov=todo_list_app

lint:
	black --check .
	flake8 todo_list_app test

security_checks:
	bandit -r todo_list_app