const express = require('express');
const cors = require('cors');
const games = require('./games.json');

const app = express();
app.use(cors());
app.use(express.json());

// Flexible Filtering Endpoint
app.get('/api/games', (req, res) => {
  const { player_count, max_explanation_time, play_style } = req.query;

  let results = games.filter(game => {
    if (player_count && game.best_player_count != player_count) return false;
    if (max_explanation_time && game.explanation_time_min > Number(max_explanation_time)) return false;
    if (play_style && game.play_style !== play_style) return false;
    return true;
  });

  // Near-match suggestion logic if empty
  if (results.length === 0 && player_count) {
    const relaxed = games.filter(g => g.explanation_time_min <= (Number(max_explanation_time) || 60));
    return res.json({ results: relaxed, isSuggested: true });
  }

  res.json({ results, isSuggested: false });
});

app.listen(5000, () => console.log('Backend running on port 5000'));