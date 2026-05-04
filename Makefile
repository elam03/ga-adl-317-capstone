.PHONY: run-backend run-frontend parse prepare-rag

run-backend:
	python -m backend.src.app

run-frontend:
	cd frontend && npm run dev

parse:
	python -m data.utils.process_raw_game_detailed_data

prepare-rag:
	curl -s -X POST http://localhost:8000/rag_prepare \
	  -H "X-API-Key: $${API_KEY}" | python3 -m json.tool
