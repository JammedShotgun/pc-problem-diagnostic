# Run

1. add base url to `frontend/.env`
```
BASE_URL=http://localhost:5000
```

2. build needed files for svelte frontend (needs nodejs 14)

```sh
cd frontend
npm i
npm run build-tailwind-win # or npm run build-tailwind for linux
npm run build 
```

3. run

```sh
FLASK_APP=main.py python3 -m flask run --host=0.0.0.0
```
