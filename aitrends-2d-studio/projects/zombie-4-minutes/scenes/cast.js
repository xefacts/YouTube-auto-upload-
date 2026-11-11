// scenes/cast.js — Zombie Apocalypse 4-Minute Countdown cast
export const YOU = { top: 'hoodie', color: '#d64a33', head: 'none' };
export const SAM = { top: 'tshirt', color: '#3a6ea5', head: 'cap', headColor: '#f2c21a' };
export const ZOMBIE_A = { top: 'tshirt', color: '#435246', head: 'spiky' };
export const ZOMBIE_B = { top: 'hoodie', color: '#38463c', head: 'none' };

export const ZOMBIE_POSE = {
  head: [17, -195], sh: [8, -166], hip: [0, -98],
  eF: [38, -152], hF: [70, -158],
  eB: [30, -144], hB: [60, -148],
  kF: [14, -48], fF: [10, 0],
  kB: [-12, -50], fB: [-18, 0]
};

export const CAST = [YOU, SAM, ZOMBIE_A, ZOMBIE_B];
