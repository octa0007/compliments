/* ════════════════════════════════════════════════════════════
   Sana Özel — uygulama mantığı
   ════════════════════════════════════════════════════════════ */

const $  = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];

const TR_M = ['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık'];
const TR_D = ['Pazar','Pazartesi','Salı','Çarşamba','Perşembe','Cuma','Cumartesi'];
const DAY  = 86400000;

/* ─── günün seçimi ──────────────────────────────────────────
   send_compliment.py ile birebir aynı formül. Bir yıl boyunca
   hiçbir iltifat tekrar etmez; sıra her yıl değişir.          */
function gcd(a, b) { while (b) { [a, b] = [b, a % b]; } return a; }

function pickIndex(d, len) {
  const n    = Math.floor(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()) / DAY);
  const year = d.getFullYear();
  let step = (year * 7919) % len;
  if (step === 0) step = 1;
  while (gcd(step, len) !== 1) step = (step + 1) % len || 1;
  const offset = (year * 104729) % len;
  return (step * n + offset) % len;
}

const dayText = d => COMPLIMENTS[pickIndex(d, COMPLIMENTS.length)].t;
const fmtDate = d => `${TR_D[d.getDay()]}, ${d.getDate()} ${TR_M[d.getMonth()]} ${d.getFullYear()}`;

/* ─── selamlama ─────────────────────────────────────────── */
function salutation() {
  const h = new Date().getHours();
  if (h < 6)  return 'Gecenin bir yarısı';
  if (h < 12) return 'Günaydın';
  if (h < 18) return 'İyi günler';
  if (h < 22) return 'İyi akşamlar';
  return 'İyi geceler';
}

/* ─── ay evresi ─────────────────────────────────────────── */
const SYNODIC = 29.530588853;
function moonPhase(d) {
  const ref = Date.UTC(2000, 0, 6, 18, 14);
  return ((((d - ref) / DAY) % SYNODIC) + SYNODIC) % SYNODIC / SYNODIC;   // 0 yeni ay, .5 dolunay
}
function moonName(p) {
  const a = p * SYNODIC;
  if (a < 1.85)  return 'Yeni Ay';
  if (a < 7.38)  return 'Büyüyen Hilal';
  if (a < 9.22)  return 'İlk Dördün';
  if (a < 14.77) return 'Büyüyen Ay';
  if (a < 16.61) return 'Dolunay';
  if (a < 22.15) return 'Azalan Ay';
  if (a < 23.99) return 'Son Dördün';
  return 'Azalan Hilal';
}
/* aydınlık kısmın yolu — gerçek terminatör geometrisi */
function litPath(R, p) {
  const x   = Math.cos(2 * Math.PI * p);
  const rx  = Math.abs(x) * R;
  const dir = p < 0.5 ? 1 : 0;                 // büyürken sağ taraf aydınlık
  const inn = x > 0 ? 1 - dir : dir;
  return `M 0 ${-R} A ${R} ${R} 0 0 ${dir} 0 ${R} A ${rx.toFixed(2)} ${R} 0 0 ${inn} 0 ${-R} Z`;
}

/* ─── Çin burcu ─────────────────────────────────────────── */
function chineseZodiac(y) {
  const animals  = ['Fare','Öküz','Kaplan','Tavşan','Ejderha','Yılan','At','Koyun','Maymun','Horoz','Köpek','Domuz'];
  const elements = ['Metal','Metal','Su','Su','Ağaç','Ağaç','Ateş','Ateş','Toprak','Toprak'];
  const mod = (a, m) => ((a % m) + m) % m;
  return { name: animals[mod(y - 1900, 12)], element: elements[mod(y - 1900, 10)] };
}

/* ─── yıllık tekrar eden tarihe kalan gün ───────────────── */
function nextAnnual(iso, now) {
  const [y, m, d] = iso.split('-').map(Number);
  let next = new Date(now.getFullYear(), m - 1, d);
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const isToday = next.getTime() === today.getTime();
  if (next < today) next = new Date(now.getFullYear() + 1, m - 1, d);
  return { isToday, days: Math.round((next - today) / DAY), n: next.getFullYear() - y, next };
}

