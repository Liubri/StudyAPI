### Install dependencies in a virtual environment
```
python3 -m venv .venv
source .venv/bin/activate
```

#### Dependencies
```
pip install fastapi uvicorn sqlalchemy pydantic python-multipart
```

#### Running APP
```
uvicorn main:app --reload
```

#### It will run at
```
http://127.0.0.1:8000
```
