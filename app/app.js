/* ═══════════════════════════════════════════════
   WANDERAI — app.js  v4.0
   New: start location · transport mode selector ·
        IRCTC / RedBus redirect banners ·
        nearest boarding point display ·
        updated history sidebar with transport info
═══════════════════════════════════════════════ */

const API_BASE = 'http://localhost:8000';

/* ── Destinations ── */
const DESTINATIONS = [
  { name:'Goa',       tagline:'Sun, Sand & Spice',      emoji:'🌊', tag:'Beach',     bg:'linear-gradient(135deg,#1a4a3a,#0d2a1e)' },
  { name:'Manali',    tagline:'Snow-Capped Adventures',  emoji:'🏔️', tag:'Adventure', bg:'linear-gradient(135deg,#1a2a4a,#0d1a2e)' },
  { name:'Kashmir',   tagline:'Paradise on Earth',       emoji:'❄️', tag:'Scenic',    bg:'linear-gradient(135deg,#2a1a4a,#1a0d2e)' },
  { name:'Ooty',      tagline:'Queen of Hill Stations',  emoji:'🌿', tag:'Hill',      bg:'linear-gradient(135deg,#1a3a1a,#0d2a0d)' },
  { name:'Rajasthan', tagline:'Royal Forts & Deserts',   emoji:'🏰', tag:'Cultural',  bg:'linear-gradient(135deg,#4a2a1a,#2e1a0d)' },
  { name:'Kerala',    tagline:"God's Own Country",       emoji:'🌴', tag:'Nature',    bg:'linear-gradient(135deg,#1a3a2a,#0d2a1a)' },
];

/* ── Progress step definitions (8 agents now) ── */
const STEPS = [
  { id:'query_planner',         label:'Analysing your request…',        icon:'🔍' },
  { id:'nearest_station_agent', label:'Finding nearest boarding point…', icon:'📍' },
  { id:'flight_agent',          label:'Searching for transport…',        icon:'🚀' },
  { id:'hotel_agent',           label:'Finding best hotels…',            icon:'🏨' },
  { id:'activity_agent',        label:'Discovering activities…',         icon:'🗺️' },
  { id:'itinerary_agent',       label:'Building itinerary…',             icon:'📅' },
  { id:'budget_agent',          label:'Estimating budget…',              icon:'💰' },
  { id:'final_agent',           label:'Compiling your plan…',            icon:'✨' },
];

/* ── App state ── */
let currentTripData = null;
let currentChatId   = null;
let modalTripData   = null;

/* ════════════════════════════════════════════
   LOADER
════════════════════════════════════════════ */
(function initLoader() {
  const sky = document.getElementById('loaderSky');
  for (let i = 0; i < 80; i++) {
    const s = document.createElement('div');
    s.className = 'star';
    const sz = Math.random() * 2 + 1;
    s.style.cssText = `left:${Math.random()*100}%;top:${Math.random()*100}%;width:${sz}px;height:${sz}px;animation-delay:${Math.random()*2}s;animation-duration:${1+Math.random()*2}s;`;
    sky.appendChild(s);
  }
  for (let i = 0; i < 4; i++) {
    const c = document.createElement('div');
    c.className = 'cloud';
    c.style.cssText = `top:${20+Math.random()*50}%;width:${100+Math.random()*140}px;height:${18+Math.random()*18}px;animation-duration:${12+Math.random()*10}s;animation-delay:${-Math.random()*10}s;`;
    sky.appendChild(c);
  }
  setTimeout(() => {
    document.getElementById('loader').classList.add('hide');
    loadHistory();
  }, 2400);
})();

/* ════════════════════════════════════════════
   TRANSPORT MODE UI
════════════════════════════════════════════ */
function getTransportMode() {
  const checked = document.querySelector('input[name="transport"]:checked');
  return checked ? checked.value : 'flight';
}

/* Update booking banner when transport mode changes */
document.querySelectorAll('input[name="transport"]').forEach(radio => {
  radio.addEventListener('change', updateTransportBanner);
});

