// Gateway: serves the frontend, validates input, forwards to FastAPI.
const express = require('express');
const path = require('path');
const app = express();
const FASTAPI = process.env.FASTAPI_URL || 'http://127.0.0.1:8000';
app.use(express.json({ limit: '10kb' }));
app.use(express.static(path.join(__dirname, '../frontend')));

app.post('/api/analyze', async (req, res) => {
  const { brand, name, requirement, reason } = req.body || {};
  if (![brand, name, requirement, reason].every(v => typeof v === 'string' && v.trim()))
    return res.status(400).json({ error: 'Brand, product, requirement and reason are all required.' });
  try {
    const r = await fetch(`${FASTAPI}/analyze`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ brand, name, requirement, reason }),
    });
    res.status(r.status).json(await r.json());
  } catch {
    res.status(503).json({ error: 'Analysis service is not reachable.' });
  }
});
app.get('/api/image', async (req, res) => {
  const { brand, name } = req.query;
  if (typeof brand !== 'string' || typeof name !== 'string' || !name.trim())
    return res.status(400).json({ error: 'brand and name are required.' });
  try {
    const r = await fetch(`${FASTAPI}/image?` + new URLSearchParams({ brand, name }));
    res.status(r.status).json(await r.json());
  } catch {
    res.json({ url: null });
  }
});

app.listen(process.env.PORT || 3000, () => console.log('ReviewLens on http://localhost:3000'));
