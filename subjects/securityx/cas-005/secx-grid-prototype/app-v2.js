(() => {
  'use strict';

  const DATA_BASE = '../study-site/data/';
  const STORAGE_KEY = 'secx-grid-progress-v1';
  const DOMAIN_ORDER = [
    'Governance, Risk, and Compliance',
    'Security Architecture',
    'Security Engineering',
    'Security Operations'
  ];
  const DOMAIN_META = {
    'Governance, Risk, and Compliance': { short: 'GRC', weight: 20, direction: '↑', root: [2, 1] },
    'Security Architecture': { short: 'Architecture', weight: 27, direction: '→', root: [3, 2] },
    'Security Engineering': { short: 'Engineering', weight: 31, direction: '↓', root: [2, 3] },
    'Security Operations': { short: 'Operations', weight: 22, direction: '←', root: [1, 2] }
  };
  const OBJECTIVES = {
    '1.1': 'Implement appropriate governance components from organizational security requirements.',
    '1.2': 'Perform risk management activities from organizational security requirements.',
    '1.3': 'Explain how compliance affects information security strategies.',
    '1.4': 'Perform threat-modeling activities in a scenario.',
    '1.5': 'Summarize information-security challenges associated with AI adoption.',
    '2.1': 'Analyze requirements to design resilient systems.',
    '2.2': 'Implement security throughout the systems life cycle.',
    '2.3': 'Integrate appropriate controls in a secure architecture.',
    '2.4': 'Apply security concepts to access, authentication, and authorization design.',
    '2.5': 'Securely implement cloud capabilities in an enterprise environment.',
    '2.6': 'Integrate Zero Trust concepts into system architecture design.',
    '3.1': 'Troubleshoot IAM components in an enterprise environment.',
    '3.2': 'Analyze requirements to enhance endpoint and server security.',
    '3.3': 'Troubleshoot complex network infrastructure security issues.',
    '3.4': 'Implement hardware security technologies and techniques.',
    '3.5': 'Secure specialized and legacy systems against threats.',
    '3.6': 'Use automation to secure the enterprise.',
    '3.7': 'Explain the importance of advanced cryptographic concepts.',
    '3.8': 'Apply the appropriate cryptographic use case and/or technique.',
    '4.1': 'Analyze data to enable monitoring and response activities.',
    '4.2': 'Analyze vulnerabilities and attacks and reduce the attack surface.',
    '4.3': 'Apply threat-hunting and threat-intelligence concepts.',
    '4.4': 'Analyze data and artifacts in support of incident response.'
  };
  const PROGRESS_LABELS = ['Unseen', 'Seen', 'Learning', 'Strong', 'Mastered'];

  const els = Object.fromEntries([
    'grid','crumbs','status','levelLabel','levelTitle','levelIntro','position',
    'detailKicker','detailTitle','chips','depthMeter','detailBody',
    'searchDialog','searchInput','searchResults','searchForm','progressSummary','relatedHint'
  ].map(id => [id, document.getElementById(id)]));

  const state = {
    cards: [], cardById: new Map(), blueprint: [], blueprintByCard: new Map(), blueprintByConcept: new Map(),
    scopes: [{ type: 'root', title: 'SecX', parentSelected: 0 }], selected: 0, depth: 0, cols: 3, items: [],
    searchMatches: [], searchSelected: 0, progress: loadProgress()
  };

  function loadProgress() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); }
    catch (_) { return {}; }
  }
  function saveProgress() { localStorage.setItem(STORAGE_KEY, JSON.stringify(state.progress)); }
  function progressLevel(id) { return Math.max(0, Math.min(4, Number(state.progress[id]?.level || 0))); }
  function setProgress(id, level) {
    state.progress[id] = { level: Math.max(0, Math.min(4, level)), updated: new Date().toISOString() };
    saveProgress();
  }
  function markSeen(card) {
    if (card && progressLevel(card.id) === 0) setProgress(card.id, 1);
  }
  function cycleProgress() {
    const item = state.items[state.selected];
    if (item?.type !== 'card') return;
    const next = progressLevel(item.card.id) >= 4 ? 1 : progressLevel(item.card.id) + 1;
    setProgress(item.card.id, next);
    render();
  }

  function loadScript(src) {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = src;
      script.onload = resolve;
      script.onerror = () => reject(new Error(`Could not load ${src}`));
      document.head.appendChild(script);
    });
  }

  async function loadDeck() {
    await loadScript(`${DATA_BASE}meta.js`);
    for (let i = 1; i <= 29; i += 1) await loadScript(`${DATA_BASE}cards-${String(i).padStart(3, '0')}.js`);
    state.cards = window.SX_DECK?.cards || [];
    if (state.cards.length !== 1156) throw new Error(`Expected audited 1156-card deck; loaded ${state.cards.length}`);
    state.cardById = new Map(state.cards.map(card => [card.id, card]));
    const response = await fetch(`${DATA_BASE}blueprint_index.json`);
    state.blueprint = response.ok ? (await response.json()).entries || [] : [];
    if (state.blueprint.length !== 618) throw new Error(`Expected 618 blueprint mappings; loaded ${state.blueprint.length}`);
    buildBlueprintMaps();
  }

  function buildBlueprintMaps() {
    for (const entry of state.blueprint) {
      const direct = state.blueprintByCard.get(entry.card_id) || [];
      direct.push(entry);
      state.blueprintByCard.set(entry.card_id, direct);
    }
    for (const card of state.cards) {
      const key = `${card.concept_id || ''}::${card.objective}`;
      const shared = state.blueprintByConcept.get(key) || [];
      for (const entry of state.blueprintByCard.get(card.id) || []) if (!shared.some(x => x.id === entry.id)) shared.push(entry);
      state.blueprintByConcept.set(key, shared);
    }
  }

  const unique = values => [...new Set(values.filter(Boolean))];
  const currentScope = () => state.scopes[state.scopes.length - 1];
  const sortObjective = (a, b) => Number(a.replace('.', '')) - Number(b.replace('.', ''));
  const cardsFor = criteria => state.cards.filter(card => Object.entries(criteria).every(([key, value]) => card[key] === value));

  function rootItems() {
    const items = [{ type: 'secx', key: 'secx', title: 'SecX', code: 'START', row: 2, col: 2, count: state.cards.length }];
    for (const domain of DOMAIN_ORDER) {
      const [col, row] = DOMAIN_META[domain].root;
      items.push({ type: 'domain', key: domain, title: domain, code: `${DOMAIN_META[domain].direction} ${DOMAIN_META[domain].weight}%`, domain, row, col, count: cardsFor({ domain }).length });
    }
    return items;
  }

  function itemsForScope(scope) {
    if (scope.type === 'root') return rootItems();
    if (scope.type === 'index') return [
      ...DOMAIN_ORDER.map(domain => ({ type: 'domain', key: domain, title: domain, code: `${DOMAIN_META[domain].weight}%`, domain, count: cardsFor({ domain }).length })),
      { type: 'acronyms', key: 'Acronyms', title: 'Acronyms', code: 'REFERENCE', count: cardsFor({ objective: 'Acronyms' }).length },
      { type: 'progress', key: 'Progress', title: 'Study Progress', code: 'LOCAL', count: Object.keys(state.progress).length }
    ];
    if (scope.type === 'domain') {
      return unique(cardsFor({ domain: scope.domain }).map(c => c.objective)).sort(sortObjective).map(objective => ({
        type: 'objective', key: objective, title: OBJECTIVES[objective] || objective, code: objective, domain: scope.domain, objective,
        count: cardsFor({ domain: scope.domain, objective }).length
      }));
    }
    if (scope.type === 'objective') {
      const cards = cardsFor({ domain: scope.domain, objective: scope.objective });
      return unique(cards.map(c => c.subdomain)).sort().map(subdomain => ({ type: 'subdomain', key: subdomain, title: subdomain, code: scope.objective, domain: scope.domain, objective: scope.objective, subdomain, count: cards.filter(c => c.subdomain === subdomain).length }));
    }
    if (scope.type === 'subdomain') {
      const cards = cardsFor({ domain: scope.domain, objective: scope.objective, subdomain: scope.subdomain });
      return unique(cards.map(c => c.topic)).sort().map(topic => ({ type: 'topic', key: topic, title: topic, code: 'TOPIC', domain: scope.domain, objective: scope.objective, subdomain: scope.subdomain, topic, count: cards.filter(c => c.topic === topic).length }));
    }
    if (scope.type === 'topic') return cardsFor({ domain: scope.domain, objective: scope.objective, subdomain: scope.subdomain, topic: scope.topic }).map(cardItem);
    if (scope.type === 'acronyms') {
      const cards = cardsFor({ objective: 'Acronyms' });
      return unique(cards.map(c => (c.topic || c.front || '#').trim().charAt(0).toUpperCase())).sort().map(letter => ({ type: 'acronym-letter', key: letter, title: `${letter} acronyms`, code: 'A–Z', letter, count: cards.filter(c => (c.topic || c.front || '#').trim().charAt(0).toUpperCase() === letter).length }));
    }
    if (scope.type === 'acronym-letter') return cardsFor({ objective: 'Acronyms' }).filter(c => (c.topic || c.front || '#').trim().charAt(0).toUpperCase() === scope.letter).sort((a, b) => (a.topic || a.front).localeCompare(b.topic || b.front)).map(cardItem);
    if (scope.type === 'related') return relatedCards(scope.card).map(({ card, relation }) => ({ ...cardItem(card), code: relation }));
    if (scope.type === 'progress') return [1, 2, 3, 4].map(level => ({ type: 'progress-level', key: String(level), title: PROGRESS_LABELS[level], code: 'STATUS', level, count: state.cards.filter(c => progressLevel(c.id) === level).length }));
    if (scope.type === 'progress-level') return state.cards.filter(c => progressLevel(c.id) === scope.level).map(cardItem);
    return [];
  }

  function cardItem(card) { return { type: 'card', key: card.id, title: card.front, code: card.card_type || 'CARD', card }; }

  function itemBlueprint(item) {
    if (item?.type !== 'card') return [];
    const direct = state.blueprintByCard.get(item.card.id) || [];
    return direct.length ? direct : (state.blueprintByConcept.get(`${item.card.concept_id || ''}::${item.card.objective}`) || []);
  }

  function relatedCards(card) {
    if (!card) return [];
    const out = new Map();
    const add = (candidate, relation) => {
      if (!candidate || candidate.id === card.id || out.has(candidate.id)) return;
      out.set(candidate.id, { card: candidate, relation });
    };
    for (const id of card.prerequisites || []) add(state.cardById.get(id), 'PREREQUISITE');
    for (const candidate of state.cards) if (card.concept_id && candidate.concept_id === card.concept_id) add(candidate, 'SAME CONCEPT');
    const bpIds = new Set(itemBlueprint({ type: 'card', card }).map(x => x.id));
    if (bpIds.size) for (const candidate of state.cards) if (itemBlueprint({ type: 'card', card: candidate }).some(x => bpIds.has(x.id))) add(candidate, 'SAME BLUEPRINT');
    for (const candidate of cardsFor({ domain: card.domain, objective: card.objective, subdomain: card.subdomain, topic: card.topic })) add(candidate, 'SAME TOPIC');
    return [...out.values()].slice(0, 40);
  }

  function colsFor(count, scope) {
    if (scope.type === 'root') return 3;
    if (count <= 4) return 2;
    if (count <= 9) return 3;
    if (count <= 16) return 4;
    return 5;
  }

  function breadcrumbParts() {
    return state.scopes.map(scope => ({ root: 'SecX', index: 'Index', acronyms: 'Acronyms', progress: 'Progress', related: 'Related' }[scope.type] || scope.letter || scope.topic || scope.subdomain || scope.objective || DOMAIN_META[scope.domain]?.short || scope.title || scope.type));
  }

  function scopeTitle(scope) {
    if (scope.type === 'root') return 'SecX';
    if (scope.type === 'index') return 'Complete SecurityX Index';
    if (scope.type === 'domain') return scope.domain;
    if (scope.type === 'objective') return `${scope.objective} · ${OBJECTIVES[scope.objective] || ''}`;
    if (scope.type === 'subdomain') return scope.subdomain;
    if (scope.type === 'topic') return scope.topic;
    if (scope.type === 'acronyms') return 'SecurityX Acronyms';
    if (scope.type === 'acronym-letter') return `${scope.letter} Acronyms`;
    if (scope.type === 'related') return `Related · ${scope.card.topic || scope.card.id}`;
    if (scope.type === 'progress') return 'Study Progress';
    if (scope.type === 'progress-level') return PROGRESS_LABELS[scope.level];
    return 'SecX';
  }

  function scopeIntro(scope) {
    if (scope.type === 'root') return 'SecX is the center. Arrow toward a domain and press Enter. Space deepens the selected idea without leaving the grid.';
    if (scope.type === 'index') return 'Domains, acronym reference, and local study progress. All navigation remains keyboard-first.';
    if (scope.type === 'domain') return `${DOMAIN_META[scope.domain]?.weight || ''}% of the public CAS-005 blueprint.`;
    if (scope.type === 'objective') return OBJECTIVES[scope.objective] || '';
    if (scope.type === 'subdomain') return `Choose a topic within ${scope.subdomain}.`;
    if (scope.type === 'topic') return 'Choose a card. Space reveals its eight audited layers; M changes study status; R opens exact related cards.';
    if (scope.type === 'related') return 'Relationships are derived only from exact prerequisite IDs, concept IDs, blueprint mappings, and same-topic membership.';
    if (scope.type === 'progress') return 'Progress is stored only in this browser.';
    if (scope.type === 'progress-level') return `Cards currently marked ${PROGRESS_LABELS[scope.level]}.`;
    return 'Use arrows to move one grid cell.';
  }

  function labelForScope(scope) { return ({ root: 'START', index: 'INDEX', domain: 'DOMAIN', objective: 'OBJECTIVE', subdomain: 'SUBDOMAIN', topic: 'TOPIC', acronyms: 'ACRONYMS', 'acronym-letter': 'ACRONYM GROUP', related: 'RELATIONSHIPS', progress: 'PROGRESS', 'progress-level': 'PROGRESS FILTER' })[scope.type] || 'GRID'; }

  function descendantCards(item) {
    if (!item) return [];
    if (item.type === 'card') return [item.card];
    const criteria = {};
    for (const key of ['domain','objective','subdomain','topic']) if (item[key]) criteria[key] = item[key];
    if (Object.keys(criteria).length) return cardsFor(criteria);
    if (item.type === 'acronyms') return cardsFor({ objective: 'Acronyms' });
    return [];
  }

  function progressText(cards) {
    if (!cards.length) return '';
    const seen = cards.filter(c => progressLevel(c.id) > 0).length;
    const mastered = cards.filter(c => progressLevel(c.id) === 4).length;
    return `${seen}/${cards.length} seen · ${mastered} mastered`;
  }

  function render() {
    const scope = currentScope();
    state.items = itemsForScope(scope);
    state.cols = colsFor(state.items.length, scope);
    state.selected = Math.max(0, Math.min(state.selected, Math.max(0, state.items.length - 1)));
    const selected = state.items[state.selected];
    if (selected?.type === 'card') markSeen(selected.card);

    els.crumbs.textContent = breadcrumbParts().join('  ›  ');
    els.levelLabel.textContent = labelForScope(scope);
    els.levelTitle.textContent = scopeTitle(scope);
    els.levelIntro.textContent = scopeIntro(scope);
    els.position.textContent = state.items.length ? `${state.selected + 1} / ${state.items.length}` : '';
    const seen = state.cards.filter(c => progressLevel(c.id) > 0).length;
    const mastered = state.cards.filter(c => progressLevel(c.id) === 4).length;
    els.status.textContent = `1,156 audited cards · 618 blueprint examples · ${seen} seen · ${mastered} mastered`;
    if (els.progressSummary) els.progressSummary.textContent = `${seen.toLocaleString()} seen · ${mastered.toLocaleString()} mastered · local only`;
    if (els.relatedHint) els.relatedHint.textContent = selected?.type === 'card' ? `${relatedCards(selected.card).length} exact related cards · R to open` : '';

    els.grid.className = `grid ${scope.type === 'root' ? 'root-grid' : ''}`;
    els.grid.style.setProperty('--cols', state.cols);
    els.grid.innerHTML = '';
    state.items.forEach((item, index) => {
      const button = document.createElement('button');
      const level = item.type === 'card' ? progressLevel(item.card.id) : 0;
      button.className = `tile ${item.type === 'secx' ? 'center' : ''} ${index === state.selected ? 'selected' : ''} progress-${level}`;
      button.type = 'button'; button.setAttribute('role', 'gridcell'); button.tabIndex = index === state.selected ? 0 : -1;
      if (scope.type === 'root') { button.style.gridColumn = item.col; button.style.gridRow = item.row; }
      const childCards = descendantCards(item);
      const sub = item.type === 'card' ? PROGRESS_LABELS[level] : progressText(childCards);
      button.innerHTML = `${item.count != null ? `<span class="count">${item.count}</span>` : ''}<span class="code">${escapeHtml(item.code || '')}</span><strong>${escapeHtml(item.title)}</strong>${sub ? `<small>${escapeHtml(sub)}</small>` : ''}`;
      button.addEventListener('click', () => { state.selected = index; state.depth = 0; render(); });
      button.addEventListener('dblclick', descend);
      els.grid.appendChild(button);
    });
    renderDetail();
    requestAnimationFrame(() => els.grid.querySelector('.tile.selected')?.scrollIntoView({ block: 'nearest', inline: 'nearest' }));
  }

  function cardChips(card) {
    const bp = itemBlueprint({ type: 'card', card });
    return [
      `ID · ${card.id}`, card.concept_id && `Concept · ${card.concept_id}`, card.domain, `Objective ${card.objective}`, card.subdomain, card.topic,
      `Type · ${card.card_type}`, `Difficulty · ${card.difficulty}`, card.stage, `Progress · ${PROGRESS_LABELS[progressLevel(card.id)]}`,
      ...bp.map(x => `Blueprint · ${x.topic}`), ...(card.source_ids || []).map(x => `Source · ${x}`), ...(card.tags || []).map(x => `Tag · ${x}`), ...(card.modalities || []).map(x => `Mode · ${x}`)
    ].filter(Boolean);
  }

  function renderDetail() {
    const item = state.items[state.selected];
    if (!item) return;
    const card = item.type === 'card' ? item.card : null;
    els.detailKicker.textContent = card ? `CARD · DEPTH ${state.depth}/8` : `${item.type.toUpperCase()} · DEPTH ${state.depth}`;
    els.detailTitle.textContent = card ? (card.topic || card.front) : item.title;
    const chips = card ? cardChips(card) : [item.type, item.domain, item.objective && `Objective ${item.objective}`, item.subdomain, item.topic].filter(Boolean);
    els.chips.innerHTML = chips.map(x => `<span class="chip">${escapeHtml(String(x))}</span>`).join('');
    const maxDepth = card ? 8 : 4;
    els.depthMeter.innerHTML = Array.from({ length: maxDepth + 1 }, (_, i) => `<span class="depth-dot ${i <= state.depth ? 'on' : ''}"></span>`).join('');
    els.detailBody.innerHTML = detailHtml(item);
  }

  function detailHtml(item) {
    if (item.type === 'card') {
      const card = item.card;
      if (state.depth === 0) return `<p><b>${escapeHtml(card.front)}</b></p><p class="hint">Space → direct answer and deeper layers · Shift+Space → shallower · M → ${escapeHtml(PROGRESS_LABELS[progressLevel(card.id)])} status · R → exact relationships.</p>`;
      const page = card.pages[state.depth - 1];
      return `<h3>${escapeHtml(page.title)}</h3><div>${cleanLayer(page.content)}</div>`;
    }
    if (item.type === 'secx') {
      const layers = [
        '<p><b>SecX</b> is the root of the SecurityX CAS-005 knowledge grid.</p>',
        '<h3>Exam map</h3><p>4 domains · 23 numbered objectives · 20/27/31/22 weighting · 1,156 audited layered cards.</p>',
        '<h3>Hierarchy</h3><p>SecX → domain → objective → subdomain → topic → card. Acronyms and progress live in the complete index.</p>',
        '<h3>Knowledge web</h3><p>The visible interface stays a deterministic grid. Exact graph edges are exposed through prerequisites, shared concept IDs, blueprint mappings, and same-topic membership.</p>',
        '<h3>Study model</h3><p>Space controls information depth. M records confidence locally. Search and relationship jumps preserve the knowledge hierarchy.</p>'
      ];
      return layers[Math.min(state.depth, 4)];
    }
    const cards = descendantCards(item);
    if (state.depth === 0) return `<p>${escapeHtml(item.title)}</p><p class="hint">${item.count != null ? `${item.count} items beneath this node. ` : ''}Enter descends; Space inspects without moving.</p>`;
    if (state.depth === 1) return `<h3>Scope</h3><p>${escapeHtml(item.type === 'objective' ? (OBJECTIVES[item.objective] || item.title) : scopeIntro({ ...item, type: item.type }))}</p>`;
    if (state.depth === 2) return `<h3>Coverage</h3><p>${escapeHtml(progressText(cards) || `${cards.length} supporting cards`)}</p><p>${unique(cards.slice(0, 24).map(c => c.topic)).slice(0, 16).map(escapeHtml).join(' · ')}</p>`;
    if (state.depth === 3) return `<h3>Representative retrieval prompts</h3>${cards.slice(0, 5).map(c => `<p>• ${escapeHtml(c.front)}</p>`).join('') || '<p>No card sample.</p>'}`;
    return `<h3>Source families</h3><p>${unique(cards.slice(0, 50).flatMap(c => c.source_ids || [])).map(escapeHtml).join(' · ') || 'CompTIA CAS-005 public blueprint and supporting sources.'}</p>`;
  }

  function cleanLayer(content) {
    const holder = document.createElement('div'); holder.innerHTML = content || '';
    for (const link of holder.querySelectorAll('a')) { link.target = '_blank'; link.rel = 'noopener noreferrer'; }
    return holder.innerHTML;
  }
  function escapeHtml(value) { return String(value ?? '').replace(/[&<>'"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[ch])); }

  function pushScope(next) {
    currentScope().parentSelected = state.selected;
    state.scopes.push({ ...next, parentSelected: 0 });
    state.selected = 0; state.depth = 0; render();
  }

  function descend() {
    const item = state.items[state.selected];
    if (!item || item.type === 'card') return;
    if (item.type === 'secx') return pushScope({ type: 'index', title: 'Complete SecurityX Index' });
    if (item.type === 'domain') return pushScope({ type: 'domain', domain: item.domain, title: item.domain });
    if (item.type === 'objective') return pushScope({ type: 'objective', domain: item.domain, objective: item.objective, title: item.objective });
    if (item.type === 'subdomain') return pushScope({ type: 'subdomain', domain: item.domain, objective: item.objective, subdomain: item.subdomain, title: item.subdomain });
    if (item.type === 'topic') return pushScope({ type: 'topic', domain: item.domain, objective: item.objective, subdomain: item.subdomain, topic: item.topic, title: item.topic });
    if (item.type === 'acronyms') return pushScope({ type: 'acronyms', title: 'Acronyms' });
    if (item.type === 'acronym-letter') return pushScope({ type: 'acronym-letter', letter: item.letter, title: item.title });
    if (item.type === 'progress') return pushScope({ type: 'progress', title: 'Study Progress' });
    if (item.type === 'progress-level') return pushScope({ type: 'progress-level', level: item.level, title: item.title });
  }

  function ascend() {
    if (state.scopes.length <= 1) return;
    state.scopes.pop();
    state.selected = currentScope().parentSelected || 0;
    state.depth = 0; render();
  }

  function resetHome() { state.scopes = [{ type: 'root', title: 'SecX', parentSelected: 0 }]; state.selected = 0; state.depth = 0; render(); }

  function move(direction) {
    const scope = currentScope();
    if (!state.items.length) return;
    if (scope.type === 'root') return moveRoot(direction);
    const n = state.items.length, cols = state.cols, rows = Math.ceil(n / cols);
    let row = Math.floor(state.selected / cols), col = state.selected % cols;
    const dr = direction === 'up' ? -1 : direction === 'down' ? 1 : 0;
    const dc = direction === 'left' ? -1 : direction === 'right' ? 1 : 0;
    for (let tries = 0; tries < Math.max(rows, cols) + 2; tries += 1) {
      row = (row + dr + rows) % rows; col = (col + dc + cols) % cols;
      const candidate = row * cols + col;
      if (candidate < n && candidate !== state.selected) { state.selected = candidate; state.depth = 0; render(); return; }
    }
  }

  function moveRoot(direction) {
    const current = state.items[state.selected];
    const coords = new Map(state.items.map((item, index) => [`${item.col},${item.row}`, index]));
    const delta = { left: [-1, 0], right: [1, 0], up: [0, -1], down: [0, 1] }[direction];
    let col = current.col, row = current.row;
    for (let i = 0; i < 3; i += 1) {
      col = ((col - 1 + delta[0] + 3) % 3) + 1; row = ((row - 1 + delta[1] + 3) % 3) + 1;
      const hit = coords.get(`${col},${row}`);
      if (hit != null && hit !== state.selected) { state.selected = hit; state.depth = 0; render(); return; }
    }
  }

  function deepen(delta = 1) {
    const item = state.items[state.selected]; if (!item) return;
    const max = item.type === 'card' ? 8 : 4;
    state.depth = Math.max(0, Math.min(max, state.depth + delta)); renderDetail();
  }

  function openRelated() {
    const item = state.items[state.selected];
    if (item?.type !== 'card') return;
    const related = relatedCards(item.card); if (!related.length) return;
    pushScope({ type: 'related', card: item.card, title: 'Related' });
  }

  function openSearch() {
    state.searchMatches = []; state.searchSelected = 0; els.searchInput.value = '';
    els.searchResults.innerHTML = '<div class="search-result"><b>Search all 1,156 cards</b><small>Concept, objective, acronym, source, tag, or tool.</small></div>';
    els.searchDialog.showModal(); requestAnimationFrame(() => els.searchInput.focus());
  }
  function search(query) {
    const q = query.trim().toLowerCase();
    state.searchMatches = !q ? [] : state.cards.filter(card => [card.front, card.topic, card.subdomain, card.objective, card.domain, card.concept_id, ...(card.tags || []), ...(card.source_ids || [])].join(' ').toLowerCase().includes(q)).slice(0, 40);
    state.searchSelected = 0; renderSearch();
  }
  function renderSearch() {
    if (!state.searchMatches.length) { els.searchResults.innerHTML = '<div class="search-result"><b>No matches yet</b><small>Try another term.</small></div>'; return; }
    els.searchResults.innerHTML = state.searchMatches.map((card, index) => `<div class="search-result ${index === state.searchSelected ? 'active' : ''}" data-search-index="${index}"><b>${escapeHtml(card.topic || card.front)}</b><small>${escapeHtml(card.objective)} · ${escapeHtml(card.subdomain || card.domain)} · ${escapeHtml(PROGRESS_LABELS[progressLevel(card.id)])}</small></div>`).join('');
  }

  function jumpToCard(card) {
    if (!card) return;
    if (card.objective === 'Acronyms') {
      const letter = (card.topic || card.front).trim().charAt(0).toUpperCase();
      state.scopes = [{ type: 'root', title: 'SecX', parentSelected: 0 }, { type: 'index', title: 'Index', parentSelected: 0 }, { type: 'acronyms', title: 'Acronyms', parentSelected: 0 }, { type: 'acronym-letter', letter, title: `${letter} Acronyms`, parentSelected: 0 }];
    } else {
      state.scopes = [{ type: 'root', title: 'SecX', parentSelected: 0 }, { type: 'domain', domain: card.domain, title: card.domain, parentSelected: 0 }, { type: 'objective', domain: card.domain, objective: card.objective, title: card.objective, parentSelected: 0 }, { type: 'subdomain', domain: card.domain, objective: card.objective, subdomain: card.subdomain, title: card.subdomain, parentSelected: 0 }, { type: 'topic', domain: card.domain, objective: card.objective, subdomain: card.subdomain, topic: card.topic, title: card.topic, parentSelected: 0 }];
    }
    state.items = itemsForScope(currentScope()); state.selected = Math.max(0, state.items.findIndex(item => item.type === 'card' && item.card.id === card.id)); state.depth = 0;
    history.replaceState(null, '', `#card=${encodeURIComponent(card.id)}`);
    if (els.searchDialog.open) els.searchDialog.close(); render();
  }

  function restoreHash() {
    const match = location.hash.match(/^#card=(SX-[A-Za-z0-9-]+)$/);
    if (match) jumpToCard(state.cardById.get(match[1]));
  }

  document.addEventListener('keydown', event => {
    if (els.searchDialog.open) return;
    const key = event.key;
    if (['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Enter','Escape',' ','Home','/','m','M','r','R'].includes(key)) event.preventDefault();
    if (key === 'ArrowLeft') move('left'); else if (key === 'ArrowRight') move('right'); else if (key === 'ArrowUp') move('up'); else if (key === 'ArrowDown') move('down');
    else if (key === 'Enter') descend(); else if (key === 'Escape') ascend(); else if (key === ' ') deepen(event.shiftKey ? -1 : 1); else if (key === 'Home') resetHome(); else if (key === '/') openSearch(); else if (key.toLowerCase() === 'm') cycleProgress(); else if (key.toLowerCase() === 'r') openRelated();
  });

  els.searchInput.addEventListener('input', () => search(els.searchInput.value));
  els.searchDialog.addEventListener('keydown', event => {
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault(); if (!state.searchMatches.length) return;
      state.searchSelected = (state.searchSelected + (event.key === 'ArrowDown' ? 1 : -1) + state.searchMatches.length) % state.searchMatches.length; renderSearch();
      els.searchResults.querySelector('.active')?.scrollIntoView({ block: 'nearest' });
    } else if (event.key === 'Enter' && state.searchMatches.length) { event.preventDefault(); jumpToCard(state.searchMatches[state.searchSelected]); }
  });
  els.searchResults.addEventListener('click', event => { const row = event.target.closest('[data-search-index]'); if (row) jumpToCard(state.searchMatches[Number(row.dataset.searchIndex)]); });

  loadDeck().then(() => { render(); restoreHash(); }).catch(error => {
    els.status.textContent = 'Alternate site data load failed'; els.levelTitle.textContent = 'Could not load SecurityX deck'; els.levelIntro.textContent = error.message; console.error(error);
  });
})();