/* ─── kısa bildirim ─────────────────────────────────────── */
let toastTimer;
function toast(msg) {
  const el = $('#toast');
  el.textContent = msg;
  el.classList.add('up');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('up'), 2600);
}

/* ─── daktilo ───────────────────────────────────────────── */
function typeOut(el, text) {
  el.innerHTML = '';
  const span  = document.createElement('span');
  const caret = document.createElement('i');
  caret.className = 'caret';
  el.append(span, caret);

  if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
    span.textContent = text; caret.remove(); return;
  }
  let i = 0;
  const speed = text.length > 90 ? 20 : 27;
  const tick = setInterval(() => {
    span.textContent = text.slice(0, ++i);
    if (i >= text.length) { clearInterval(tick); setTimeout(() => caret.remove(), 700); }
  }, speed);
}

/* ─── gece göğü ─────────────────────────────────────────── */
function startSky() {
  const cv = $('#sky'), ctx = cv.getContext('2d');
  const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let W, H, dpr, stars = [], petals = [], shoot = null, next = 6000;

  const resize = () => {
    dpr = Math.min(devicePixelRatio || 1, 2);
    W = cv.width  = innerWidth  * dpr;
    H = cv.height = innerHeight * dpr;
    cv.style.width = innerWidth + 'px';
    cv.style.height = innerHeight + 'px';
  };
  addEventListener('resize', resize, { passive: true });
  resize();

  for (let i = 0; i < 150; i++) stars.push({
    x: Math.random(), y: Math.random(),
    r: Math.random() < .14 ? 1.5 : Math.random() * .8 + .35,
    a: Math.random(), s: .002 + Math.random() * .005,
    d: Math.random() > .5 ? 1 : -1,
    warm: Math.random() < .3
  });

  /* kaydedilen iltifatlarda dökülen gül yaprakları */
  window.petalBurst = (x, y) => {
    if (calm) return;
    for (let i = 0; i < 22; i++) petals.push({
      x: x * dpr, y: y * dpr,
      vx: (Math.random() - .5) * 3.4 * dpr,
      vy: (Math.random() * -2.6 - .4) * dpr,
      r: (3 + Math.random() * 4) * dpr,
      rot: Math.random() * 6.28, vr: (Math.random() - .5) * .18,
      life: 1
    });
  };

  let last = performance.now();
  (function frame(now) {
    const dt = Math.min((now - last) / 16.7, 3); last = now;
    ctx.clearRect(0, 0, W, H);

    for (const s of stars) {
      if (!calm) { s.a += s.s * s.d * dt; if (s.a > .9) s.d = -1; if (s.a < .06) s.d = 1; }
      ctx.globalAlpha = s.a;
      ctx.fillStyle = s.warm ? '#e7ce8c' : '#ffffff';
      ctx.beginPath(); ctx.arc(s.x * W, s.y * H, s.r * dpr, 0, 6.2832); ctx.fill();
    }

    if (!calm) {
      next -= dt * 16.7;
      if (next <= 0 && !shoot) {
        shoot = { x: Math.random() * W * .7, y: Math.random() * H * .35, len: 0, life: 1 };
        next = 14000 + Math.random() * 22000;
      }
      if (shoot) {
        shoot.x += 6 * dpr * dt; shoot.y += 2.4 * dpr * dt;
        shoot.len = Math.min(shoot.len + 7 * dpr * dt, 130 * dpr);
        shoot.life -= .012 * dt;
        const g = ctx.createLinearGradient(shoot.x, shoot.y, shoot.x - shoot.len, shoot.y - shoot.len * .4);
        g.addColorStop(0, `rgba(255,255,255,${Math.max(shoot.life, 0)})`);
        g.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.globalAlpha = 1; ctx.strokeStyle = g; ctx.lineWidth = 1.4 * dpr;
        ctx.beginPath(); ctx.moveTo(shoot.x, shoot.y);
        ctx.lineTo(shoot.x - shoot.len, shoot.y - shoot.len * .4); ctx.stroke();
        if (shoot.life <= 0) shoot = null;
      }
    }

    for (let i = petals.length - 1; i >= 0; i--) {
      const p = petals[i];
      p.vy += .07 * dpr * dt; p.x += p.vx * dt; p.y += p.vy * dt;
      p.rot += p.vr * dt; p.life -= .009 * dt;
      if (p.life <= 0 || p.y > H + 40) { petals.splice(i, 1); continue; }
      ctx.globalAlpha = Math.max(p.life, 0) * .9;
      ctx.fillStyle = ['#a3384f', '#d98ba0', '#c8a24c'][i % 3];
      ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.rot);
      ctx.beginPath(); ctx.ellipse(0, 0, p.r, p.r * .55, 0, 0, 6.2832); ctx.fill();
      ctx.restore();
    }

    ctx.globalAlpha = 1;
    requestAnimationFrame(frame);
  })(last);
}

