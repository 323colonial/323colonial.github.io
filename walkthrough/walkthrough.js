// First-person walk through the 323 Colonial model.
// The model, its baked lightmaps and scene.json come from scripts/walkthrough/build.py.
// Model frame (scene.json, physics): metres, x = west, y = south, z = up.
// three.js frame: (X, Y, Z) = (x, z, -y).
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { Reflector } from 'three/addons/objects/Reflector.js';

const ASSETS = '../assets/walkthrough/';
const $ = (id) => document.getElementById(id);
const canvas = $('view');

const EYE = 1.62, EYE_CROUCH = 1.0, RADIUS = 0.22, STEP = 0.36;
const WALK = 2.6, RUN = 5.2, JUMP = 3.4, GRAVITY = 12.0, TURN = 2.2;

const ROOMS = [
  // name, [x, y, z] feet position in model metres, heading degrees (0 = south)
  ['Front walk', [6.83, -6.7, -0.49], 0],
  ['Great room', [5.2, 6.4, 0], 250],
  ['Kitchen', [5.9, 5.6, 0], 40],
  ['Primary bedroom', [10.2, 3.3, 0], 60],
  ['Loft', [9.5, 4.6, 2.774], 250],
  ['Screened porch', [10.0, 9.5, -0.076], 270],
];

function fail(msg) {
  $('loading').hidden = true;
  $('start').hidden = true;
  $('why').textContent = msg;
  $('fail').hidden = false;
}

let renderer;
try {
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
} catch (e) {
  fail('This browser could not open a 3D view (WebGL is unavailable).');
  throw e;
}
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.NeutralToneMapping;
renderer.toneMappingExposure = 1.0;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(72, 1, 0.06, 900);
camera.rotation.order = 'YXZ';

