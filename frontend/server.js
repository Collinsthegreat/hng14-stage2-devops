const express = require('express');
const axios = require('axios');
const path = require('path');
const app = express();

const API_URL = process.env.API_URL || 'http://api:8000';
const PORT = parseInt(process.env.FRONTEND_PORT || '3000', 10);

app.use(express.json());
app.use(express.static(path.join(__dirname, 'views')));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ message: 'healthy' });
});

app.post('/submit', async (req, res) => {
  try {
    const response = await axios.post(`${API_URL}/jobs`, req.body || {});
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: 'Failed to submit job' });
  }
});

app.get('/status/:id', async (req, res) => {
  try {
    const response = await axios.get(`${API_URL}/jobs/${req.params.id}`);
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: 'Failed to get job status' });
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Frontend running on port ${PORT}`);  // eslint-disable-line no-console
});
