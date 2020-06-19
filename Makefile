check: typecheck test
	# Run tests and typecheck

test:
	poetry run pytest

typecheck:
	poetry run mypy fbchatbot
