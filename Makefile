bootstrap:
	bash scripts/bootstrap.sh

check:
	uv run ecommerce-datagen check

seed:
	uv run ecommerce-datagen seed

test:
	uv run pytest

doctor:
	uv run python -m ecommerce_datagen doctor
