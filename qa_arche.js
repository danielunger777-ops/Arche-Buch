/**
 * qa_arche.js — Automatisierter Ein-Befehl-Browser-QA-Runner (Zero-Dependency CDP)
 * Startet lokalen HTTP-Server + Headless Chrome (1440x900, WebGL/ANGLE),
 * führt T01–T101 aus, prüft Console-/Page-/WebGL-Shader-Fehler, misst FPS
 * pro Arche.QA-Preset und speichert PNG-Screenshots nach scratch/.
 *
 * Aufruf:
 *   node qa_arche.js              # Alle Arche.QA-Presets (oder Standard-Set)
 *   node qa_arche.js --quick      # Nur shipyard, aqueduct, overview
 *   node qa_arche.js --critic     # Visual-Critic-Set (shipyard, botany_close, ark_interior, ararat_altar, storm_ocean, overview)
 *   node qa_arche.js --ipad       # Zusätzlicher iPad-Emulationslauf (1024x768, DPR=2, Touch, scratch/qa_ipad.png)
 *   node qa_arche.js --no-shots   # Nur Tests, Shader & FPS ohne PNGs
 */
const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { spawn } = require('child_process');

const args = process.argv.slice(2);
const QUICK_MODE = args.includes('--quick');
const CRITIC_MODE = args.includes('--critic');
const IPAD_MODE = args.includes('--ipad');
const NO_SHOTS = args.includes('--no-shots');
const XRAY_MODE = args.includes('--xray');
const HTML_FILE = 'Arche Simulation 3.0.html';
const SCRATCH_DIR = path.join(__dirname, 'scratch');
const MIN_PNG_BYTES = 30 * 1024;
const IPAD_UA = 'Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1';

function checkPngSanity(buf, relPath) {
  if (!buf || buf.length < 24) {
    return { ok: false, bytes: buf ? buf.length : 0, width: 0, height: 0, reason: 'Datei zu klein / kein PNG-Header' };
  }
  const pngSig = '89504e470d0a1a0a';
  if (buf.subarray(0, 8).toString('hex') !== pngSig) {
    return { ok: false, bytes: buf.length, width: 0, height: 0, reason: 'Ungültige PNG-Signatur' };
  }
  const width = buf.readUInt32BE(16);
  const height = buf.readUInt32BE(20);
  if (width <= 0 || height <= 0) {
    return { ok: false, bytes: buf.length, width, height, reason: 'Ungültige PNG-Abmessungen' };
  }
  if (buf.length < MIN_PNG_BYTES) {
    return {
      ok: false,
      bytes: buf.length,
      width,
      height,
      reason: `Triviale Bildgröße (${(buf.length / 1024).toFixed(1)} KB < ${(MIN_PNG_BYTES / 1024).toFixed(0)} KB — Verdacht auf leeres/schwarzes Canvas)`
    };
  }
  return { ok: true, bytes: buf.length, width, height, relPath };
}

function findBrowserExe() {
  const candidates = [
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    path.join(process.env.LOCALAPPDATA || '', 'Google\\Chrome\\Application\\chrome.exe'),
    'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe'
  ];
  return candidates.find((p) => p && fs.existsSync(p)) || null;
}

function startStaticServer(rootDir) {
  return new Promise((resolve, reject) => {
    const server = http.createServer((req, res) => {
      const cleanUrl = decodeURIComponent((req.url || '/').split('?')[0]);
      const rel = cleanUrl === '/' ? HTML_FILE : cleanUrl.replace(/^\/+/, '');
      const fullPath = path.resolve(rootDir, rel);
      if (!fullPath.startsWith(path.resolve(rootDir))) {
        res.writeHead(403);
        return res.end('Forbidden');
      }
      if (!fs.existsSync(fullPath) || fs.statSync(fullPath).isDirectory()) {
        res.writeHead(404);
        return res.end('Not found');
      }
      const ext = path.extname(fullPath).toLowerCase();
      const mime = ext === '.html' ? 'text/html; charset=utf-8'
        : ext === '.js' ? 'application/javascript; charset=utf-8'
        : ext === '.css' ? 'text/css; charset=utf-8'
        : ext === '.png' ? 'image/png'
        : 'application/octet-stream';
      res.writeHead(200, { 'Content-Type': mime });
      fs.createReadStream(fullPath).pipe(res);
    });
    server.on('error', reject);
    server.listen(0, '127.0.0.1', () => resolve(server));
  });
}

async function waitForDevToolsPort(userDataDir, timeoutMs = 15000) {
  const portFile = path.join(userDataDir, 'DevToolsActivePort');
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    if (fs.existsSync(portFile)) {
      const lines = fs.readFileSync(portFile, 'utf8').trim().split(/\r?\n/);
      const port = Number(lines[0]);
      if (port > 0) return port;
    }
    await new Promise((r) => setTimeout(r, 120));
  }
  throw new Error('Timeout beim Warten auf Chrome DevToolsActivePort');
}