/* ─── kavanoz (localStorage) ────────────────────────────── */
const JAR = 'kavanoz.v2';
const jarRead  = () => { try { return JSON.parse(localStorage.getItem(JAR)) || []; } catch { return []; } };
const jarWrite = v => { try { localStorage.setItem(JAR, JSON.stringify(v)); } catch {} };

function renderJar() {
  const box = $('#jar'), items = jarRead();
  $('#jar-count').textContent = items.length ? `${items.length} not` : '';
  if (!items.length) {
    box.innerHTML = '<p class="jar-note">Kavanoz henüz boş. Beğendiğin bir cümleyi “Kavanoza koy” ile buraya saklayabilirsin.</p>';
    return;
  }
  box.innerHTML = '';
  items.slice().reverse().forEach(it => {
    const row = document.createElement('article');
    row.className = 'jar-item';
    const p = document.createElement('p');
    p.textContent = '“' + it.t + '”';
    const time = document.createElement('time');
    time.textContent = fmtDate(new Date(it.d));
    p.appendChild(time);
    const del = document.createElement('button');
    del.className = 'jar-drop'; del.type = 'button';
    del.setAttribute('aria-label', 'Kavanozdan çıkar');
    del.textContent = '×';
    del.onclick = () => { jarWrite(jarRead().filter(x => x.t !== it.t)); renderJar(); syncSaveBtn(); toast('Kavanozdan çıkarıldı'); };
    row.append(p, del);
    box.appendChild(row);
  });
}

/* ─── arşiv ─────────────────────────────────────────────── */
let archiveShown = 7;
function renderArchive() {
  const box = $('#archive'); box.innerHTML = '';
  const now = new Date();
  for (let i = 1; i <= archiveShown; i++) {
    const d = new Date(now.getFullYear(), now.getMonth(), now.getDate() - i);
    const row = document.createElement('div');
    row.className = 'arch-row';
    const day = document.createElement('span');
    day.className = 'arch-day';
    day.textContent = `${String(d.getDate()).padStart(2, '0')} ${TR_M[d.getMonth()].slice(0, 3)}`;
    const txt = document.createElement('p');
    txt.className = 'arch-txt';
    txt.textContent = dayText(d);
    row.append(day, txt);
    box.appendChild(row);
  }
  $('#more').style.display = archiveShown >= 30 ? 'none' : '';
}

