const KARACHI_AREAS = [
  { key: "gulshan_iqbal", name: "Gulshan-e-Iqbal Town" },
  { key: "gulistan_jauhar", name: "Gulistan-e-Jauhar" },
  { key: "fb_area", name: "Federal B Area" },
  { key: "north_nazimabad", name: "North Nazimabad" },
  { key: "nazimabad", name: "Nazimabad" },
  { key: "naya_nazimabad", name: "Naya Nazimabad" },
  { key: "north_karachi", name: "North Karachi" },
  { key: "new_karachi", name: "New Karachi" },
  { key: "saddar_town", name: "Saddar Town" },
  { key: "dha_defence_karachi", name: "DHA Defence (Karachi)" },
  { key: "clifton", name: "Clifton" },
  { key: "buffer_zone_north", name: "North Karachi - Buffer Zone" },
  { key: "buffer_zone_2", name: "Buffer Zone 2" },
  { key: "khalid_bin_walid", name: "Khalid Bin Walid Road" }
];

const KARACHI_AREA_KEYS = new Set(KARACHI_AREAS.map((x) => x.key));

module.exports = {
  KARACHI_AREAS,
  KARACHI_AREA_KEYS
};

