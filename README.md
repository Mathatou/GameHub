# GameHub

## Setup

The setup scripts create a virtual environment, install the Python
dependencies, and download the board-games dataset into `data/`.

### Linux and macOS

```bash
chmod +x setup.sh
./setup.sh
```

### Windows

Run `setup.bat` from the project directory.

The dataset is downloaded from
[Kaggle](https://www.kaggle.com/datasets/andrewmvd/board-games). Kaggle
authentication may be required.

## Run the backend

### Linux and macOS

```bash
chmod +x z_launchBackend.sh
./z_launchBackend.sh
```

### Windows

Run `z_launchBackend.bat` from the project directory.

Open [http://localhost:8000](http://localhost:8000) in your browser.
