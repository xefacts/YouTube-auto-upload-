export const INK = "#241726";
export const SKIN = "#ffe2c2";
const WHITE = "#ffffff";
const MOUTH = "#5a1e28";
const TONGUE = "#e86e78";
const SH_SKIN = [
    0.96,
    0.86,
    0.84
];
const SH_CLOTH = [
    0.64,
    0.66,
    0.74
];
const SH_FELT = [
    0.62,
    0.62,
    0.7
];
const rad = (d)=>d * Math.PI / 180;
const clamp = (x, a, b)=>Math.max(a, Math.min(b, x));
export const mul = (c, m)=>{
    const n = parseInt(c.slice(1), 16);
    const ch = (v, k)=>Math.min(255, Math.round(v * k)).toString(16).padStart(2, "0");
    return `#${ch(n >> 16 & 255, m[0])}${ch(n >> 8 & 255, m[1])}${ch(n & 255, m[2])}`;
};
export const shade = (c, k)=>mul(c, [
        k,
        k,
        k
    ]);
export const mix = (a, b, t)=>{
    const A = parseInt(a.slice(1), 16), B = parseInt(b.slice(1), 16);
    const ch = (s)=>Math.round((A >> s & 255) * (1 - t) + (B >> s & 255) * t).toString(16).padStart(2, "0");
    return `#${ch(16)}${ch(8)}${ch(0)}`;
};
const rnd = (seed, k)=>{
    const x = Math.sin(seed * 127.1 + k * 311.7) * 43758.5453;
    return x - Math.floor(x);
};
const rotPts = (pts, a, cx, cy)=>pts.map(([x, y])=>[
            cx + (x - cx) * Math.cos(a) - (y - cy) * Math.sin(a),
            cy + (x - cx) * Math.sin(a) + (y - cy) * Math.cos(a)
        ]);
const rotAbout = (q, a, c)=>rotPts([
        q
    ], a, c[0], c[1])[0];
const lerp2 = (a, b, t)=>[
        a[0] + (b[0] - a[0]) * t,
        a[1] + (b[1] - a[1]) * t
    ];
const curve = (a, k, b, n = 10)=>{
    const c = [
        2 * k[0] - (a[0] + b[0]) / 2,
        2 * k[1] - (a[1] + b[1]) / 2
    ], out = [];
    for(let i = 0; i <= n; i++){
        const t = i / n, s = 1 - t;
        out.push([
            s * s * a[0] + 2 * s * t * c[0] + t * t * b[0],
            s * s * a[1] + 2 * s * t * c[1] + t * t * b[1]
        ]);
    }
    return out;
};
export const RIFLEMAN = {
    jacket: "#357650",
    pants: "#3d4440",
    boots: INK,
    hat: "shako",
    belt: "#f1efe6",
    buttons: "#d9dde0",
    rifle: true
};
export const OFFICER = {
    ...RIFLEMAN,
    hat: "shako_tall",
    buttons: "#e8c45a",
    sash: "#c0353a",
    sword: true,
    moustache: "#4a3020",
    rifle: false,
    belt: null,
    build: "stout"
};
export const KID = {
    jacket: "#f08a2c",
    pants: "#3b5b9a",
    boots: "#f4f1ea",
    hat: "cap",
    cap: "#e2453c",
    build: "kid"
};
export const PARENT = {
    jacket: "#7b5ac9",
    pants: "#3b3f52",
    boots: "#5a3b2a",
    hat: "hair",
    hair: "#5a3b2a"
};
export const SKINS = [
    SKIN,
    "#f5c9a0",
    "#ecd0b6",
    "#c99067"
];
export const soldier = (v = 0, extra = {})=>{
    const o = {
        ...RIFLEMAN,
        skin: SKINS[v % 4]
    };
    if (v % 4 === 1) o.moustache = "#4a3426";
    if (v % 4 === 3) o.moustache = "#2a201a";
    return {
        ...o,
        ...extra
    };
};
export const townsfolk = (v = 0)=>{
    const coats = [
        "#3f6fb5",
        "#8c3b4a",
        "#5d7a3a",
        "#b5653f",
        "#2f5f6a",
        "#7b5ac9"
    ];
    const o = {
        jacket: coats[v % 6],
        pants: "#3b3f52",
        boots: "#4a3426",
        skin: SKINS[v % 4]
    };
    return v % 2 ? {
        ...o,
        hat: "bonnet",
        dress: [
            "#d9a441",
            "#c25a7a",
            "#5a8fc2"
        ][v % 3]
    } : {
        ...o,
        hat: "tophat"
    };
};
export class Pen {
    g;
    ol = 12;
    rot = null;
    constructor(g){
        this.g = g;
    }
    P(x, y) {
        if (!this.rot) return [
            x,
            y
        ];
        const r = this.rot, a = r[0], cx = r[1], cy = r[2], dx = r.length > 3 ? r[3] : 0, dy = r.length > 4 ? r[4] : 0, c = Math.cos(a), s = Math.sin(a);
        return [
            cx + (x - cx) * c - (y - cy) * s + dx,
            cy + (x - cx) * s + (y - cy) * c + dy
        ];
    }
    path(pts, close) {
        const g = this.g;
        g.beginPath();
        pts.forEach((p, i)=>{
            const [x, y] = this.P(p[0], p[1]);
            if (i) g.lineTo(x, y);
            else g.moveTo(x, y);
        });
        if (close) g.closePath();
    }
    poly(pts, fill, ol) {
        const g = this.g, w = ol ?? this.ol;
        this.path(pts, true);
        if (fill) {
            g.fillStyle = fill;
            g.fill();
        }
        if (w) {
            g.lineWidth = w;
            g.strokeStyle = INK;
            g.lineJoin = "round";
            g.stroke();
        }
    }
    ell(cx, cy, rx, ry, fill, ol, a0 = 0, a1 = 360, rot = 0) {
        this.poly(ellPts(cx, cy, rx, ry, a0, a1, rot), fill, ol);
    }
    line(pts, fill, w, ink = true) {
        const g = this.g;
        g.lineCap = "round";
        g.lineJoin = "round";
        if (ink) {
            this.path(pts, false);
            g.strokeStyle = INK;
            g.lineWidth = w + 2 * this.ol * 0.9;
            g.stroke();
        }
        this.path(pts, false);
        g.strokeStyle = fill;
        g.lineWidth = w;
        g.stroke();
    }
    stroke(pts, w, fill = INK) {
        const g = this.g;
        g.lineCap = "round";
        g.lineJoin = "round";
        this.path(pts, false);
        g.strokeStyle = fill;
        g.lineWidth = w;
        g.stroke();
    }
    arc(cx, cy, rx, ry, a0, a1, w, fill = INK) {
        const pts = [];
        for(let i = 0; i <= 24; i++)pts.push([
            cx + rx * Math.cos(rad(a0 + (a1 - a0) * i / 24)),
            cy + ry * Math.sin(rad(a0 + (a1 - a0) * i / 24))
        ]);
        this.stroke(pts, w, fill);
    }
    dot(cx, cy, r, fill = INK) {
        const [x, y] = this.P(cx, cy);
        this.g.beginPath();
        this.g.arc(x, y, r, 0, Math.PI * 2);
        this.g.fillStyle = fill;
        this.g.fill();
    }
    clip(pts, fn) {
        const g = this.g;
        g.save();
        this.path(pts, true);
        g.clip();
        fn();
        g.restore();
    }
    shadedFill(pts, base, shadow, light, R, shift = 0.45, r0 = 1.05, r1 = 1.25) {
        const g = this.g, n = pts.length;
        let cx = 0, cy = 0;
        for (const [x, y] of pts){
            cx += x / n;
            cy += y / n;
        }
        const [gx, gy] = this.P(cx + Math.cos(light) * shift * R, cy + Math.sin(light) * shift * R);
        const gr = g.createRadialGradient(gx, gy, 0, gx, gy, r1 * R);
        gr.addColorStop(0, base);
        gr.addColorStop(r0 / r1, base);
        gr.addColorStop(1, shadow);
        this.path(pts, true);
        g.fillStyle = gr;
        g.fill();
    }
    gradFill(pts, base, shadow, light, flat = 0.22) {
        const g = this.g, dx = Math.cos(light), dy = Math.sin(light), n = pts.length;
        let cx = 0, cy = 0, lo = Infinity, hi = -Infinity;
        for (const [x, y] of pts){
            cx += x / n;
            cy += y / n;
            const d = x * dx + y * dy;
            lo = Math.min(lo, d);
            hi = Math.max(hi, d);
        }
        const dc = cx * dx + cy * dy;
        const [ax, ay] = this.P(cx + dx * (hi - dc), cy + dy * (hi - dc)), [bx, by] = this.P(cx + dx * (lo - dc), cy + dy * (lo - dc));
        const gr = g.createLinearGradient(ax, ay, bx, by);
        gr.addColorStop(0, base);
        gr.addColorStop(flat, base);
        gr.addColorStop(1, shadow);
        this.path(pts, true);
        g.fillStyle = gr;
        g.fill();
    }
    inkRing(pts, w0, thick, k = 0.45, col = INK) {
        const n = pts.length;
        let cx = 0, cy = 0;
        for (const [x, y] of pts){
            cx += x / n;
            cy += y / n;
        }
        const out = [], inn = [];
        pts.forEach((q, i)=>{
            const a = pts[(i + n - 1) % n], b = pts[(i + 1) % n];
            let nx = b[1] - a[1], ny = a[0] - b[0];
            const l = Math.hypot(nx, ny) || 1;
            nx /= l;
            ny /= l;
            const h = 0.5 * w0 * (1 + k * Math.cos(Math.atan2(q[1] - cy, q[0] - cx) - thick));
            out.push([
                q[0] + nx * h,
                q[1] + ny * h
            ]);
            inn.push([
                q[0] - nx * h,
                q[1] - ny * h
            ]);
        });
        const g = this.g;
        const trace = (r)=>{
            r.forEach(([x0, y0], i)=>{
                const [x, y] = this.P(x0, y0);
                if (i) g.lineTo(x, y);
                else g.moveTo(x, y);
            });
            g.closePath();
        };
        g.beginPath();
        trace(out);
        trace(inn.reverse());
        g.fillStyle = col;
        g.fill("evenodd");
    }
    band(pts, fill, w, rim, cap = "butt") {
        const g = this.g;
        g.lineCap = cap;
        g.lineJoin = "round";
        this.path(pts, false);
        g.strokeStyle = INK;
        g.lineWidth = w + 2 * rim;
        g.stroke();
        this.path(pts, false);
        g.strokeStyle = fill;
        g.lineWidth = w;
        g.stroke();
        g.lineCap = "round";
    }
}
const ellPts = (cx, cy, rx, ry, a0 = 0, a1 = 360, rot = 0, n = 48)=>{
    const r = rad(rot), pts = [];
    for(let i = 0; i <= n; i++){
        const a = rad(a0 + (a1 - a0) * i / n), x = rx * Math.cos(a), y = ry * Math.sin(a);
        pts.push([
            cx + x * Math.cos(r) - y * Math.sin(r),
            cy + x * Math.sin(r) + y * Math.cos(r)
        ]);
    }
    return pts;
};
const rrect = (x0, y0, x1, y1, r, n = 8)=>{
    const pts = [];
    for (const [cx, cy, a] of [
        [
            x1 - r,
            y0 + r,
            -90
        ],
        [
            x1 - r,
            y1 - r,
            0
        ],
        [
            x0 + r,
            y1 - r,
            90
        ],
        [
            x0 + r,
            y0 + r,
            180
        ]
    ])for(let i = 0; i <= n; i++)pts.push([
        cx + r * Math.cos(rad(a + 90 * i / n)),
        cy + r * Math.sin(rad(a + 90 * i / n))
    ]);
    return pts;
};
const taper = (p, a, b, wa, wb, col = INK)=>{
    const dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1, nx = -dy / l, ny = dx / l;
    p.poly([
        [
            a[0] + nx * wa / 2,
            a[1] + ny * wa / 2
        ],
        [
            b[0] + nx * wb / 2,
            b[1] + ny * wb / 2
        ],
        [
            b[0] - nx * wb / 2,
            b[1] - ny * wb / 2
        ],
        [
            a[0] - nx * wa / 2,
            a[1] - ny * wa / 2
        ]
    ], col, 0);
    p.dot(a[0], a[1], wa / 2, col);
    p.dot(b[0], b[1], wb / 2, col);
};
export const blobPts = (cx, cy, B, n = 72)=>{
    const ph = [
        rnd(B.seed, 11),
        rnd(B.seed, 12),
        rnd(B.seed, 13)
    ].map((v)=>v * Math.PI * 2);
    const pts = [];
    for(let i = 0; i < n; i++){
        const t = i / n * Math.PI * 2, c = Math.cos(t), s = Math.sin(t), e = 2 / (s < 0 ? B.nTop : B.nBot);
        let X = Math.sign(c) * Math.abs(c) ** e;
        const Y = Math.sign(s) * Math.abs(s) ** e;
        X *= (1 + B.egg * Y) * (1 + B.asym * Math.sign(X));
        const r = 1 + B.noise * (Math.cos(2 * t + ph[0]) + 0.7 * Math.cos(3 * t + ph[1]) + 0.5 * Math.cos(4 * t + ph[2]));
        const x = B.a * X * r, y = B.b * Y * r;
        pts.push([
            cx + x * Math.cos(B.rot) - y * Math.sin(B.rot),
            cy + x * Math.sin(B.rot) + y * Math.cos(B.rot)
        ]);
    }
    return pts;
};
export const headBlob = (seed, a = 118, facing = 0)=>({
        a,
        b: a * (0.94 + 0.08 * (rnd(seed, 1) - 0.5)),
        nTop: 1.75 + 0.3 * (rnd(seed, 2) - 0.5),
        nBot: 2.3 + 0.3 * (rnd(seed, 3) - 0.5),
        egg: -0.12 + 0.06 * (rnd(seed, 4) - 0.5),
        asym: (0.06 + 0.04 * rnd(seed, 5)) * (facing || (rnd(seed, 6) < 0.5 ? -1 : 1)),
        rot: rad(8 * (rnd(seed, 7) - 0.5)),
        noise: 0.008,
        seed
    });
