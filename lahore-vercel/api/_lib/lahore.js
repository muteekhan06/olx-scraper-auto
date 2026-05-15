const LAHORE_AREAS = [
  { key: "dha_defence", name: "DHA Defence" },
  { key: "johar_town", name: "Johar Town" },
  { key: "allama_iqbal_town", name: "Allama Iqbal Town" },
  { key: "gulberg", name: "Gulberg" },
  { key: "bahria_town", name: "Bahria Town" },
  { key: "cantt", name: "Cantt" },
  { key: "model_town", name: "Model Town" },
  { key: "sabzazar", name: "Sabzazar" },
  { key: "township", name: "Township" },
  { key: "wapda_town", name: "Wapda Town" },
  { key: "samanabad", name: "Samanabad" },
  { key: "faisal_town", name: "Faisal Town" },
  { key: "gulshan_e_ravi", name: "Gulshan-e-Ravi" },
  { key: "gt_road", name: "GT Road" },
  { key: "shahdara", name: "Shahdara" },
  { key: "askari", name: "Askari" },
  { key: "valencia_town", name: "Valencia Town" },
  { key: "raiwind_road", name: "Raiwind Road" },
  { key: "shadbagh", name: "Shadbagh" },
  { key: "jail_road", name: "Jail Road" },
  { key: "al_rehman_garden", name: "Al Rehman Garden" },
  { key: "mughalpura", name: "Mughalpura" },
  { key: "park_view_villas", name: "Park View Villas" },
  { key: "thokar_niaz_baig", name: "Thokar Niaz Baig" },
  { key: "bahria_orchard", name: "Bahria Orchard" },
  { key: "baghbanpura", name: "Baghbanpura" },
  { key: "pak_arab_housing", name: "Pak Arab Housing Society" },
  { key: "marghzar_officers", name: "Marghzar Officers Colony" },
  { key: "harbanspura", name: "Harbanspura" },
  { key: "central_park", name: "Central Park Housing Scheme" },
  { key: "chungi_amar_sadhu", name: "Chungi Amar Sadhu" },
  { key: "gajju_matah", name: "Gajju Matah" },
  { key: "garden_town", name: "Garden Town" },
  { key: "daroghewala", name: "Daroghewala" },
  { key: "ferozepur_road", name: "Ferozepur Road" },
  { key: "tajpura", name: "Tajpura" },
  { key: "lda_avenue", name: "LDA Avenue" },
  { key: "walton_road", name: "Walton Road" },
  { key: "maulana_shaukat_ali_road", name: "Maulana Shaukat Ali Road" },
  { key: "taj_bagh", name: "Taj Bagh" }
];

const LAHORE_AREA_KEYS = new Set(LAHORE_AREAS.map((x) => x.key));

module.exports = {
  LAHORE_AREAS,
  LAHORE_AREA_KEYS
};
