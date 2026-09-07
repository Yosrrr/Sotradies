// src/utils/categories.js

const KNOWN_LABELS = {
  MATERIEL_ROULANT: "Matériel roulant",
  ENGINS_TP: "Engins TP",
  MANUTENTION: "Manutention",
  ENGINS_SPECIAUX: "Engins spéciaux",
  GROUPES_ELECTROGENES: "Groupes électrogènes",
};

// Export pour compatibilité avec les composants existants
export const CATEGORY_LABELS = KNOWN_LABELS;

export function categoryLabel(key) {
  if (!key) return "—";

  if (KNOWN_LABELS[key]) {
    return KNOWN_LABELS[key];
  }

  return key
    .replace(/_/g, " ")
    .toLowerCase()
    .replace(/^\w/, (c) => c.toUpperCase());
}