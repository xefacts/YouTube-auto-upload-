#!/usr/bin/env bash
# Checks (and where possible installs) what the pipeline needs: node 18+ (22+ preferred), ffmpeg, python3 + numpy,
# and a Chrome/Chromium binary for headless WebGL rendering. Safe to run repeatedly.
set -u
ok() { printf '  \033[32m✓\033[0m %s\n' "$1"; }; bad() { printf '  \033[31m✗\033[0m %s\n' "$1"; }; info() { printf '    %s\n' "$1"; }
HERE="$(cd "$(dirname "$0")" && pwd)"; FAIL=0
echo "Blocky Shorts setup check"

if command -v node >/dev/null; then V=$(node -e 'console.log(process.versions.node.split(".")[0])'); ok "node $(node -v)"; [ "$V" -lt 22 ] && info "Node < 22: run 'npm i ws' in $HERE if rendering complains about WebSocket"; else bad "node missing (install Node.js 22+)"; FAIL=1; fi
if command -v ffmpeg >/dev/null; then ok "ffmpeg"; else bad "ffmpeg missing"; (command -v apt-get >/dev/null && (sudo -n apt-get install -y ffmpeg >/dev/null 2>&1 || apt-get install -y ffmpeg >/dev/null 2>&1) && ok "ffmpeg installed") || { info "install ffmpeg (brew install ffmpeg / apt install ffmpeg)"; FAIL=1; }; fi
if python3 -c 'import numpy' 2>/dev/null; then ok "python3 + numpy"; else pip install numpy --quiet 2>/dev/null || pip install numpy --break-system-packages --quiet 2>/dev/null; python3 -c 'import numpy' 2>/dev/null && ok "numpy installed" || { bad "numpy missing (pip install numpy)"; FAIL=1; }; fi

find_chrome() { node --input-type=module -e "
const fs=await import('node:fs'),path=await import('node:path'),os=await import('node:os'),{execSync}=await import('node:child_process');
const c=[process.env.CHROME_PATH];for(const n of ['google-chrome','google-chrome-stable','chromium','chromium-browser','chrome','chrome-headless-shell','headless_shell']){try{c.push(execSync('command -v '+n,{stdio:['ignore','pipe','ignore']}).toString().trim())}catch{}}
c.push('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','/Applications/Chromium.app/Contents/MacOS/Chromium');
function*walk(d,k){if(k<0)return;let e=[];try{e=fs.readdirSync(d,{withFileTypes:true})}catch{return}for(const x of e){const p=path.join(d,x.name);if(x.isDirectory())yield*walk(p,k-1);else yield p}}
for(const b of [path.join(os.homedir(),'.cache/ms-playwright'),path.join(os.homedir(),'.cache/puppeteer'),path.join(os.homedir(),'Library/Caches/ms-playwright'),'/ms-playwright','/opt/pw-browsers'])for(const f of walk(b,4))if(/(chrome|headless_shell|chrome-headless-shell|Chromium)$/.test(f))c.push(f);
console.log(c.find(p=>p&&fs.existsSync(p))||'')" 2>/dev/null; }
CH="$(find_chrome)"
if [ -z "$CH" ]; then
  info "no Chrome found — trying to install one…"
  (npx -y @puppeteer/browsers install chrome-headless-shell@stable --path "$HOME/.cache/puppeteer" >/dev/null 2>&1) || true
  CH="$(find_chrome)"
  if [ -z "$CH" ]; then (pip install playwright --quiet 2>/dev/null || pip install playwright --break-system-packages --quiet 2>/dev/null) && python3 -m playwright install chromium >/dev/null 2>&1; CH="$(find_chrome)"; fi
  if [ -z "$CH" ] && command -v apt-get >/dev/null; then (sudo -n apt-get install -y chromium >/dev/null 2>&1 || apt-get install -y chromium >/dev/null 2>&1); CH="$(find_chrome)"; fi
fi
if [ -n "$CH" ]; then ok "browser: $CH"; else bad "no Chrome/Chromium available (install Google Chrome, or set CHROME_PATH)"; FAIL=1; fi
[ -d "$HERE/../assets/sfx" ] && ok "sound pack: $(ls "$HERE/../assets/sfx" | wc -l | tr -d ' ') sounds" || { python3 "$HERE/bs.py" sfx-pack >/dev/null && ok "sound pack generated"; }
[ $FAIL = 0 ] && echo "Ready." || echo "Some requirements are missing (see above)."
exit $FAIL
