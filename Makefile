.PHONY: install run seed test docker-up docker-down docker-prod-up docker-prod-down

install:
	pip install -r medconnect/requirements.txt

run:
	cd medconnect && python app.py

seed:
	cd medconnect && python seed.py

test:
	pytest -q

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

docker-prod-up:
	docker compose -f docker-compose.prod.yml up --build -d

docker-prod-down:
	docker compose -f docker-compose.prod.yml down -v
