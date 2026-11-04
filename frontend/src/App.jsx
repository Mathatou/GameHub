import React, { useState, useEffect } from 'react';

export default function GameExplorer() {
  const [games, setGames] = useState([]);
  const [playerCount, setPlayerCount] = useState('');
  const [maxExplanation, setMaxExplanation] = useState('');
  const [isSuggested, setIsSuggested] = useState(false);

  // Fetch updated list from backend API on filter change
  useEffect(() => {
    const query = new URLSearchParams({
      player_count: playerCount,
      max_explanation_time: maxExplanation
    }).toString();

    fetch(`http://localhost:5000/api/games?${query}`)
      .then(res => res.json())
      .then(data => {
        setGames(data.results);
        setIsSuggested(data.isSuggested);
      });
  }, [playerCount, maxExplanation]);

  return (
    <div style={{ display: 'flex', gap: '20px', padding: '20px' }}>
      {/* Controls */}
      <div style={{ width: '250px' }}>
        <h3>Filters</h3>
        <label>Best Player Count:</label>
        <input 
          type="number" 
          value={playerCount} 
          onChange={(e) => setPlayerCount(e.target.value)} 
          placeholder="e.g. 4"
        />

        <br/><br/>
        <label>Max Rules Explanation Time (min):</label>
        <input 
          type="number" 
          value={maxExplanation} 
          onChange={(e) => setMaxExplanation(e.target.value)} 
          placeholder="e.g. 10"
        />
      </div>

      {/* Results Display */}
      <div>
        <h2>Board Game Catalog</h2>
        {isSuggested && <p style={{ color: 'orange' }}>No exact match found. Showing near matches:</p>}
        <ul>
          {games.map(game => (
            <li key={game.id}>
              <strong>{game.title}</strong> — Best for {game.best_player_count} players | Rules: {game.explanation_time_min} mins
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}