function updateTransportBanner() {
  const mode   = getTransportMode();
  const banner  = document.getElementById('bookingBanner');
  const icon    = document.getElementById('bookingBannerIcon');
  const title   = document.getElementById('bookingBannerTitle');
  const sub     = document.getElementById('bookingBannerSub');
  const btn     = document.getElementById('bookingBannerBtn');
  const start   = document.getElementById('inputStart').value.trim();
  const dest    = document.getElementById('inputDest').value.trim();

  banner.className = 'booking-redirect-banner';

  if (mode === 'train') {
    banner.style.display = 'flex';
    banner.classList.add('train-mode');
    icon.textContent  = '🚂';
    title.textContent = 'Book your train on IRCTC';
    sub.textContent   = 'Direct IRCTC booking link will be included in your plan';
    const url = start && dest
      ? `https://www.irctc.co.in/nget/train-search?fromStation=${encodeURIComponent(start)}&toStation=${encodeURIComponent(dest)}`
      : 'https://www.irctc.co.in/nget/train-search';
    btn.href = url;
    btn.textContent = '🚂 Open IRCTC →';

  } else if (mode === 'bus') {
    banner.style.display = 'flex';
    banner.classList.add('bus-mode');
    icon.textContent  = '🚌';
    title.textContent = 'Book your bus on RedBus';
    sub.textContent   = 'Direct RedBus booking link will be included in your plan';
    const from = (start || 'your-city').toLowerCase().replace(/\s+/g, '-');
    const to   = (dest  || 'destination').toLowerCase().replace(/\s+/g, '-');
    btn.href = `https://www.redbus.in/bus-tickets/${from}-to-${to}`;
    btn.textContent = '🚌 Open RedBus →';

  } else {
    banner.style.display = 'none';
  }
}

/* Re-update banner when start/dest inputs change */
document.getElementById('inputStart').addEventListener('input', updateTransportBanner);
document.getElementById('inputDest').addEventListener('input', updateTransportBanner);

/* ════════════════════════════════════════════
   GEOLOCATION — detect my location
════════════════════════════════════════════ */
function detectMyLocation() {
  const hint = document.getElementById('locationHint');
  hint.textContent = 'Detecting…';

  if (!navigator.geolocation) {
    hint.textContent = '';
    showToast('⚠️ Geolocation not supported by your browser.');
    return;
  }

  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      const { latitude, longitude } = pos.coords;
      try {
        // Reverse-geocode using a free public API (no key needed)
        const resp = await fetch(
          `https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json`
        );
        const data = await resp.json();
        const city =
          data.address?.city      ||
          data.address?.town      ||
          data.address?.village   ||
          data.address?.state_district ||
          data.address?.state     ||
          '';
        if (city) {
          document.getElementById('inputStart').value = city;
          hint.textContent = `✓ ${city}`;
          setTimeout(() => { hint.textContent = ''; }, 3000);
          updateTransportBanner();
        } else {
          hint.textContent = '';
          showToast('📍 Could not determine city from coordinates.');
        }
      } catch {
        hint.textContent = '';
        showToast('📍 Location detected but could not reverse-geocode.');
        // Fallback: fill with coords so backend can work with it
        document.getElementById('inputStart').value = `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`;
      }
    },
    (err) => {
      hint.textContent = '';
      showToast(`⚠️ Location error: ${err.message}`);
    },
    { enableHighAccuracy: true, timeout: 8000 }
  );
}

function detectStartLocation(val) {
  // Live update banner when user types manually
  updateTransportBanner();
}

/* ════════════════════════════════════════════
   CAROUSEL
════════════════════════════════════════════ */
(function initCarousel() {
  const track   = document.getElementById('carouselTrack');
  const dotsWrap = document.getElementById('carouselDots');
  const counter  = document.getElementById('carouselCounter');
  const bar      = document.getElementById('carouselProgressBar');
  const prevBtn  = document.getElementById('carouselPrev');
  const nextBtn  = document.getElementById('carouselNext');
  if (!track) return;

  const slides  = Array.from(track.querySelectorAll('.carousel-slide'));
  const total   = slides.length;
  let current   = 0;
  let timer     = null;
  const INTERVAL = 4000;

  slides.forEach((_, i) => {
    const dot = document.createElement('button');
    dot.className = 'carousel-dot' + (i === 0 ? ' active' : '');
    dot.setAttribute('aria-label', `Go to slide ${i+1}`);
    dot.addEventListener('click', () => goTo(i));
    dotsWrap.appendChild(dot);
  });
  const dots = Array.from(dotsWrap.querySelectorAll('.carousel-dot'));

  function goTo(n) {
    n = ((n % total) + total) % total;
    slides[current].classList.remove('active');
    slides[n].classList.add('active');
    track.style.transform = `translateX(-${n*100}%)`;
    dots[current].classList.remove('active');
    dots[n].classList.add('active');
    current = n;
    counter.textContent = `${current+1} / ${total}`;
    restartBar();
  }
  function restartBar() {
    bar.style.transition = 'none'; bar.style.width = '0%';
    void bar.offsetWidth;
    bar.style.transition = `width ${INTERVAL}ms linear`; bar.style.width = '100%';
  }
  function startAuto() { stopAuto(); timer = setInterval(() => goTo(current+1), INTERVAL); restartBar(); }
  function stopAuto()  { clearInterval(timer); }

  prevBtn.addEventListener('click', () => { stopAuto(); goTo(current-1); startAuto(); });
  nextBtn.addEventListener('click', () => { stopAuto(); goTo(current+1); startAuto(); });

  let touchStartX = 0;
  track.addEventListener('touchstart', e => { touchStartX = e.touches[0].clientX; }, { passive: true });
  track.addEventListener('touchend',   e => {
    const dx = e.changedTouches[0].clientX - touchStartX;
    if (Math.abs(dx) > 40) { stopAuto(); goTo(current + (dx < 0 ? 1 : -1)); startAuto(); }
  }, { passive: true });
  track.closest('.carousel-frame').addEventListener('mouseenter', stopAuto);
  track.closest('.carousel-frame').addEventListener('mouseleave', startAuto);
  document.addEventListener('keydown', e => {
    if (e.key === 'ArrowLeft')  { stopAuto(); goTo(current-1); startAuto(); }
    if (e.key === 'ArrowRight') { stopAuto(); goTo(current+1); startAuto(); }
  });
  startAuto();
})();

