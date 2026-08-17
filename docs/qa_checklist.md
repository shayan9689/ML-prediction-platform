# QA checklist (Phase 9)

- [ ] `GET /health` returns `{ status: ok }`
- [ ] `GET /tasks` returns three tasks with feature schemas
- [ ] Valid house-price form → 200 + numeric prediction + confidence
- [ ] Missing field → 422
- [ ] `median_income: "abc"` → 422
- [ ] `POST /predict/not_a_task` → 404
- [ ] Frontend loading spinner while request is in flight
- [ ] Frontend error card if API is down
- [ ] Performance page charts render for each task
- [ ] `logs/app.log` contains JSON lines after a prediction
- [ ] CORS: Vite `localhost:5173` can call the API