class CDPClient {
  constructor(wsUrl) {
    this.ws = new WebSocket(wsUrl);
    this.nextId = 1;
    this.pending = new Map();
    this.listeners = new Map();
  }
  connect() {
    return new Promise((resolve, reject) => {
      this.ws.addEventListener('open', resolve, { once: true });
      this.ws.addEventListener('error', (e) => reject(e.error || new Error('WebSocket error')), { once: true });
      this.ws.addEventListener('message', (evt) => {
        const msg = JSON.parse(evt.data);
        if (msg.id && this.pending.has(msg.id)) {
          const { res, rej } = this.pending.get(msg.id);
          this.pending.delete(msg.id);
          if (msg.error) rej(new Error(`${msg.error.message} (${msg.error.code})`));
          else res(msg.result);
        } else if (msg.method && this.listeners.has(msg.method)) {
          for (const fn of this.listeners.get(msg.method)) fn(msg.params);
        }
      });
    });
  }
  on(method, fn) {
    if (!this.listeners.has(method)) this.listeners.set(method, []);
    this.listeners.get(method).push(fn);
  }
  send(method, params = {}) {
    const id = this.nextId++;
    return new Promise((res, rej) => {
      this.pending.set(id, { res, rej });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }
  async eval(expression) {
    const out = await this.send('Runtime.evaluate', {
      expression,
      awaitPromise: true,
      returnByValue: true
    });
    if (out.exceptionDetails) {
      const txt = out.exceptionDetails.exception?.description || out.exceptionDetails.text || 'JS eval error';
      throw new Error(txt);
    }
    return out.result ? out.result.value : undefined;
  }
  close() {
    try { this.ws.close(); } catch (_) {}
  }
}

async function run() {
  if (!fs.existsSync(HTML_FILE)) {
    console.error(`FAIL: ${HTML_FILE} nicht gefunden.`);
    process.exit(1);
  }
  const browserExe = findBrowserExe();
  if (!browserExe) {
    console.error('FAIL: Weder Google Chrome noch Microsoft Edge gefunden.');
    process.exit(1);
  }
  if (!NO_SHOTS && !fs.existsSync(SCRATCH_DIR)) fs.mkdirSync(SCRATCH_DIR, { recursive: true });

  const server = await startStaticServer(__dirname);
  const httpPort = server.address().port;
  const tmpProfile = fs.mkdtempSync(path.join(os.tmpdir(), 'arche-qa-'));
  let chromeProc = null;
  let cdp = null;

  try {
    chromeProc = spawn(browserExe, [
      '--headless=new',
      '--remote-debugging-port=0',
      `--user-data-dir=${tmpProfile}`,
      '--window-size=1440,900',
      '--use-gl=angle',
      '--use-angle=d3d11',
      '--enable-webgl',
      '--ignore-gpu-blocklist',
      '--no-first-run',
      '--no-default-browser-check',
      'about:blank'
    ], { stdio: 'ignore' });

    const devPort = await waitForDevToolsPort(tmpProfile);
    const targetsRes = await fetch(`http://127.0.0.1:${devPort}/json/list`);
    const targets = await targetsRes.json();
    const pageTarget = targets.find((t) => t.type === 'page') || targets[0];
    if (!pageTarget || !pageTarget.webSocketDebuggerUrl) {
      throw new Error('Kein DevTools-Page-Target gefunden.');
    }

    cdp = new CDPClient(pageTarget.webSocketDebuggerUrl);
    await cdp.connect();
    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');
    await cdp.send('Emulation.setDeviceMetricsOverride', {
      width: 1440, height: 900, deviceScaleFactor: 1, mobile: false
    });

    const consoleErrors = [];
    const pageErrors = [];
    let inDesktopPhase = true;
    cdp.on('Runtime.consoleAPICalled', (p) => {
      if (!inDesktopPhase) return;
      if (p.type === 'error') {
        const text = (p.args || []).map((a) => a.value ?? a.description ?? '').join(' ');
        if (!text.includes('__TEST_RESULTS__')) consoleErrors.push(text);
      }
    });
    cdp.on('Runtime.exceptionThrown', (p) => {
      if (!inDesktopPhase) return;
      pageErrors.push(p.exceptionDetails?.exception?.description || p.exceptionDetails?.text || 'Uncaught exception');
    });

    const url = `http://127.0.0.1:${httpPort}/${encodeURIComponent(HTML_FILE)}?v=qa_${Date.now()}`;
    await cdp.send('Page.navigate', { url });

    // Warte auf vollständige Engine-Initialisierung & erstes gerendertes Frame
    const bootStart = Date.now();
    let ready = false;
    while (Date.now() - bootStart < 60000) {
      if (pageErrors.length > 0 && Date.now() - bootStart > 3500) {
        throw new Error(`Boot-Abbruch nach Uncaught Exception:\n  pageErrors: ${pageErrors.join(' | ')}\n  consoleErrors: ${consoleErrors.join(' | ')}`);
      }
      ready = await cdp.eval(`Boolean(
        typeof Arche !== 'undefined' &&
        Arche.QA &&
        typeof runArcheUnitTests === 'function' &&
        typeof renderer !== 'undefined' &&
        renderer.info &&
        renderer.info.render &&
        renderer.info.render.frame >= 2
      )`);
      if (ready) break;
      await new Promise((r) => setTimeout(r, 250));
    }
    if (!ready) throw new Error(`Timeout beim Initialisieren der 3D-Simulation (> 60s). pageErrors=${JSON.stringify(pageErrors)}, consoleErrors=${JSON.stringify(consoleErrors)}`);

    // Onboarding-/Lade-Overlay automatisch schließen, damit 3D-Canvas für Screenshots frei liegt
    await cdp.eval(`(() => {
      const btn = document.getElementById('btn-start-lab');
      if (btn) btn.click();
    })()`);
    await new Promise((r) => setTimeout(r, 500));

    const testRes = await cdp.eval(`(() => {
      const r = runArcheUnitTests();
      const fails = (r.results || []).filter(t => !t.ok).map(t => (t.suite || 'Test') + ': ' + t.name);
      return { passed: r.passedCount, failed: r.failedCount, ms: r.elapsedMs, fails };
    })()`);

    const envInfo = await cdp.eval(`(() => {
      const gl = renderer.getContext();
      const dbg = gl.getExtension('WEBGL_debug_renderer_info');
      const gpu = dbg ? gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER);
      const progs = renderer.info.programs || [];
      let broken = 0;
      for (let i = 0; i < progs.length; i++) {
        const p = progs[i];
        if (p.program && !gl.getProgramParameter(p.program, gl.LINK_STATUS)) broken++;
        else if (p.diagnostics && p.diagnostics.runnable === false) broken++;
      }
      return {
        gpu,
        dpr: renderer.getPixelRatio(),
        canvasW: renderer.domElement.width,
        canvasH: renderer.domElement.height,
        shadowType: renderer.shadowMap.type,
        tier: Arche.Performance ? Arche.Performance.currentTier : -1,
        totalPrograms: progs.length,
        brokenPrograms: broken,
        presets: Arche.QA.list()
      };
    })()`);

    if (XRAY_MODE) {
      // Warte auf asynchrone Blender-Botanik-Hydration (bis zu 20s)
      const hydStart = Date.now();
      let hydState = { forest: false, extra: false };
      while (Date.now() - hydStart < 20000) {
        hydState = await cdp.eval(`(() => {
          const ud = (typeof shipyardGroup !== 'undefined' && shipyardGroup && shipyardGroup.userData) ? shipyardGroup.userData : {};
          return { forest: Boolean(ud.blenderForestHydrated || ud.blenderHydrated), extra: Boolean(ud.blenderExtraHydrated), city: Boolean(ud.mesopotamiaCityHydrated) };
        })()`);
        if (hydState.forest && hydState.extra && hydState.city) break;
        await new Promise((r) => setTimeout(r, 250));
      }

      // Installiere präzisen Frame-/Render-Profiler (hookt rAF + renderer.render im RAM)
      await cdp.eval(`(() => {
        if (window._archeXray) return;
        const origRAF = window.requestAnimationFrame.bind(window);
        const origRender = renderer.render.bind(renderer);
        let frameStart = performance.now();
        let activeRun = null;

        window.requestAnimationFrame = function(cb) {
          return origRAF(function(ts) {
            frameStart = performance.now();
            return cb(ts);
          });
        };

        renderer.render = function(sc, cam) {
          const tR0 = performance.now();
          const cpuBefore = tR0 - frameStart;
          origRender(sc, cam);
          const tR1 = performance.now();
          const renderMs = tR1 - tR0;
          if (activeRun && sc === scene && cam === camera) {
            activeRun.warmup++;
            if (activeRun.warmup > 3) {
              activeRun.samples.push({
                ts: tR1,
                cpuBefore,
                renderMs,
                calls: renderer.info.render.calls,
                tris: renderer.info.render.triangles
              });
            }
          }
        };

        window._archeXray = {
          measure(durationMs = 1400) {
            return new Promise((resolve) => {
              const t0 = performance.now();
              activeRun = { warmup: 0, samples: [] };
              const check = () => {
                if (performance.now() - t0 >= durationMs && activeRun.samples.length >= 10) {
                  const s = activeRun.samples;
                  activeRun = null;
                  const n = s.length;
                  const spanMs = n > 1 ? (s[n - 1].ts - s[0].ts) : durationMs;
                  const fps = n > 1 ? ((n - 1) * 1000) / spanMs : 0;
                  let sumCpu = 0, sumRen = 0, sumCalls = 0, sumTris = 0;
                  for (let i = 0; i < n; i++) {
                    sumCpu += s[i].cpuBefore;
                    sumRen += s[i].renderMs;
                    sumCalls += s[i].calls;
                    sumTris += s[i].tris;
                  }
                  resolve({
                    frames: n,
                    fps: Number(fps.toFixed(2)),
                    frameTimeMs: fps > 0 ? Number((1000 / fps).toFixed(2)) : 0,
                    cpuBeforeMs: Number((sumCpu / n).toFixed(2)),
                    renderDispatchMs: Number((sumRen / n).toFixed(2)),
                    calls: Math.round(sumCalls / n),
                    tris: Math.round(sumTris / n),
                    callsMin: Math.min(...s.map(x => x.calls)),
                    callsMax: Math.max(...s.map(x => x.calls))
                  });
                } else {
                  setTimeout(check, 80);
                }
              };
              setTimeout(check, durationMs);
            });
          },
          inspectSceneTop() {
            const items = [];
            const groups = new Map();
            const isVis = (o) => {
              let cur = o;
              while (cur) { if (!cur.visible) return false; cur = cur.parent; }
              return true;
            };
            const getGroupTag = (o) => {
              let cur = o;
              while (cur && cur !== scene) {
                if (cur.name === 'blender_botany_forest') return 'blender_botany_forest (Bäume)';
                if (cur.name === 'blender_extra_botany') return 'blender_extra_botany (Unterholz/Zier)';
                if (cur.userData && cur.userData.tooltipKey === 'land_shipyard_city') return 'Ur-Schinar / bronzeCityGroup';
                if (cur.userData && cur.userData.tooltipKey) return 'grp:' + cur.userData.tooltipKey;
                if (cur.name) return 'grp:' + cur.name;
                cur = cur.parent;
              }
              return o.name || o.type || 'unnamed';
            };
            scene.traverse((obj) => {
              if (!obj.geometry || (!obj.isMesh && !obj.isInstancedMesh && !obj.isPoints && !obj.isLine)) return;
              if (!isVis(obj)) return;
              const inst = obj.isInstancedMesh ? obj.count : 1;
              if (inst <= 0) return;
              const geo = obj.geometry;
              const baseTris = geo.index ? (geo.index.count / 3) : (geo.attributes.position ? geo.attributes.position.count / 3 : 0);
              const totalTris = Math.round(baseTris * inst);
              const callsPerPass = (geo.groups && geo.groups.length > 0 && Array.isArray(obj.material)) ? geo.groups.length : 1;
              const shadowFactor = (obj.castShadow && typeof sunLight !== 'undefined' && sunLight.castShadow) ? 2 : 1;
              const estCalls = callsPerPass * shadowFactor;
              const tag = getGroupTag(obj);
              items.push({
                name: obj.name || '(unnamed)',
                type: obj.isInstancedMesh ? 'InstancedMesh' : obj.type,
                group: tag,
                meshes: 1,
                instances: inst,
                tris: totalTris,
                callsPerPass,
                castShadow: Boolean(obj.castShadow)
              });
              if (!groups.has(tag)) {
                groups.set(tag, { name: tag, type: 'Group', meshes: 0, instances: 0, tris: 0, callsPerPass: 0, shadowMeshes: 0 });
              }
              const g = groups.get(tag);
              g.meshes += 1;
              g.instances += inst;
              g.tris += totalTris;
              g.callsPerPass += callsPerPass;
              if (obj.castShadow) g.shadowMeshes += 1;
            });
            const grpList = Array.from(groups.values());
            const topGroupsByCalls = [...grpList].sort((a, b) => b.callsPerPass - a.callsPerPass).slice(0, 10);
            const topGroupsByTris = [...grpList].sort((a, b) => b.tris - a.tris).slice(0, 10);
            const topMeshesByTris = [...items].sort((a, b) => b.tris - a.tris).slice(0, 10);
            return { topGroupsByCalls, topGroupsByTris, topMeshesByTris, totalActiveMeshes: items.length };
          }
        };
      })()`);

      console.log(`=== ARCHÉ PERFORMANCE-RÖNTGENBLICK (Hydration: forest=${hydState.forest}, extra=${hydState.extra}) ===`);
      console.log(`GPU: ${envInfo.gpu}`);
      console.log(`Renderer: DPR=${envInfo.dpr} (${envInfo.canvasW}x${envInfo.canvasH}) | Tier=${envInfo.tier} | ShadowType=${envInfo.shadowType}`);
      console.log('');

      // 1. CPU vs. GPU Split auf shipyard, ur_city, botany_close, overview
      const xrayPresets = ['shipyard', 'ur_city', 'botany_close', 'overview'];
      console.log('--- 1. CPU vs. GPU Split ---');
      console.log('Preset           |    FPS | Frame(ms) | CPU_Update(ms) | RenderDispatch(ms) | Rest/GPU(ms) | Calls (min-max) |      Tris');
      for (const p of xrayPresets) {
        await cdp.eval(`Arche.QA.go(${JSON.stringify(p)})`);
        await new Promise((r) => setTimeout(r, 500));
        const m = await cdp.eval(`window._archeXray.measure(1400)`);
        const restMs = Math.max(0, m.frameTimeMs - m.cpuBeforeMs - m.renderDispatchMs).toFixed(2);
        console.log(
          `${p.padEnd(16)} | ${String(m.fps).padStart(6)} | ${String(m.frameTimeMs).padStart(9)} | ${String(m.cpuBeforeMs).padStart(14)} | ${String(m.renderDispatchMs).padStart(18)} | ${String(restMs).padStart(12)} | ${String(m.calls).padStart(5)} (${m.callsMin}-${m.callsMax}) | ${String(m.tris).padStart(9)}`
        );
      }
      console.log('');

      // 2. Botanik- & Shadow-A/B-Messung auf overview & botany_close
      console.log('--- 2. Botanik- & Shadow-A/B-Messung ---');
      for (const p of ['overview', 'botany_close']) {
        await cdp.eval(`Arche.QA.go(${JSON.stringify(p)})`);
        await new Promise((r) => setTimeout(r, 500));
        console.log(`[Preset: ${p}]`);
        console.log('Variante                              |    FPS | Frame(ms) | CPU_Upd | Render | Calls |      Tris');
        const variants = [
          {
            label: 'Baseline (alles an)',
            setup: `(() => {})()`,
            restore: `(() => {})()`
          },
          {
            label: 'Ohne Schatten (castShadow=false)',
            setup: `(() => { window._xrayPrevShadow = sunLight.castShadow; sunLight.castShadow = false; })()`,
            restore: `(() => { sunLight.castShadow = window._xrayPrevShadow; })()`
          },
          {
            label: 'Ohne Blender-Botanik (forest+extra)',
            setup: `(() => {
              window._xrayHiddenBot = [];
              ['blender_botany_forest', 'blender_extra_botany'].forEach(n => {
                const o = scene.getObjectByName(n);
                if (o) { window._xrayHiddenBot.push([o, o.visible]); o.visible = false; }
              });
            })()`,
            restore: `(() => {
              (window._xrayHiddenBot || []).forEach(([o, v]) => { o.visible = v; });
            })()`
          },
          {
            label: 'Ohne Stadt Ur-Schinar',
            setup: `(() => {
              window._xrayHiddenCity = [];
              scene.traverse(o => {
                if (o.userData && o.userData.tooltipKey === 'land_shipyard_city') {
                  window._xrayHiddenCity.push([o, o.visible]);
                  o.visible = false;
                }
              });
            })()`,
            restore: `(() => {
              (window._xrayHiddenCity || []).forEach(([o, v]) => { o.visible = v; });
            })()`
          }
        ];
        for (const v of variants) {
          await cdp.eval(v.setup);
          await new Promise((r) => setTimeout(r, 250));
          const m = await cdp.eval(`window._archeXray.measure(1200)`);
          await cdp.eval(v.restore);
          console.log(
            `${v.label.padEnd(37)} | ${String(m.fps).padStart(6)} | ${String(m.frameTimeMs).padStart(9)} | ${String(m.cpuBeforeMs).padStart(7)} | ${String(m.renderDispatchMs).padStart(6)} | ${String(m.calls).padStart(5)} | ${String(m.tris).padStart(9)}`
          );
        }
        console.log('');
      }

      // 3. Draw-Call-Hitliste (Top 10 auf overview)
      await cdp.eval(`Arche.QA.go('overview')`);
      await new Promise((r) => setTimeout(r, 400));
      const top = await cdp.eval(`window._archeXray.inspectSceneTop()`);
      console.log(`--- 3. Draw-Call-Hitliste (Szenen-Snapshot: ${top.totalActiveMeshes} aktive sichtbare Meshes) ---`);
      console.log('Top-10 Gruppen nach Draw-Calls (pro Render-Pass):');
      top.topGroupsByCalls.forEach((g, idx) => {
        console.log(`  ${String(idx + 1).padStart(2)}. ${g.name.padEnd(38)} | Meshes=${String(g.meshes).padStart(4)} | Calls/Pass=${String(g.callsPerPass).padStart(4)} (ShadowMeshes=${g.shadowMeshes}) | Inst=${String(g.instances).padStart(6)} | Tris=${g.tris}`);
      });
      console.log('\nTop-10 Gruppen nach Triangles:');
      top.topGroupsByTris.forEach((g, idx) => {
        console.log(`  ${String(idx + 1).padStart(2)}. ${g.name.padEnd(38)} | Meshes=${String(g.meshes).padStart(4)} | Calls/Pass=${String(g.callsPerPass).padStart(4)} | Inst=${String(g.instances).padStart(6)} | Tris=${g.tris}`);
      });
      console.log('\nTop-10 Einzel-Meshes / InstancedMeshes nach Triangles:');
      top.topMeshesByTris.forEach((m, idx) => {
        console.log(`  ${String(idx + 1).padStart(2)}. ${m.name.padEnd(38)} | ${m.type.padEnd(13)} | Group=${m.group} | Inst=${String(m.instances).padStart(5)} | Tris=${m.tris} | CastShadow=${m.castShadow}`);
      });
      return;
    }

    // Warte kurz auf asynchrone Blender-Botanik-Hydration + ersten Render-Warmup, bevor Benchmarks laufen
    const preHydStart = Date.now();
    while (Date.now() - preHydStart < 15000) {
      const hs = await cdp.eval(`(() => {
        const ud = (typeof shipyardGroup !== 'undefined' && shipyardGroup && shipyardGroup.userData) ? shipyardGroup.userData : {};
        return Boolean((ud.blenderForestHydrated || ud.blenderHydrated) && ud.blenderExtraHydrated && ud.mesopotamiaCityHydrated && ud.shipyardIndustryHydrated);
      })()`);
      if (hs) break;
      await new Promise((r) => setTimeout(r, 200));
    }

    const quickSet = ['shipyard', 'aqueduct', 'overview'];
    const criticSet = ['shipyard', 'botany_close', 'ark_interior', 'ararat_altar', 'storm_ocean', 'overview'];
    let targetPresets = envInfo.presets;
    if (QUICK_MODE && CRITIC_MODE) {
      targetPresets = [...new Set([...quickSet, ...criticSet])].filter((n) => envInfo.presets.includes(n));
    } else if (QUICK_MODE) {
      targetPresets = quickSet.filter((n) => envInfo.presets.includes(n));
    } else if (CRITIC_MODE) {
      targetPresets = criticSet.filter((n) => envInfo.presets.includes(n));
    }

    const generatedShots = [];
    const sanityFails = [];
    const viewStats = [];
    const measureViewMetrics = async (durationMs = 650) => cdp.eval(`new Promise(resolve => {
      const origRender = renderer.render.bind(renderer);
      let renSum = 0, renCount = 0;
      renderer.render = function(sc, cam) {
        const tA = performance.now();
        origRender(sc, cam);
        if (sc === scene && cam === camera) { renSum += (performance.now() - tA); renCount++; }
      };
      const t0 = performance.now();
      let frames = 0;
      function tick(now) {
        frames++;
        if (now - t0 >= ${durationMs}) {
          renderer.render = origRender;
          resolve({
            fps: Number(((frames * 1000) / (now - t0)).toFixed(2)),
            renderDispatchMs: renCount > 0 ? Number((renSum / renCount).toFixed(2)) : 0,
            calls: renderer.info.render.calls,
            tris: renderer.info.render.triangles
          });
        } else {
          requestAnimationFrame(tick);
        }
      }
      requestAnimationFrame(tick);
    })`);
    for (const preset of targetPresets) {
      await cdp.eval(`Arche.QA.go(${JSON.stringify(preset)})`);
      await new Promise((r) => setTimeout(r, 350));
      const metrics = await measureViewMetrics(650);

      let shotRel = null;
      let sanity = null;
      if (!NO_SHOTS) {
        const shot = await cdp.send('Page.captureScreenshot', { format: 'png' });
        const pngBuf = Buffer.from(shot.data, 'base64');
        shotRel = path.join('scratch', `qa_${preset}.png`);
        fs.writeFileSync(path.join(__dirname, shotRel), pngBuf);
        sanity = checkPngSanity(pngBuf, shotRel);
        generatedShots.push({ rel: shotRel.replace(/\\/g, '/'), ...sanity });
        if (!sanity.ok) sanityFails.push(`${shotRel}: ${sanity.reason}`);
      }
      viewStats.push({ preset, ...metrics, shotRel, sanity });
    }

    // Real-Desktop-Check: 1920x1080 @ DPR 1.25 auf 'shipyard' (Arche + Karawane + Werft)
    let realDesktopReport = null;
    if (!XRAY_MODE) {
      await cdp.send('Emulation.setDeviceMetricsOverride', {
        width: 1920, height: 1080, deviceScaleFactor: 1.25, mobile: false
      });
      await new Promise((r) => setTimeout(r, 250));
      await cdp.eval(`Arche.QA.go('shipyard')`);
      await new Promise((r) => setTimeout(r, 400));
      const rdInfo = await cdp.eval(`({
        w: window.innerWidth, h: window.innerHeight,
        dpr: renderer.getPixelRatio(),
        cw: renderer.domElement.width, ch: renderer.domElement.height
      })`);
      const rdMetrics = await measureViewMetrics(900);
      realDesktopReport = { ...rdInfo, ...rdMetrics };
      await cdp.send('Emulation.setDeviceMetricsOverride', {
        width: 1440, height: 900, deviceScaleFactor: 0, mobile: false
      });
    }

    let ipadReport = null;
    if (IPAD_MODE) {
      inDesktopPhase = false;
      const ipadConsoleErrors = [];
      const ipadPageErrors = [];
      let inIpadPhase = true;
      cdp.on('Runtime.consoleAPICalled', (p) => {
        if (!inIpadPhase) return;
        if (p.type === 'error') {
          const text = (p.args || []).map((a) => a.value ?? a.description ?? '').join(' ');
          if (!text.includes('__TEST_RESULTS__')) ipadConsoleErrors.push(text);
        }
      });
      cdp.on('Runtime.exceptionThrown', (p) => {
        if (!inIpadPhase) return;
        ipadPageErrors.push(p.exceptionDetails?.exception?.description || p.exceptionDetails?.text || 'Uncaught exception');
      });

      await cdp.send('Emulation.setUserAgentOverride', { userAgent: IPAD_UA, platform: 'iPad' });
      await cdp.send('Emulation.setDeviceMetricsOverride', {
        width: 1024, height: 768, deviceScaleFactor: 2, mobile: true
      });
      await cdp.send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 5 });

      const ipadUrl = `http://127.0.0.1:${httpPort}/${encodeURIComponent(HTML_FILE)}?v=qa_ipad_${Date.now()}`;
      await cdp.send('Page.navigate', { url: ipadUrl });

      const ipadBootStart = Date.now();
      let ipadReady = false;
      while (Date.now() - ipadBootStart < 60000) {
        if (ipadPageErrors.length > 0 && Date.now() - ipadBootStart > 3500) {
          throw new Error(`iPad-Boot-Abbruch nach Uncaught Exception:\n  pageErrors: ${ipadPageErrors.join(' | ')}\n  consoleErrors: ${ipadConsoleErrors.join(' | ')}`);
        }
        ipadReady = await cdp.eval(`Boolean(
          typeof Arche !== 'undefined' &&
          Arche.QA &&
          typeof renderer !== 'undefined' &&
          renderer.info &&
          renderer.info.render &&
          renderer.info.render.frame >= 2
        )`);
        if (ipadReady) break;
        await new Promise((r) => setTimeout(r, 250));
      }
      if (!ipadReady) throw new Error(`Timeout beim iPad-Boot (> 60s). pageErrors=${JSON.stringify(ipadPageErrors)}`);

      await cdp.eval(`(() => {
        const btn = document.getElementById('btn-start-lab');
        if (btn) btn.click();
        if (typeof Arche !== 'undefined' && Arche.QA) Arche.QA.go('shipyard');
      })()`);
      const ipadHydStart = Date.now();
      while (Date.now() - ipadHydStart < 12000) {
        const hs = await cdp.eval(`(() => {
          const ud = (typeof shipyardGroup !== 'undefined' && shipyardGroup && shipyardGroup.userData) ? shipyardGroup.userData : {};
          return Boolean((ud.blenderForestHydrated || ud.blenderHydrated) && ud.mesopotamiaCityHydrated && ud.shipyardIndustryHydrated);
        })()`);
        if (hs) break;
        await new Promise((r) => setTimeout(r, 200));
      }
      await new Promise((r) => setTimeout(r, 500));

      const ipadCheck = await cdp.eval(`(() => {
        const gl = renderer.getContext();
        const progs = renderer.info.programs || [];
        let broken = 0;
        for (let i = 0; i < progs.length; i++) {
          const p = progs[i];
          if (p.program && !gl.getProgramParameter(p.program, gl.LINK_STATUS)) broken++;
          else if (p.diagnostics && p.diagnostics.runnable === false) broken++;
        }
        const dc = (Arche.Performance && Arche.Performance.getDeviceClass) ? Arche.Performance.getDeviceClass() : null;
        const detectedTier = (Arche.Performance && Arche.Performance.detectInitialTier) ? Arche.Performance.detectInitialTier() : -1;
        const currentTier = Arche.Performance ? Arche.Performance.currentTier : -1;

        const selectors = ['#telemetry-panel', '.lil-gui.root', '#legend-panel', '#mobile-cam-dpad'];
        const rects = [];
        const outOfBounds = [];
        for (const sel of selectors) {
          const el = document.querySelector(sel);
          if (!el) continue;
          const st = getComputedStyle(el);
          if (st.display === 'none' || st.visibility === 'hidden' || Number(st.opacity) === 0) continue;
          const r = el.getBoundingClientRect();
          if (r.width <= 1 || r.height <= 1) continue;
          const box = { sel, left: Math.round(r.left), top: Math.round(r.top), right: Math.round(r.right), bottom: Math.round(r.bottom), w: Math.round(r.width), h: Math.round(r.height) };
          rects.push(box);
          if (r.left < -2 || r.top < -2 || r.right > window.innerWidth + 2 || r.bottom > window.innerHeight + 2) {
            outOfBounds.push(box);
          }
        }
        const overlaps = [];
        for (let i = 0; i < rects.length; i++) {
          for (let j = i + 1; j < rects.length; j++) {
            const a = rects[i], b = rects[j];
            const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left);
            const oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
            if (ox > 2 && oy > 2) {
              overlaps.push({ a: a.sel, b: b.sel, ox: Math.round(ox), oy: Math.round(oy) });
            }
          }
        }
        return {
          innerW: window.innerWidth,
          innerH: window.innerHeight,
          dpr: renderer.getPixelRatio(),
          canvasW: renderer.domElement.width,
          canvasH: renderer.domElement.height,
          detectedTier,
          currentTier,
          isTablet: Boolean(dc && dc.isTablet),
          isPhone: Boolean(dc && dc.isPhone),
          touchPts: dc ? dc.touchPts : 0,
          tabletCompact: document.body.classList.contains('tablet-hud-compact'),
          brokenPrograms: broken,
          totalPrograms: progs.length,
          visiblePanels: rects.map(r => r.sel),
          overlaps,
          outOfBounds
        };
      })()`);

      const ipadMetrics = await cdp.eval(`new Promise(resolve => {
        const t0 = performance.now();
        let frames = 0;
        function tick(now) {
          frames++;
          if (now - t0 >= 650) {
            resolve({
              fps: Number(((frames * 1000) / (now - t0)).toFixed(2)),
              calls: renderer.info.render.calls,
              tris: renderer.info.render.triangles
            });
          } else {
            requestAnimationFrame(tick);
          }
        }
        requestAnimationFrame(tick);
      })`);

      let ipadShotRel = null;
      let ipadSanity = null;
      if (!NO_SHOTS) {
        const shot = await cdp.send('Page.captureScreenshot', { format: 'png' });
        const pngBuf = Buffer.from(shot.data, 'base64');
        ipadShotRel = path.join('scratch', 'qa_ipad.png');
        fs.writeFileSync(path.join(__dirname, ipadShotRel), pngBuf);
        ipadSanity = checkPngSanity(pngBuf, ipadShotRel);
        generatedShots.push({ rel: ipadShotRel.replace(/\\/g, '/'), ...ipadSanity });
        if (!ipadSanity.ok) sanityFails.push(`${ipadShotRel}: ${ipadSanity.reason}`);
      }
      inIpadPhase = false;
      ipadReport = {
        ...ipadCheck,
        ...ipadMetrics,
        consoleErrors: ipadConsoleErrors,
        pageErrors: ipadPageErrors,
        shotRel: ipadShotRel,
        sanity: ipadSanity
      };
    }

    console.log(`GPU: ${envInfo.gpu}`);
    console.log(`Renderer: DPR=${envInfo.dpr} (${envInfo.canvasW}x${envInfo.canvasH}) | Tier=${envInfo.tier} | ShadowType=${envInfo.shadowType}`);
    console.log(`Shaders: ${envInfo.totalPrograms} Programme, ${envInfo.brokenPrograms} fehlerhaft`);
    console.log(`Errors: console=${consoleErrors.length}, page=${pageErrors.length}`);
    if (consoleErrors.length) console.error('Console-Errors:', consoleErrors);
    if (pageErrors.length) console.error('Page-Errors:', pageErrors);
    console.log(`Unit-Tests: ${testRes.passed} / ${testRes.passed + testRes.failed} PASS (${testRes.ms.toFixed(1)} ms)`);
    if (testRes.fails.length) console.error('Fehlgeschlagene Tests:', testRes.fails);
    for (const v of viewStats) {
      const sanStr = v.sanity ? ` | ${v.sanity.ok ? 'IMG_OK' : 'IMG_FAIL'} (${(v.sanity.bytes / 1024).toFixed(1)} KB, ${v.sanity.width}x${v.sanity.height})` : '';
      const dispStr = (v.renderDispatchMs !== undefined) ? ` | dispatch=${v.renderDispatchMs}ms` : '';
      console.log(`  - ${v.preset.padEnd(16)}: ${String(v.fps).padStart(6)} FPS | calls=${v.calls} | tris=${v.tris}${dispStr}${v.shotRel ? ' | ' + v.shotRel : ''}${sanStr}`);
    }
    if (realDesktopReport) {
      console.log(`Real-Desktop (${realDesktopReport.w}x${realDesktopReport.h}, DPR=${realDesktopReport.dpr} -> ${realDesktopReport.cw}x${realDesktopReport.ch}, shipyard): ${realDesktopReport.fps} FPS | calls=${realDesktopReport.calls} | tris=${realDesktopReport.tris} | dispatch=${realDesktopReport.renderDispatchMs}ms`);
    }

    if (ipadReport) {
      console.log(`iPad-Emulation (${ipadReport.innerW}x${ipadReport.innerH}, DPR=${ipadReport.dpr}, canvas=${ipadReport.canvasW}x${ipadReport.canvasH}):`);
      console.log(`  - detectInitialTier=${ipadReport.detectedTier} | currentTier=${ipadReport.currentTier} | isTablet=${ipadReport.isTablet} | tabletCompact=${ipadReport.tabletCompact} | touchPts=${ipadReport.touchPts}`);
      console.log(`  - Shaders=${ipadReport.totalPrograms} (${ipadReport.brokenPrograms} fehlerhaft) | Errors: console=${ipadReport.consoleErrors.length}, page=${ipadReport.pageErrors.length}`);
      console.log(`  - Touch-UI Panels=[${ipadReport.visiblePanels.join(', ')}] | Overlaps=${ipadReport.overlaps.length} | OutOfBounds=${ipadReport.outOfBounds.length}`);
      if (ipadReport.overlaps.length) console.error('  - iPad Overlaps:', ipadReport.overlaps);
      if (ipadReport.outOfBounds.length) console.error('  - iPad OutOfBounds:', ipadReport.outOfBounds);
      if (ipadReport.consoleErrors.length) console.error('  - iPad Console-Errors:', ipadReport.consoleErrors);
      if (ipadReport.pageErrors.length) console.error('  - iPad Page-Errors:', ipadReport.pageErrors);
      const ipadSanStr = ipadReport.sanity ? ` | ${ipadReport.sanity.ok ? 'IMG_OK' : 'IMG_FAIL'} (${(ipadReport.sanity.bytes / 1024).toFixed(1)} KB, ${ipadReport.sanity.width}x${ipadReport.sanity.height})` : '';
      console.log(`  - iPad FPS=${ipadReport.fps} | calls=${ipadReport.calls} | tris=${ipadReport.tris}${ipadReport.shotRel ? ' | ' + ipadReport.shotRel : ''}${ipadSanStr}`);
    }

    if (sanityFails.length) {
      console.error('Bild-Sanity-Check FEHLGESCHLAGEN:', sanityFails);
    }

    const previewDir = path.join(__dirname, 'assets', 'previews');
    const previewShots = fs.existsSync(previewDir)
      ? fs.readdirSync(previewDir).filter((f) => f.toLowerCase().endsWith('.png')).sort().map((f) => `assets/previews/${f}`)
      : [];

    if (!NO_SHOTS || previewShots.length > 0) {
      console.log('\nVisual Critic Prüfliste (rules/visual-critic.md):');
      for (const s of generatedShots) {
        console.log(`  [LIVE]    ${s.rel} (${(s.bytes / 1024).toFixed(1)} KB, ${s.width}x${s.height}) -> ${s.ok ? 'SANITY_OK' : 'SANITY_FAIL'}`);
      }
      for (const p of previewShots) {
        const st = fs.statSync(path.join(__dirname, p));
        console.log(`  [PREVIEW] ${p} (${(st.size / 1024).toFixed(1)} KB)`);
      }
    }

    const ipadOk = !ipadReport || (
      ipadReport.detectedTier === 2 &&
      ipadReport.isTablet &&
      ipadReport.brokenPrograms === 0 &&
      ipadReport.consoleErrors.length === 0 &&
      ipadReport.pageErrors.length === 0 &&
      ipadReport.overlaps.length === 0 &&
      ipadReport.outOfBounds.length === 0
    );

    const ok = testRes.failed === 0 &&
      consoleErrors.length === 0 &&
      pageErrors.length === 0 &&
      envInfo.brokenPrograms === 0 &&
      sanityFails.length === 0 &&
      ipadOk;
    if (!ok) {
      console.error('QA_ARCHE_FAIL');
      process.exitCode = 1;
    } else {
      console.log('QA_ARCHE_PASS');
    }
  } finally {
    if (cdp) cdp.close();
    if (chromeProc && !chromeProc.killed) {
      try { chromeProc.kill('SIGKILL'); } catch (_) {}
    }
    await new Promise((r) => server.close(r));
    try { fs.rmSync(tmpProfile, { recursive: true, force: true }); } catch (_) {}
  }
}

run().catch((err) => {
  console.error('QA_ARCHE_ERROR:', err);
  process.exit(1);
});

