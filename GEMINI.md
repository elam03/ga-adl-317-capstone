# Notes about this repo

- This is a repo for a capstone project for a data analytics course.
- The project is about analyzing board game data and building a recommendation system.
- Skip writing tests for python code.
- The backend is a FastAPI server located at `src/backend/app.py`.
- A separate frontend will be built in the future; keep backend and frontend logic decoupled.
- Always use dynamic, absolute paths (using `os.path` relative to `__file__`) when loading assets from the `models/` directory, as the execution directory might change.
- We use a `Makefile` for core commands. Use `make run-backend` to start the FastAPI server.