export const thickAngle = (light)=>Math.atan2(-Math.sin(light) + 0.8, -Math.cos(light));
const DEF_LIGHT = rad(-120);
const FACE = {
    neutral: {
        eye: [
            "lid",
            "lid"
        ],
        brow: [
            0,
            -1
        ],
        mouth: "dash"
    },
    stern: {
        eye: [
            "lid",
            "lid"
        ],
        brow: [
            3,
            -2
        ],
        mouth: "frown"
    },
    grin: {
        eye: [
            "happy",
            "happy"
        ],
        brow: [
            -3,
            -3
        ],
        mouth: "grin"
    },
    laugh: {
        eye: [
            "squeeze",
            "squeeze"
        ],
        brow: [
            -4,
            -4
        ],
        mouth: "laugh"
    },
    whistle: {
        eye: [
            "dash",
            "dash"
        ],
        brow: [
            -2,
            -4
        ],
        mouth: "o"
    },
    nervous: {
        eye: [
            "small",
            "small"
        ],
        brow: [
            -3,
            2
        ],
        mouth: "wave"
    },
    shock: {
        eye: [
            "shock",
            "shock"
        ],
        brow: [
            -7,
            -6
        ],
        mouth: "O"
    },
    relief: {
        eye: [
            "happy",
            "happy"
        ],
        brow: [
            -2,
            1
        ],
        mouth: "smileWide"
    },
    relief_open: {
        eye: [
            "happy",
            "happy"
        ],
        brow: [
            -2,
            1
        ],
        mouth: "grin"
    },
    dazed: {
        eye: [
            "spiral",
            "spiral"
        ],
        brow: [
            -3,
            2
        ],
        mouth: "wave"
    },
    pained: {
        eye: [
            "squeeze",
            "lid"
        ],
        brow: [
            -3,
            2
        ],
        mouth: "teeth"
    },
    smile: {
        eye: [
            "dot",
            "dot"
        ],
        brow: [
            0,
            -1
        ],
        mouth: "smirk"
    },
    smile_closed: {
        eye: [
            "happy",
            "happy"
        ],
        brow: [
            0,
            -1
        ],
        mouth: "smile"
    },
    lick: {
        eye: [
            "dot",
            "dot"
        ],
        brow: [
            0,
            -1
        ],
        mouth: "lick"
    }
};
const halfLid = (k)=>k === "dot" || k === "small" ? "lid" : k === "lid" ? "slit" : k === "shock" ? "shockHalf" : k;
const eyeKind = (k, lid)=>lid >= 1 && k !== "happy" && k !== "squeeze" && k !== "spiral" ? "dash" : lid > 0 ? halfLid(k) : k;
const lidOf = (b)=>b === true ? 1 : Number(b) || 0;
const eye = (p, kind, x, ey, u, side, look, skin)=>{
    const lx = x + look * 3 * u, lw = 3.8 * u;
    switch(kind){
        case "dot":
            p.ell(lx, ey, 3.8 * u, 5.5 * u, INK, 0);
            break;
        case "small":
            p.ell(lx, ey, 3 * u, 4.4 * u, INK, 0);
            break;
        case "lid":
            p.ell(lx, ey - u, 7 * u, 6 * u, INK, 0, 0, 180);
            p.stroke([
                [
                    x - 9 * u,
                    ey - u
                ],
                [
                    x + 9 * u,
                    ey - u
                ]
            ], lw);
            break;
        case "slit":
            p.ell(lx, ey, 7 * u, 2.6 * u, INK, 0, 0, 180);
            p.stroke([
                [
                    x - 9 * u,
                    ey
                ],
                [
                    x + 9 * u,
                    ey
                ]
            ], lw);
            break;
        case "happy":
            p.arc(x, ey + 3 * u, 8 * u, 6 * u, 200, 340, lw);
            break;
        case "dash":
            p.stroke([
                [
                    x - 8.5 * u,
                    ey
                ],
                [
                    x + 8.5 * u,
                    ey
                ]
            ], lw);
            break;
        case "squeeze":
            p.stroke([
                [
                    x + 6 * u * side,
                    ey - 5 * u
                ],
                [
                    x - 6 * u * side,
                    ey
                ],
                [
                    x + 6 * u * side,
                    ey + 5 * u
                ]
            ], lw);
            break;
        case "shock":
        case "shockHalf":
            p.ell(x, ey, 11 * u, 11 * u, WHITE, 2.6 * u);
            p.dot(lx - side * 1.5 * u, ey + 1.5 * u, 3 * u);
            if (kind === "shockHalf") {
                p.ell(x, ey, 11 * u, 11 * u, skin, 0, 180, 360);
                p.stroke([
                    [
                        x - 11 * u,
                        ey
                    ],
                    [
                        x + 11 * u,
                        ey
                    ]
                ], 2.6 * u);
            }
            break;
        default:
            {
                const s = [];
                for(let t = 1; t < 15; t++)s.push([
                    x + Math.cos(t * 0.9) * t * 0.55 * u,
                    ey + Math.sin(t * 0.9) * t * 0.55 * u
                ]);
                p.stroke(s, 2.4 * u);
            }
    }
};
const dmouth = (p, mx, y, rx, ry, u, tongue = false)=>{
    p.ell(mx, y, rx, ry, MOUTH, 0, 0, 180);
    p.clip([
        [
            mx - rx,
            y
        ],
        [
            mx + rx,
            y
        ],
        [
            mx + rx,
            y + 3 * u
        ],
        [
            mx - rx,
            y + 3 * u
        ]
    ], ()=>p.ell(mx, y, rx, ry, WHITE, 0, 0, 180));
    if (tongue) p.ell(mx + 2 * u, y + 0.62 * ry, 0.4 * rx, 0.28 * ry, TONGUE, 0);
    p.ell(mx, y, rx, ry, null, 3 * u, 0, 180);
};
const mouth = (p, kind, mx, my, u, k = 1)=>{
    const mw = 4 * u;
    switch(kind){
        case "dash":
            p.stroke([
                [
                    mx - 5.5 * u * k,
                    my
                ],
                [
                    mx + 5.5 * u * k,
                    my - 0.8 * u
                ]
            ], mw);
            break;
        case "frown":
            p.arc(mx, my + 3 * u, 6.5 * u * k, 3.5 * u, 200, 340, mw);
            break;
        case "smirk":
            p.arc(mx + u, my - 3 * u, 7 * u * k, 4 * u, 10, 150, mw);
            break;
        case "smile":
            p.arc(mx, my - 3 * u, 8 * u * k, 4.5 * u, 20, 160, mw);
            break;
        case "smileWide":
            p.arc(mx, my - 4 * u, 11 * u * k, 6 * u, 15, 165, mw);
            break;
        case "grin":
            dmouth(p, mx, my - u, 12 * u * k, 8 * u, u);
            break;
        case "laugh":
            dmouth(p, mx, my, 16 * u * k, 11 * u, u, true);
            break;
        case "o":
            p.ell(mx + 4 * u, my, 3.5 * u, 4 * u, MOUTH, 2.8 * u);
            break;
        case "O":
            p.ell(mx, my + 2 * u, 9 * u * k, 11 * u, MOUTH, 3.2 * u);
            break;
        case "wave":
            {
                const s = [];
                for(let i = 0; i <= 12; i++)s.push([
                    mx - 9 * u * k + i * 1.5 * u * k,
                    my + 1.5 * u * Math.sin(i * 1.3)
                ]);
                p.stroke(s, 3 * u);
                break;
            }
        case "teeth":
            p.poly([
                [
                    mx - 12 * u * k,
                    my - 4 * u
                ],
                [
                    mx + 12 * u * k,
                    my - 4 * u
                ],
                [
                    mx + 11 * u * k,
                    my + 4 * u
                ],
                [
                    mx - 11 * u * k,
                    my + 4 * u
                ]
            ], WHITE, 3 * u);
            for (const j of [
                -1,
                0,
                1
            ])p.stroke([
                [
                    mx + j * 6 * u * k,
                    my - 4 * u
                ],
                [
                    mx + j * 6 * u * k,
                    my + 4 * u
                ]
            ], 1.5 * u);
            break;
        case "lick":
            p.arc(mx, my - 3 * u, 8 * u * k, 4.5 * u, 20, 160, mw);
            p.ell(mx + 6 * u * k, my + 3 * u, 3.6 * u, 4.6 * u, TONGUE, 2.4 * u);
            break;
    }
};
const faceFront = (p, cx, cy, W, expr, facing, look, lid, brim, skin, moustache, stout = false)=>{
    const u = W / 100, F = FACE[expr], fx = cx + 7 * u * facing;
    const ex = (F.eye[0] === "shock" ? 12 : 13) * u, ey = cy;
    for (const side of [
        -1,
        1
    ]){
        const x = fx + side * ex;
        const kind = eyeKind(F.eye[(facing ? side === facing : side > 0) ? 1 : 0], lid);
        eye(p, kind, x, ey, u, side, look, skin);
        const [dI, dO] = F.brow, by = ey - (brim ? 17 : 20) * u;
        if (kind === "shock" || kind === "shockHalf") p.arc(x, by - 6 * u, 9 * u, 3 * u, 200, 340, 4 * u);
        else taper(p, [
            x - side * 8.5 * u,
            by + dI * u
        ], [
            x + side * 8.5 * u,
            by + dO * u
        ], 5 * u, 2.5 * u);
    }
    const mx = cx + 8 * u * facing, my = cy + 20 * u;
    mouth(p, F.mouth, mx, my, u);
    if (moustache) for (const s of [
        -1,
        1
    ])taper(p, [
        mx + s * 1.5 * u,
        cy + 12.5 * u
    ], [
        mx + s * (stout ? 19 : 15) * u,
        cy + (stout ? 10.5 : 15) * u
    ], stout ? 5.5 * u : 4.5 * u, 1.6 * u, moustache);
    if (expr === "nervous") p.ell(cx + 40 * u * (facing || 1), cy - 22 * u, 3 * u, 5 * u, "#9fd4ff", 2 * u);
};
const faceSide = (p, hx, hy, W, expr, lid, brim, skin, moustache, stout = false)=>{
    const u = W / 100, F = FACE[expr], ex = hx + 27 * u, ey = hy;
    const kind = eyeKind(F.eye[1], lid);
    eye(p, kind, ex, ey, u, 1, 0.6, skin);
    const by = ey - (brim ? 17 : 20) * u, [dI, dO] = F.brow;
    if (kind === "shock" || kind === "shockHalf") p.arc(ex, by - 6 * u, 9 * u, 3 * u, 200, 340, 4 * u);
    else taper(p, [
        ex + 8 * u,
        by + dI * u
    ], [
        ex - 7 * u,
        by - u + dO * u
    ], 5 * u, 2.5 * u);
    p.stroke([
        [
            hx + 44 * u,
            hy + 4 * u
        ],
        [
            hx + 47.5 * u,
            hy + 9 * u
        ],
        [
            hx + 43 * u,
            hy + 10 * u
        ]
    ], 3 * u);
    mouth(p, F.mouth, hx + 33 * u, hy + 21 * u, u, 0.62);
    if (moustache) taper(p, [
        hx + 41 * u,
        hy + 13.5 * u
    ], [
        hx + 25 * u,
        hy + (stout ? 11.5 : 16) * u
    ], stout ? 5.5 * u : 4.5 * u, 1.6 * u, moustache);
    if (expr === "nervous") p.ell(hx - 30 * u, hy - 24 * u, 3 * u, 5 * u, "#9fd4ff", 2 * u);
};
const BONNET = "#e9cf8f", BONNET_BRIM = "#d6b46a";
const hatBehind = (p, o, H, cx, hc, light, thick, ow, side)=>{
    if (o.hat !== "bonnet") return;
    const bb = blobPts(cx - (side ? 12 : 0) * (H.a / 50), hc - 0.07 * 2 * H.b, {
        ...H,
        a: H.a * 1.17,
        b: H.b * 1.13,
        asym: 0,
        egg: 0.04,
        seed: H.seed + 3
    });
    p.shadedFill(bb, BONNET, mul(BONNET, SH_CLOTH), light, H.a * 1.17);
    p.inkRing(bb, ow * 0.85, thick);
};
const hatOn = (p, o, hp, H, cx, hc, light, seed, facing, side)=>{
    const W = 2 * H.a, HH = 2 * H.b, u = W / 100, crown = hc - H.b, ow = 0.85 * 5 * u;
    const a = H.rot + rad(4 * (rnd(seed, 20) - 0.5));
    const R = (pts)=>rotPts(pts, a, cx, hc);
    const sag = (yb, wb)=>{
        const base = [];
        for(let i = 0; i <= 12; i++){
            const t = i / 12;
            base.push([
                cx + wb * (2 * t - 1),
                yb + 3 * u * (1 - (2 * t - 1) ** 2)
            ]);
        }
        return base;
    };
    if (o.hat === "shako" || o.hat === "shako_tall") {
        const tall = o.hat === "shako_tall", yb = crown + 0.25 * HH, ht = (tall ? 0.66 : 0.56) * HH, wb = 46 * u, wt = 52 * u;
        const body = R([
            ...sag(yb, wb).reverse(),
            [
                cx - wt,
                yb - ht
            ],
            [
                cx + wt,
                yb - ht
            ]
        ]);
        p.shadedFill(body, "#3a3d47", "#24262d", light, wt, 0.4);
        if (tall) p.clip(body, ()=>p.band(R([
                [
                    cx - wt - 5 * u,
                    yb - ht + 0.07 * HH
                ],
                [
                    cx + wt + 5 * u,
                    yb - ht + 0.07 * HH
                ]
            ]), "#e8c45a", 0.06 * HH, 1.5 * u));
        p.poly(body, null, ow);
        const deg = a * 180 / Math.PI;
        if (side) {
            p.poly(R([
                [
                    cx + 36 * u,
                    yb - 1 * u
                ],
                [
                    cx + 60 * u,
                    yb + 8 * u
                ],
                [
                    cx + 34 * u,
                    yb + 6 * u
                ]
            ]), "#16171b", 2.5 * u);
            const [tx, ty] = R([
                [
                    cx + 24 * u,
                    yb - ht - 6 * u
                ]
            ])[0];
            p.ell(tx, ty, 7 * u, 7 * u, "#2b7a4b", 2.5 * u);
        } else {
            const [px, py] = R([
                [
                    cx + 3 * u * facing,
                    yb + 3 * u
                ]
            ])[0];
            p.ell(px, py, 34 * u, 0.045 * HH, "#16171b", 2.5 * u, 0, 180, deg);
            const [bx, by] = R([
                [
                    cx,
                    yb - 0.45 * ht
                ]
            ])[0];
            p.ell(bx, by, 7 * u, 6 * u, tall ? "#e8c45a" : "#c9ccd2", 2 * u, 0, 360, deg);
            p.arc(bx, by, 3.5 * u, 2.8 * u, 200, 500, 1.6 * u);
            const [tx, ty] = R([
                [
                    cx,
                    yb - ht - 6 * u
                ]
            ])[0];
            p.ell(tx, ty, 7 * u, 7 * u, "#2b7a4b", 2.5 * u);
        }
    } else if (o.hat === "cap" || o.hat === "hair") {
        const cut = crown + (o.hat === "cap" ? 0.3 : 0.42) * HH;
        const keep = (x, y)=>y < cut || side && o.hat === "hair" && x < cx - 6 * u && y < hc + 0.42 * H.b;
        const n = hp.length, startIdx = Math.max(0, hp.findIndex(([x, y], i)=>keep(x, y) && !keep(hp[(i + n - 1) % n][0], hp[(i + n - 1) % n][1])));
        const arc = [
            ...hp.slice(startIdx),
            ...hp.slice(0, startIdx)
        ].filter(([x, y])=>keep(x, y)).map(([x, y])=>[
                cx + (x - cx) * 1.03,
                hc + (y - hc) * 1.03
            ]);
        if (arc.length < 3) return;
        if (o.hat === "hair") {
            const [x0, y0] = arc[arc.length - 1], [x1, y1] = arc[0];
            for(let i = 1; i < 6; i++)arc.push([
                x0 + (x1 - x0) * i / 6,
                y0 + (y1 - y0) * i / 6 + (i % 2 ? 4 * u : 0)
            ]);
        }
        const col = o.hat === "cap" ? o.cap : o.hair;
        p.shadedFill(arc, col, mul(col, SH_FELT), light, H.a, 0.35);
        p.poly(arc, null, ow);
        if (o.hat === "hair") {
            const s = side ? -1 : facing || 1;
            p.stroke([
                [
                    cx + s * 10 * u,
                    cut - 30 * u
                ],
                [
                    cx + s * 2 * u,
                    cut - 12 * u
                ]
            ], 1.2 * u);
        }
        if (o.hat === "cap") {
            const deg = a * 180 / Math.PI;
            if (side) p.poly(R([
                [
                    cx + 40 * u,
                    cut - 2 * u
                ],
                [
                    cx + 74 * u,
                    cut + 4 * u
                ],
                [
                    cx + 40 * u,
                    cut + 6 * u
                ]
            ]), shade(col, 0.8), ow);
            else {
                const s = facing || (rnd(seed, 21) < 0.5 ? -1 : 1), [px, py] = R([
                    [
                        cx + s * 4 * u,
                        cut + 1.5 * u
                    ]
                ])[0];
                p.ell(px, py, 32 * u, 0.06 * HH, shade(col, 0.8), ow, 0, 180, deg);
            }
        }
    } else if (o.hat === "tophat") {
        const yb = crown + 0.22 * HH, ht = 0.8 * HH, wb = 0.31 * W, wt = 0.33 * W, col = "#2e2a36";
        const body = R([
            ...sag(yb, wb).reverse(),
            [
                cx - wt,
                yb - ht
            ],
            [
                cx + wt,
                yb - ht
            ]
        ]);
        p.shadedFill(body, col, mul(col, SH_FELT), light, wt, 0.4);
        p.clip(body, ()=>p.band(R([
                [
                    cx - wt - 4 * u,
                    yb - 0.13 * HH
                ],
                [
                    cx + wt + 4 * u,
                    yb - 0.13 * HH
                ]
            ]), shade(o.jacket, 0.9), 0.14 * HH, 0.8 * u));
        p.poly(body, null, ow);
        const [bx, by] = R([
            [
                cx,
                yb + 1 * u
            ]
        ])[0];
        p.ell(bx, by, 0.45 * W, 0.05 * HH, "#1d1b22", ow, 0, 360, a * 180 / Math.PI);
    } else if (o.hat === "bonnet") {
        const [bx, by] = R([
            [
                cx + (side ? 6 * u : 0),
                crown + 0.16 * HH
            ]
        ])[0];
        p.arc(bx, by, 0.5 * W, 0.2 * HH, 200, 340, 7 * u, BONNET_BRIM);
        p.arc(bx, by, 0.5 * W + 3.5 * u, 0.2 * HH + 3.5 * u, 200, 340, 1.2 * u);
        const cy = hc + H.b * 0.98;
        p.stroke([
            [
                cx - 14 * u,
                cy - 4 * u
            ],
            [
                cx,
                cy + 2 * u
            ],
            [
                cx + 14 * u,
                cy - 4 * u
            ]
        ], 2 * u, BONNET_BRIM);
    }
};
const BUILD = {
    adult: {
        a: 118,
        torso: 1.1,
        legs: 1.4,
        tw: 0.8
    },
    stout: {
        a: 118,
        torso: 1.15,
        legs: 1.32,
        tw: 0.92
    },
    kid: {
        a: 112,
        torso: 0.85,
        legs: 1.0,
        tw: 0.72
    }
};
const footStroke = (p, a, b, w, col)=>{
    if (col !== INK) p.stroke([
        a,
        b
    ], w + 3, INK);
    p.stroke([
        a,
        b
    ], w, col);
};
export const bodyFront = (p, o, opts)=>{
    const { phase = 0, expr = "neutral", mode = "march", look = 0, blink = false, lift = 60, prop = null, tilt = 0, headTilt = 0, wave, light = DEF_LIGHT, facing = 0, seed = 1 } = opts;
    const Bd = BUILD[o.build ?? "adult"], skin = o.skin ?? SKIN, two = Math.PI * 2, lid = lidOf(blink);
    const H = headBlob(seed, Bd.a, facing), W = 2 * H.a, HH = 2 * H.b, u = W / 100;
    const tall = (1 + Bd.torso + Bd.legs) * HH, sole = 975;
    const bob = mode === "march" ? 0.025 * tall * Math.cos(2 * two * phase) : mode === "stroll" ? 0.015 * tall * Math.cos(2 * two * phase) : 0;
    const torsoBot = mode === "sit" ? sole - 0.2 * HH : sole - Bd.legs * HH + bob;
    const chin = torsoBot - Bd.torso * HH, hc = chin - H.b, crown = hc - H.b, hipY = torsoBot - 0.12 * HH;
    const thick = thickAngle(light), ow = 5 * u;
    const legCol = mix(o.pants, INK, 0.55), armCol = mix(o.jacket, INK, 0.5), footCol = o.boots;
    const legW = 5.8 * u, footW = 7.5 * u;
    p.rot = null;
    if (mode === "sit") {
        for (const side of [
            -1,
            1
        ]){
            const h = [
                300 + side * 15 * u,
                hipY
            ], k = [
                300 + side * 36 * u,
                hipY + 0.2 * HH
            ], f = [
                300 + side * 44 * u,
                sole - 8 * u
            ];
            p.stroke(curve(h, k, f), legW, legCol);
            footStroke(p, [
                f[0] - side * 2 * u,
                f[1]
            ], [
                f[0] + side * 12 * u,
                f[1] - 5 * u
            ], footW, footCol);
        }
    } else if (mode === "fall") {
        const legs = [
            [
                [
                    300 - 15 * u,
                    hipY
                ],
                [
                    300 - 46 * u,
                    hipY + 0.5 * HH
                ],
                [
                    300 - 70 * u,
                    hipY + 0.72 * HH
                ]
            ],
            [
                [
                    300 + 15 * u,
                    hipY
                ],
                [
                    300 + 50 * u,
                    hipY + 0.45 * HH
                ],
                [
                    300 + 76 * u,
                    hipY + 0.22 * HH
                ]
            ]
        ];
        legs.forEach(([h, k, f], i)=>{
            p.stroke(curve(h, k, f), legW, legCol);
            footStroke(p, f, [
                f[0] + (i ? 14 : -14) * u,
                f[1] + (i ? -6 : 4) * u
            ], footW, footCol);
        });
    } else if (o.dress) {
        for (const side of [
            -1,
            1
        ]){
            const fx = 300 + side * 12 * u, fy = sole - 4 * u;
            p.stroke([
                [
                    fx,
                    sole - 0.4 * HH
                ],
                [
                    fx + side * u,
                    fy
                ]
            ], legW, legCol);
            footStroke(p, [
                fx - side * 3 * u,
                fy
            ], [
                fx + side * 12 * u,
                fy + u
            ], footW, footCol);
        }
    } else {
        const L = mode === "march" ? lift * 1.25 : mode === "stroll" ? lift * 0.55 : 0;
        for (const [side, ph] of [
            [
                -1,
                0
            ],
            [
                1,
                0.5
            ]
        ]){
            const up = Math.max(0, Math.sin(two * (phase + ph))) * L;
            const hx = 300 + side * 15 * u, fx = 300 + side * 22 * u, fy = sole - 4 * u - up;
            const k = [
                (hx + fx) / 2 + side * (1.5 * u + up * 0.16),
                (hipY + fy) / 2 - up * 0.08
            ];
            p.stroke(curve([
                hx,
                hipY
            ], k, [
                fx,
                fy
            ]), legW, legCol);
            footStroke(p, [
                fx - side * 3 * u,
                fy
            ], [
                fx + side * 13 * u,
                fy + 0.5 * u
            ], footW, footCol);
        }
    }
    const sway = mode === "march" ? 1.6 * Math.sin(two * phase) : mode === "stroll" ? 1.0 * Math.sin(two * phase) : 0;
    const A = tilt + sway;
    p.rot = A ? [
        rad(A),
        300,
        hipY
    ] : null;
    const dress = !!o.dress && mode !== "sit" && mode !== "fall";
    const T = {
        a: Bd.tw / 2 * W / 1.06,
        b: 0.5 * (torsoBot - (chin - 0.25 * HH)),
        nTop: 2.2,
        nBot: 2.6,
        egg: o.build === "stout" ? 0.17 : 0.12,
        asym: 0.04 * facing,
        rot: 0,
        noise: 0.006,
        seed: seed + 7
    };
    const tcx = 300 + 3 * u * facing, tcy = torsoBot - T.b, tp = blobPts(tcx, tcy, T);
    const sh = (side)=>[
            tcx + side * 0.85 * T.a,
            chin + 0.12 * HH
        ];
    const hang = (side, fwd)=>{
        const S = sh(side), ex = tcx + side * (1.12 * T.a + 4 * u);
        const hx = ex + side * 3 * u - side * 6 * u * Math.max(0, fwd) + side * 4 * u * Math.max(0, -fwd);
        return [
            S,
            [
                ex,
                S[1] + 0.48 * HH
            ],
            [
                hx,
                chin + 1.04 * HH - Math.abs(fwd) * 9 * u
            ]
        ];
    };
    const sw = mode === "march" || mode === "stroll" ? Math.sin(two * phase) : 0;
    const R0 = [
        300 + 47 * u,
        torsoBot + 0.12 * HH
    ], R1 = [
        300 + 64 * u,
        crown - 0.32 * HH
    ];
    const rifle = !!o.rifle && (mode === "march" || mode === "stand" || mode === "stroll");
    const arms = [];
    if (mode === "sit") for (const side of [
        -1,
        1
    ])arms.push({
        pts: [
            sh(side),
            [
                tcx + side * (1.1 * T.a + 6 * u),
                sh(side)[1] + 0.4 * HH
            ],
            [
                tcx + side * (1.2 * T.a + 10 * u),
                torsoBot + 0.04 * HH
            ]
        ],
        front: false
    });
    else if (mode === "fall") for (const side of [
        -1,
        1
    ])arms.push({
        pts: [
            sh(side),
            [
                tcx + side * (1.15 * T.a + 12 * u),
                sh(side)[1] - 0.25 * HH
            ],
            [
                tcx + side * (1.3 * T.a + 24 * u),
                sh(side)[1] - 0.68 * HH
            ]
        ],
        front: false
    });
    else {
        arms.push({
            pts: prop === "shako" ? hang(-1, 0) : hang(-1, -sw),
            front: false
        });
        if (rifle) {
            const G = lerp2(R0, R1, 0.1);
            arms.push({
                pts: [
                    sh(1),
                    [
                        tcx + 1.12 * T.a + 5 * u,
                        sh(1)[1] + 0.45 * HH
                    ],
                    G
                ],
                front: false
            });
        } else if (wave !== undefined) {
            const S = sh(1);
            arms.push({
                pts: [
                    S,
                    [
                        tcx + 1.1 * T.a + 10 * u + 3 * u * wave,
                        S[1] - 0.22 * HH
                    ],
                    [
                        tcx + 1.18 * T.a + 16 * u + 12 * u * wave,
                        S[1] - 0.6 * HH
                    ]
                ],
                front: false
            });
        } else if (prop === "icecream") {
            const S = sh(1);
            arms.push({
                pts: [
                    S,
                    [
                        tcx + 1.05 * T.a + 4 * u,
                        S[1] + 0.45 * HH
                    ],
                    [
                        tcx + 0.5 * T.a,
                        S[1] + 0.4 * HH
                    ]
                ],
                front: true
            });
        } else if (Array.isArray(prop)) {
            const S = sh(1), k = clamp(prop[1], 0, 1);
            const E = lerp2([
                tcx + 1.1 * T.a + 10 * u,
                S[1] - 0.15 * HH
            ], [
                tcx + 1.2 * T.a + 10 * u,
                S[1] + 0.3 * HH
            ], k);
            const Hd = lerp2([
                tcx + 1.15 * T.a + 14 * u,
                S[1] - 0.55 * HH
            ], [
                tcx + 1.45 * T.a + 22 * u,
                S[1] + 0.35 * HH
            ], k);
            arms.push({
                pts: [
                    S,
                    E,
                    Hd
                ],
                front: true
            });
        } else arms.push({
            pts: hang(1, sw),
            front: false
        });
    }
    const drawArm = (a)=>{
        p.stroke(curve(a.pts[0], a.pts[1], a.pts[2]), 5.2 * u, armCol);
        p.dot(a.pts[2][0], a.pts[2][1], 5.5 * u);
    };
    if (rifle) {
        p.band([
            R0,
            R1
        ], "#7a4b2a", 5 * u, 1.5 * u, "round");
        p.band([
            lerp2(R0, R1, 0.6),
            R1
        ], "#8d949c", 2.4 * u, 1.2 * u, "round");
    }
    if (o.sword && mode !== "sit") {
        const s0 = [
            tcx - 0.75 * T.a,
            torsoBot - 0.2 * HH
        ];
        p.band([
            s0,
            [
                s0[0] - Math.sin(rad(25)) * 0.8 * HH,
                s0[1] + Math.cos(rad(25)) * 0.8 * HH
            ]
        ], "#c9ccd2", 3 * u, 1.2 * u, "round");
    }
    for (const a of arms)if (!a.front) drawArm(a);
    if (dress) {
        const D = {
            a: 0.5 * W * 0.98,
            b: 0.5 * (sole - 0.35 * HH - (chin - 0.2 * HH)),
            nTop: 2.0,
            nBot: 3.0,
            egg: 0.35,
            asym: 0.03 * facing,
            rot: 0,
            noise: 0.006,
            seed: seed + 9
        };
        const dp = blobPts(300, sole - 0.35 * HH - D.b, D);
        p.gradFill(dp, o.dress, mul(o.dress, SH_CLOTH), light);
        p.inkRing(dp, ow, thick);
        const Sw = {
            a: 0.37 * W,
            b: 0.3 * HH,
            nTop: 2.2,
            nBot: 2.4,
            egg: 0.1,
            asym: 0,
            rot: 0,
            noise: 0.006,
            seed: seed + 8
        };
        const sp = blobPts(300, chin + 0.12 * HH, Sw);
        p.gradFill(sp, o.jacket, mul(o.jacket, SH_CLOTH), light);
        p.inkRing(sp, ow * 0.9, thick);
    } else {
        p.gradFill(tp, o.jacket, mul(o.jacket, SH_CLOTH), light);
        p.clip(tp, ()=>{
            if (o.belt) {
                for (const s of [
                    -1,
                    1
                ])p.band([
                    [
                        tcx - s * 0.75 * T.a,
                        chin - 0.05 * HH
                    ],
                    [
                        tcx + s * 0.8 * T.a,
                        torsoBot - 0.1 * HH
                    ]
                ], o.belt, 5.5 * u, 1.8 * u);
                const xc = tcx + 0.025 * T.a, yc = chin - 0.05 * HH + (torsoBot - 0.1 * HH - (chin - 0.05 * HH)) * (0.75 / 1.55);
                p.poly([
                    [
                        xc - 3.5 * u,
                        yc - 3.5 * u
                    ],
                    [
                        xc + 3.5 * u,
                        yc - 3.5 * u
                    ],
                    [
                        xc + 3.5 * u,
                        yc + 3.5 * u
                    ],
                    [
                        xc - 3.5 * u,
                        yc + 3.5 * u
                    ]
                ], "#d9dde0", 1.5 * u);
            }
            if (o.sash) p.band([
                [
                    tcx - 1.3 * T.a,
                    torsoBot - 0.32 * HH
                ],
                [
                    tcx + 1.3 * T.a,
                    torsoBot - 0.32 * HH
                ]
            ], o.sash, 0.13 * HH, 1.8 * u);
            for(let i = 0; i < 4; i++){
                const y = chin + 0.12 * HH + i * 0.2 * HH;
                if (o.sash && Math.abs(y - (torsoBot - 0.32 * HH)) < 0.08 * HH) continue;
                p.dot(tcx + 2 * u * facing, y, 2.2 * u + 0.8 * u, INK);
                p.dot(tcx + 2 * u * facing, y, 2.2 * u, o.buttons ?? shade(o.jacket, 0.7));
            }
        });
        if (o.sash) {
            const s = facing || 1;
            p.poly([
                [
                    tcx + s * 0.55 * T.a,
                    torsoBot - 0.3 * HH
                ],
                [
                    tcx + s * 0.75 * T.a,
                    torsoBot + 0.05 * HH
                ],
                [
                    tcx + s * 0.45 * T.a,
                    torsoBot + 0.02 * HH
                ]
            ], o.sash, 1.6 * u);
        }
        p.inkRing(tp, ow, thick);
    }
    for (const a of arms)if (a.front) {
        drawArm(a);
        const [hx, hy] = a.pts[2];
        if (prop === "icecream") {
            p.poly([
                [
                    hx - 8 * u,
                    hy - 12 * u
                ],
                [
                    hx + 8 * u,
                    hy - 12 * u
                ],
                [
                    hx,
                    hy + 7 * u
                ]
            ], "#e0a35a", 1.8 * u);
            p.ell(hx, hy - 19 * u, 11 * u, 10 * u, "#f7c6d9", 2.2 * u);
            p.dot(hx, hy, 5.5 * u);
        } else if (Array.isArray(prop)) {
            const ang = rad(-70 + 105 * clamp(prop[1], 0, 1));
            const Rh = (pts)=>rotPts(pts, ang, hx, hy);
            p.band(Rh([
                [
                    hx,
                    hy + 12 * u
                ],
                [
                    hx,
                    hy - 44 * u
                ]
            ]), "#8a5a34", 5 * u, 1.5 * u, "round");
            p.poly(Rh([
                [
                    hx - 12 * u,
                    hy - 58 * u
                ],
                [
                    hx + 20 * u,
                    hy - 58 * u
                ],
                [
                    hx + 20 * u,
                    hy - 42 * u
                ],
                [
                    hx - 12 * u,
                    hy - 42 * u
                ]
            ]), "#7d848c", 2.2 * u);
            p.dot(hx, hy, 5.5 * u);
        }
    }
    if (prop === "shako") {
        const [hx, hy] = arms[0].pts[2];
        p.poly([
            [
                hx - 14 * u,
                hy + 3 * u
            ],
            [
                hx + 14 * u,
                hy + 3 * u
            ],
            [
                hx + 16 * u,
                hy + 30 * u
            ],
            [
                hx - 16 * u,
                hy + 30 * u
            ]
        ], "#3a3d47", 2.2 * u);
        p.ell(hx, hy + 31 * u, 3.5 * u, 3.5 * u, "#2b7a4b", 1.5 * u);
        p.dot(hx, hy, 5.5 * u);
    }
    const Ah = A + headTilt, [cpx, cpy] = rotAbout([
        300,
        chin
    ], rad(A), [
        300,
        hipY
    ]);
    p.rot = Ah ? [
        rad(Ah),
        300,
        chin,
        cpx - 300,
        cpy - chin
    ] : null;
    hatBehind(p, o, H, 300, hc, light, thick, ow, false);
    const hp = blobPts(300, hc, H);
    p.shadedFill(hp, skin, mul(skin, SH_SKIN), light, H.a);
    p.inkRing(hp, ow, thick);
    hatOn(p, o, hp, H, 300, hc, light, seed, facing, false);
    const brim = !!o.hat && o.hat !== "hair" && o.hat !== "bonnet" && o.hat !== "cap";
    faceFront(p, 300, hc, W, expr, facing, look, lid, brim, skin, o.moustache, o.build === "stout");
    p.rot = null;
};
const ik = (hip, ank, l1, l2)=>{
    const dx = ank[0] - hip[0], dy = ank[1] - hip[1], d = clamp(Math.hypot(dx, dy), 1, l1 + l2 - 0.01);
    const A = Math.acos(clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1)), k = Math.atan2(dy, dx) - A;
    return [
        hip[0] + l1 * Math.cos(k),
        hip[1] + l1 * Math.sin(k)
    ];
};
const SWING_HIP = 733;
export const bodySide = (p, o, opts)=>{
    const { phase = 0, expr = "neutral", mode = "march", blink = false, stomp = 1, pose = 0, stride = 1, light = DEF_LIGHT, seed = 1 } = opts;
    const Bd = BUILD[o.build ?? "adult"], skin = o.skin ?? SKIN, two = Math.PI * 2, lid = lidOf(blink);
    const H = {
        ...headBlob(seed, Bd.a, 1),
        asym: 0.12,
        rot: rad(3 + 3 * (rnd(seed, 7) - 0.5))
    };
    const W = 2 * H.a, HH = 2 * H.b, u = W / 100, sole = 975, ankY = sole - 4 * u;
    const thick = thickAngle(light), ow = 5 * u;
    const legLen = (Bd.legs + 0.12) * HH - 4 * u, l1 = legLen / 2, l2 = legLen / 2;
    const nearCol = mix(o.pants, INK, 0.55), farCol = mix(o.pants, INK, 0.75), footCol = o.boots;
    const legs = [];
    let hipY = ankY - legLen * 0.995, lean = 0, nearFwd = 0;
    if (mode === "march") {
        const S = 370 * stride, liftH = Math.max(22, 40 + 70 * (stomp - 1));
        const st = (ph)=>{
            const c = ((phase + ph) % 1 + 1) % 1;
            if (c < 0.5) {
                const s = c / 0.5;
                return {
                    x: S / 2 - S * s,
                    h: 0,
                    stance: true,
                    s
                };
            }
            const s = (c - 0.5) / 0.5;
            return {
                x: -S / 2 + S * s - S / Math.PI * Math.sin(2 * Math.PI * s),
                h: liftH * Math.sin(Math.PI * s),
                stance: false,
                s
            };
        };
        const nL = st(0), fL = st(0.5), stance = nL.stance ? nL : fL;
        const Leff = legLen * (1 - 0.035 * Math.sin(Math.PI * stance.s));
        hipY = ankY - Math.sqrt(Math.max(1, Leff * Leff - stance.x * stance.x));
        for (const [L, near] of [
            [
                fL,
                false
            ],
            [
                nL,
                true
            ]
        ])legs.push({
            ank: [
                300 + L.x,
                ankY - L.h
            ],
            pitch: L.stance ? 0 : rad(35 * Math.sin(Math.PI * L.s) * (1 - 1.6 * L.s)),
            near
        });
        lean = 4 + 3 * Math.cos(2 * two * phase);
        nearFwd = nL.x / (S / 2);
    } else if (mode === "push") {
        hipY = ankY - 0.87 * legLen;
        legs.push({
            ank: [
                300 - 0.5 * legLen,
                ankY
            ],
            pitch: rad(-8),
            near: false
        }, {
            ank: [
                300 + 0.32 * legLen,
                ankY
            ],
            pitch: 0,
            near: true
        });
        lean = 14 * pose;
    } else if (mode === "swing") {
        hipY = SWING_HIP;
        const a = rad(60 * pose);
        for (const [dx, near] of [
            [
                -6,
                false
            ],
            [
                0,
                true
            ]
        ]){
            const knee = [
                300 + l1 * 0.98 + dx * u,
                hipY + 6 * u
            ];
            legs.push({
                ank: [
                    knee[0] + l2 * Math.sin(a),
                    knee[1] + l2 * Math.cos(a)
                ],
                pitch: -a * 0.5,
                near
            });
        }
    } else {
        legs.push({
            ank: [
                300 - 4 * u,
                ankY
            ],
            pitch: 0,
            near: false
        }, {
            ank: [
                300 + 4 * u,
                ankY
            ],
            pitch: 0,
            near: true
        });
    }
    const torsoBot = hipY + 0.12 * HH, chin = torsoBot - Bd.torso * HH, hc = chin - H.b, crown = hc - H.b, hip = [
        300,
        hipY
    ];
    p.rot = null;
    for (const L of legs){
        const knee = mode === "swing" ? [
            300 + l1 * 0.98 + (L.near ? 0 : -6 * u),
            hipY + 6 * u
        ] : ik(hip, L.ank, l1, l2);
        const hp0 = [
            300 + (L.near ? 0 : -5 * u),
            hipY
        ];
        p.stroke([
            hp0,
            knee,
            L.ank
        ], 5.8 * u, L.near ? nearCol : farCol);
        const c = Math.cos(L.pitch), s = Math.sin(L.pitch);
        footStroke(p, [
            L.ank[0] - 3 * u * c,
            L.ank[1] - 3 * u * s
        ], [
            L.ank[0] + 13 * u * c,
            L.ank[1] + 13 * u * s + 0.5 * u
        ], 7.5 * u, L.near ? footCol : footCol === INK ? INK : shade(footCol, 0.82));
    }
    p.rot = lean ? [
        rad(lean),
        300,
        hipY
    ] : null;
    const T = {
        a: (o.build === "stout" ? 0.36 : 0.31) * W,
        b: 0.5 * (torsoBot - (chin - 0.25 * HH)),
        nTop: 2.2,
        nBot: 2.5,
        egg: 0.1,
        asym: 0.06,
        rot: 0,
        noise: 0.006,
        seed: seed + 7
    };
    const tcx = 300 + 2 * u, tcy = torsoBot - T.b, tp = blobPts(tcx, tcy, T);
    const armCol = mix(o.jacket, INK, 0.5), farArm = mix(o.jacket, INK, 0.68);
    const S = [
        tcx + 0.05 * T.a,
        chin + 0.14 * HH
    ], aLen = 0.95 * HH;
    const swingArm = (ang)=>{
        const e = [
            S[0] + Math.sin(ang) * aLen * 0.5,
            S[1] + Math.cos(ang) * aLen * 0.5
        ], a2 = ang + rad(16) * Math.sign(ang || 1);
        return [
            S,
            e,
            [
                e[0] + Math.sin(a2) * aLen * 0.5,
                e[1] + Math.cos(a2) * aLen * 0.5
            ]
        ];
    };
    const rifle = !!o.rifle && (mode === "march" || mode === "stand");
    const B0 = [
        tcx + 0.72 * T.a,
        chin + 0.58 * HH
    ], B1 = [
        tcx - 0.95 * T.a - 22 * u,
        crown - 0.4 * HH
    ];
    let near, far;
    if (mode === "swing") {
        near = [
            S,
            [
                S[0] + 12 * u,
                S[1] - 0.16 * HH
            ],
            [
                300 + 6 * u,
                chin - 0.3 * HH
            ]
        ];
        far = [
            S,
            [
                S[0] + 8 * u,
                S[1] - 0.18 * HH
            ],
            [
                300 + 2 * u,
                chin - 0.36 * HH
            ]
        ];
    } else if (mode === "push") {
        const reach = 0.55 * HH + 0.45 * HH * pose;
        let hN = [
            S[0] + reach,
            S[1] + 0.06 * HH
        ];
        if (opts.hand) {
            const th = -rad(lean), dx = opts.hand[0] - 300, dy = opts.hand[1] - hipY;
            const tg = [
                300 + dx * Math.cos(th) - dy * Math.sin(th),
                hipY + dx * Math.sin(th) + dy * Math.cos(th)
            ];
            hN = [
                hN[0] + (tg[0] - hN[0]) * pose,
                hN[1] + (tg[1] - hN[1]) * pose
            ];
        }
        near = [
            S,
            [
                (S[0] + hN[0]) / 2,
                (S[1] + hN[1]) / 2 + 0.06 * HH
            ],
            hN
        ];
        far = [
            S,
            [
                (S[0] + hN[0]) / 2 - 4 * u,
                (S[1] + hN[1]) / 2 - 0.02 * HH
            ],
            [
                hN[0] - 6 * u,
                hN[1] - 0.08 * HH
            ]
        ];
    } else if (rifle) {
        near = [
            S,
            [
                S[0] - 4 * u,
                S[1] + 0.42 * HH
            ],
            B0
        ];
        far = mode === "march" ? swingArm(rad(30) * nearFwd) : swingArm(0);
    } else {
        near = swingArm(rad(-30) * nearFwd);
        far = mode === "march" ? swingArm(rad(30) * nearFwd) : null;
    }
    if (far) {
        p.stroke(curve(far[0], far[1], far[2]), 5.2 * u, farArm);
        p.dot(far[2][0], far[2][1], 5.5 * u);
    }
    p.gradFill(tp, o.jacket, mul(o.jacket, SH_CLOTH), light);
    p.clip(tp, ()=>{
        if (o.belt) p.band([
            [
                tcx - 0.65 * T.a,
                chin - 0.05 * HH
            ],
            [
                tcx + 0.75 * T.a,
                torsoBot - 0.1 * HH
            ]
        ], o.belt, 5.5 * u, 1.8 * u);
        if (o.sash) p.band([
            [
                tcx - 1.3 * T.a,
                torsoBot - 0.32 * HH
            ],
            [
                tcx + 1.3 * T.a,
                torsoBot - 0.32 * HH
            ]
        ], o.sash, 0.13 * HH, 1.8 * u);
        if (!o.dress) for(let i = 0; i < 3; i++){
            const y = chin + 0.16 * HH + i * 0.24 * HH;
            p.dot(tcx + 0.8 * T.a, y, 3 * u, INK);
            p.dot(tcx + 0.8 * T.a, y, 2.2 * u, o.buttons ?? shade(o.jacket, 0.7));
        }
    });
    p.inkRing(tp, ow, thick);
    if (rifle) {
        p.band([
            B0,
            B1
        ], "#7a4b2a", 5 * u, 1.5 * u, "round");
        p.band([
            lerp2(B0, B1, 0.6),
            B1
        ], "#8d949c", 2.4 * u, 1.2 * u, "round");
    }
    p.stroke(curve(near[0], near[1], near[2]), 5.2 * u, armCol);
    p.dot(near[2][0], near[2][1], 5.5 * u);
    const hx = 300 + 4 * u;
    hatBehind(p, o, H, hx, hc, light, thick, ow, true);
    const hp = blobPts(hx, hc, H);
    p.shadedFill(hp, skin, mul(skin, SH_SKIN), light, H.a);
    p.inkRing(hp, ow, thick);
    hatOn(p, o, hp, H, hx, hc, light, seed, 1, true);
    const brim = !!o.hat && o.hat !== "hair" && o.hat !== "bonnet" && o.hat !== "cap";
    faceSide(p, hx, hc, W, expr, lid, brim, skin, o.moustache, o.build === "stout");
    p.rot = null;
};
export const swingKid = (p, o, kick, expr, light = DEF_LIGHT, blink = 0)=>{
    const rope = 1830, k = 1.1, HH = 2 * headBlob(5, BUILD[o.build ?? "adult"].a, 1).b;
    const seat = rope + 18, x0 = 150, x1 = 550;
    p.line([
        [
            350,
            20
        ],
        [
            x0 + 16,
            seat + 4
        ]
    ], "#a07a4c", 10);
    p.poly(rrect(x0, seat, x1, seat + 36, 10), "#b5653f", 9);
    const g = p.g;
    g.save();
    g.translate(350 - 300 * k, rope + 18 - (SWING_HIP + 0.12 * HH) * k);
    g.scale(k, k);
    bodySide(new Pen(g), o, {
        expr,
        mode: "swing",
        pose: kick,
        light,
        seed: 5,
        blink
    });
    g.restore();
    p.line([
        [
            350,
            20
        ],
        [
            x1 - 16,
            seat + 4
        ]
    ], "#a07a4c", 10);
};
export const fxNote = (p, kind, col = "#1f2a44")=>{
    p.ell(70, 200, 46, 34, col, 8, 0, 360, -20);
    p.stroke([
        [
            110,
            190
        ],
        [
            110,
            40
        ]
    ], 14);
    if (kind === 0) p.poly([
        [
            110,
            40
        ],
        [
            170,
            70
        ],
        [
            170,
            110
        ],
        [
            110,
            82
        ]
    ], col, 8);
    else {
        p.ell(150, 170, 40, 30, col, 8, 0, 360, -20);
        p.stroke([
            [
                186,
                160
            ],
            [
                186,
                20
            ]
        ], 14);
        p.poly([
            [
                110,
                40
            ],
            [
                186,
                20
            ],
            [
                186,
                50
            ],
            [
                110,
                70
            ]
        ], col, 8);
    }
};
export const fxBurst = (p, t, col = "#fff3b0", rays = 10, r0 = 40, r1 = 230)=>{
    const c = 250, e = 1 - (1 - t) ** 3;
    for(let i = 0; i < rays; i++){
        const a = rad(i * 360 / rays + 7 * (i % 2)), ra = r0 + (r1 - r0) * e * (0.75 + 0.25 * (i % 2));
        p.poly([
            [
                c + r0 * 0.5 * Math.cos(a + 0.18),
                c + r0 * 0.5 * Math.sin(a + 0.18)
            ],
            [
                c + ra * Math.cos(a),
                c + ra * Math.sin(a)
            ],
            [
                c + r0 * 0.5 * Math.cos(a - 0.18),
                c + r0 * 0.5 * Math.sin(a - 0.18)
            ]
        ], col, Math.max(3, 8 * (1 - t)));
    }
    if (t < 0.5) p.ell(c, c, r0 * (1.4 - t), r0 * (1.4 - t), WHITE, 8);
};
export const fxSplash = (p, t)=>{
    const c = 400, size = 800, rise = Math.sin(Math.min(1, t * 1.3) * Math.PI);
    const blue = "#bfe8ff", deep = "#6cc0f0";
    if (rise > 0.02) {
        const pts = [];
        for(let i = 0; i < 19; i++){
            const h = (i % 2 ? 260 : 130) * rise * (0.7 + 0.3 * Math.sin(i * 1.7));
            pts.push([
                c - 330 + 660 * i / 18,
                size - 120 - h
            ]);
        }
        p.poly([
            ...pts,
            [
                c + 330,
                size - 90
            ],
            [
                c - 330,
                size - 90
            ]
        ], blue, 10);
        p.ell(c, size - 100, 360, 46, deep, 10);
    }
    for(let i = 0; i < 8; i++){
        const a = rad(200 + i * 18), d = 120 + 380 * t, y = size - 160 + d * Math.sin(a) + 520 * t * t, r = 26 * (1 - t) + 6;
        if (t > 0.08 && y < size - 40) p.ell(c + d * Math.cos(a), y, r, r * 1.25, blue, 7);
    }
};
export const fxPuff = (p, t)=>{
    for(let i = 0; i < 5; i++){
        const a = rad(160 + i * 55), d = 40 + 70 * t, r = (34 + 20 * (i % 2)) * (1 - 0.6 * t);
        p.ell(150 + d * Math.cos(a), 180 + d * 0.45 * Math.sin(a), r, r * 0.8, `rgba(238,225,205,${(1 - t).toFixed(3)})`, 0);
    }
};
export const fxStars = (p, t)=>{
    for(let i = 0; i < 4; i++){
        const a = t * Math.PI * 2 + i * Math.PI / 2, x = 210 + 150 * Math.cos(a), y = 110 + 40 * Math.sin(a), pts = [];
        for(let k = 0; k < 10; k++){
            const r = k % 2 ? 14 : 34, b = rad(k * 36 - 90);
            pts.push([
                x + r * Math.cos(b),
                y + r * Math.sin(b)
            ]);
        }
        p.poly(pts, "#ffd84a", 6);
    }
};
export const fxCreak = (p, t)=>{
    const j = 6 * Math.sin(t * 40);
    for (const a of [
        -30,
        0,
        30
    ]){
        const b = rad(a - 90);
        p.stroke([
            [
                150 + 70 * Math.cos(b) + j,
                230 + 70 * Math.sin(b)
            ],
            [
                150 + 100 * Math.cos(b) + 10 + j,
                230 + 100 * Math.sin(b)
            ],
            [
                150 + 130 * Math.cos(b) + j,
                230 + 130 * Math.sin(b)
            ]
        ], 10);
    }
};
export const fxRing = (p, t)=>{
    const g = p.g;
    for(let k = 0; k < 3; k++){
        const u = t - k * 0.22;
        if (u <= 0 || u >= 1) continue;
        g.beginPath();
        g.ellipse(300, 300, 60 + 230 * u, 60 + 230 * u, 0, 0, Math.PI * 2);
        g.strokeStyle = k === 0 ? "#f6fcff" : "#cfe8fa";
        g.lineWidth = 9 * (1 - u) + 3;
        g.stroke();
    }
};
export const fxSign = (p)=>{
    const g = p.g, RED = "#d42f2f";
    p.poly(rrect(14, 14, 686, 506, 40), "#f6ecd2", 0);
    p.poly(rrect(14, 14, 686, 506, 40), null, 14);
    p.poly(rrect(70, 352, 630, 384, 8), "#8a5a3a", 9);
    g.beginPath();
    g.moveTo(112, 470);
    g.quadraticCurveTo(350, 300, 588, 470);
    g.strokeStyle = INK;
    g.lineWidth = 16;
    g.lineCap = "round";
    g.stroke();
    for (const x of [
        88,
        612
    ])p.poly(rrect(x - 16, 384, x + 16, 470, 4), "#8a5a3a", 9);
    for (const x of [
        150,
        278,
        406,
        534
    ]){
        p.poly(rrect(x - 30, 150, x + 30, 214, 14), "#357650", 9);
        p.stroke([
            [
                x - 8,
                210
            ],
            [
                x + 34,
                262
            ],
            [
                x + 46,
                338
            ]
        ], 15, INK);
        p.stroke([
            [
                x + 6,
                210
            ],
            [
                x - 12,
                274
            ],
            [
                x - 36,
                336
            ]
        ], 15, INK);
        p.poly(rrect(x + 30, 330, x + 74, 350, 9), INK, 0);
        p.poly(rrect(x - 52, 328, x - 8, 348, 9), INK, 0);
    }
    for (const [a, b] of [
        [
            [
                96,
                70
            ],
            [
                604,
                452
            ]
        ],
        [
            [
                604,
                70
            ],
            [
                96,
                452
            ]
        ]
    ]){
        p.stroke([
            a,
            b
        ], 58, "#ffffff");
        p.stroke([
            a,
            b
        ], 42, RED);
    }
};
export const fxCloud = (p, seed)=>{
    const blobs = [
        [
            150,
            190,
            80
        ],
        [
            250,
            150,
            105
        ],
        [
            360,
            160,
            95
        ],
        [
            450,
            195,
            70
        ],
        [
            300,
            210,
            90
        ]
    ];
    for (const [x, y, r] of blobs)p.ell(x + seed * 37 % 20 - 10, y, r, r * 0.8, "#ffffff", 0);
    p.ell(300, 235, 230, 40, "#ffffff", 0);
};
export const fxShadow = (p, col)=>{
    const g = p.g;
    g.fillStyle = WHITE;
    g.fillRect(0, 0, 128, 256);
    g.save();
    g.filter = "blur(9px)";
    const lg = g.createLinearGradient(0, 205, 0, 22);
    lg.addColorStop(0, mix(col, WHITE, 0.08));
    lg.addColorStop(0.55, mix(col, WHITE, 0.3));
    lg.addColorStop(1, mix(col, WHITE, 0.85));
    g.fillStyle = lg;
    g.beginPath();
    g.moveTo(40, 205);
    g.bezierCurveTo(36, 120, 46, 50, 64, 30);
    g.bezierCurveTo(82, 50, 92, 120, 88, 205);
    g.closePath();
    g.fill();
    g.fillStyle = col;
    g.beginPath();
    g.ellipse(64, 205, 30, 17, 0, 0, Math.PI * 2);
    g.fill();
    g.restore();
};
export const fxContact = (p, col)=>{
    const g = p.g;
    g.fillStyle = WHITE;
    g.fillRect(0, 0, 128, 128);
    const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
    for (const [r, k] of [
        [
            0,
            0
        ],
        [
            0.32,
            0.02
        ],
        [
            0.5,
            0.22
        ],
        [
            0.66,
            0.58
        ],
        [
            0.82,
            0.88
        ],
        [
            1,
            1
        ]
    ])gr.addColorStop(r, mix(col, WHITE, k));
    g.fillStyle = gr;
    g.fillRect(0, 0, 128, 128);
};
export const fxPlank = (p)=>{
    p.poly(rrect(14, 30, 306, 78, 10), "#a8744a", 9);
    p.line([
        [
            40,
            46
        ],
        [
            150,
            44
        ],
        [
            270,
            50
        ]
    ], "#7d5234", 4);
    p.line([
        [
            60,
            62
        ],
        [
            200,
            64
        ],
        [
            284,
            60
        ]
    ], "#7d5234", 4);
    p.dot(36, 54, 5, INK);
    p.dot(284, 54, 5, INK);
};
export const fxDrum = (p)=>{
    p.poly(rrect(40, 70, 220, 190, 16), "#f1ece0", 9);
    p.poly(rrect(32, 58, 228, 86, 12), "#c9373a", 8);
    p.poly(rrect(32, 176, 228, 204, 12), "#c9373a", 8);
    p.line([
        [
            52,
            88
        ],
        [
            82,
            172
        ],
        [
            112,
            88
        ],
        [
            142,
            172
        ],
        [
            172,
            88
        ],
        [
            202,
            172
        ]
    ], INK, 6);
    p.ell(130, 58, 98, 18, "#f7f3ea", 8);
};
export const fxBlob = (p, col)=>{
    const g = p.g;
    g.fillStyle = WHITE;
    g.fillRect(0, 0, 128, 128);
    const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
    for (const [r, k] of [
        [
            0,
            0
        ],
        [
            0.5,
            0.04
        ],
        [
            0.64,
            0.18
        ],
        [
            0.76,
            0.42
        ],
        [
            0.87,
            0.72
        ],
        [
            0.95,
            0.92
        ],
        [
            1,
            1
        ]
    ])gr.addColorStop(r, mix(col, WHITE, k));
    g.fillStyle = gr;
    g.fillRect(0, 0, 128, 128);
};
// V3 Studio Master Cast & Biomechanics Upgrade:
// - True 2-Bone Anatomical Sprint/Walk Kinematics (Far-Limb Behind Torso, Near-Limb In Front,
//   Full -36°..+50° Thigh Stride, 82° Heel-Kick Recovery Knee Fold, Ground-Locked Foot Strike!)
// - 12 Situation-Accurate Rick Clips Human Facial Expressions (Zero sleepy half-lids during panic!)
// - Nightmare Horror Zombies (Necrotic Veins, Sunken Bruised Sockets, Glowing Pinprick Eyes, Bloody Fangs!)
// - Full V3 5-Act Cast: YOU, Police Officer, Woman (Plead -> Uncanny Twist), Infected Road Runner,
//   Fleeing Civilians, 3 Nightmare Zombies, Underground Older Survivor Man (Shush -> Pale Horror) & Young Boy!
// Appended to toonbase.js -> toon.js