function resize() {
  const w = window.innerWidth, h = window.innerHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
window.addEventListener('resize', resize);
resize();

// ---------------------------------------------------------------- loading
const manager = new THREE.LoadingManager();
manager.onProgress = (_url, done, total) => { $('bar').style.width = `${Math.round(100 * done / total)}%`; };
const texLoader = new THREE.TextureLoader(manager);
const textureLoads = [];

function loadTexture(url, { srgb = true, repeat = false } = {}) {
  let t;
  // Keep materials synchronous, but do not start the view/probe until every image settles.
  textureLoads.push(new Promise((resolve) => {
    t = texLoader.load(url, () => resolve(null), undefined, () => resolve(new Error(`Texture failed: ${url}`)));
  }));
  t.flipY = false;                       // glTF UV convention
  t.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
  if (repeat) t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
  return t;
}

const world = { solids: [], floors: [], terrain: null, doors: [] };
const photoMix = { value: 0 };     // P toggles the projected photographs (off until surfaces are fitted)
let sky = null;

function skyMaterial(tex, rot) {
  // Same lookup Blender uses for its environment texture, so the sun in the
  // backdrop agrees with the baked shadows.
  return new THREE.ShaderMaterial({
    uniforms: { map: { value: tex }, rot: { value: rot } },
    side: THREE.BackSide, depthWrite: false, depthTest: false, toneMapped: false,
    vertexShader: 'varying vec3 d; void main(){ d = position; vec4 p = modelViewMatrix * vec4(position, 0.0); gl_Position = projectionMatrix * vec4(p.xyz, 1.0); }',
    fragmentShader: `uniform sampler2D map; uniform float rot; varying vec3 d;
      void main(){
        vec3 b = normalize(vec3(d.x, -d.z, d.y));           // three -> model frame
        float c = cos(rot), s = sin(rot);
        vec2 r = vec2(c * b.x + s * b.y, -s * b.x + c * b.y); // undo the sky rotation
        float u = atan(r.y, -r.x) / 6.28318530718 + 0.5;
        float v = 0.5 + asin(clamp(b.z, -1.0, 1.0)) / 3.14159265359;
        gl_FragColor = vec4(texture2D(map, vec2(u, v)).rgb, 1.0);
        #include <colorspace_fragment>
      }`,
  });
}

async function load() {
  const [info, lm] = await Promise.all([
    ...['scene.json', 'lightmaps.json'].map(async (name) => {
      const response = await fetch(ASSETS + name, { cache: 'no-cache' });
      if (!response.ok) throw new Error(`${name}: HTTP ${response.status}`);
      return response.json();
    }),
  ]);
  // the model and its lightmap atlas only make sense as a matched set, so
  // every asset URL carries the build stamp and a stale cached copy is never mixed in
  const stamp = `?v=${info.build || 0}`;
  world.solids = info.solids;
  world.floors = info.floors;
  world.terrain = info.terrain;

  const skyTex = await texLoader.loadAsync(ASSETS + 'sky.jpg' + stamp);
  skyTex.colorSpace = THREE.SRGBColorSpace;
  skyTex.wrapS = THREE.RepeatWrapping;
  skyTex.minFilter = THREE.LinearFilter;
  skyTex.generateMipmaps = false;
  sky = new THREE.Mesh(new THREE.SphereGeometry(1, 48, 24), skyMaterial(skyTex, info.sun_rot));
  sky.renderOrder = -1;
  sky.frustumCulled = false;

  const lightmaps = {};
  for (const page of (info.baked === false ? [] : info.pages)) {
    const t = loadTexture(`${ASSETS}lm_${page}.webp${stamp}`);
    t.channel = 1;
    t.generateMipmaps = false;
    t.minFilter = THREE.LinearFilter;
    lightmaps[page] = t;
  }
  // listing photographs projected onto the model, one RGBA atlas per lightmap page
  const photos = {};
  for (const page of (info.baked === false ? [] : info.photoPages || [])) {
    const t = loadTexture(`${ASSETS}photo_${page}.webp${stamp}`);
    t.generateMipmaps = false;
    t.minFilter = THREE.LinearFilter;
    photos[page] = t;
  }
  const textures = {};
  const tex = (name, repeat) => (textures[name + repeat] ??= loadTexture(`${ASSETS}tex/${name}.webp${stamp}`, { repeat }));

  const materials = {};
  const metals = [];
  function material(key) {
    if (materials[key]) return materials[key];
    const [name, page] = key.split('__');
    const spec = info.materials[name] || {};
    const color = new THREE.Color().setRGB(...(spec.color || [1, 1, 1]), THREE.LinearSRGBColorSpace);
    let map = spec.tex ? tex(spec.tex, !spec.fit || spec.wrap) : null;
    if (map && spec.rot) {                       // its own copy, so the rotation does not leak to other users of the image
      map = loadTexture(`${ASSETS}tex/${spec.tex}.webp${stamp}`, { repeat: true });
      map.rotation = spec.rot * Math.PI / 180;
    }
    let m;
    if (spec.glass) {
      m = new THREE.MeshStandardMaterial({ color: 0x1c2622, roughness: 0.03, metalness: 0, transparent: true,
        opacity: 0.2, envMapIntensity: 1.6, side: THREE.DoubleSide, depthWrite: false });
    } else if (spec.screen) {
      m = new THREE.MeshBasicMaterial({ color: 0x111111, transparent: true, opacity: 0.22, side: THREE.DoubleSide, depthWrite: false });
    } else if (spec.unlit) {
      m = new THREE.MeshBasicMaterial({ map, color: new THREE.Color(spec.unlit, spec.unlit, spec.unlit), alphaTest: 0.5, side: THREE.DoubleSide });
    } else if (spec.emit) {
      const k = Math.min(spec.emit, 1.6);
      if (name === 'fire') {
        // the stove: flames from scrolling noise, so the fire moves the way fire does
        m = world.fire = new THREE.ShaderMaterial({
          uniforms: { time: { value: 0 } }, side: THREE.DoubleSide,
          vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
          fragmentShader: `uniform float time; varying vec2 vUv;
            float h(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
            float n(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
              return mix(mix(h(i), h(i + vec2(1, 0)), f.x), mix(h(i + vec2(0, 1)), h(i + vec2(1, 1)), f.x), f.y); }
            float fbm(vec2 p){ float a = 0.5, s = 0.0; for (int k = 0; k < 4; k++) { s += a * n(p); p *= 2.03; a *= 0.5; } return s; }
            void main(){
              float y = 1.0 - vUv.y, x = vUv.x;                       // y up from the grate
              vec2 q = vec2(x * 3.2, y * 2.4 - time * 1.15);
              float turb = fbm(q + vec2(fbm(q * 1.7 + time * 0.3) * 0.9, 0.0));
              float body = 1.0 - smoothstep(0.0, 0.55, abs(x - 0.5 + 0.12 * sin(time * 0.7 + y * 3.0)) * (0.9 + y * 1.6));
              float f = clamp(body * (1.25 - y * 1.15) + (turb - 0.5) * 1.1, 0.0, 1.0);
              f *= smoothstep(0.0, 0.06, y);
              vec3 c = mix(vec3(0.02, 0.01, 0.01), vec3(0.75, 0.1, 0.0), smoothstep(0.08, 0.35, f));
              c = mix(c, vec3(1.0, 0.5, 0.05), smoothstep(0.3, 0.6, f));
              c = mix(c, vec3(1.0, 0.9, 0.55), smoothstep(0.62, 0.95, f));
              float ember = smoothstep(0.16, 0.0, y) * (0.55 + 0.45 * n(vec2(x * 18.0, time * 0.9)));
              c += vec3(0.9, 0.25, 0.03) * ember;
              gl_FragColor = vec4(c, 1.0);
              #include <colorspace_fragment>
            }`,
        });
      } else m = new THREE.MeshBasicMaterial({ map, color: color.multiplyScalar(k), side: THREE.DoubleSide });
      if (name === 'water') { m.transparent = true; m.opacity = 0.85; }
    } else {
      // metals keep some diffuse so the baked light still shapes them indoors
      m = new THREE.MeshStandardMaterial({ map, color, roughness: spec.rough ?? 0.7, metalness: spec.metal ? 0.35 : 0 });
      m.envMapIntensity = spec.metal ? 0.6 : (spec.rough ?? 0.7) < 0.45 ? 0.3 : 0.1;
      if (name === 'mirror') { m.metalness = 0; m.roughness = 0.15; m.color.set(0xf2f6f6); m.lightMapIntensity *= 1.5; }   // one room probe cannot serve every mirror
      else if (spec.metal) metals.push(m);
      if (name === 'granite' || name === 'oakfloor') metals.push(m);
      if (spec.alpha) { m.alphaTest = 0.5; m.side = THREE.DoubleSide; }
      const lmTex = info.baked === false ? null : lightmaps[page];
      if (lmTex) {
        m.lightMap = lmTex;
        const photo = photos[page];
        if (photo) {
          // where a photograph covers the texel, show it as shot instead of the computed shading
          m.onBeforeCompile = (sh) => {
            sh.uniforms.photoMap = { value: photo };
            sh.uniforms.photoMix = photoMix;
            sh.fragmentShader = 'uniform sampler2D photoMap;\nuniform float photoMix;\n' + sh.fragmentShader.replace('#include <colorspace_fragment>',
              'vec4 ph = texture2D(photoMap, vLightMapUv);\n gl_FragColor.rgb = mix(gl_FragColor.rgb, ph.rgb, ph.a * photoMix);\n#include <colorspace_fragment>');
          };
          m.customProgramCacheKey = () => 'photo';
        }
        // stored = (L * gain / range) ** (1 / 2.2); three divides lightmap irradiance by pi
        m.lightMapIntensity = lm.range * Math.PI;
      } else {
        m.envMapIntensity = 0;                             // unbaked preview: plain lights added below
      }
    }
    // The generator emits single-sided faces; render both sides so a face seen
    // from behind (soffits, thin trim) never drops out.
    m.side = THREE.DoubleSide;
    m.name = key;
    return (materials[key] = m);
  }

  const draco = new DRACOLoader(manager).setDecoderPath('../vendor/three-0.186.1/draco/');
  let gltf;
  try {
    gltf = await new GLTFLoader(manager).setDRACOLoader(draco).loadAsync(ASSETS + 'house.glb' + stamp);
  } finally {
    draco.dispose();
  }
  gltf.scene.traverse((o) => {
    if (!o.isMesh) return;
    o.material = material(o.material.name);
    o.matrixAutoUpdate = false;
    o.updateMatrix();
    if (o.material.transparent) o.renderOrder = 2;
  });
  scene.add(gltf.scene);
  if (info.baked === false) {
    // geometry preview without a lighting bake: flat, even light so shapes read clearly
    scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8478, 2.2));
    const sun = new THREE.DirectionalLight(0xffffff, 1.2);
    sun.position.set(-30, 60, -40);
    scene.add(sun);
    $('room').dataset.note = 'unbaked preview';
  }
  // Bath mirrors become real planar reflections. The model's mirror panes are flat quads;
  // each is replaced by a Reflector facing both ways (only the side being looked at renders).
  gltf.scene.updateMatrixWorld(true);
  const panes = [];
  gltf.scene.traverse((o) => { if (o.isMesh && o.material.name.startsWith('mirror__')) panes.push(o); });
  for (const o of panes) {
    const pos = o.geometry.attributes.position, idx = o.geometry.index;
    const at = (i) => new THREE.Vector3().fromBufferAttribute(pos, idx ? idx.getX(i) : i).applyMatrix4(o.matrixWorld);
    const count = idx ? idx.count : pos.count;
    for (let t = 0; t + 5 < count + 1; t += 6) {
      const pts = [0, 1, 2, 3, 4, 5].map((k) => at(t + k));
      const nrm = new THREE.Vector3().subVectors(pts[1], pts[0]).cross(new THREE.Vector3().subVectors(pts[2], pts[0])).normalize();
      const up = new THREE.Vector3(0, 1, 0), right = new THREE.Vector3().crossVectors(up, nrm).normalize();
      const box = new THREE.Box3().setFromPoints(pts), c = box.getCenter(new THREE.Vector3());
      const us = pts.map((p) => p.dot(right)), vs = pts.map((p) => p.y);
      const w = Math.max(...us) - Math.min(...us), h = Math.max(...vs) - Math.min(...vs);
      for (const sgn of [1, -1]) {
        const r = new Reflector(new THREE.PlaneGeometry(w, h), { textureWidth: 768, textureHeight: 768, color: 0xe6ecec });
        r.position.copy(c).addScaledVector(nrm, 0.004 * sgn);
        r.lookAt(c.clone().addScaledVector(nrm, sgn));
        scene.add(r);
      }
    }
    o.visible = false;
  }
  // swinging doors: each is one or two top-level nodes pivoted on the hinge
  world.doors = (info.doors || []).map((d) => {
    const nodes = gltf.scene.children.filter((o) => o.name === d.name || o.name.startsWith(d.name + '__'));
    for (const n of nodes) n.matrixAutoUpdate = true;
    return { ...d, nodes, t: 0, cx: (d.seg[0] + d.seg[2]) / 2, cy: (d.seg[1] + d.seg[3]) / 2 };
  });

  const textureError = (await Promise.all(textureLoads)).find(Boolean);
  if (textureError) throw textureError;

  // image-based reflections from the same sky
  const pm = new THREE.PMREMGenerator(renderer);
  const envScene = new THREE.Scene();
  envScene.add(sky);
  sky.scale.setScalar(50);
  scene.environment = pm.fromScene(envScene, 0, 0.1, 100).texture;
  pm.dispose();
  sky.scale.setScalar(1);
  scene.add(sky);
  // Real reflections: once the textures are in, photograph the kitchen in all six directions
  // and let the metals (and, faintly, granite and the floor finish) reflect that room.
  {
    const rt = new THREE.WebGLCubeRenderTarget(256);
    const cam = new THREE.CubeCamera(0.1, 200, rt);
    cam.position.set(17.5 * 0.3048, 4.6 * 0.3048, -19.5 * 0.3048);
    scene.add(cam);
    cam.update(renderer, scene);
    scene.remove(cam);
    const pm2 = new THREE.PMREMGenerator(renderer);
    const env = pm2.fromCubemap(rt.texture).texture;
    pm2.dispose(); rt.dispose();
    for (const m of metals) {
      m.envMap = env;
      const isMetal = m.metalness > 0;
      if (isMetal) { m.metalness = 0.92; m.envMapIntensity = 1.0; } else { m.envMapIntensity = 0.5; }
      m.needsUpdate = true;
    }
  }
  return info;
}

