// scenes/cast.js — Cast & Center-Safe 9:16 Hybrid Bounds for "Neurological Outbreak"
export const YOU = { top: 'hoodie', color: '#2b4566', head: 'none' };
export const DRIVER = { top: 'tshirt', color: '#c4712b', head: 'cap', headColor: '#e09b3d' };
export const WOMAN_GLASS = { top: 'hoodie', color: '#6b567a', head: 'long', headColor: '#121622' };
export const INFECTED_A = { top: 'tshirt', color: '#3b4a42', head: 'spiky', headColor: '#151c19' };
export const INFECTED_B = { top: 'hoodie', color: '#333f47', head: 'none' };
export const CONTROL_MAN = { top: 'hoodie', color: '#3d5245', head: 'short', headColor: '#1a2029' };
export const BOY = { top: 'hoodie', color: '#874c3a', head: 'short', headColor: '#171c26' };

// Unnatural neurological outbreak posture ("isn't walking normally")
export const TWITCH_POSE = {
  head: [19, -193], sh: [9, -165], hip: [0, -98],
  eF: [36, -148], hF: [64, -154],
  eB: [-18, -140], hB: [-26, -108],
  kF: [15, -48], fF: [11, 0],
  kB: [-13, -50], fB: [-19, 0]
};

// Center 9:16 Safe Zone inside 1920x1080 (608x1080 centered at x=960 -> x=656..1264)
export const SAFE = {
  L: 656,
  R: 1264,
  W: 608,
  CX: 960,
  IN_L: 695,
  IN_R: 1225
};