const RICK_HEAD = "#f7f3ea";
const PALE_HEAD = "#dfe5e3";
const INF_HEAD  = "#9eb0a6";

export const ROLES = {
  you:       { jacket: "#2c5b7c", jacket2: "#1d3e56", trim: "#dce7ef", pants: "#262e3a", hair: "#3a271d", skin: RICK_HEAD, hoodie: true, seed: 11 },
  police:    { jacket: "#1c2d45", jacket2: "#121e30", badge: "#f2c64b", belt: "#181a1f", pants: "#182436", cap: "#19283e", hair: "#2b1e17", skin: RICK_HEAD, seed: 23 },
  woman:     { jacket: "#8c384a", jacket2: "#662635", trim: "#f2e5dd", pants: "#322c38", hair: "#2b1b20", longHair: true, skin: RICK_HEAD, seed: 37 },
  carMan:    { jacket: "#b83e32", jacket2: "#872b22", trim: "#e6dec8", pants: "#2b323b", hair: "#3d2a20", skin: "#d9dad4", seed: 41 },
  runnerA:   { jacket: "#d49c38", jacket2: "#a87926", trim: "#2d3b48", pants: "#2e343d", hair: "#261c18", skin: RICK_HEAD, seed: 53 },
  runnerB:   { jacket: "#4b754e", jacket2: "#365739", trim: "#e8dfc8", pants: "#2b3238", cap: "#3a5a3d", hair: "#5a3c28", skin: RICK_HEAD, seed: 61 },
  survMan:   { jacket: "#4b5747", jacket2: "#333d30", trim: "#c8c2b2", pants: "#2c302d", hair: "#4a4642", stubble: true, skin: "#efe8dc", seed: 71 },
  survBoy:   { jacket: "#d9862b", jacket2: "#a86219", trim: "#f5ebd6", pants: "#2d3644", hair: "#473022", hoodie: true, skin: RICK_HEAD, seed: 79 },
  infectedA: { jacket: "#364045", jacket2: "#22292d", pants: "#1f2427", hair: "#181b1d", skin: INF_HEAD, infected: true, jawOpen: 0.90, seed: 83 },
  infectedB: { jacket: "#474037", jacket2: "#2e2923", pants: "#23201c", hair: "#211b18", skin: "#94a69d", infected: true, jawOpen: 0.78, seed: 89 },
  infectedC: { jacket: "#2f3744", jacket2: "#1d232c", pants: "#1a1e25", hair: "#15171b", skin: "#a8b8b0", infected: true, jawOpen: 0.96, seed: 97 },
};

