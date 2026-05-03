.PHONY: run-backend parse

run-backend:
	python -m src.backend.app

parse:
	python -m src.parsing.process_raw_game_detailed_data