/* ════════════════════════════════════════════
   NAVBAR
════════════════════════════════════════════ */
const hamburger = document.getElementById('navHamburger');
const navLinks  = document.getElementById('navLinks');
hamburger.addEventListener('click', () => {
  hamburger.classList.toggle('open');
  navLinks.classList.toggle('open');
});
function closeMenu() {
  hamburger.classList.remove('open');
  navLinks.classList.remove('open');
}

/* ════════════════════════════════════════════
   SIDEBAR
════════════════════════════════════════════ */
const sidebar        = document.getElementById('sidebar');
const sidebarOverlay = document.getElementById('sidebarOverlay');
const sidebarToggle  = document.getElementById('sidebarToggle');
const sidebarClose   = document.getElementById('sidebarClose');

sidebarToggle.addEventListener('click', toggleSidebar);
sidebarClose.addEventListener('click',  closeSidebar);

function toggleSidebar() {
  sidebar.classList.toggle('open');
  sidebarOverlay.classList.toggle('show');
}
function closeSidebar() {
  sidebar.classList.remove('open');
  sidebarOverlay.classList.remove('show');
}
function openSidebar() {
  sidebar.classList.add('open');
  sidebarOverlay.classList.add('show');
}

/* ════════════════════════════════════════════
   DESTINATIONS
════════════════════════════════════════════ */
(function renderDests() {
  const grid = document.getElementById('destGrid');
  DESTINATIONS.forEach(d => {
    grid.innerHTML += `
      <div class="dest-card" onclick="quickPlan('${d.name}')">
        <div style="width:100%;height:100%;${d.bg};display:flex;align-items:center;justify-content:center;font-size:66px;opacity:.35">${d.emoji}</div>
        <div class="dest-card-overlay"></div>
        <div class="dest-card-body">
          <div class="dest-tag">${d.tag}</div>
          <div class="dest-name">${d.name}</div>
          <div class="dest-tagline">${d.tagline}</div>
        </div>
        <div class="dest-quick-plan">Plan Trip →</div>
      </div>`;
  });
})();

/* ════════════════════════════════════════════
   CHIPS
════════════════════════════════════════════ */
document.querySelectorAll('.chip').forEach(c => {
  c.addEventListener('click', () => c.classList.toggle('active'));
});

/* ════════════════════════════════════════════
   SESSION ID
════════════════════════════════════════════ */
function getSessionId() {
  let sid = localStorage.getItem('wanderai_session');
  if (!sid) {
    sid = 'sess_' + Date.now() + '_' + Math.random().toString(36).slice(2);
    localStorage.setItem('wanderai_session', sid);
  }
  return sid;
}