// ---------------------------------------------------------------- physics
const player = { x: 0, y: 0, z: 0, vz: 0, heading: 0, pitch: 0, grounded: true, crouch: 0 };

function terrainAt(x, y) {
  const t = world.terrain;
  const fx = Math.min(Math.max((x - t.x0) / t.step, 0), t.n - 1.001);
  const fy = Math.min(Math.max((y - t.y0) / t.step, 0), t.n - 1.001);
  const i = Math.floor(fx), j = Math.floor(fy), a = fx - i, b = fy - j;
  const h = (ii, jj) => t.h[jj * t.n + ii];
  return (h(i, j) * (1 - a) + h(i + 1, j) * a) * (1 - b) + (h(i, j + 1) * (1 - a) + h(i + 1, j + 1) * a) * b;
}

function inPoly(x, y, poly) {
  let inside = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i], [xj, yj] = poly[j];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
}

function floorAt(x, y, z) {
  let best = -Infinity;
  for (const f of world.floors) {
    if (!inPoly(x, y, f.poly)) continue;
    let fz = f.z;
    if (f.ramp) {
      const [y0, z0, y1, z1] = f.ramp;
      const t = Math.min(Math.max((y - y0) / (y1 - y0), 0), 1);
      fz = z0 + (z1 - z0) * t;
    }
    if (fz <= z + STEP && fz > best) best = fz;
  }
  const g = terrainAt(x, y);
  if (g <= z + STEP && g > best) best = g;
  return best === -Infinity ? g : best;
}