function drawModernHairFront(p, R, H, cx, hc, u, ow, thick, light) {
  if (R.cap) {
    const capCol = R.cap, capDark = mul(capCol, [0.72, 0.72, 0.78]);
    const dome = ellPts(cx, hc - H.b * 0.28, H.a * 1.04, H.b * 0.78, 180, 360, 0, 36);
    p.shadedFill(dome, capCol, capDark, light, H.a, 0.35);
    p.inkRing(dome, ow * 0.9, thick);
    const brim = [
      [cx - H.a * 0.76, hc - H.b * 0.30],
      [cx + H.a * 1.18, hc - H.b * 0.23],
      [cx + H.a * 1.12, hc - H.b * 0.09],
      [cx - H.a * 0.70, hc - H.b * 0.16],
    ];
    p.poly(brim, "#141920", ow * 0.82);
    // Gold police shield emblem or cap patch
    const patchCol = R.badge ? "#f2c64b" : "#f5efe0";
    p.poly(rrect(cx - 13 * u, hc - H.b * 0.68, cx + 13 * u, hc - H.b * 0.44, 4 * u), patchCol, ow * 0.48);
    return;
  }
  const hCol = R.hair || "#3b2920", hDark = mul(hCol, [0.70, 0.68, 0.74]), hHi = mix(hCol, "#ffffff", 0.16);
  const topArc = ellPts(cx, hc - H.b * 0.06, H.a * 1.04, H.b * 1.01, 174, 366, 0, 36);
  const bangs = R.infected
    ? [
        [cx + H.a * 0.96, hc - H.b * 0.14],
        [cx + H.a * 0.60, hc - H.b * 0.44],
        [cx + H.a * 0.26, hc + H.b * 0.05],
        [cx - H.a * 0.16, hc - H.b * 0.45],
        [cx - H.a * 0.56, hc + H.b * 0.02],
        [cx - H.a * 0.98, hc - H.b * 0.22],
      ]
    : [
        [cx + H.a * 0.98, hc - H.b * 0.20],
        [cx + H.a * 0.48, hc - H.b * 0.35],
        [cx + H.a * 0.08, hc - H.b * 0.24],
        [cx - H.a * 0.36, hc - H.b * 0.36],
        [cx - H.a * 0.98, hc - H.b * 0.20],
      ];
  const hairPoly = [...topArc, ...bangs];
  p.shadedFill(hairPoly, hCol, hDark, light, H.a, 0.35);
  if (!R.infected) {
    p.clip(hairPoly, () => {
      p.stroke(ellPts(cx - 18 * u, hc - H.b * 0.56, H.a * 0.44, H.b * 0.20, 200, 325, 0, 18), 5 * u, hHi);
    });
  }
  p.inkRing(hairPoly, ow * 0.88, thick);
}

