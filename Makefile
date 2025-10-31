mig:
	alembic revision --autogenerate -m "Create a baseline migrations"

up:
	alembic upgrade head

downup:
	alembic downgrade head


web_admin:
	uvicorn web.app:app --host localhost --port 8000

docker_up:
	docker compose down
	docker volume rm evos_pgdata
	docker compose up