function updateDoors(dt) {
  for (const d of world.doors) {
    const near = Math.hypot(player.x - d.cx, player.y - d.cy);
    const level = player.z > d.z0 - 1.2 && player.z < d.z1;
    if (level && near < 1.9) d.want = 1; else if (!level || near > 2.5) d.want = 0;
    const t = Math.min(1, Math.max(0, d.t + Math.sign((d.want || 0) - d.t) * dt * 3));
    if (t === d.t) continue;
    d.t = t;
    const e = t * t * (3 - 2 * t);
    for (const n of d.nodes) n.rotation.y = d.open * e;
  }
}

function collide(p, height) {
  for (let pass = 0; pass < 3; pass++) {
    for (const d of world.doors) {            // a door blocks until it is mostly open
      if (d.t > 0.5 || p.z + STEP >= d.z1 || p.z + height <= d.z0) continue;
      const ax = d.seg[0], ay = d.seg[1], bx = d.seg[2] - ax, by = d.seg[3] - ay;
      const t = Math.min(Math.max(((p.x - ax) * bx + (p.y - ay) * by) / (bx * bx + by * by), 0), 1);
      const dx = p.x - (ax + bx * t), dy = p.y - (ay + by * t), d2 = dx * dx + dy * dy;
      if (d2 < RADIUS * RADIUS && d2 > 1e-10) { const k = (RADIUS - Math.sqrt(d2)) / Math.sqrt(d2); p.x += dx * k; p.y += dy * k; }
    }
    for (const s of world.solids) {
      if (p.z + STEP >= s[5] || p.z + height <= s[4]) continue;
      const ax = s[0], ay = s[1], bx = s[2] - ax, by = s[3] - ay;
      const L2 = bx * bx + by * by;
      let t = L2 > 0 ? ((p.x - ax) * bx + (p.y - ay) * by) / L2 : 0;
      t = Math.min(Math.max(t, 0), 1);
      const dx = p.x - (ax + bx * t), dy = p.y - (ay + by * t);
      const d2 = dx * dx + dy * dy;
      if (d2 >= RADIUS * RADIUS) continue;
      if (d2 > 1e-10) {
        const d = Math.sqrt(d2), push = (RADIUS - d) / d;
        p.x += dx * push; p.y += dy * push;
      } else {
        const L = Math.sqrt(L2) || 1;
        p.x += (-by / L) * RADIUS; p.y += (bx / L) * RADIUS;
      }
    }
  }
}

