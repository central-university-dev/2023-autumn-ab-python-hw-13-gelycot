make_migration:
	alembic -c ./todo_list_app/alembic.ini revision --autogenerate -m '$(message)'

apply_migration:
	 alembic -c ./todo_list_app/alembic.ini upgrade '$(hash)'