/** Upgraded Nightmare Horror Zombie Face: Necrotic Veins, Torn Scar, Sunken Sockets, Glowing Eyes & Bloody Fangs */
function drawHorrorInfectedFace(p, cx, hc, H, u, ow, facing, jawAnim = 0.85, seed = 83) {
  const fx = cx + facing * 15 * u;
  // Upper skull necrotic shadow wash
  p.ell(fx, hc - 8 * u, 42 * u, 24 * u, "rgba(28, 36, 32, 0.34)", 0);

  // Branching dark crimson-violet necrotic veins across temples, cheeks & jaw
  const veinCol = "rgba(64, 14, 28, 0.74)";
  const veinSub = "rgba(88, 18, 32, 0.52)";
  p.stroke([[fx - 38 * u, hc - 28 * u], [fx - 24 * u, hc - 10 * u], [fx - 31 * u, hc + 12 * u]], 2.5 * u, veinCol);
  p.stroke([[fx - 24 * u, hc - 10 * u], [fx - 12 * u, hc - 1 * u]], 1.7 * u, veinSub);
  p.stroke([[fx + 36 * u, hc - 24 * u], [fx + 22 * u, hc + 2 * u], [fx + 29 * u, hc + 24 * u]], 2.5 * u, veinCol);
  p.stroke([[fx + 22 * u, hc + 2 * u], [fx + 10 * u, hc + 12 * u]], 1.7 * u, veinSub);
  p.stroke([[fx - 18 * u, hc + 26 * u], [fx - 24 * u, hc + 42 * u]], 2.0 * u, veinCol);

  // Torn cheek gash on right side
  p.stroke([[fx + 18 * u, hc + 10 * u], [fx + 32 * u, hc + 18 * u]], 3.4 * u, "#4f0c14");

  // Deep bruised sunken eye sockets
  const exL = fx - 18.5 * u, exR = fx + 18.5 * u, ey = hc - 2 * u;
  p.ell(exL, ey, 15.8 * u, 13.5 * u, "rgba(24, 12, 20, 0.72)", 0);
  p.ell(exR, ey - 1.5 * u, 14.5 * u, 12.5 * u, "rgba(24, 12, 20, 0.72)", 0);

  // Bloodshot dark-crimson sclera + piercing glowing amber-white pinprick horror pupils!
  p.ell(exL, ey, 12.0 * u, 10.0 * u, "#320d14", ow * 0.58);
  p.ell(exR, ey - 1.5 * u, 10.6 * u, 9.0 * u, "#320d14", ow * 0.58);
  p.dot(exL + 1.5 * u, ey, 4.8 * u, "#ffd24c");
  p.dot(exL + 1.5 * u, ey, 2.2 * u, "#ffffff");
  p.dot(exR + 1.0 * u, ey - 1.5 * u, 4.2 * u, "#ffd24c");
  p.dot(exR + 1.0 * u, ey - 1.5 * u, 2.0 * u, "#ffffff");

  // Contorted snarling brows
  p.stroke([[exL - 13 * u, ey - 14 * u], [exL + 11 * u, ey - 6 * u]], 4.6 * u, "#180f12");
  p.stroke([[exR - 11 * u, ey - 6 * u], [exR + 13 * u, ey - 15 * u]], 4.6 * u, "#180f12");

  // Snapping gaping horror jaw with jagged stained teeth & dripping dark crimson blood!
  const mw = 23 * u, mh = (10 + 14 * jawAnim) * u, my = hc + 26 * u;
  p.ell(fx + 1 * u, my + mh * 0.72, mw * 0.92, mh * 0.62, "rgba(108, 12, 20, 0.65)", 0);
  // Blood drips down chin
  p.stroke([[fx - 6 * u, my + mh * 0.8], [fx - 7 * u, my + mh + 9 * u]], 3.2 * u, "#6e0b14");
  p.stroke([[fx + 8 * u, my + mh * 0.7], [fx + 9 * u, my + mh + 6 * u]], 2.6 * u, "#6e0b14");

  const mPoly = ellPts(fx, my, mw, mh, 0, 360, 0, 24);
  p.poly(mPoly, "#1f060a", ow * 0.66);
  p.clip(mPoly, () => {
    for (let k = -3; k <= 3; k++) {
      const tx = fx + k * 5.6 * u;
      p.poly([[tx - 2.6 * u, my - mh], [tx + 2.6 * u, my - mh], [tx, my - mh + 8.5 * u]], "#e3dac6", 0);
      p.poly([[tx - 2.4 * u, my + mh], [tx + 2.4 * u, my + mh], [tx, my + mh - 8.0 * u]], "#d1c5b0", 0);
    }
  });
}

