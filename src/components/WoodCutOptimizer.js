import React, { useState, useRef, useEffect } from "react";
import "../index.css";

function WoodCutOptimizer() {
  const [width, setWidth] = useState(""); // Largeur du panneau global
  const [height, setHeight] = useState(""); // Hauteur du panneau global
  const [sections, setSections] = useState([]); // Liste des sections
  const [results, setResults] = useState(null); // Résultats d'optimisation
  const [hoveredSection, setHoveredSection] = useState(null); // Section survolée
  const [errorMessage, setErrorMessage] = useState(null);
  const canvasRef = useRef(null); // Référence pour le canvas

  const handleAddSection = () => {
    setSections([...sections, { sectionWidth: "", sectionHeight: "" }]);
  };

  const handleRemoveSection = (index) => {
    const newSections = [...sections];
    newSections.splice(index, 1);
    setSections(newSections);
  };

  const handleOptimize = async () => {
    const panelWidth = parseFloat(width);
    const panelHeight = parseFloat(height);

    if (isNaN(panelWidth) || isNaN(panelHeight) || panelWidth <= 0 || panelHeight <= 0) {
      setErrorMessage("Veuillez entrer des dimensions valides pour la largeur et la hauteur.");
      return;
    }

    const sectionDimensions = sections.map((section) => ({
      width: parseFloat(section.sectionWidth),
      height: parseFloat(section.sectionHeight),
    }));

    if (sectionDimensions.some((section) => isNaN(section.width) || isNaN(section.height) || section.width <= 0 || section.height <= 0)) {
      setErrorMessage("Veuillez entrer des dimensions valides pour toutes les sections.");
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:5000/optimize", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          width: panelWidth,
          height: panelHeight,
          sections: sectionDimensions,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        setErrorMessage(errorData.error || "Erreur lors de l'optimisation des découpes.");
      } else {
        const data = await response.json();
        setResults(data.cuts);
        setErrorMessage(null);
      }
    } catch (error) {
      console.error("Erreur:", error);
      setErrorMessage("Erreur inconnue lors de l'optimisation des découpes.");
    }
  };

  useEffect(() => {
    if (canvasRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext("2d");
      const totalWidth = parseFloat(width) || 800; // Valeur par défaut si non spécifiée
      const totalHeight = parseFloat(height) || 600;
  
      // Effacez le canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);
  
      // Dessinez le panneau global
      ctx.fillStyle = "#D3D3D3";
      ctx.fillRect(0, 0, totalWidth, totalHeight);
  
      // Dessinez les résultats (sections optimisées)
      if (results) {
        results.forEach((cut, index) => {
          const color = `hsl(${index * 137.5 % 360}, 70%, 50%)`; // Couleur unique
          ctx.fillStyle = color;
          ctx.fillRect(cut.x, cut.y, cut.width, cut.height);
  
          // Associer la couleur à la section
          cut.color = color;
  
          // Afficher les dimensions
          const label = `${cut.width.toFixed(0)} x ${cut.height.toFixed(0)}`;
          ctx.fillStyle = "black";
          ctx.font = "10px Arial";
  
          // Dimensions au milieu
          const textX = cut.x + cut.width / 2 - ctx.measureText(label).width / 2;
          const textY = cut.y + cut.height / 2 + 4; // Centré verticalement
          ctx.fillText(label, textX, textY);
  
          // Afficher l'identifiant de la section
          const idLabel = `S${cut.id + 1}`;
          ctx.fillStyle = "white";
          ctx.fillText(idLabel, cut.x + 5, cut.y + 15);
        });
      }
  
      // Afficher l'effet popup lors du survol
      if (hoveredSection) {
        // Si la hauteur ou la largeur est inférieure à 80, multiplier par 3 ; sinon, multiplier par 1.5
        var scaleFactor = hoveredSection.width < 30 || hoveredSection.height < 30 ? 10 :
                  hoveredSection.width < 50 || hoveredSection.height < 50 ? 5 :
                  hoveredSection.width < 100 || hoveredSection.height < 100 ? 2 :
                  1; // Default value if none of the conditions are met
        const popupWidth = hoveredSection.width * scaleFactor;
        const popupHeight = hoveredSection.height * scaleFactor;
        const centerX = (canvas.width - popupWidth) / 2;
        const centerY = (canvas.height - popupHeight) / 2;
  
        // Dessiner l'arrière-plan semi-transparent
        ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
  
        // Dessiner la section agrandie (popup)
        ctx.fillStyle = hoveredSection.color; // Utiliser la couleur de la section survolée
        ctx.fillRect(centerX, centerY, popupWidth, popupHeight);
  
        // Afficher les dimensions et l'identifiant
        ctx.fillStyle = "white";
        ctx.font = "14px Arial";
        const label = `S${hoveredSection.id + 1}: ${hoveredSection.width} x ${hoveredSection.height}`;
        const textWidth = ctx.measureText(label).width;
        ctx.fillText(label, centerX + popupWidth / 2 - textWidth / 2, centerY + popupHeight / 2 + 5);
      }
    }
  }, [results, width, height, hoveredSection]);
  

  const handleMouseMove = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // Vérifier si la souris est au-dessus d'une section (results)
    const hovered = results?.find(
      (cut) =>
        mouseX >= cut.x &&
        mouseX <= cut.x + cut.width &&
        mouseY >= cut.y &&
        mouseY <= cut.y + cut.height
    );

    setHoveredSection(hovered || null); // Mettre à jour la section survolée
  };

  const handleMouseLeave = () => {
    setHoveredSection(null); // Réinitialiser lorsqu'on quitte le canvas
  };

  return (
    <div className="container">
      <h2>Optimisation des Coupes</h2>
      <label>
        Largeur du panneau global:
        <input
          type="number"
          value={width}
          onChange={(e) => setWidth(e.target.value)}
        />
      </label>
      <label>
        Hauteur du panneau global:
        <input
          type="number"
          value={height}
          onChange={(e) => setHeight(e.target.value)}
        />
      </label>

      <h3>Ajouter des sections à découper</h3>
      <div id="labels">
        {sections.map((section, index) => (
          <div className="label" key={index}>
            <label>
              Largeur de la section {index + 1}:
              <input
                type="number"
                value={section.sectionWidth}
                onChange={(e) => {
                  const newSections = [...sections];
                  newSections[index].sectionWidth = e.target.value;
                  setSections(newSections);
                }}
              />
            </label>
            <label>
              Hauteur de la section {index + 1}:
              <input
                type="number"
                value={section.sectionHeight}
                onChange={(e) => {
                  const newSections = [...sections];
                  newSections[index].sectionHeight = e.target.value;
                  setSections(newSections);
                }}
              />
            </label>
            <button
              className="remove-section"
              onClick={() => handleRemoveSection(index)}
            >
              Supprimer cette section
            </button>
          </div>
        ))}
      </div>
      <button onClick={handleAddSection}>Ajouter une section</button>
      <button onClick={handleOptimize}>Optimiser</button>

      {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}

      <canvas 
        ref={canvasRef} 
        width={parseFloat(width)} 
        height={parseFloat(height)}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        style={{ border: "1px solid black", marginTop: "20px" }}
      ></canvas>

      {results && (
        <div>
          <h3>Résultats de l'Optimisation</h3>
          <ul>
            {results.map((cut, index) => (
              <li key={index}>
                Section {index + 1}: {cut.width.toFixed(2)} x{" "}
                {cut.height.toFixed(2)}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default WoodCutOptimizer;
