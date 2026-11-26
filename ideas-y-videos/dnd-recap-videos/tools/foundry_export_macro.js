// Pega esto como Macro (tipo Script) en Foundry/Forge y ejecútala como GM.
// Descarga chatlog.json con tiradas, speaker y flavor. Luego pásalo a tools/rank_moments.py
const data = game.messages.contents.map(m => ({
  ts: m.timestamp,
  speaker: m.alias,
  flavor: m.flavor,
  content: (m.content || "").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim(),
  rolls: (m.rolls || []).map(r => ({
    formula: r.formula,
    total: r.total,
    dice: r.dice.map(d => ({ faces: d.faces, results: d.results.map(x => x.result) }))
  }))
}));
saveDataToFile(JSON.stringify(data, null, 2), "application/json", "chatlog.json");