const keys = new Set();
let fly = false, note = '', noteUntil = 0;
const touch = { move: null, look: null, mx: 0, my: 0 };

function step(dt) {
  let f = 0, r = 0;
  if (keys.has('KeyW') || keys.has('ArrowUp')) f += 1;
  if (keys.has('KeyS') || keys.has('ArrowDown')) f -= 1;
  if (keys.has('KeyD')) r += 1;
  if (keys.has('KeyA')) r -= 1;
  // left / right arrows turn; with Alt held they strafe instead
  const arrow = (keys.has('ArrowRight') ? 1 : 0) - (keys.has('ArrowLeft') ? 1 : 0);
  if (keys.has('AltLeft') || keys.has('AltRight')) r += arrow;
  else player.heading += arrow * TURN * dt;
  f += -touch.my; r += touch.mx;
  const len = Math.hypot(f, r);
  if (len > 1) { f /= len; r /= len; }
  const crouching = keys.has('KeyC');
  player.crouch += ((crouching ? 1 : 0) - player.crouch) * Math.min(1, dt * 10);
  const speed = (keys.has('ShiftLeft') || keys.has('ShiftRight')) && !crouching ? RUN : crouching ? WALK * 0.5 : WALK;
  const sh = Math.sin(player.heading), ch = Math.cos(player.heading);
  // heading 0 faces +y (south); +x (west) is then on the right
  const vx = (sh * f + ch * r) * speed, vy = (ch * f - sh * r) * speed;
  const height = EYE + 0.12 - (EYE - EYE_CROUCH) * player.crouch;
  if (fly) {                                    // F: no walls, no gravity; Space / C go up and down
    const k = speed * 1.6 * dt;
    player.x += vx * 1.6 * dt; player.y += vy * 1.6 * dt;
    player.z += ((keys.has('Space') ? 1 : 0) - (keys.has('KeyC') ? 1 : 0)) * k + f * Math.sin(player.pitch) * k;
    player.grounded = false; player.vz = 0;
    camera.position.set(player.x, player.z + EYE, -player.y);
    camera.rotation.set(player.pitch, -player.heading, 0);
    if (sky) sky.position.copy(camera.position);
    return;
  }
  const n = Math.max(1, Math.ceil((speed * dt) / (RADIUS * 0.6)));
  for (let i = 0; i < n; i++) {
    player.x += (vx * dt) / n; player.y += (vy * dt) / n;
    collide(player, height);
  }
  if (keys.has('Space') && player.grounded) { player.vz = JUMP; player.grounded = false; }
  const ground = floorAt(player.x, player.y, player.z);
  if (player.grounded) {
    if (ground < player.z - STEP) player.grounded = false;            // walked off an edge
    else player.z += (ground - player.z) * Math.min(1, dt * 18);      // ease over steps and stairs
  }
  if (!player.grounded) {
    player.vz -= GRAVITY * dt;
    player.z += player.vz * dt;
    if (player.z <= ground && player.vz <= 0) { player.z = ground; player.vz = 0; player.grounded = true; }
  }
  const eye = EYE - (EYE - EYE_CROUCH) * player.crouch;
  camera.position.set(player.x, player.z + eye, -player.y);
  camera.rotation.set(player.pitch, -player.heading, 0);
  if (sky) sky.position.copy(camera.position);
}

