src = open('../../flannan_isles_short/prod/web/main.js').read()
head = src.split('/* ---------- sea ---------- */')[0]
post = '/* ============================ post' + src.split('/* ============================ post',1)[1].split('const tmpV = new THREE.Vector3();')[0]
draw = 'function drawActors(list, cam)' + src.split('function drawActors(list, cam)',1)[1].split('function worldState(S, f, t) {')[0]
world = open('world_new.js').read()
tail = open('tail_new.js').read()
OV = open('ov_new.js').read()
i = head.index('const OV = {'); j = head.index('\n};', i) + 3
head = head[:i] + OV.rstrip() + head[j:]
open('web/main.js','w').write(head + world + '\n\n' + post + draw + tail)
print('main.js rebuilt')
