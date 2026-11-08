#!/usr/bin/env bash
# ============================================================================
# bpy (Blender-as-python-module) sandbox loader — BUILD & USAGE RECIPE
# ============================================================================
# Purpose: make `import bpy` work in THIS sandbox, where Blender's wheel needs
# X11/GL shared libraries that cannot be installed (no OS package mirror in
# the network allowlist). We generate no-op STUB shared libraries that export
# every symbol bpy asks for, so the dynamic linker is satisfied. Rendering is
# 100% real (Cycles CPU); only the windowing/GL entry points are stubbed,
# which headless rendering never actually calls.
#
# Prereqs: gcc, python3, pip.  Venv:  python3 -m venv ~/.bpytest
#          ~/.bpytest/bin/pip install bpy==5.0.1 pillow  (PIL for checks)
#
# BUILD:   bash rebuild.sh          (writes .so files next to this script)
# USE:     LD_LIBRARY_PATH="$(pwd)" ~/.bpytest/bin/python your_scene.py
#
# ----------------------------------------------------------------------------
# HARD-WON LESSONS (do not "simplify" these away):
#
# 1. VERSIONED SYMBOLS. The failing import error looks like:
#        undefined symbol: xkb_state_update_mask, version V_0.5.0
#    A bare `void* sym(){return 0;}` export is NOT enough — the symbol must be
#    exported under an ld VERSION NODE. gcc flag:
#        -Wl,--version-script=libxkbcommon.so.0.vs
#
# 2. VERSION SCRIPT SYNTAX. On this box's ld, the node MUST be multi-line:
#        V_0.5.0 {
#        global:
#            sym_a;
#            sym_b;
#        local:
#            *;
#        };
#    A one-liner `V_0.5.0 { global: sym_a sym_b; local: *; };` is a SYNTAX
#    ERROR when it contains 2+ symbols, but silently WORKS with exactly one.
#    -> always emit the multi-line form.
#
# 3. SYMBOL NAME SANITIZING. Symbols scraped from error messages must match
#    ^[A-Za-z0-9_]+$ — an invisible comma/quote glued onto a name makes gcc
#    warn "extra tokens" yet still compile an EMPTY library. ALWAYS verify
#    with `nm -D lib.so | grep <name>` after building, not just gcc's rc.
#
# 4. WHICH LIB GETS WHICH SYMBOL. The import error only says the symbol name,
#    not the library. Route by prefix (the mapping below was derived from the
#    actual missing-symbol list; xkb_* -> libxkbcommon, glX* -> libGL, X*
#    -> libX11, the rest no-op). If a NEW undefined symbol appears, append it
#    to the right .c / .sym file and re-run this script (the loop below was
#    originally ~25 iterations).
# 5. Blender's wheel may also want libXext.so.6 / libXxf86vm.so.1 — add as
#    no-op libs (copy stub.c pattern) if your build complains.
# ============================================================================

set -euo pipefail
cd "$(dirname "$0")"

CC="gcc -shared -fPIC -O0"

# ---- generic no-op libs (no versioned symbols needed) --------------------
for L in libICE.so.6 libSM.so.6 libXrender.so.1 libXfixes.so.3 libXi.so.6 libXxf86vm.so.1; do
    [ -f "$L.c" ] || cp stub.c "$L.c"
    $CC -o "$L" "$L.c"
done

# ---- libGL: glX* entry points (unversioned exports are fine) -------------
$CC -o libGL.so.1 gl_stub.c

# ---- libX11: big X* surface (~110 syms) -----------------------------------
$CC -o libX11.so.6 libX11.so.6.c

# ---- libxkbcommon: VERSIONED xkb_* syms (see lesson 1+2) -----------------
$CC -o libxkbcommon.so.0 libxkbcommon.so.0.c -Wl,--version-script=libxkbcommon.so.0.vs

# ---- verify: every promised symbol really is exported --------------------
fail=0
while read -r lib syms; do
    for s in $syms; do
        nm -D "$lib" | grep -q " $s\$" || { echo "MISSING in $lib: $s"; fail=1; }
    done
done <<'EOF'
libGL.so.1 glXChooseVisual glXCopyContext glXCreateContext glXCreateNewContext glXDestroyContext glXGetConfig glXGetCurrentContext glXGetCurrentDrawable glXIsDirect glXMakeCurrent glXQueryExtensionsString glXQueryVersion glXSwapBuffers glXUseXFont glXWaitGL glXWaitX
EOF
[ "$fail" = 0 ] && echo "stub libs OK -> export LD_LIBRARY_PATH=$(pwd)"

# Smoke test (run from video_studio/engine/blender/):
#   LD_LIBRARY_PATH=$(pwd) ~/.bpytest/bin/python -c "import bpy; print('BPY_OK', bpy.app.version_string)"
