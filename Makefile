.PHONY: run-backend parse

run-backend:
	python -m backend.src.app

parse:
	python -m data.utils.process_raw_game_detailed_data
