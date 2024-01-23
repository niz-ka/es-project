# Elasticsearch Full Text Search Application

## Requirements
- Linux (including curl)
- Docker
- Python 3 (venv recommended)


## Running
```sh
python3 -m venv venv
cd venv
source bin/activate
git clone git@github.com:niz-ka/es-project.git
cd es-project
pip3 install -r requirements.txt
./init.sh
./start.sh
```

Run your browser in another terminal:
```sh
firefox localhost:5000
```