/**
 * Custom High-Readability Rick-Clips Situation-Accurate Human Face Renderer!
 * Eliminates sleepy half-closed eyelids during tense/horror beats; every emotion reads unmistakably!
 */
function drawSituationHumanFace(p, roleKey, R, cx, hc, H, u, ow, expr, facing, blink, speakOpen) {
  const fx = cx + facing * 15 * u;
  const ey = hc - 1 * u;
  const exL = fx - 18.5 * u;
  const exR = fx + 18.5 * u;

  // Special Case: Woman's Spine-Chilling Uncanny Twist ("Her expression changes: 'Please, open the door'")
  if (expr === "woman_uncanny") {
    p.ell(fx, ey - 8 * u, 40 * u, 20 * u, "rgba(32, 26, 42, 0.24)", 0);
    // Creeping dark veins on cheeks
    p.stroke([[exL - 12 * u, ey + 10 * u], [exL - 4 * u, ey + 22 * u]], 1.8 * u, "rgba(72, 24, 44, 0.52)");
    p.stroke([[exR + 12 * u, ey + 8 * u], [exR + 5 * u, ey + 21 * u]], 1.8 * u, "rgba(72, 24, 44, 0.52)");
    // Unblinking asymmetric bloodshot pale eyes with pinprick black-amber dots!
    p.ell(exL, ey, 12.2 * u, 11.4 * u, "#f0dcd8", ow * 0.62);
    p.ell(exR, ey - 1.2 * u, 10.6 * u, 9.8 * u, "#f0dcd8", ow * 0.62);
    p.dot(exL + facing * 2 * u, ey, 3.6 * u, "#8f241e");
    p.dot(exL + facing * 2 * u, ey, 1.8 * u, "#12080a");
    p.dot(exR + facing * 2 * u, ey - 1.2 * u, 3.2 * u, "#8f241e");
    p.dot(exR + facing * 2 * u, ey - 1.2 * u, 1.6 * u, "#12080a");
    // Eerie flat/crooked brows
    p.stroke([[exL - 12 * u, ey - 14 * u], [exL + 11 * u, ey - 12 * u]], 3.8 * u, "#241726");
    p.stroke([[exR - 11 * u, ey - 13 * u], [exR + 12 * u, ey - 16 * u]], 3.8 * u, "#241726");
    // Uncanny crooked mouth (speaking "Please, open the door" with zero human warmth)
    const my = hc + 25 * u;
    if (speakOpen > 0.05) {
      p.ell(fx, my, (8 + 5 * speakOpen) * u, (4 + 7 * speakOpen) * u, "#280e14", ow * 0.58);
    } else {
      p.stroke([[fx - 13 * u, my + 2 * u], [fx, my + 4 * u], [fx + 14 * u, my - 4 * u]], 3.6 * u, "#241726");
    }
    return;
  }

  // Optional stubble on Older Survivor Man
  if (R.stubble) {
    p.ell(fx, hc + 24 * u, 32 * u, 18 * u, "rgba(68, 66, 62, 0.16)", 0);
  }

  // Map legacy expression names cleanly to V3 situation states
  const mode = ({
    neutral: "calm_work",
    alert: "startled_shock",
    panic: "extreme_panic",
    tense: "dread_reading",
    plead: "plead_terror",
    exhausted: "exhausted_hush",
     road_trance: "road_trance",
  })[expr] || expr;

  // KNOCKED OUT / dead: X-closed eyes, flat lifeless brows, slack open jaw.
  if (mode === "knocked_out") {
    const k = 9 * u;
    p.stroke([[exL - k, ey - k], [exL + k, ey + k]], 3.8 * u, "#241726");
    p.stroke([[exL - k, ey + k], [exL + k, ey - k]], 3.8 * u, "#241726");
    p.stroke([[exR - k, ey - k], [exR + k, ey + k]], 3.8 * u, "#241726");
    p.stroke([[exR - k, ey + k], [exR + k, ey - k]], 3.8 * u, "#241726");
    p.stroke([[exL - 12 * u, ey - 17 * u], [exL + 11 * u, ey - 15 * u]], 4.0 * u, "#241726");
    p.stroke([[exR - 11 * u, ey - 15 * u], [exR + 12 * u, ey - 17 * u]], 4.0 * u, "#241726");
    p.ell(fx, hc + 26 * u, 11 * u, 8 * u, "#2a0e14", ow * 0.55);
    return;
  }

  // Forehead dread shadow on intense terror states
  if (mode === "extreme_panic" || mode === "frozen_terror" || mode === "pale_horror") {
    p.ell(fx, hc - 18 * u, 42 * u, 16 * u, "rgba(30, 38, 56, 0.18)", 0);
  }

  // Dark under-eye exhaustion circles for underground survivors or frozen terror
  if (mode === "exhausted_hush" || mode === "pale_horror" || mode === "frozen_terror" || mode === "extreme_panic") {
    p.arc(exL, ey + 4 * u, 10 * u, 8 * u, 25, 155, 2.2 * u, "rgba(62, 46, 58, 0.42)");
    p.arc(exR, ey + 4 * u, 10 * u, 8 * u, 25, 155, 2.2 * u, "rgba(62, 46, 58, 0.42)");
  }

  // Eye geometry per emotional situation (NEVER sleepy during shock/panic!)
  const canBlink = !(mode === "extreme_panic" || mode === "frozen_terror" || mode === "startled_shock" || mode === "pale_horror" || mode === "road_trance");
  const isBlinking = canBlink && blink > 0.65;

  let eyeRx = 10.2 * u, eyeRy = 10.8 * u, pupR = 4.6 * u, lookX = facing * 3.2 * u, lookY = 0;
  if (mode === "extreme_panic" || mode === "frozen_terror" || mode === "pale_horror") {
    eyeRx = 12.6 * u; eyeRy = 13.8 * u; pupR = 3.1 * u; // Wide whites + tiny contracted panic pupils!
  } else if (mode === "startled_shock" || mode === "boy_hope") {
    eyeRx = 11.8 * u; eyeRy = 12.6 * u; pupR = 3.8 * u;
  } else if (mode === "dread_reading") {
    eyeRx = 10.6 * u; eyeRy = 10.4 * u; pupR = 4.2 * u; lookY = 2.8 * u; // Looking down at phone!
  } else if (mode === "straining_effort") {
    eyeRx = 10.8 * u; eyeRy = 8.8 * u; pupR = 4.2 * u; // Intense focused squint!
  } else if (mode === "plead_terror" || mode === "hesitant_conflict") {
    eyeRx = 11.6 * u; eyeRy = 12.2 * u; pupR = 4.8 * u;
  } else if (mode === "exhausted_hush") {
    eyeRx = 10.2 * u; eyeRy = 8.6 * u; pupR = 4.4 * u;
  } else if (mode === "road_trance") {
    eyeRx = 11.4 * u; eyeRy = 11.8 * u; pupR = 2.6 * u; lookY = -3.2 * u; // Staring blankly upward at nothing!
  }

  if (isBlinking) {
    p.stroke([[exL - 10 * u, ey], [exL + 10 * u, ey]], 3.8 * u, "#241726");
    p.stroke([[exR - 10 * u, ey], [exR + 10 * u, ey]], 3.8 * u, "#241726");
  } else {
    p.ell(exL, ey, eyeRx, eyeRy, "#ffffff", ow * 0.62);
    p.ell(exR, ey, eyeRx, eyeRy, "#ffffff", ow * 0.62);
    p.dot(exL + lookX, ey + lookY, pupR, "#18141c");
    p.dot(exR + lookX, ey + lookY, pupR, "#18141c");
    // Crisp eye catchlight for life & emotion!
    if (mode !== "road_trance") {
      p.dot(exL + lookX - 1.6 * u, ey + lookY - 1.8 * u, 1.5 * u, "#ffffff");
      p.dot(exR + lookX - 1.6 * u, ey + lookY - 1.8 * u, 1.5 * u, "#ffffff");
    }
    // Upper weary lid line ONLY for exhausted_hush
    if (mode === "exhausted_hush") {
      p.stroke([[exL - eyeRx, ey - eyeRy * 0.45], [exL + eyeRx, ey - eyeRy * 0.35]], 3.2 * u, "#241726");
      p.stroke([[exR - eyeRx, ey - eyeRy * 0.35], [exR + eyeRx, ey - eyeRy * 0.45]], 3.2 * u, "#241726");
    }
  }

  // Glistening tear droplets on pleading terror faces
  if (mode === "plead_terror") {
    p.dot(exL - 5 * u, ey + eyeRy + 2.5 * u, 3.3 * u, "#8fd8ff");
    p.dot(exR + 5 * u, ey + eyeRy + 2.5 * u, 3.3 * u, "#8fd8ff");
  }

  // Expressive Eyebrows per situation
  const bw = 4.2 * u;
  if (mode === "extreme_panic" || mode === "plead_terror" || mode === "hesitant_conflict" || mode === "pale_horror") {
    // Steep worried/terrified upturned inner brows (/  \)
    p.stroke([[exL - 12 * u, ey - eyeRy - 3 * u], [exL + 11 * u, ey - eyeRy - 11 * u]], bw, "#241726");
    p.stroke([[exR - 11 * u, ey - eyeRy - 11 * u], [exR + 12 * u, ey - eyeRy - 3 * u]], bw, "#241726");
  } else if (mode === "dread_reading" || mode === "straining_effort") {
    // Tense angled furrowed brows (\  /)
    p.stroke([[exL - 12 * u, ey - eyeRy - 9 * u], [exL + 11 * u, ey - eyeRy - 3 * u]], bw, "#241726");
    p.stroke([[exR - 11 * u, ey - eyeRy - 3 * u], [exR + 12 * u, ey - eyeRy - 9 * u]], bw, "#241726");
  } else if (mode === "startled_shock" || mode === "frozen_terror" || mode === "boy_hope") {
    // High raised shock arches
    p.stroke([[exL - 12 * u, ey - eyeRy - 8 * u], [exL, ey - eyeRy - 13 * u], [exL + 11 * u, ey - eyeRy - 8 * u]], bw, "#241726");
    p.stroke([[exR - 11 * u, ey - eyeRy - 8 * u], [exR, ey - eyeRy - 13 * u], [exR + 12 * u, ey - eyeRy - 8 * u]], bw, "#241726");
  } else {
    // Calm / neutral / trance brows
    p.stroke([[exL - 11 * u, ey - eyeRy - 6 * u], [exL + 10 * u, ey - eyeRy - 6 * u]], 3.8 * u, "#241726");
    p.stroke([[exR - 10 * u, ey - eyeRy - 6 * u], [exR + 11 * u, ey - eyeRy - 6 * u]], 3.8 * u, "#241726");
  }

  // Subtle nose bridge line
  p.stroke([[fx + facing * 3 * u, ey + 3 * u], [fx + facing * 5 * u, ey + 13 * u], [fx + facing * 1 * u, ey + 15 * u]], 2.6 * u, "rgba(36,23,38,0.65)");

  // Mouth per situation + active lip-sync override
  const my = hc + 25.5 * u;
  if (speakOpen > 0.05) {
    const mw = (7.0 + 6.5 * speakOpen) * u;
    const mh = (3.5 + 8.5 * speakOpen) * u;
    p.ell(fx, my, mw, mh, "#38151e", ow * 0.56);
    if (speakOpen > 0.22) {
      p.poly(rrect(fx - mw * 0.65, my - mh * 0.82, fx + mw * 0.65, my - mh * 0.30, 1.5 * u), "#f7f3ea", 0);
    }
  } else if (mode === "extreme_panic") {
    // Wide open trembling horror mouth with clenched upper & lower teeth!
    const mw = 14.5 * u, mh = 9.2 * u;
    const mp = ellPts(fx, my, mw, mh, 0, 360, 0, 20);
    p.poly(mp, "#331119", ow * 0.58);
    p.clip(mp, () => {
      p.poly(rrect(fx - mw, my - mh, fx + mw, my - mh + 4.2 * u, 1 * u), "#f7f3ea", 0);
      p.poly(rrect(fx - mw, my + mh - 3.6 * u, fx + mw, my + mh, 1 * u), "#ece5d8", 0);
    });
  } else if (mode === "startled_shock" || mode === "pale_horror") {
    p.ell(fx, my, 8.8 * u, 9.6 * u, "#331119", ow * 0.58);
  } else if (mode === "straining_effort") {
    // Gritted clenched teeth grimace
    const mp = rrect(fx - 13 * u, my - 5 * u, fx + 13 * u, my + 5 * u, 4 * u);
    p.poly(mp, "#f7f3ea", ow * 0.56);
    p.stroke([[fx - 11 * u, my], [fx + 11 * u, my]], 2.2 * u, "#241726");
  } else if (mode === "frozen_terror" || mode === "dread_reading" || mode === "plead_terror" || mode === "hesitant_conflict") {
    // Quivering downturn / tense horror frown
    p.stroke([[fx - 11 * u, my + 3.5 * u], [fx, my - 1.5 * u], [fx + 11 * u, my + 3.5 * u]], 3.6 * u, "#241726");
  } else if (mode === "boy_hope") {
    p.arc(fx, my - 2 * u, 9 * u, 5 * u, 20, 160, 3.4 * u, "#241726");
  } else {
    // Calm neutral slight line
    p.stroke([[fx - 9 * u, my + 1 * u], [fx + 9 * u, my + 1 * u]], 3.4 * u, "#241726");
  }
}

/** Ground-Clamped Fallen Pose */
function drawFallenChar(p, R, opts, u, ow, thick, light) {
  const skin = R.skin || RICK_HEAD;
  const sole = 964;
  const cx = 300;
  p.band([[cx - 175, sole - 22], [cx - 95, sole - 34], [cx - 20, sole - 26]], R.pants || "#2f3640", 26, ow * 0.72, "round");
  p.band([[cx - 155, sole - 8], [cx - 78, sole - 16], [cx - 10, sole - 18]], R.pants || "#2f3640", 26, ow * 0.72, "round");
  p.ell(cx - 185, sole - 18, 18, 11, "#2a2226", ow * 0.68);
  p.ell(cx - 166, sole - 5, 18, 11, "#2a2226", ow * 0.68);
  const tPoly = rrect(cx - 32, sole - 76, cx + 112, sole - 12, 28);
  p.gradFill(tPoly, R.jacket, R.jacket2, light, 0.28);
  p.inkRing(tPoly, ow * 0.95, thick);
  p.band([[cx + 88, sole - 42], [cx + 152, sole - 24], [cx + 205, sole - 14]], R.jacket, 22, ow * 0.68, "round");
  p.ell(cx + 214, sole - 13, 13, 9, skin, ow * 0.62);
  const H = headBlob(R.seed, 98, 0.25);
  const hx = cx + 148, hy = sole - 68;
  const hp = blobPts(hx, hy, H);
  p.shadedFill(hp, skin, "#d8d0c4", light, H.a, 0.42);
  p.inkRing(hp, ow * 0.95, thick);
  drawSituationHumanFace(p, "carMan", R, hx, hy + 4, H, (2 * H.a) / 100, ow * 0.9, "extreme_panic", 0.25, 0, 0);
  drawModernHairFront(p, R, H, hx, hy, (2 * H.a) / 100, ow * 0.9, thick, light);
}

