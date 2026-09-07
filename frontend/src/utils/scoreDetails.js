// src/utils/scoreDetails.js
//
// Extrait le meilleur score et la catégorie dominante depuis score_details.
// Fonctionne avec n'importe quelle catégorie (dynamique depuis la config admin).
//
// Format de score_details :
// { "NOM_CATEGORIE": { "score": 90, "mots_cles_matches": [...] }, ... }

export function extractScoreInfo(scoreDetails) {
  if (!scoreDetails || typeof scoreDetails !== "object") {
    return { hasScore: false, score: 0, topCategory: null };
  }

  let best = null;
  for (const [category, value] of Object.entries(scoreDetails)) {
    const numericScore =
      typeof value === "number"
        ? value
        : value && typeof value === "object" && typeof value.score === "number"
          ? value.score
          : null;

    if (numericScore !== null && (best === null || numericScore > best.score)) {
      best = { category, score: numericScore };
    }
  }

  if (!best) return { hasScore: false, score: 0, topCategory: null };
  return { hasScore: true, score: best.score, topCategory: best.category };
}