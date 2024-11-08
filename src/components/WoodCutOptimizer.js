// src/components/WoodCutOptimizer.js
import React, { useState } from 'react';

const WoodCutOptimizer = () => {
  const [width, setWidth] = useState('');
  const [height, setHeight] = useState('');
  const [segments, setSegments] = useState(''); // Nouvel état pour le nombre de segments
  const [results, setResults] = useState(null); // Pour stocker les résultats de l'optimisation

  const handleOptimize = () => {
    // Vérification de validité des entrées
    const panelWidth = parseFloat(width);
    const panelHeight = parseFloat(height);
    const numSegments = parseInt(segments, 10);

    if (isNaN(panelWidth) || isNaN(panelHeight) || panelWidth <= 0 || panelHeight <= 0) {
      alert("Veuillez entrer des dimensions valides pour la largeur et la hauteur.");
      return;
    }

    if (isNaN(numSegments) || numSegments <= 0) {
      alert("Veuillez entrer un nombre valide de segments.");
      return;
    }

    // Simuler l'algorithme d'optimisation
    const optimalCuts = calculateOptimalCuts(panelWidth, panelHeight, numSegments);

    // Stocker les résultats dans l'état
    setResults(optimalCuts);
  };

  // Fonction pour calculer un agencement optimal
  const calculateOptimalCuts = (panelWidth, panelHeight, numSegments) => {
    const cuts = [];

    // Logique simple pour diviser le panneau en `numSegments` sections
    const pieceWidth = panelWidth / numSegments;
    const pieceHeight = panelHeight / numSegments;

    for (let i = 0; i < numSegments; i++) {
      cuts.push({ width: pieceWidth, height: pieceHeight });
    }

    return cuts;
  };

  return (
    <div>
      <h2>Optimisation des Coupes de Bois</h2>
      <label>
        Largeur:
        <input
          type="number"
          value={width}
          onChange={(e) => setWidth(e.target.value)}
        />
      </label>
      <label>
        Hauteur:
        <input
          type="number"
          value={height}
          onChange={(e) => setHeight(e.target.value)}
        />
      </label>
      <label>
        Nombre de segments:
        <input
          type="number"
          value={segments}
          onChange={(e) => setSegments(e.target.value)}
        />
      </label>
      <button onClick={handleOptimize}>Optimiser</button>

      {results && (
        <div>
          <h3>Résultats de l'Optimisation</h3>
          <ul>
            {results.map((cut, index) => (
              <li key={index}>
                Section {index + 1}: {cut.width.toFixed(2)} x {cut.height.toFixed(2)}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default WoodCutOptimizer;
