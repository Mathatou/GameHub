import kagglehub
from pathlib import Path

# Download the latest version into the project's data directory.
data_dir = Path(__file__).resolve().parent / "data"
data_dir.mkdir(exist_ok=True)
if data_dir.exists():
    print("Data directory already exists:", data_dir)
    if any(data_dir.iterdir()):
        print("Data directory is not empty. Skipping dataset download.")
        exit(0)
else:
    print("Data directory created:", data_dir)

path = kagglehub.dataset_download("andrewmvd/board-games", output_dir=str(data_dir))

print("Path to dataset files:", path)