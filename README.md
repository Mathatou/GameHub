1. python -m venv .venv  and activate it
2. pip install -r requirements.txt
3. Download the dataset from https://www.kaggle.com/datasets/andrewmvd/board-games
   and save the CSV as data/bgg_dataset.csv
4. uvicorn backend.main:app --reload
5. Open http://localhost:8000