function teleport(i) {
  if (!Number.isInteger(i) || i < 0 || i >= ROOMS.length) return;
  const [, p, deg] = ROOMS[i];
  Object.assign(player, { x: p[0], y: p[1], z: p[2], vz: 0, heading: THREE.MathUtils.degToRad(deg), pitch: 0, grounded: true });
}

function roomName() {
  const ft = 0.3048, x = player.x / ft, y = player.y / ft, z = player.z / ft;
  if (z > 7) {
    if (x > 45.7) return 'Upstairs bedroom';
    if (x > 20.4 && x < 29.1 && y > 17.5) return 'Upstairs bath';
    return 'Loft';
  }
  if (x < 0.2 && y > -0.5 && y < 35.4) return 'Deck';
  if (y > 27.2 && y < 35.4 && x > 0 && x < 46) return 'Screened porch';
  if (x > 46) return y > 0.5 && y < 27 && x < 69.8 ? 'Garage' : '';
  if (x < 0.2 || y < 0.6 || y > 27.2) return y < 0.6 && y > -6.5 && x > 16 && x < 29 ? 'Front porch' : '';
  if (x < 20.3) return y > 16.2 && x > 11.5 ? 'Kitchen' : y > 17.2 ? 'Dining area' : 'Great room';
  if (x < 24.3) return y < 13.3 ? 'Entry' : 'Kitchen';
  if (x > 33.6 && y > 14.5 && y < 22.8) return 'Primary bath';
  if (x > 30.9 && y < 14.4) return 'Primary bedroom';
  if (x < 30.7 && y < 10.1) return 'Primary closet';
  if (x < 29.6 && y > 21.0) return 'Half bath';
  return y > 22.9 ? 'Mudroom' : 'Hall';
}

