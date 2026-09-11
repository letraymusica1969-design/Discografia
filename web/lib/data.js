import box from '../data/box.json';

export function getDiscos() {
  return box.map((d) => ({
    ...d,
    totalDur: d.tracklist.reduce((a, t) => a + t.duracion, 0),
  }));
}

export function getDisco(slug) {
  return getDiscos().find((d) => d.slug === slug) || null;
}

export function fmtTime(s) {
  const m = Math.floor(s / 60);
  const ss = Math.floor(s % 60);
  return `${m}:${String(ss).padStart(2, '0')}`;
}