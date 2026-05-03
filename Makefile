.PHONY: run-backend run-frontend parse

run-backend:
	python -m backend.src.app

run-frontend:
	cd frontend && npm run dev

parse:
	python -m data.utils.process_raw_game_detailed_data