// ---------------------------------------------------------------- input
const locked = () => document.pointerLockElement === canvas;
let running = false;

function begin() {
  $('start').hidden = true;
  $('hud').hidden = false;
  running = true;
  if (matchMedia('(pointer: fine)').matches) {
    $('dot').hidden = false;
    canvas.requestPointerLock?.();
  }
}
$('go').addEventListener('click', begin);
canvas.addEventListener('click', () => { if (running && !locked() && matchMedia('(pointer: fine)').matches) canvas.requestPointerLock?.(); });
document.addEventListener('pointerlockchange', () => {
  if (!locked() && running && !typing && matchMedia('(pointer: fine)').matches) {
    running = false; keys.clear();
    $('dot').hidden = true;
    $('go').textContent = 'Keep walking';
    $('start').hidden = false;
  }
});
document.addEventListener('mousemove', (e) => {
  if (!locked()) return;
  player.heading += e.movementX * 0.0022;
  player.pitch = Math.min(1.5, Math.max(-1.5, player.pitch - e.movementY * 0.0022));
});
// K: freeze the view, take its picture and position, and ask for a note about it.
let typing = false, pending = null;
function openNote() {
  const ft = 0.3048, deg = (a) => ((a * 180 / Math.PI) % 360 + 360) % 360;
  const spot = `at ${(player.x / ft).toFixed(1)}, ${(player.y / ft).toFixed(1)}, ${(player.z / ft).toFixed(1)} ft, facing ${deg(player.heading).toFixed(0)}°, pitch ${(player.pitch * 180 / Math.PI).toFixed(0)}°`;
  renderer.render(scene, camera);
  const small = document.createElement('canvas');
  small.width = 1280; small.height = Math.round(1280 * canvas.height / canvas.width);
  small.getContext('2d').drawImage(canvas, 0, 0, small.width, small.height);
  pending = { spot, image: small.toDataURL('image/jpeg', 0.85) };
  typing = true; keys.clear();
  if (locked()) document.exitPointerLock();
  $('notebox').hidden = false;
  $('notetext').value = '';
  setTimeout(() => $('notetext').focus(), 0);
}
function closeNote(save) {
  const text = $('notetext').value.trim();
  $('notebox').hidden = true;
  $('notetext').blur();
  typing = false;
  if (save && pending) {
    const line = pending.spot + (text ? ` :: ${text}` : '');
    navigator.clipboard?.writeText(line).catch(() => {});
    note = 'saving…'; noteUntil = performance.now() + 4000;
    if (['127.0.0.1', 'localhost'].includes(location.hostname)) {
      // local preview only: scripts/walkthrough/serve.py appends it to .walkthrough-notes/
      fetch('/__note', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ note: line, image: pending.image }) })
        .then((r) => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); }).then((j) => { note = `saved view ${j.n}` + (text ? `: ${text}` : ''); noteUntil = performance.now() + 6000; })
        .catch(() => { note = 'could not save (is serve.py running?)'; noteUntil = performance.now() + 6000; });
    } else { note = line; noteUntil = performance.now() + 15000; }
  }
  pending = null;
  if (running && matchMedia('(pointer: fine)').matches) canvas.requestPointerLock?.();
}
$('notetext').addEventListener('keydown', (e) => {
  e.stopPropagation();
  if (e.key === 'Enter') { e.preventDefault(); closeNote(true); }
  if (e.key === 'Escape') { e.preventDefault(); closeNote(false); }
});