/* ════════════════════════════════════════════════════════
   BAŞLAT
   ════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  startSky();

  const now   = new Date();
  const today = dayText(now);
  let shown   = today;

  document.title = `${CONFIG.name} için · Sana Özel`;
  $('#salutation').textContent = salutation() + ',';
  $('#name').textContent       = CONFIG.name;
  $('#datestamp').textContent  = fmtDate(now);
  $('#signature').textContent  = '— ' + CONFIG.senderName;
  $('#whisper').textContent    = CONFIG.secretNote;

  /* ── özel gün ── */
  const bd  = nextAnnual(CONFIG.birthday, now);
  const ann = CONFIG.togetherSince ? nextAnnual(CONFIG.togetherSince, now) : null;
  const occ = $('#occasion');
  const setOcc = (t, n) => { $('#occ-title').textContent = t; $('#occ-note').textContent = n; occ.classList.add('show'); };

  if (bd.isToday)        setOcc(`Mutlu yıllar, ${CONFIG.name} — ${bd.n} yaşındasın`, 'Bugün dünyanın en güzel günü, çünkü sen bugün doğdun.');
  else if (ann?.isToday) setOcc(`${ann.n}. yıl dönümümüz`, 'Aynı kararı bugün de veriyorum: sen.');
  else if (bd.days === 1)  setOcc('Yarın doğum günün', 'Bu gece uyumadan bir dilek tut.');
  else if (bd.days <= 7)   setOcc(`Doğum gününe ${bd.days} gün`, `${bd.n} yaşına hazır mısın?`);
  else if (ann && ann.days <= 7) setOcc(`Yıl dönümümüze ${ann.days} gün`, `${ann.n}. yılımızı birlikte tamamlıyoruz.`);

  /* ── mektup ── */
  const comp = $('#compliment');

  /* ── kaydet ── */
  const saveBtn = $('#save');
  function syncSaveBtn() {
    const has = jarRead().some(x => x.t === shown);
    saveBtn.classList.toggle('on', has);
    $('#save-label').textContent = has ? 'Kavanozda' : 'Kavanoza koy';
  }
  window.syncSaveBtn = syncSaveBtn;

  saveBtn.addEventListener('click', () => {
    const items = jarRead();
    if (items.some(x => x.t === shown)) { toast('Bu zaten kavanozda'); return; }
    items.push({ t: shown, d: Date.now() });
    jarWrite(items); renderJar(); syncSaveBtn();
    const r = saveBtn.getBoundingClientRect();
    window.petalBurst(r.left + r.width / 2, r.top + r.height / 2);
    toast('Kavanoza kondu');
  });

  /* ── dinle ── */
  const readBtn = $('#read');
  if ('speechSynthesis' in window) {
    readBtn.addEventListener('click', () => {
      if (speechSynthesis.speaking) { speechSynthesis.cancel(); $('#read-label').textContent = 'Dinle'; return; }
      const u = new SpeechSynthesisUtterance(shown);
      u.lang = 'tr-TR'; u.rate = .92; u.pitch = 1.02;
      const tr = speechSynthesis.getVoices().find(v => v.lang.startsWith('tr'));
      if (tr) u.voice = tr;
      u.onend = () => { $('#read-label').textContent = 'Dinle'; };
      $('#read-label').textContent = 'Durdur';
      speechSynthesis.speak(u);
    });
  } else readBtn.remove();

  /* ── kopyala ── */
  $('#copy').addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(`“${shown}”\n— ${CONFIG.senderName}`); toast('Kopyalandı'); }
    catch { toast('Kopyalanamadı — cümleyi seçip elle kopyalayabilirsin'); }
  });

  /* ── paylaş ── */
  const shareBtn = $('#share');
  if (navigator.share) {
    shareBtn.addEventListener('click', () =>
      navigator.share({ title: 'Sana Özel', text: shown, url: location.href }).catch(() => {}));
  } else shareBtn.remove();

  /* ── bir tane daha ── */
  const again = $('#again');
  let extras = 3;
  again.addEventListener('click', () => {
    const pool = COMPLIMENTS.filter(c => c.t !== shown);
    shown = pool[Math.floor(Math.random() * pool.length)].t;
    typeOut(comp, shown);
    syncSaveBtn();
    if (--extras <= 0) { again.disabled = true; again.textContent = 'Gerisi yarına'; }
    else again.textContent = `Bir tane daha (${extras})`;
  });

  /* ── ruh hâli ── */
  $$('.mood').forEach(btn => btn.addEventListener('click', () => {
    $$('.mood').forEach(b => b.setAttribute('aria-pressed', String(b === btn)));
    const tag  = btn.dataset.tag;
    const pool = COMPLIMENTS.filter(c => c.g.includes(tag));
    const pick = pool[Math.floor(Math.random() * pool.length)].t;
    const out  = $('#mood-reply');
    $('#mood-text').textContent = '“' + pick + '”';
    out.classList.add('open');
  }));

  /* ── birlikte sayacı ── */
  if (CONFIG.togetherSince) {
    const start = new Date(CONFIG.togetherSince + 'T00:00:00');
    const tickClock = () => {
      const ms = Date.now() - start;
      const days = Math.floor(ms / DAY);
      const h = Math.floor(ms / 3600000) % 24;
      const m = Math.floor(ms / 60000) % 60;
      const s = Math.floor(ms / 1000) % 60;
      $('#clock-days').textContent = days.toLocaleString('tr-TR');
      $('#clock-fine').textContent = `${h} saat ${m} dakika ${String(s).padStart(2, '0')} saniye`;
    };
    tickClock(); setInterval(tickClock, 1000);

    /* sıradaki dönüm noktası */
    const days = Math.floor((Date.now() - start) / DAY);
    const marks = [100, 250, 365, 500, 730, 1000, 1095, 1460, 1500, 1825, 2000, 2555, 3000, 3650];
    const target = marks.find(m => m > days) || (Math.ceil(days / 1000) + 1) * 1000;
    const prev   = marks.filter(m => m <= days).pop() || 0;
    $('#mile-value').textContent = `${(target - days).toLocaleString('tr-TR')} gün`;
    $('#mile-note').textContent  = `${target.toLocaleString('tr-TR')}. günümüze`;
    requestAnimationFrame(() =>
      $('#mile-bar').style.width = Math.round((days - prev) / (target - prev) * 100) + '%');
  } else {
    $('#clock-section').remove();
  }

  /* ── geri sayımlar ── */
  $('#bd-value').textContent = bd.isToday ? 'Bugün' : `${bd.days} gün`;
  $('#bd-note').textContent  = bd.isToday ? `${bd.n} yaşındasın` : `${bd.n} yaşına`;
  if (ann) {
    $('#ann-value').textContent = ann.isToday ? 'Bugün' : `${ann.days} gün`;
    $('#ann-note').textContent  = `${ann.n}. yılımıza`;
  } else $('#ann-item').remove();

  /* ── gökyüzü ── */
  const p = moonPhase(now);
  $('#moon-lit').setAttribute('d', litPath(30, p));
  $('#moon-name').textContent = moonName(p);
  $('#moon-pct').textContent  = '%' + Math.round((1 - Math.cos(2 * Math.PI * p)) / 2 * 100) + ' aydınlık';
  const cz = chineseZodiac(Number(CONFIG.birthday.slice(0, 4)));
  $('#cz').textContent = `${cz.name} · ${cz.element}`;

  /* ── mühür sırrı ── */
  $('#seal').addEventListener('click', () => {
    const w = $('#whisper');
    w.classList.toggle('open');
    if (w.classList.contains('open')) window.petalBurst(innerWidth / 2, innerHeight * .5);
  });

  /* ── listeler ── */
  renderJar(); syncSaveBtn(); renderArchive();
  $('#more').addEventListener('click', () => { archiveShown = 30; renderArchive(); });

  /* ── görünürlük animasyonu ── */
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
  }), { rootMargin: '-40px' });
  $$('.reveal').forEach(el => io.observe(el));

  /* ── perde kalkıyor ── */
  setTimeout(() => {
    $('#curtain').classList.add('gone');
    setTimeout(() => typeOut(comp, today), 350);
  }, 700);
});

/* ─── çevrimdışı çalışsın ───────────────────────────────── */
if ('serviceWorker' in navigator) {
  addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
}