export function rickChar(p, roleKey = "you", opts = {}) {
  const R = ROLES[roleKey] || ROLES.you;
  const {
    expr = R.infected ? "infected" : "calm_work",
    blink = 0,
    facing = 0,
    L = "hang",
    R: Rarm = "hang",
    tilt = 0,
    headTilt = 0,
    bob = 0,
    step = 0,            // 0..1 continuous velocity-locked gait phase
    isRunning = false,   // true -> full athletic sprint stride, 82° knee recovery, 20° forward lean, pumping arms!
    reverseWalk = false, // true -> cautious backward step while facing threat (Police Officer / YOU stepping back)
    crouchSit = false,   // true -> seated/crouched bent knees at y=0
    hasBackpack = false, // true -> survival backpack straps on YOU (Act IV & V)
    fallU = 0,
    breath = 0,
    sweat = false,
    speakOpen = 0,
    phoneBuzz = 0,
    shakeAmt = 0,
    jawAnim = R.infected ? 0.85 : 0,
    light = rad(-125),
  } = opts;

  const seed = opts.seed ?? R.seed;
  const H = headBlob(seed, 120, facing);
  const W = 2 * H.a, HH = 2 * H.b, u = W / 100;
  const thick = thickAngle(light);
  const ow = 4.5 * u;

  if (fallU >= 0.55) {
    drawFallenChar(p, R, opts, u, ow, thick, light);
    return;
  }

  // Dynamic skin pallor when Older Man goes pale or Woman turns uncanny!
  const skin = (expr === "pale_horror" || expr === "woman_uncanny")
    ? PALE_HEAD
    : (R.skin || RICK_HEAD);

  const sole = 968;
  const moveDir = facing < -0.05 ? -1 : 1;
  const gaitSign = reverseWalk ? -1 : 1;

  // Athletic vertical sprint bounce (peaks twice per full stride during flight phase!)
  const hasGait = step > 0.0001;
  const runBounce = (hasGait && isRunning)
    ? Math.abs(Math.sin(Math.PI * 2 * step)) * 0.105
    : (hasGait ? Math.abs(Math.sin(Math.PI * 2 * step)) * 0.038 : 0);

  const sitDrop  = crouchSit ? 0.42 : 0;
  const tripDrop = fallU > 0 ? fallU * 0.65 : 0;
  const legsL = 1.24 - sitDrop - tripDrop;
  const torsoL = 1.03;
  const breathLift = breath * 0.022;

  const torsoBot = sole - legsL * HH - (bob + runBounce) * HH;
  const hipY = torsoBot - 0.06 * HH;
  const chin = torsoBot - (torsoL + breathLift) * HH;
  const hc = chin - H.b * 0.90;

  // Pelvis shifts slightly forward during sprint so center-of-gravity leads the push-off foot!
  const cx = 300 + (isRunning ? moveDir * 14 * u : 0);
  const pantsCol = R.pants || "#2b3340";
  const pantsFar = mul(pantsCol, [0.78, 0.78, 0.84]);

  // Natural forward torso lean during sprint (19° human sprint, 25° zombie lunge!)
  const autoLean = (fallU > 0 ? fallU * 48 : 0)
    + (isRunning ? (R.infected ? 25 : 19) * moveDir : 0)
    + (R.infected && !isRunning ? 11 * moveDir : 0)
    + (reverseWalk ? -6 * moveDir : 0)
    + tilt;

  p.rot = null;

  // Subtle cartoon sprint speed lines behind fast human sprinters!
  if (isRunning && !R.infected && Math.abs(facing) > 0.25) {
    const backX = cx - moveDir * 115 * u;
    p.stroke([[backX, hipY - 45 * u], [backX - moveDir * 52 * u, hipY - 45 * u]], 3.0 * u, "rgba(255,255,255,0.34)");
    p.stroke([[backX + moveDir * 12 * u, hipY + 25 * u], [backX - moveDir * 44 * u, hipY + 25 * u]], 2.6 * u, "rgba(255,255,255,0.28)");
  }

  // Long hair back layer (for Woman)
  if (R.longHair) {
    const hCol = R.hair || "#2b1b20";
    const backHair = rrect(cx - H.a * 1.04, hc - H.b * 0.16, cx + H.a * 1.04, chin + 0.30 * HH, 24 * u);
    p.shadedFill(backHair, mul(hCol, [0.82, 0.80, 0.85]), mul(hCol, [0.58, 0.56, 0.62]), light, H.a);
    p.inkRing(backHair, ow * 0.82, thick);
  }

  // ---- TRUE 2-BONE ANATOMICAL LEG SOLVER (Far leg draws BEHIND torso; Near leg draws IN FRONT!) ----
  const isProfile = Math.abs(facing) > 0.22;
  const computeLeg = (side) => {
    const isNear = isProfile ? (side * moveDir > 0) : (side > 0);
    const hipX = cx + (isProfile ? side * 6 * u : side * 15 * u);
    const col = isNear ? pantsCol : pantsFar;

    if (crouchSit) {
      const kneeX = hipX + (isProfile ? moveDir * 36 * u : side * 24 * u);
      const kneeY = hipY + (sole - hipY) * 0.48;
      const fx = hipX + (isProfile ? moveDir * 24 * u : side * 18 * u);
      const fy = sole - 7 * u;
      return { hipX, kneeX, kneeY, fx, fy, shoeAng: 0, col, isNear };
    }

    if (hasGait) {
      // Phase u_ang in [0..2π); side > 0 is 180° out of phase with side < 0
      const ph = ((step * gaitSign + (side > 0 ? 0.5 : 0.0)) % 1 + 1) % 1;
      const ang = ph * Math.PI * 2;
      const s = Math.sin(ang);
      const c = Math.cos(ang);

      const L1 = 0.53 * (sole - hipY); // Thigh bone length
      const L2 = 0.52 * (sole - hipY); // Shin bone length

      if (isRunning) {
        // FULL ATHLETIC SPRINT BIOMECHANICS:
        // Thigh swings wide from -37° (rear push-off) to +51° (high forward knee drive)!
        const thighAng = (0.12 + 0.77 * s) * moveDir;
        // Knee folds anatomically BACKWARD (-moveDir) up to 84° during forward recovery (c > 0),
        // and straightens cleanly on rear push-off & front foot strike!
        const recovery = Math.max(0, Math.cos(ang - 0.32));
        const kneeFold = (0.12 + 1.32 * Math.pow(recovery, 1.45)) * moveDir;
        const shinAng  = thighAng - kneeFold;

        const kneeX = hipX + Math.sin(thighAng) * L1;
        const kneeY = hipY + Math.cos(thighAng) * L1;
        let fx = kneeX + Math.sin(shinAng) * L2;
        let fy = Math.min(sole - 6 * u, kneeY + Math.cos(shinAng) * L2);
        // Natural plantarflexion on rear push-off & dorsiflexion on front strike!
        const shoeAng = (-0.34 * s + 0.25 * recovery) * moveDir;
        return { hipX, kneeX, kneeY, fx, fy, shoeAng, col, isNear };
      } else {
        // NATURAL GROUNDED WALK / BACKING-AWAY BIOMECHANICS:
        const thighAng = (0.04 + 0.44 * s) * moveDir;
        const recovery = Math.max(0, Math.cos(ang - 0.25));
        const kneeFold = (0.06 + 0.68 * Math.pow(recovery, 1.5)) * moveDir;
        const shinAng  = thighAng - kneeFold;

        const kneeX = hipX + Math.sin(thighAng) * L1 * 0.96;
        const kneeY = hipY + Math.cos(thighAng) * L1 * 0.96;
        let fx = kneeX + Math.sin(shinAng) * L2 * 0.96;
        let fy = Math.min(sole - 6 * u, kneeY + Math.cos(shinAng) * L2 * 0.96);
        const shoeAng = (-0.18 * s) * moveDir;
        return { hipX, kneeX, kneeY, fx, fy, shoeAng, col, isNear };
      }
    }

    // Standing idle / zombie wide stance
    const fx = hipX + side * (R.infected ? 10 : 4) * u;
    const fy = sole - 6 * u;
    const kneeX = (hipX + fx) * 0.5 + (R.infected ? moveDir * 9 * u : 0);
    const kneeY = (hipY + fy) * 0.5;
    return { hipX, kneeX, kneeY, fx, fy, shoeAng: 0, col, isNear };
  };

  const drawOneLeg = (lg) => {
    p.band([[lg.hipX, hipY], [lg.kneeX, lg.kneeY], [lg.fx, lg.fy]], lg.col, 14.2 * u, ow * 0.60, "round");
    const shX = lg.fx + moveDir * 7.5 * u;
    const shY = lg.fy + 2 * u;
    p.rot = lg.shoeAng ? [lg.shoeAng, lg.fx, lg.fy] : null;
    p.ell(shX, shY, 15.2 * u, 7.6 * u, "#231c20", ow * 0.72);
    // Crisp sneaker/boot sole accent so foot movement reads with razor clarity!
    p.stroke([[shX - 11 * u, shY + 4.5 * u], [shX + 11 * u, shY + 4.5 * u]], 2.4 * u, "#d8d3c8");
    p.rot = null;
  };

  const legs = [computeLeg(-1), computeLeg(1)];
  // Draw FAR leg behind torso first!
  for (const lg of legs) if (!lg.isNear) drawOneLeg(lg);

  // ---- Breathing Pill/Bean Torso + Survival Backpack ----
  const jx = shakeAmt ? Math.sin(seed * 13 + shakeAmt * 38) * 3.5 * u : 0;
  p.rot = autoLean ? [rad(autoLean), cx, hipY] : null;

  const breathW = 1.0 + breath * 0.036;
  const T = {
    a: 0.40 * W * breathW,
    b: 0.53 * (torsoBot - (chin - 0.15 * HH)),
    nTop: 2.35,
    nBot: 2.35,
    egg: 0.08,
    asym: 0.03 * facing,
    rot: 0,
    noise: 0.005,
    seed: seed + 7,
  };
  const tcx = cx + 3.5 * u * facing + jx;
  const tcy = torsoBot - T.b + 0.05 * HH;
  const tp = blobPts(tcx, tcy, T);

  // Survival Backpack behind back when `hasBackpack` is active (Act IV & V)
  if (hasBackpack) {
    const bpSide = facing >= 0 ? -1 : 1;
    const bpPoly = rrect(tcx + bpSide * T.a * 0.45 - 18 * u, tcy - T.b * 0.65, tcx + bpSide * T.a * 0.45 + 18 * u, tcy + T.b * 0.58, 12 * u);
    p.poly(bpPoly, "#2d3530", ow * 0.72);
  }

  const shY = chin + (0.16 - breath * 0.025) * HH;
  const shoulder = (side) => [
    tcx + (isProfile ? side * 0.32 * T.a : side * 0.80 * T.a),
    shY
  ];

  // ---- Articulated Sleeved Arms & Connected Hands ----
  const makeArm = (side, pose) => {
    const s = shoulder(side);
    const X = (k) => tcx + side * (T.a * 0.88 + k * u);
    const isNearArm = isProfile ? (side * moveDir > 0) : (side > 0);

    // Full biomechanical opposite-phase arm pumping when walking or sprinting!
    if ((pose === "hang" || pose === "run") && hasGait) {
      const ph = ((step * gaitSign + (side > 0 ? 0.0 : 0.5)) % 1 + 1) % 1;
      const sw = Math.sin(ph * Math.PI * 2); // opposes same-side leg!
      if (isRunning) {
        // 90°-bent athletic sprint arms pumping vigorously from hip to chin!
        const shAng = (0.15 + 0.92 * sw) * moveDir;
        const L_up = 0.34 * HH, L_fore = 0.32 * HH;
        const elbX = s[0] + Math.sin(shAng) * L_up;
        const elbY = s[1] + Math.cos(shAng) * L_up;
        // Forearm bent ~85° FORWARD (+moveDir) relative to upper arm!
        const foreAng = shAng + 1.38 * moveDir;
        const hndX = elbX + Math.sin(foreAng) * L_fore;
        const hndY = elbY + Math.cos(foreAng) * L_fore;
        return { pts: [s, [elbX, elbY], [hndX, hndY]], front: isNearArm, fist: true, farDim: !isNearArm };
      } else {
        const elbX = s[0] + sw * 16 * u * moveDir + side * 4 * u;
        const elbY = s[1] + 0.35 * HH;
        const hndX = elbX + (sw * 22 + 5) * u * moveDir;
        const hndY = elbY + 0.30 * HH - Math.abs(sw) * 4 * u;
        return { pts: [s, [elbX, elbY], [hndX, hndY]], front: isNearArm, fist: true, farDim: !isNearArm };
      }
    }

    switch (pose) {
      case "phoneBuzz": {
        const vb = Math.sin(phoneBuzz * 52) * 3.5 * u;
        return { pts: [s, [X(18), s[1] + 0.24 * HH], [tcx + side * 0.44 * T.a + vb, s[1] + 0.06 * HH]], front: true, overHead: true, prop: "phoneBuzz" };
      }
      case "flashlight":
        return { pts: [s, [X(18), s[1] + 0.16 * HH], [tcx + moveDir * 48 * u, s[1] + 0.02 * HH]], front: true, prop: "flashlight" };
      case "pullShutter":
        // Reaching high overhead to yank down the heavy metal shutter handle!
        return { pts: [s, [X(16), s[1] - 0.22 * HH], [tcx + side * 18 * u, s[1] - 0.56 * HH]], front: true, overHead: true, fist: true };
      case "lockDoor":
        return { pts: [s, [X(18), s[1] + 0.12 * HH], [tcx + moveDir * 44 * u, s[1] + 0.04 * HH]], front: true, fist: true };
      case "plead":
        return { pts: [s, [X(22), s[1] + 0.04 * HH], [X(26), s[1] - 0.34 * HH]], front: true, overHead: true, palmSpread: true };
      case "slam":
        return { pts: [s, [X(22), s[1] - 0.04 * HH], [X(28), s[1] - 0.38 * HH]], front: true, overHead: true, palmSpread: true };
      case "shush": {
        // Older Man raising 1 index finger directly to his lips ("Don't make a sound")!
        const fxLip = cx + facing * 15 * u;
        return { pts: [s, [X(16), s[1] + 0.18 * HH], [fxLip + 4 * u, hc + 34 * u]], front: true, overHead: true, shushFinger: true };
      }
      case "grabSleeve":
        // Young Boy reaching across in panic to grab YOU's jacket sleeve!
        return { pts: [s, [s[0] + moveDir * 24 * u, s[1] + 0.08 * HH], [s[0] + moveDir * 56 * u, s[1] - 0.02 * HH]], front: true, overHead: true, fist: true };
      case "shake": {
        const sh = Math.sin(shakeAmt * 48 + side * 2) * 4 * u;
        return { pts: [s, [X(14), s[1] + 0.28 * HH], [tcx + side * 0.34 * T.a + sh, s[1] + 0.12 * HH]], front: true, fist: true };
      }
      case "zombieReach": {
        const tw = Math.sin(seed * 5 + step * Math.PI * 4 + side) * 7 * u;
        const reachF = isRunning ? 58 : 46;
        return {
          pts: [
            s,
            [s[0] + moveDir * 26 * u + side * 6 * u, s[1] + 0.02 * HH],
            [s[0] + moveDir * reachF * u + side * 8 * u, s[1] - 0.12 * HH + tw]
          ],
          front: isNearArm,
          claw: true,
          farDim: !isNearArm,
        };
      }
      default:
        return { pts: [s, [X(8), s[1] + 0.38 * HH], [X(6), s[1] + 0.72 * HH]], front: false, fist: true };
    }
  };

  const arms = [makeArm(-1, L), makeArm(1, Rarm)];

  const drawOneArm = (a) => {
    const slvCol = a.farDim ? R.jacket2 : R.jacket;
    p.band(a.pts, slvCol, 13.0 * u, ow * 0.58, "round");
    const [hx, hy] = a.pts[2];

    if (a.palmSpread) {
      p.ell(hx, hy, 8.8 * u, 9.8 * u, skin, ow * 0.62);
      for (let f = -2; f <= 2; f++) {
        const ang = rad(f * 18 - 90);
        p.band([[hx + Math.cos(ang) * 5 * u, hy + Math.sin(ang) * 5 * u],
                [hx + Math.cos(ang) * 13 * u, hy + Math.sin(ang) * 14 * u]], skin, 3.8 * u, ow * 0.35, "round");
      }
    } else if (a.shushFinger) {
      p.ell(hx, hy, 7.2 * u, 6.8 * u, skin, ow * 0.58);
      p.band([[hx, hy - 3 * u], [hx, hy - 19 * u]], skin, 4.2 * u, ow * 0.42, "round");
    } else if (a.claw) {
      p.ell(hx, hy, 7.8 * u, 7.0 * u, skin, ow * 0.58);
      for (const f of [-1.5, -0.5, 0.5, 1.5]) {
        p.stroke([[hx + f * 3.2 * u, hy], [hx + (f * 4.5 + moveDir * 8) * u, hy + 5 * u], [hx + (f * 5 + moveDir * 12) * u, hy + 12 * u]], 2.8 * u, "#240d12");
      }
    } else {
      p.ell(hx, hy, 7.4 * u, 7.0 * u, skin, ow * 0.58);
    }

    if (a.prop === "phoneBuzz") {
      p.poly(rrect(hx - 11 * u, hy - 26 * u, hx + 11 * u, hy + 6 * u, 4 * u), "#1a1d24", ow * 0.68);
      p.poly(rrect(hx - 8.5 * u, hy - 22 * u, hx + 8.5 * u, hy + 2 * u, 2 * u), "#ff3328", 0);
      p.poly(rrect(hx - 6.5 * u, hy - 18 * u, hx + 6.5 * u, hy - 12 * u, 1 * u), "#ffffff", 0);
      p.ell(hx - 9.5 * u, hy - 5 * u, 4.2 * u, 3.2 * u, skin, ow * 0.45);
      if (phoneBuzz > 0) {
        const pulse = (phoneBuzz * 6) % 1;
        for (const sgn of [-1, 1]) {
          const rx = hx + sgn * (15 + pulse * 7) * u;
          p.stroke([[rx, hy - 20 * u], [rx + sgn * 3 * u, hy - 10 * u], [rx, hy]], 2.6 * u, "#ff6247");
          const rx2 = hx + sgn * (21 + pulse * 9) * u;
          p.stroke([[rx2, hy - 17 * u], [rx2 + sgn * 3 * u, hy - 10 * u], [rx2, hy - 3 * u]], 2.0 * u, "#ffcf48");
        }
      }
    } else if (a.prop === "flashlight") {
      p.poly(rrect(hx - 6 * u, hy - 6.5 * u, hx + 20 * u, hy + 6.5 * u, 3 * u), "#323840", ow * 0.62);
      p.poly(rrect(hx + 16 * u, hy - 8.5 * u, hx + 24 * u, hy + 8.5 * u, 2 * u), "#ffd452", ow * 0.52);
    }
  };

  // Draw FAR arm behind torso!
  for (let i = 0; i < 2; i++) if (!arms[i].front) drawOneArm(arms[i]);

  // Torso fill + clothing details
  p.gradFill(tp, R.jacket, R.jacket2, light, 0.26);
  p.clip(tp, () => {
    if (R.badge) {
      // Police Officer uniform details: center placket + gold shield badge + utility belt!
      p.stroke([[tcx, tcy - T.b * 0.85], [tcx, tcy + T.b * 0.85]], 2.8 * u, R.jacket2);
      p.poly([
        [tcx + 14 * u, tcy - T.b * 0.42],
        [tcx + 23 * u, tcy - T.b * 0.36],
        [tcx + 20 * u, tcy - T.b * 0.16],
        [tcx + 14 * u, tcy - T.b * 0.10],
        [tcx + 8 * u,  tcy - T.b * 0.16],
        [tcx + 5 * u,  tcy - T.b * 0.36],
      ], R.badge, ow * 0.38);
      p.poly(rrect(tcx - T.a, tcy + T.b * 0.62, tcx + T.a, tcy + T.b * 0.86, 2 * u), R.belt, 0);
    } else if (R.hoodie) {
      p.stroke([[tcx, tcy - T.b * 0.82], [tcx, tcy + T.b * 0.88]], 2.8 * u, R.jacket2);
      p.poly(rrect(tcx - T.a * 0.58, tcy + T.b * 0.18, tcx + T.a * 0.58, tcy + T.b * 0.68, 6 * u), R.jacket2, ow * 0.45);
      p.stroke([[tcx - 9 * u, tcy - T.b * 0.72], [tcx - 10 * u, tcy - T.b * 0.28]], 2.4 * u, R.trim);
      p.stroke([[tcx + 9 * u, tcy - T.b * 0.72], [tcx + 10 * u, tcy - T.b * 0.28]], 2.4 * u, R.trim);
    } else if (R.trim) {
      p.poly([[tcx - 15 * u, tcy - T.b * 0.88], [tcx, tcy - T.b * 0.42], [tcx + 15 * u, tcy - T.b * 0.88]], R.trim, ow * 0.5);
    }
    if (hasBackpack) {
      p.stroke([[tcx - T.a * 0.46, tcy - T.b * 0.80], [tcx - T.a * 0.52, tcy + T.b * 0.55]], 5.5 * u, "#232926");
      p.stroke([[tcx + T.a * 0.46, tcy - T.b * 0.80], [tcx + T.a * 0.52, tcy + T.b * 0.55]], 5.5 * u, "#232926");
    }
    if (R.infected) {
      // Heavy crimson blood splatters & ragged tears on horror zombie clothing!
      p.ell(tcx - 6 * u, tcy - T.b * 0.52, 26 * u, 20 * u, "rgba(104, 10, 18, 0.68)", 0);
      p.ell(tcx + 12 * u, tcy + 8 * u, 18 * u, 26 * u, "rgba(86, 12, 18, 0.52)", 0);
      p.stroke([[tcx - 26 * u, tcy + 2 * u], [tcx + 14 * u, tcy + 28 * u]], 4.8 * u, "#170e10");
      p.stroke([[tcx - 14 * u, tcy - 18 * u], [tcx + 20 * u, tcy - 4 * u]], 3.8 * u, "#170e10");
    }
  });
  p.inkRing(tp, ow, thick);

  if (R.hoodie) {
    const hoodCollar = ellPts(tcx, chin + 0.06 * HH, T.a * 0.64, 12 * u, 0, 180, 0, 20);
    p.poly(hoodCollar, R.jacket2, ow * 0.70);
  }

  p.rot = null;
  // Draw NEAR leg in front of hip seam for crisp side-run depth!
  for (const lg of legs) if (lg.isNear) drawOneLeg(lg);

  p.rot = autoLean ? [rad(autoLean), cx, hipY] : null;
  // Draw NEAR arm in front of torso!
  for (let i = 0; i < 2; i++) if (arms[i].front && !arms[i].overHead) drawOneArm(arms[i]);

  // ---- Head ----
  const infTwitch = R.infected ? (20 + Math.sin(step * Math.PI * 6 + seed) * 9) : 0;
  const totHeadRot = rad(autoLean * 0.45 + headTilt + infTwitch);
  p.rot = totHeadRot ? [totHeadRot, cx + jx, chin] : null;
  const hp = blobPts(cx + jx, hc, H);
  const skinShadow = R.infected ? "#72827b" : (skin === PALE_HEAD ? "#bfc8c5" : "#d9d1c4");
  p.shadedFill(hp, skin, skinShadow, light, H.a, 0.42);
  p.inkRing(hp, ow * 1.04, thick);

  if (R.infected) {
    drawHorrorInfectedFace(p, cx + jx, hc + 4 * u, H, u, ow, facing, jawAnim, seed);
  } else {
    drawSituationHumanFace(p, roleKey, R, cx + jx, hc + 4 * u, H, u, ow, expr, facing, blink, speakOpen);
  }

  const showSweat = sweat || expr === "extreme_panic" || expr === "frozen_terror" || expr === "pale_horror";
  if (showSweat && !R.infected) {
    const sx = cx + jx + H.a * 0.66, sy = hc - H.b * 0.04;
    p.poly([[sx, sy - 11 * u], [sx + 6 * u, sy + 3 * u], [sx, sy + 8 * u], [sx - 6 * u, sy + 3 * u]], "#8ad4ff", ow * 0.45);
  }

  drawModernHairFront(p, R, H, cx + jx, hc, u, ow, thick, light);
  p.rot = null;

  // Draw foreground raised hands/props (phoneBuzz, Woman's palm, Shutter pull, Man's shush finger, Boy's sleeve grab) IN FRONT of head!
  for (let i = 0; i < 2; i++) if (arms[i].overHead) drawOneArm(arms[i]);
}