window.addEventListener('keydown', (e) => {
  if (!running || typing) return;
  // leave system and browser shortcuts alone (e.g. macOS screenshots: Cmd-Ctrl-Shift-4)
  if (e.metaKey || e.ctrlKey) { keys.clear(); return; }
  keys.add(e.code);
  if (/^Digit[1-6]$/.test(e.code)) teleport(Number(e.code.slice(5)) - 1);
  if (e.code === 'KeyP' && !e.repeat) photoMix.value = photoMix.value ? 0 : 1;
  if (e.code === 'KeyF' && !e.repeat) { fly = !fly; note = fly ? 'fly mode' : 'walking'; noteUntil = performance.now() + 2500; }
  if (e.code === 'KeyK' && !e.repeat) { e.preventDefault(); openNote(); return; }
  if (['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'AltLeft', 'AltRight'].includes(e.code)) e.preventDefault();
});
window.addEventListener('keyup', (e) => keys.delete(e.code));
window.addEventListener('blur', () => {
  keys.clear();
  touch.move = touch.look = null;
  touch.mx = touch.my = 0;
});

canvas.addEventListener('pointerdown', (e) => {
  if (e.pointerType === 'mouse' || !running || typing) return;
  canvas.setPointerCapture(e.pointerId);
  const side = e.clientX < window.innerWidth / 2 ? 'move' : 'look';
  if (!touch[side]) touch[side] = { id: e.pointerId, x: e.clientX, y: e.clientY };
});
canvas.addEventListener('pointermove', (e) => {
  if (typing) return;
  if (touch.move && e.pointerId === touch.move.id) {
    touch.mx = Math.max(-1, Math.min(1, (e.clientX - touch.move.x) / 60));
    touch.my = Math.max(-1, Math.min(1, (e.clientY - touch.move.y) / 60));
  } else if (touch.look && e.pointerId === touch.look.id) {
    player.heading += (e.clientX - touch.look.x) * 0.005;
    player.pitch = Math.min(1.5, Math.max(-1.5, player.pitch - (e.clientY - touch.look.y) * 0.005));
    touch.look.x = e.clientX; touch.look.y = e.clientY;
  }
});
const lift = (e) => {
  if (touch.move && e.pointerId === touch.move.id) { touch.move = null; touch.mx = touch.my = 0; }
  if (touch.look && e.pointerId === touch.look.id) touch.look = null;
};
canvas.addEventListener('pointerup', lift);
canvas.addEventListener('pointercancel', lift);

// ---------------------------------------------------------------- main loop
let last = performance.now(), labelAt = 0;
let slow = 0, ratio = Math.min(window.devicePixelRatio || 1, 2);
let lastDraw = 0;
function frame(now) {
  requestAnimationFrame(frame);
  // Draw only when there is something to show: at most 60 frames a second while walking,
  // and about two a second while paused, so an idle or forgotten tab leaves the GPU alone.
  if (document.hidden || now - lastDraw < (running ? 15 : 500)) return;
  lastDraw = now;
  const raw = (now - last) / 1000;
  const dt = Math.min(0.05, raw);
  last = now;
  // drop render resolution a notch if the machine cannot hold about 40 fps
  slow = running && raw > 0.028 && raw < 0.2 ? slow + 1 : Math.max(0, slow - 2);
  if (slow > 45 && ratio > 0.75) {
    ratio = Math.max(0.75, ratio - 0.25);
    renderer.setPixelRatio(ratio);
    resize();
    slow = 0;
  }
  if (!typing) {
    if (world.fire) world.fire.uniforms.time.value = now / 1000;
    if (running) step(dt); else step(0);
    updateDoors(dt);
  }
  if (now > labelAt) {
    const extra = now < noteUntil ? note : ($('room').dataset.note || '');
    $('room').textContent = [roomName(), extra].filter(Boolean).join(' · ');
    labelAt = now + 250;
  }
  renderer.render(scene, camera);
}
// give the GPU memory back as soon as the page is left
window.addEventListener('pagehide', (event) => {
  if (!event.persisted) { renderer.dispose(); renderer.forceContextLoss(); }
});

load().then((info) => {
  const s = info.spawn;
  Object.assign(player, { x: s.pos[0], y: s.pos[1], z: s.pos[2], heading: THREE.MathUtils.degToRad(s.yaw_deg) });
  const q = new URLSearchParams(location.search);
  if (q.has('room')) teleport(Math.max(0, Math.min(ROOMS.length - 1, Number(q.get('room')) - 1)));
  $('loading').hidden = true;
  $('start').hidden = false;
  // hooks for later additions (wandering sprites, sounds) and for testing
  window.colonial = { THREE, scene, camera, renderer, player, world, teleport, begin, floorAt, terrainAt };
  requestAnimationFrame(frame);
}).catch((e) => {
  console.error(e);
  fail('The 3D model did not load. Please check your connection and try again.');
});