/* ════════════════════════════════════════════
   SAVE HISTORY
════════════════════════════════════════════ */
async function saveToHistory(data, query) {
  try {
    const vibes  = [...document.querySelectorAll('.chip.active')].map(c => c.dataset.vibe).join(', ');
    const tInfo  = data.transport_info || {};
    const resp = await fetch(`${API_BASE}/history/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id:       getSessionId(),
        destination:      data.destination      || '',
        user_query:       query,
        start_location:   data.start_location   || '',
        transport_mode:   data.transport_mode   || 'flight',
        nearest_station:  data.nearest_station  || '',
        booking_url:      tInfo.booking_url     || '',
        flight_result:    data.flight_result    || '',
        hotel_results:    data.hotel_results    || '',
        activity_results: data.activity_results || '',
        itinerary:        data.itinerary        || '',
        budget_estimate:  data.budget_estimate  || '',
        final_plan:       data.final_plan       || '',
        vibes,
        llm_calls:        data.llm_calls        || 0,
      }),
    });
    const saved = await resp.json();
    return saved.id || null;
  } catch (err) {
    console.warn('History save failed:', err.message);
    return null;
  }
}

/* ════════════════════════════════════════════
   LOAD HISTORY — fill sidebar
════════════════════════════════════════════ */
async function loadHistory() {
  try {
    const resp = await fetch(`${API_BASE}/history/${getSessionId()}`);
    const data = await resp.json();
    renderHistoryList(data.chats || []);
  } catch {
    // silence if backend offline
  }
}

function renderHistoryList(chats) {
  const list  = document.getElementById('historyList');
  const empty = document.getElementById('historyEmpty');

  if (!chats.length) {
    empty.style.display = 'flex';
    return;
  }
  empty.style.display = 'none';

  Array.from(list.querySelectorAll('.history-item')).forEach(el => el.remove());

  chats.forEach(chat => {
    const item = document.createElement('div');
    item.className = 'history-item';
    item.dataset.chatId = chat.id;

    const dest  = chat.destination || 'Unknown';
    const emoji = getDestEmoji(dest);
    const mode  = chat.transport_mode || 'flight';
    const modeIcon = { flight: '✈️', train: '🚂', bus: '🚌' }[mode] || '✈️';
    const vibes = chat.vibes
      ? chat.vibes.split(',').slice(0, 2).map(v => `<span class="history-vibe-tag">${v.trim()}</span>`).join('')
      : '';
    const date  = formatDate(chat.created_at || chat.timestamp);
    const startFrom = chat.start_location ? `${chat.start_location} → ` : '';

    item.innerHTML = `
      <div class="history-item-body" onclick="openHistoryModal(${chat.id})">
        <div class="history-dest">
          <span class="history-dest-emoji">${emoji}</span>${dest}
          <span class="history-transport-badge ${mode}">${modeIcon} ${mode}</span>
        </div>
        <div class="history-route">${startFrom}${dest}</div>
        <div class="history-query">${(chat.user_query || '').slice(0, 50)}${(chat.user_query || '').length > 50 ? '…' : ''}</div>
        <div class="history-vibe-tags">${vibes}</div>
        <div class="history-date">🕐 ${date}</div>
      </div>
      <div class="history-item-actions">
        <button class="history-action-btn" title="Open" onclick="openHistoryModal(${chat.id})">📋</button>
        <button class="history-action-btn del" title="Delete" onclick="deleteHistoryItem(event,${chat.id})">🗑</button>
      </div>`;
    list.appendChild(item);
  });
}

function getDestEmoji(dest) {
  const map = { goa:'🌊', manali:'🏔️', kashmir:'❄️', ooty:'🌿', rajasthan:'🏰', kerala:'🌴', ladakh:'🏔️', delhi:'🕌', mumbai:'🏙️', agra:'🕌', jaipur:'🏯', varanasi:'⛵', darjeeling:'🍵' };
  const k = dest.toLowerCase();
  return map[k] || '✈️';
}

function formatDate(str) {
  if (!str) return '';
  try {
    return new Date(str).toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' });
  } catch { return str; }
}

/* ════════════════════════════════════════════
   DELETE HISTORY ITEM
════════════════════════════════════════════ */
async function deleteHistoryItem(e, chatId) {
  e.stopPropagation();
  if (!confirm('Delete this trip from history?')) return;
  try {
    await fetch(`${API_BASE}/history/${getSessionId()}/${chatId}`, { method: 'DELETE' });
    document.querySelector(`.history-item[data-chat-id="${chatId}"]`)?.remove();
    if (!document.querySelectorAll('.history-item').length)
      document.getElementById('historyEmpty').style.display = 'flex';
    showToast('✅ Trip removed from history.');
    if (currentChatId === chatId) closeHistoryModal();
  } catch {
    showToast('❌ Failed to delete trip.');
  }
}

/* ════════════════════════════════════════════
   HISTORY MODAL — open / close
════════════════════════════════════════════ */
async function openHistoryModal(chatId) {
  currentChatId = chatId;
  modalTripData = null;

  try {
    const resp = await fetch(`${API_BASE}/history/${getSessionId()}/${chatId}`);
    if (!resp.ok) throw new Error();
    modalTripData = await resp.json();
  } catch {
    showToast('❌ Could not load trip details.');
    return;
  }

  const mode = modalTripData.transport_mode || 'flight';
  document.getElementById('modalTitle').textContent = modalTripData.destination || 'Trip Plan';
  document.getElementById('modalMeta').textContent  =
    `${modalTripData.start_location ? modalTripData.start_location + ' → ' : ''}${modalTripData.destination || ''} · ${mode.toUpperCase()} · ${modalTripData.llm_calls || 0} AI calls`;

  document.getElementById('modalPlanContent').innerHTML     = markdownToHtml(modalTripData.final_plan       || 'No plan available.');
  document.getElementById('modalHotelsContent').textContent     = modalTripData.hotel_results    || 'No hotel data.';
  document.getElementById('modalActivitiesContent').textContent = modalTripData.activity_results || 'No activity data.';
  document.getElementById('modalBudgetContent').textContent     = modalTripData.budget_estimate  || 'No budget data.';

  // Populate transport tab
  renderModalTransport(modalTripData);

  document.getElementById('modalChatMessages').innerHTML = '';
  document.getElementById('modalChatInput').value        = '';

  switchHistoryTab('plan');
  document.getElementById('historyModal').classList.add('show');
  document.getElementById('modalBackdrop').classList.add('show');
  document.body.style.overflow = 'hidden';

  document.querySelectorAll('.history-item').forEach(el => el.classList.remove('active'));
  document.querySelector(`.history-item[data-chat-id="${chatId}"]`)?.classList.add('active');
}

function renderModalTransport(data) {
  const mode  = data.transport_mode || 'flight';
  const tInfo = {};  // booking_url stored separately
  const bookingUrl = data.booking_url || '';
  const nearest    = data.nearest_station || '';
  const start      = data.start_location  || '';
  const dest       = data.destination     || '';
  const cont       = document.getElementById('modalTransportContent');

  const modeIcons = { flight: '✈️', train: '🚂', bus: '🚌' };
  const modeNames = { flight: 'Flight', train: 'Train (IRCTC)', bus: 'Bus (RedBus)' };

  let bookingHtml = '';
  if (bookingUrl && mode === 'train') {
    bookingHtml = `<a href="${bookingUrl}" target="_blank" rel="noopener" class="transport-book-link irctc">🚂 Book on IRCTC →</a>`;
  } else if (bookingUrl && mode === 'bus') {
    bookingHtml = `<a href="${bookingUrl}" target="_blank" rel="noopener" class="transport-book-link redbus">🚌 Book on RedBus →</a>`;
  } else if (mode === 'flight') {
    bookingHtml = `<div class="result-content" style="margin-top:10px">${data.flight_result || 'No flight data.'}</div>`;
  }

  cont.innerHTML = `
    <div class="transport-detail-card">
      <h3>${modeIcons[mode] || '🚀'} ${modeNames[mode] || mode}</h3>
      ${start ? `<p><strong>From:</strong> ${start}</p>` : ''}
      ${dest  ? `<p><strong>To:</strong>   ${dest}</p>`  : ''}
      ${nearest ? `<p><strong>Boarding Point:</strong> ${nearest}</p>` : ''}
      ${bookingHtml}
    </div>`;
}

function closeHistoryModal() {
  document.getElementById('historyModal').classList.remove('show');
  document.getElementById('modalBackdrop').classList.remove('show');
  document.body.style.overflow = '';
  document.querySelectorAll('.history-item').forEach(el => el.classList.remove('active'));
  currentChatId = null;
  modalTripData = null;
}

function switchHistoryTab(name) {
  const names = ['plan','transport','hotels','activities','budget','chat'];
  document.querySelectorAll('.htab-btn').forEach((btn, i) => {
    btn.classList.toggle('active', names[i] === name);
  });
  document.querySelectorAll('.htab-panel').forEach(panel => {
    panel.classList.toggle('active', panel.id === `htab-${name}`);
  });
}

/* ════════════════════════════════════════════
   MODAL CHAT
════════════════════════════════════════════ */
async function sendModalChat() {
  const input = document.getElementById('modalChatInput');
  const msg   = input.value.trim();
  if (!msg || !modalTripData) return;
  input.value = '';

  const container = document.getElementById('modalChatMessages');
  appendChatMsg(container, msg, 'user');
  const typingEl = appendChatMsg(container, 'Thinking…', 'ai typing');
  container.scrollTop = container.scrollHeight;

  try {
    const context = `
You are a helpful travel assistant. The user has a saved trip plan:

Destination: ${modalTripData.destination}
Starting From: ${modalTripData.start_location || 'not specified'}
Transport Mode: ${(modalTripData.transport_mode || 'flight').toUpperCase()}
Nearest Boarding Point: ${modalTripData.nearest_station || 'N/A'}
Original Query: ${modalTripData.user_query}
Budget Estimate: ${modalTripData.budget_estimate || 'N/A'}
Itinerary Summary: ${(modalTripData.itinerary || '').slice(0, 1200)}
Final Plan Summary: ${(modalTripData.final_plan || '').slice(0, 1200)}

Answer the user's follow-up question helpfully and concisely.
User question: ${msg}`;

    const resp = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'claude-sonnet-4-6', max_tokens: 1000,
        messages: [{ role: 'user', content: context }],
      }),
    });
    const data   = await resp.json();
    const answer = data.content?.[0]?.text || 'Sorry, I could not generate a response.';
    typingEl.textContent = answer;
    typingEl.classList.remove('typing');
  } catch {
    typingEl.textContent = 'Failed to get a response.';
    typingEl.classList.remove('typing');
  }
  container.scrollTop = container.scrollHeight;
}

/* ════════════════════════════════════════════
   INLINE TRIP CHAT
════════════════════════════════════════════ */
async function sendTripChat() {
  const input = document.getElementById('tripChatInput');
  const msg   = input.value.trim();
  if (!msg || !currentTripData) return;
  input.value = '';

  const container = document.getElementById('tripChatMessages');
  appendChatMsg(container, msg, 'user');
  const typingEl = appendChatMsg(container, 'Thinking…', 'ai typing');
  container.scrollTop = container.scrollHeight;

  try {
    const tInfo = currentTripData.transport_info || {};
    const context = `
You are a helpful travel assistant. The user just received this trip plan:

Destination: ${currentTripData.destination}
Starting From: ${currentTripData.start_location || 'not specified'}
Transport Mode: ${(currentTripData.transport_mode || 'flight').toUpperCase()}
Nearest Boarding: ${currentTripData.nearest_station || 'N/A'}
Booking URL: ${tInfo.booking_url || 'N/A'}
Budget Estimate: ${currentTripData.budget_estimate || 'N/A'}
Itinerary: ${(currentTripData.itinerary || '').slice(0, 1200)}
Final Plan: ${(currentTripData.final_plan || '').slice(0, 1200)}

Answer the user's follow-up question helpfully and concisely.
User question: ${msg}`;

    const resp = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'claude-sonnet-4-6', max_tokens: 1000,
        messages: [{ role: 'user', content: context }],
      }),
    });
    const data   = await resp.json();
    const answer = data.content?.[0]?.text || 'Sorry, I could not generate a response.';
    typingEl.textContent = answer;
    typingEl.classList.remove('typing');
  } catch {
    typingEl.textContent = 'Failed to get a response.';
    typingEl.classList.remove('typing');
  }
  container.scrollTop = container.scrollHeight;
}

function appendChatMsg(container, text, cls) {
  const el = document.createElement('div');
  el.className = `chat-msg ${cls}`;
  el.textContent = text;
  container.appendChild(el);
  return el;
}

/* ════════════════════════════════════════════
   PLANNER HELPERS
════════════════════════════════════════════ */
function quickPlan(dest) {
  document.getElementById('inputDest').value = dest;
  scrollToPlanner();
}
function scrollToPlanner() {
  document.getElementById('planner').scrollIntoView({ behavior:'smooth' });
}
function scrollToTop() {
  window.scrollTo({ top:0, behavior:'smooth' });
}

function buildQuery() {
  const start      = document.getElementById('inputStart').value.trim();
  const dest       = document.getElementById('inputDest').value.trim();
  const dates      = document.getElementById('inputDates').value.trim();
  const travellers = document.getElementById('inputTravellers').value.trim();
  const budget     = document.getElementById('inputBudget').value.trim();
  const extra      = document.getElementById('inputExtra').value.trim();
  const vibes      = [...document.querySelectorAll('.chip.active')].map(c => c.dataset.vibe).join(', ');
  const mode       = getTransportMode();

  if (!dest) { showToast('⚠️ Please enter a destination first.'); return null; }

  let q = `Plan a ${mode} trip`;
  if (start) q += ` from ${start}`;
  q += ` to ${dest}`;
  if (dates)      q += ` for ${dates}`;
  if (travellers) q += ` for ${travellers}`;
  if (budget)     q += ` with a budget of ${budget}`;
  if (vibes)      q += `. Trip vibe: ${vibes}`;
  if (extra)      q += `. Additional notes: ${extra}`;
  return q;
}

/* ════════════════════════════════════════════
   PROGRESS STEPS
════════════════════════════════════════════ */
function renderProgressSteps(activeIdx) {
  const container = document.getElementById('progressSteps');
  container.innerHTML = STEPS.map((s, i) => {
    let cls = 'progress-step', icon;
    if      (i < activeIdx)   { cls += ' done';   icon = `<div class="step-icon">✅</div>`; }
    else if (i === activeIdx) { cls += ' active'; icon = `<div class="step-spinner"></div>`; }
    else                      {                   icon = `<div class="step-icon" style="opacity:.3">${s.icon}</div>`; }
    return `<div class="${cls}">${icon}<span>${s.label}</span></div>`;
  }).join('');
}

/* ════════════════════════════════════════════
   PLAN TRIP
════════════════════════════════════════════ */
async function planTrip() {
  const query = buildQuery();
  if (!query) return;

  const startLocation = document.getElementById('inputStart').value.trim();
  const transportMode = getTransportMode();

  const btn = document.getElementById('planBtn');
  btn.disabled = true;

  const pw = document.getElementById('progressWrap');
  pw.classList.add('show');
  renderProgressSteps(0);
  document.getElementById('results').classList.remove('show');

  let currentStep = 0;
  const stepTimer = setInterval(() => {
    if (currentStep < STEPS.length - 1) {
      currentStep++;
      renderProgressSteps(currentStep);
    }
  }, 2800);

  try {
    const resp = await fetch(`${API_BASE}/planner/plan`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ query, start_location: startLocation, transport_mode: transportMode }),
    });
    clearInterval(stepTimer);

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(err.detail || `HTTP ${resp.status}`);
    }

    const data = await resp.json();
    currentTripData = data;
    renderProgressSteps(STEPS.length);

    const savedId = await saveToHistory(data, query);
    if (savedId) await loadHistory();

    setTimeout(() => {
      pw.classList.remove('show');
      showResults(data);
      btn.disabled = false;
    }, 700);

  } catch (err) {
    clearInterval(stepTimer);
    pw.classList.remove('show');
    btn.disabled = false;
    showToast(`❌ Error: ${err.message}`);
    console.error(err);
  }
}

/* ════════════════════════════════════════════
   SHOW RESULTS
════════════════════════════════════════════ */
function showResults(data) {
  const mode  = data.transport_mode || 'flight';
  const tInfo = data.transport_info || {};
  const start = data.start_location || '';

  document.getElementById('resultsMeta').textContent =
    `${start ? start + ' → ' : ''}${data.destination || 'N/A'} · ${mode.toUpperCase()} · ${data.llm_calls} AI calls`;

  document.getElementById('finalPlanContent').innerHTML    = markdownToHtml(data.final_plan  || 'No plan generated.');
  document.getElementById('hotelsContent').textContent     = data.hotel_results               || 'No hotel data.';
  document.getElementById('activitiesContent').textContent = data.activity_results            || 'No activity data.';
  document.getElementById('budgetContent').textContent     = data.budget_estimate             || 'No budget data.';

  // ── Populate transport tab ──
  renderTransportTab(data);

  // ── Nearest station bar ──
  const nsBar  = document.getElementById('nearestStationBar');
  const nsText = document.getElementById('nsText');
  const nsBtn  = document.getElementById('nsBookBtn');
  const nsIcon = document.getElementById('nsIcon');

  if (data.nearest_station) {
    nsBar.style.display = 'flex';
    nsBar.className = `nearest-station-bar ${mode}-mode`;
    nsText.textContent = data.nearest_station;
    nsIcon.textContent = { flight:'✈️', train:'🚂', bus:'🚌' }[mode] || '📍';

    if (tInfo.booking_url && mode !== 'flight') {
      nsBtn.style.display = 'inline-flex';
      nsBtn.href          = tInfo.booking_url;
      nsBtn.textContent   = tInfo.booking_label || 'Book →';
    } else {
      nsBtn.style.display = 'none';
    }
  } else {
    nsBar.style.display = 'none';
  }

  // Clear chat
  document.getElementById('tripChatMessages').innerHTML = '';
  document.getElementById('tripChatInput').value        = '';

  switchTab('full');
  const results = document.getElementById('results');
  results.classList.add('show');
  setTimeout(() => results.scrollIntoView({ behavior:'smooth' }), 100);
}

function renderTransportTab(data) {
  const mode    = data.transport_mode || 'flight';
  const tInfo   = data.transport_info || {};
  const start   = data.start_location || '';
  const dest    = data.destination    || '';
  const nearest = data.nearest_station || '';
  const cont    = document.getElementById('transportContent');

  const modeIcons = { flight:'✈️', train:'🚂', bus:'🚌' };
  const modeNames = { flight:'Flight', train:'Train (IRCTC)', bus:'Bus (RedBus)' };

  let bookingHtml = '';
  if (tInfo.booking_url && mode === 'train') {
    bookingHtml = `<a href="${tInfo.booking_url}" target="_blank" rel="noopener" class="transport-book-link irctc">🚂 Book on IRCTC →</a>`;
  } else if (tInfo.booking_url && mode === 'bus') {
    bookingHtml = `<a href="${tInfo.booking_url}" target="_blank" rel="noopener" class="transport-book-link redbus">🚌 Book on RedBus →</a>`;
  } else if (mode === 'flight') {
    bookingHtml = `<div class="result-content" style="margin-top:10px;white-space:pre-wrap">${data.flight_result || 'No flight data.'}</div>`;
  }

  cont.innerHTML = `
    <div class="transport-detail-card">
      <h3>${modeIcons[mode] || '🚀'} ${modeNames[mode] || mode} Details</h3>
      ${start   ? `<p><strong>Starting From:</strong> ${start}</p>` : ''}
      ${dest    ? `<p><strong>Destination:</strong>   ${dest}</p>`  : ''}
      ${nearest ? `<p><strong>Nearest Boarding Point:</strong><br/>${nearest}</p>` : ''}
      ${tInfo.boarding_tip ? `<p><strong>Tip:</strong> ${tInfo.boarding_tip}</p>` : ''}
      ${bookingHtml}
    </div>`;
}

/* ════════════════════════════════════════════
   MARKDOWN → HTML
════════════════════════════════════════════ */
function markdownToHtml(md) {
  return md
    .replace(/^### (.+)$/gm,   '<h3>$1</h3>')
    .replace(/^## (.+)$/gm,    '<h2>$1</h2>')
    .replace(/^# (.+)$/gm,     '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
    .replace(/^---$/gm,         '<hr/>')
    .replace(/^[-*•] (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>[\s\S]*?<\/li>\n?)+/g, m => `<ul>${m}</ul>`)
    .replace(/\n\n/g, '</p><p>')
    .replace(/^(?!<[huli]|<hr)/gm, '<p>')
    .replace(/<p>(<[hul])/g, '$1')
    + '</p>';
}

/* ════════════════════════════════════════════
   TAB SWITCHING (results section)
════════════════════════════════════════════ */
function switchTab(name) {
  const tabNames = ['full','transport','hotels','activities','budget'];
  document.querySelectorAll('.tab-btn').forEach((btn, i) => {
    btn.classList.toggle('active', tabNames[i] === name);
  });
  document.querySelectorAll('.tab-panel').forEach(panel => {
    panel.classList.toggle('active', panel.id === `tab-${name}`);
  });
}

/* ════════════════════════════════════════════
   RESET PLANNER
════════════════════════════════════════════ */
function resetPlanner() {
  document.getElementById('results').classList.remove('show');
  currentTripData = null;
  ['inputStart','inputDest','inputDates','inputTravellers','inputBudget','inputExtra'].forEach(id => {
    document.getElementById(id).value = '';
  });
  document.querySelectorAll('.chip.active').forEach(c => c.classList.remove('active'));
  // Reset transport to flight
  document.querySelector('input[name="transport"][value="flight"]').checked = true;
  document.getElementById('bookingBanner').style.display = 'none';
  scrollToPlanner();
}

/* ════════════════════════════════════════════
   START NEW TRIP (from sidebar)
════════════════════════════════════════════ */
function startNewTrip() {
  closeSidebar();
  resetPlanner();
  scrollToPlanner();
}

/* ════════════════════════════════════════════
   COPY TO CLIPBOARD
════════════════════════════════════════════ */
function copyToClipboard(id) {
  const el = document.getElementById(id);
  navigator.clipboard.writeText(el.innerText)
    .then(() => showToast('✅ Copied to clipboard!'))
    .catch(() => showToast('❌ Copy failed.'));
}

/* ════════════════════════════════════════════
   TOAST
════════════════════════════════════════════ */
function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3500);
}