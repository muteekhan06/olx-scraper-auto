const LAHORE_AREAS = [
  { key: "johar_town", name: "Johar Town" },
  { key: "model_town", name: "Model Town" },
  { key: "valencia_town", name: "Valencia Town" },
  { key: "askari", name: "Askari" },
  { key: "dha_defence", name: "DHA Defence (Lahore)" }
];

const LAHORE_AREA_KEYS = new Set(LAHORE_AREAS.map((x) => x.key));

module.exports = {
  LAHORE_AREAS,
  LAHORE_AREA_KEYS
};
