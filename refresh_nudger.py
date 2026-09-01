// Second line of defence. refresh_nudger.py already filters on
// hs_is_closed = false, but if the JSON is ever stale or hand-edited,
// nothing dead should reach the card.
const NUDGER_CLOSED_STAGES = new Set([
  'Sales Qualified Out',
  'Closed Lost',
  'Churned',
  'Paused',
  'Email activity'
]);

function nudgerStorageKey(rep) {
  const id = (rep && rep.rep && rep.rep.id) ? rep.rep.id : currentRepIdx;
  return 'nudgerIdx:' + id;
}

function buildNudgerQueue() {
  const rep = DATA.reps[currentRepIdx];

  nudgerQueue = (rep.nudger || []).filter(function (d) {
    return d && d.date && !NUDGER_CLOSED_STAGES.has(d.stage);
  });

  // Resume where you left off instead of restarting at deal 1 on every
  // rep switch and period-tab click.
  let saved = 0;
  try {
    saved = parseInt(localStorage.getItem(nudgerStorageKey(rep)) || '0', 10) || 0;
  } catch (e) {
    saved = 0;
  }
  nudgerIdx = nudgerQueue.length
    ? Math.min(Math.max(saved, 0), nudgerQueue.length - 1)
    : 0;
}