/** Authentic Rick-Clips Over-the-Shoulder / Running Away Back Card */
export function rickBackPOV(p, roleKey = "you", opts = {}) {
  const R = ROLES[roleKey] || ROLES.you;
  const { headTilt = 0, bob = 0, step = 0, isRunning = false, breath = 0, fullBody = false, hasBackpack = false, light = rad(-125) } = opts;

  if (fullBody) {
    const H = headBlob(R.seed, 120, 0);
    const W = 2 * H.a, HH = 2 * H.b, u = W / 100;
    const ow = 4.5 * u, thick = thickAngle(light);
    const sole = 968, cx = 300;
    const bounce = step > 0 ? Math.abs(Math.sin(Math.PI * 2 * step)) * (isRunning ? 0.095 : 0.035) : 0;
    const torsoBot = sole - 1.24 * HH - (bob + bounce) * HH;
    const chin = torsoBot - (1.03 + breath * 0.02) * HH;
    const hc = chin - H.b * 0.90;
    const hipY = torsoBot - 0.06 * HH;

    for (const side of [-1, 1]) {
      const ph = step > 0 ? Math.sin(Math.PI * 2 * (step + (side > 0 ? 0.5 : 0))) : 0;
      const lift = Math.max(0, ph) * (isRunning ? 68 : 28) * u;
      const hx = cx + side * 16 * u;
      const fy = sole - 6 * u - lift;
      p.band([[hx, hipY], [hx + side * 4 * u, (hipY + fy) * 0.5], [hx, fy]], R.pants || "#2b3340", 14.2 * u, ow * 0.58, "round");
      p.ell(hx, fy + 2 * u, 12 * u, 8.5 * u, "#231c20", ow * 0.70);
      if (lift > 16 * u) {
        // Shoe sole visible when heel kicks up while running away!
        p.ell(hx, fy + 1 * u, 9.5 * u, 12 * u, "#3b3538", ow * 0.55);
      }
    }
    for (const side of [-1, 1]) {
      const ph = step > 0 ? Math.sin(Math.PI * 2 * (step + (side > 0 ? 0 : 0.5))) : 0;
      const sx = cx + side * 0.36 * W, sy = chin + 0.16 * HH;
      const ex = sx + side * 18 * u, ey = sy + (0.32 - ph * 0.12) * HH;
      const hx = ex + side * 4 * u, hy = ey + (isRunning ? -0.12 : 0.28) * HH;
      p.band([[sx, sy], [ex, ey], [hx, hy]], R.jacket, 12.8 * u, ow * 0.58, "round");
      p.ell(hx, hy, 7 * u, 7 * u, R.skin, ow * 0.55);
    }
    const tp = rrect(cx - 0.40 * W, chin + 0.05 * HH, cx + 0.40 * W, torsoBot, 38 * u);
    p.gradFill(tp, R.jacket, R.jacket2, light, 0.25);
    p.inkRing(tp, ow, thick);
    if (hasBackpack) {
      const bp = rrect(cx - 0.27 * W, chin + 0.22 * HH, cx + 0.27 * W, torsoBot - 16 * u, 18 * u);
      p.poly(bp, "#2d3530", ow * 0.75);
    } else if (R.hoodie) {
      p.poly(ellPts(cx, chin + 0.22 * HH, 0.28 * W, 22 * u, 0, 180, 0, 20), R.jacket2, ow * 0.75);
    }
    const hp = blobPts(cx, hc, H);
    p.shadedFill(hp, R.hair || "#3a271d", mul(R.hair || "#3a271d", [0.7, 0.68, 0.74]), light, H.a, 0.35);
    p.inkRing(hp, ow, thick);
    return;
  }

  const H = headBlob(R.seed, 146, 0);
  const W = 2 * H.a, u = W / 100;
  const cx = 300, hc = 545 - (bob + breath * 0.08) * 38;
  const ow = 5.0 * u, thick = thickAngle(light);

  const shPts = rrect(cx - 195 * (1 + breath * 0.02), hc + H.b * 0.78, cx + 195 * (1 + breath * 0.02), 995, 68);
  p.gradFill(shPts, R.jacket, R.jacket2, light, 0.25);
  p.inkRing(shPts, ow, thick);
  const hoodPts = ellPts(cx, hc + H.b * 0.92, 118, 48, 0, 180, 0, 24);
  p.poly(hoodPts, R.jacket2, ow * 0.85);

  p.rot = headTilt ? [rad(headTilt), cx, hc + H.b] : null;
  const hp = blobPts(cx, hc, H);
  p.shadedFill(hp, R.skin, "#d8d1c5", light, H.a, 0.4);
  const hairBack = ellPts(cx, hc - H.b * 0.06, H.a * 1.02, H.b * 0.96, 155, 385, 0, 40);
  hairBack.push([cx + H.a * 0.92, hc + H.b * 0.42], [cx, hc + H.b * 0.52], [cx - H.a * 0.92, hc + H.b * 0.42]);
  const hCol = R.hair || "#3a271d";
  p.shadedFill(hairBack, hCol, mul(hCol, [0.7, 0.68, 0.74]), light, H.a, 0.35);
  p.inkRing(hp, ow * 1.05, thick);
  p.inkRing(hairBack, ow * 0.9, thick);
  p.rot = null;
}

/** Seamless Horror Zombie Arm + Veins + Claws */
export function creepyArmCard(p, opts = {}) {
  const { openClose = 0.5, reach = 0.78, twitch = 0 } = opts;
  const skin = "#aeb9b3", sh = "#83918b", sleeve = "#2c3338";
  const ow = 9.5;
  const yMid = 505 + Math.sin(twitch * 17) * 12;
  const elbowX = 175 + reach * 88;
  const wristX = 335 + reach * 125;
  const wristY = yMid + Math.cos(twitch * 12) * 16;

  p.poly([[0, yMid - 64], [148, yMid - 46], [134, yMid - 8], [154, yMid + 22], [138, yMid + 50], [0, yMid + 64]], sleeve, ow * 0.85);
  p.band([[125, yMid + 2], [elbowX, yMid - 12], [wristX, wristY]], skin, 44, ow * 0.52, "round");
  p.stroke([[155, yMid - 6], [elbowX + 18, yMid - 16], [wristX - 24, wristY - 4]], 4.2, "rgba(74, 18, 28, 0.62)");
  p.stroke([[elbowX, yMid + 4], [wristX - 10, wristY + 10]], 3.2, "rgba(92, 16, 22, 0.55)");
  p.ell(wristX + 24, wristY, 34, 28, skin, ow * 0.80);

  const spread = 0.32 + 0.68 * openClose;
  const curl = 1.05 - 0.58 * openClose;
  const angles = [-58, -27, 0, 27, 55];
  angles.forEach((deg, idx) => {
    const a1 = rad(deg * spread);
    const a2 = a1 + rad((idx === 0 ? -30 : 38) * curl);
    const len1 = idx === 0 ? 36 : 46;
    const len2 = idx === 0 ? 28 : 38;
    const bx = wristX + 36 + Math.cos(a1) * 14;
    const by = wristY + Math.sin(a1) * 18;
    const kx = bx + Math.cos(a1) * len1;
    const ky = by + Math.sin(a1) * len1;
    const tx = kx + Math.cos(a2) * len2;
    const ty = ky + Math.sin(a2) * len2;
    p.band([[bx, by], [kx, ky], [tx, ty]], sh, 12.5, ow * 0.38, "round");
    p.poly([
      [tx, ty - 4],
      [tx + Math.cos(a2) * 13, ty + Math.sin(a2) * 13],
      [tx - 3, ty + 4],
    ], "#1e1216", 2);
  });
}
