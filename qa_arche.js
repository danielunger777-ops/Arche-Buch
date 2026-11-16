/**
 * qa_arche.js — Automatisierter Ein-Befehl-Browser-QA-Runner (Zero-Dependency CDP)
 * Startet lokalen HTTP-Server + Headless Chrome (1440x900, WebGL/ANGLE),
 * führt T01–T101 aus, prüft Console-/Page-/WebGL-Shader-Fehler, misst FPS
 * pro Arche.QA-Preset und speichert PNG-Screenshots nach scratch/.
 *
 * Aufruf:
 *   node qa_arche.js              # Alle Arche.QA-Presets (oder Standard-Set)
 *   node qa_arche.js --quick      # Nur shipyard, aqueduct, overview
 *   node qa_arche.js --no-shots   # Nur Tests, Shader & FPS ohne PNGs
 */
const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { spawn } = require('child_process');

const args = process.argv.slice(2);
const QUICK_MODE = args.includes('--quick');
const NO_SHOTS = args.includes('--no-shots');
const HTML_FILE = 'Arche Simulation 3.0.html';
const SCRATCH_DIR = path.join(__dirname, 'scratch');

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
    cdp.on('Runtime.consoleAPICalled', (p) => {
      if (p.type === 'error') {
        const text = (p.args || []).map((a) => a.value ?? a.description ?? '').join(' ');
        if (!text.includes('__TEST_RESULTS__')) consoleErrors.push(text);
      }
    });
    cdp.on('Runtime.exceptionThrown', (p) => {
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

    const targetPresets = QUICK_MODE
      ? ['shipyard', 'aqueduct', 'overview'].filter((n) => envInfo.presets.includes(n))
      : envInfo.presets;

    const viewStats = [];
    for (const preset of targetPresets) {
      await cdp.eval(`Arche.QA.go(${JSON.stringify(preset)})`);
      await new Promise((r) => setTimeout(r, 300));
      const metrics = await cdp.eval(`new Promise(resolve => {
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

      let shotRel = null;
      if (!NO_SHOTS) {
        const shot = await cdp.send('Page.captureScreenshot', { format: 'png' });
        shotRel = path.join('scratch', `qa_${preset}.png`);
        fs.writeFileSync(path.join(__dirname, shotRel), Buffer.from(shot.data, 'base64'));
      }
      viewStats.push({ preset, ...metrics, shotRel });
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
      console.log(`  - ${v.preset.padEnd(12)}: ${String(v.fps).padStart(6)} FPS | calls=${v.calls} | tris=${v.tris}${v.shotRel ? ' | ' + v.shotRel : ''}`);
    }

    const ok = testRes.failed === 0 && consoleErrors.length === 0 && pageErrors.length === 0 && envInfo.brokenPrograms === 0;
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

