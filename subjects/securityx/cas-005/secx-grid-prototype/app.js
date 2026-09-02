(() => {
  'use strict';

  const DATA_BASE = '../study-site/data/';
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

  const els = Object.fromEntries([
    'grid','crumbs','status','levelLabel','levelTitle','levelIntro','position',
    'detailKicker','detailTitle','chips','depthMeter','detailBody',
    'searchDialog','searchInput','searchResults','searchForm'
  ].map(id => [id, document.getElementById(id)]));

  const state = {
    cards: [],
    blueprint: [],
    blueprintByCard: new Map(),
    blueprintByConcept: new Map(),
    scopes: [{ type: 'root', title: 'SecX' }],
    selected: 0,
    depth: 0,
    cols: 3,
    items: [],
    searchMatches: [],
    searchSelected: 0
  };

  function loadScript(src) {
    return new Promise((resolve, reject) => {
      const s = document.createElement('script');
      s.src = src;
      s.onload = resolve;
      s.onerror = () => reject(new Error(`Could not load ${src}`));
      document.head.appendChild(s);
    });
  }

  async function loadDeck() {
    await loadScript(`${DATA_BASE}meta.js`);
    for (let i = 1; i <= 29; i += 1) {
      await loadScript(`${DATA_BASE}cards-${String(i).padStart(3, '0')}.js`);
    }
    state.cards = window.SX_DECK?.cards || [];
    if (state.cards.length !== 1156) {
      throw new Error(`Expected audited 1156-card deck; loaded ${state.cards.length}`);
    }
    try {
      const response = await fetch(`${DATA_BASE}blueprint_index.json`);
      if (response.ok) state.blueprint = (await response.json()).entries || [];
    } catch (_) {
      state.blueprint = [];
    }
    buildBlueprintMaps();
  }

  function buildBlueprintMaps() {
    for (const entry of state.blueprint) {
      const arr = state.blueprintByCard.get(entry.card_id) || [];
      arr.push(entry);
      state.blueprintByCard.set(entry.card_id, arr);
    }
    for (const card of state.cards) {
      const key = `${card.concept_id || ''}::${card.objective}`;
      const arr = state.blueprintByConcept.get(key) || [];
      for (const entry of state.blueprintByCard.get(card.id) || []) {
        if (!arr.some(x => x.id === entry.id)) arr.push(entry);
      }
      state.blueprintByConcept.set(key, arr);
    }
  }

  function currentScope() { return state.scopes[state.scopes.length - 1]; }
  function unique(values) { return [...new Set(values.filter(Boolean))]; }
  function sortObjective(a, b) { return Number(a.replace('.', '')) - Number(b.replace('.', '')); }
  function cardsFor(criteria) {
    return state.cards.filter(card => Object.entries(criteria).every(([k, v]) => card[k] === v));
  }

  function rootItems() {
    const items = [{ type: 'secx', key: 'secx', title: 'SecX', code: 'START', row: 2, col: 2, count: state.cards.length }];
    for (const domain of DOMAIN_ORDER) {
      const [col, row] = DOMAIN_META[domain].root;
      items.push({
        type: 'domain', key: domain, title: domain, code: `${DOMAIN_META[domain].direction} ${DOMAIN_META[domain].weight}%`,
        domain, row, col, count: cardsFor({ domain }).length
      });
    }
    return items;
  }

  function itemsForScope(scope) {
    if (scope.type === 'root') return rootItems();
    if (scope.type === 'index') {
      return [
        ...DOMAIN_ORDER.map(domain => ({ type: 'domain', key: domain, title: domain, code: `${DOMAIN_META[domain].weight}%`, domain, count: cardsFor({ domain }).length })),
        { type: 'acronyms', key: 'Acronyms', title: 'Acronyms', code: 'REFERENCE', count: cardsFor({ objective: 'Acronyms' }).length }
      ];
    }
    if (scope.type === 'domain') {
      const objectives = unique(cardsFor({ domain: scope.domain }).map(c => c.objective)).sort(sortObjective);
      return objectives.map(objective => {
        const cards = cardsFor({ domain: scope.domain, objective });
        return { type: 'objective', key: objective, title: OBJECTIVES[objective] || objective, code: objective, domain: scope.domain, objective, count: cards.length };
      });
    }
    if (scope.type === 'objective') {
      const cards = cardsFor({ domain: scope.domain, objective: scope.objective });
      return unique(cards.map(c => c.subdomain)).sort().map(subdomain => ({
        type: 'subdomain', key: subdomain, title: subdomain, code: scope.objective,
        domain: scope.domain, objective: scope.objective, subdomain,
        count: cards.filter(c => c.subdomain === subdomain).length
      }));
    }
    if (scope.type === 'subdomain') {
      const cards = cardsFor({ domain: scope.domain, objective: scope.objective, subdomain: scope.subdomain });
      return unique(cards.map(c => c.topic)).sort().map(topic => ({
        type: 'topic', key: topic, title: topic, code: 'TOPIC',
        domain: scope.domain, objective: scope.objective, subdomain: scope.subdomain, topic,
        count: cards.filter(c => c.topic === topic).length
      }));
    }
    if (scope.type === 'topic') {
      return cardsFor({ domain: scope.domain, objective: scope.objective, subdomain: scope.subdomain, topic: scope.topic })
        .map(card => ({ type: 'card', key: card.id, title: card.front, code: card.card_type, card, count: null }));
    }
    if (scope.type === 'acronyms') {
      const cards = cardsFor({ objective: 'Acronyms' });
      const letters = unique(cards.map(c => (c.topic || c.front || '#').trim().charAt(0).toUpperCase())).sort();
      return letters.map(letter => ({
        type: 'acronym-letter', key: letter, title: `${letter} acronyms`, code: 'A–Z', letter,
        count: cards.filter(c => (c.topic || c.front || '#').trim().charAt(0).toUpperCase() === letter).length
      }));
    }
    if (scope.type === 'acronym-letter') {
      return cardsFor({ objective: 'Acronyms' })
        .filter(c => (c.topic || c.front || '#').trim().charAt(0).toUpperCase() === scope.letter)
        .sort((a, b) => (a.topic || a.front).localeCompare(b.topic || b.front))
        .map(card => ({ type: 'card', key: card.id, title: card.front, code: 'ACRONYM', card, count: null }));
    }
    return [];
  }

  function colsFor(count, scope) {
    if (scope.type === 'root') return 3;
    if (count <= 4) return 2;
    if (count <= 9) return 3;
    if (count <= 16) return 4;
    return 5;
  }

  function labelForScope(scope) {
    return ({ root: 'START', index: 'INDEX', domain: 'DOMAIN', objective: 'OBJECTIVE', subdomain: 'SUBDOMAIN', topic: 'TOPIC', acronyms: 'ACRONYMS', 'acronym-letter': 'ACRONYM GROUP' })[scope.type] || 'GRID';
  }

  function introForScope(scope) {
    if (scope.type === 'root') return 'Four SecurityX domains surround the center. Arrow to a domain, then Enter to descend. Enter on SecX opens the complete index.';
    if (scope.type === 'index') return 'All exam domains plus the official acronym-support deck. Arrows move one grid cell; Enter descends.';
    if (scope.type === 'domain') return `${DOMAIN_META[scope.domain]?.weight || ''}% of the public CAS-005 blueprint. Choose an objective.`;
    if (scope.type === 'objective') return OBJECTIVES[scope.objective] || 'Choose a subdomain.';
    if (scope.type === 'subdomain') return `Choose a topic within ${scope.subdomain}.`;
    if (scope.type === 'topic') return 'Choose a recall or application card. Space reveals its audited layers one at a time.';
    if (scope.type === 'acronyms') return 'Browse the supporting acronym deck alphabetically.';
    if (scope.type === 'acronym-letter') return `Acronyms beginning with ${scope.letter}.`;
    return '';
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
    return 'SecX';
  }

  function breadcrumbParts() {
    return state.scopes.map(scope => {
      if (scope.type === 'root') return 'SecX';
      if (scope.type === 'domain') return DOMAIN_META[scope.domain]?.short || scope.domain;
      if (scope.type === 'objective') return scope.objective;
      if (scope.type === 'subdomain') return scope.subdomain;
      if (scope.type === 'topic') return scope.topic;
      if (scope.type === 'index') return 'Index';
      if (scope.type === 'acronyms') return 'Acronyms';
      if (scope.type === 'acronym-letter') return scope.letter;
      return scope.title || scope.type;
    });
  }

  function render() {
    const scope = currentScope();
    state.items = itemsForScope(scope);
    state.cols = colsFor(state.items.length, scope);
    if (state.selected >= state.items.length) state.selected = Math.max(0, state.items.length - 1);

    els.crumbs.textContent = breadcrumbParts().join('  ›  ');
    els.levelLabel.textContent = labelForScope(scope);
    els.levelTitle.textContent = scopeTitle(scope);
    els.levelIntro.textContent = introForScope(scope);
    els.status.textContent = `${state.cards.length.toLocaleString()} audited cards · ${state.blueprint.length || 618} blueprint examples · keyboard mode`;
    els.position.textContent = state.items.length ? `${state.selected + 1} / ${state.items.length}` : '';

    els.grid.className = `grid ${scope.type === 'root' ? 'root-grid' : ''}`;
    els.grid.style.setProperty('--cols', state.cols);
    els.grid.innerHTML = '';
    state.items.forEach((item, index) => {
      const button = document.createElement('button');
      button.className = `tile ${item.type === 'secx' ? 'center' : ''} ${index === state.selected ? 'selected' : ''}`;
      button.type = 'button';
      button.setAttribute('role', 'gridcell');
      button.tabIndex = index === state.selected ? 0 : -1;
      button.dataset.index = index;
      if (scope.type === 'root') {
        button.style.gridColumn = item.col;
        button.style.gridRow = item.row;
      }
      button.innerHTML = `${item.count != null ? `<span class="count">${item.count}</span>` : ''}<span class="code">${escapeHtml(item.code || '')}</span><strong>${escapeHtml(item.title)}</strong>${item.type === 'secx' ? '<small>SecurityX CAS-005 knowledge grid</small>' : ''}`;
      button.addEventListener('click', () => select(index, true));
      button.addEventListener('dblclick', descend);
      els.grid.appendChild(button);
    });
    renderDetail();
    requestAnimationFrame(() => els.grid.querySelector('.tile.selected')?.focus({ preventScroll: true }));
  }

  function select(index, focus = false) {
    if (!state.items.length) return;
    state.selected = Math.max(0, Math.min(index, state.items.length - 1));
    state.depth = 0;
    render();
    if (focus) els.grid.querySelector('.tile.selected')?.focus({ preventScroll: true });
  }

  function itemBlueprint(item) {
    if (item?.type !== 'card') return [];
    const direct = state.blueprintByCard.get(item.card.id) || [];
    if (direct.length) return direct;
    return state.blueprintByConcept.get(`${item.card.concept_id || ''}::${item.card.objective}`) || [];
  }

  function chipValues(item) {
    if (!item) return [];
    if (item.type === 'card') {
      const c = item.card;
      const bp = itemBlueprint(item);
      return [
        c.domain,
        `Objective ${c.objective}`,
        c.subdomain,
        c.topic,
        c.card_type,
        `Difficulty ${c.difficulty}`,
        c.stage,
        ...bp.slice(0, 4).map(x => `Blueprint · ${x.topic}`),
        ...(c.source_ids || []).slice(0, 4)
      ].filter(Boolean);
    }
    return [item.type, item.domain, item.objective && `Objective ${item.objective}`, item.subdomain, item.topic].filter(Boolean);
  }

  function renderDetail() {
    const item = state.items[state.selected];
    if (!item) {
      els.detailTitle.textContent = 'No items';
      els.detailBody.textContent = '';
      return;
    }
    els.detailKicker.textContent = item.type === 'card' ? `CARD · DEPTH ${state.depth}/8` : `${item.type.toUpperCase()} · DEPTH ${state.depth}`;
    els.detailTitle.textContent = item.type === 'card' ? (item.card.topic || item.card.front) : item.title;
    els.chips.innerHTML = chipValues(item).map(x => `<span class="chip">${escapeHtml(String(x))}</span>`).join('');

    const maxDepth = item.type === 'card' ? 8 : 4;
    els.depthMeter.innerHTML = Array.from({ length: maxDepth + 1 }, (_, i) => `<span class="depth-dot ${i <= state.depth ? 'on' : ''}"></span>`).join('');
    els.detailBody.innerHTML = detailHtml(item);
  }

  function detailHtml(item) {
    if (item.type === 'secx') {
      const layers = [
        '<p><b>SecX</b> is the root of the SecurityX CAS-005 knowledge system.</p><p class="hint">Arrow to a domain. Enter opens hierarchy. Space deepens information without changing position.</p>',
        '<h3>Exam structure</h3><p>4 domains · 23 numbered objectives · 20/27/31/22 weighting · 1,156 audited layered cards.</p>',
        '<h3>Navigation model</h3><p>Hierarchy is deterministic: domain → objective → subdomain → topic → card. Search can jump directly to any card while preserving its hierarchy.</p>',
        '<h3>Learning model</h3><p>Names and basic rules stay visible first. Space reveals mechanism, application, boundaries, relationships, transfer prompts, mastery evidence, and sources only when requested.</p>',
        '<h3>Why a grid?</h3><p>Every arrow key has one predictable meaning. The graph/web still exists in metadata and cross-links, but the primary interaction never requires guessing which diagonal node an arrow will choose.</p>'
      ];
      return layers[Math.min(state.depth, layers.length - 1)];
    }
    if (item.type === 'card') {
      const c = item.card;
      if (state.depth === 0) {
        return `<p><b>${escapeHtml(c.front)}</b></p><p class="hint">Press Space for the direct answer. Continue pressing Space for progressively deeper layers.</p>`;
      }
      const page = c.pages[state.depth - 1];
      return `<h3>${escapeHtml(page.title)}</h3><div>${cleanLayer(page.content)}</div>`;
    }

    const count = item.count != null ? item.count : 0;
    if (state.depth === 0) return `<p>${escapeHtml(item.title)}</p><p class="hint">${count ? `${count} cards beneath this node. ` : ''}Press Enter to descend or Space to inspect the node before moving.</p>`;
    if (state.depth === 1) {
      if (item.type === 'objective') return `<h3>${escapeHtml(item.code)}</h3><p>${escapeHtml(OBJECTIVES[item.objective] || item.title)}</p>`;
      return `<h3>Scope</h3><p>${escapeHtml(scopeSentence(item))}</p>`;
    }
    if (state.depth === 2) {
      const children = previewChildren(item);
      return `<h3>What sits underneath</h3><p>${children.map(escapeHtml).join(' · ') || 'Cards and supporting knowledge.'}</p>`;
    }
    if (state.depth === 3) {
      const sample = sampleCards(item);
      return `<h3>Representative retrieval prompts</h3>${sample.map(c => `<p>• ${escapeHtml(c.front)}</p>`).join('') || '<p>No sample available.</p>'}`;
    }
    const sources = unique(sampleCards(item, 20).flatMap(c => c.source_ids || []));
    return `<h3>Source families</h3><p>${sources.map(escapeHtml).join(' · ') || 'CompTIA CAS-005 public blueprint and supporting references.'}</p>`;
  }

  function scopeSentence(item) {
    if (item.type === 'domain') return `${item.domain} represents ${DOMAIN_META[item.domain]?.weight || '?'}% of the current public CAS-005 blueprint.`;
    if (item.type === 'subdomain') return `${item.subdomain} groups related concepts within objective ${item.objective}.`;
    if (item.type === 'topic') return `${item.topic} is a concept cluster under ${item.subdomain}, objective ${item.objective}.`;
    if (item.type === 'acronyms') return 'The supporting acronym deck preserves the public CAS-005 acronym vocabulary as retrievable cards.';
    if (item.type === 'acronym-letter') return `This group contains audited acronym cards beginning with ${item.letter}.`;
    return item.title;
  }

  function previewChildren(item) {
    if (item.type === 'domain') return unique(cardsFor({ domain: item.domain }).map(c => c.objective)).sort(sortObjective).slice(0, 16);
    if (item.type === 'objective') return unique(cardsFor({ domain: item.domain, objective: item.objective }).map(c => c.subdomain)).sort().slice(0, 16);
    if (item.type === 'subdomain') return unique(cardsFor({ domain: item.domain, objective: item.objective, subdomain: item.subdomain }).map(c => c.topic)).sort().slice(0, 16);
    if (item.type === 'topic') return cardsFor({ domain: item.domain, objective: item.objective, subdomain: item.subdomain, topic: item.topic }).map(c => c.front).slice(0, 10);
    return [];
  }

  function sampleCards(item, limit = 4) {
    if (item.type === 'domain') return cardsFor({ domain: item.domain }).slice(0, limit);
    if (item.type === 'objective') return cardsFor({ domain: item.domain, objective: item.objective }).slice(0, limit);
    if (item.type === 'subdomain') return cardsFor({ domain: item.domain, objective: item.objective, subdomain: item.subdomain }).slice(0, limit);
    if (item.type === 'topic') return cardsFor({ domain: item.domain, objective: item.objective, subdomain: item.subdomain, topic: item.topic }).slice(0, limit);
    if (item.type === 'acronyms') return cardsFor({ objective: 'Acronyms' }).slice(0, limit);
    if (item.type === 'acronym-letter') return cardsFor({ objective: 'Acronyms' }).filter(c => (c.topic || c.front).trim().charAt(0).toUpperCase() === item.letter).slice(0, limit);
    return [];
  }

  function cleanLayer(content) {
    const holder = document.createElement('div');
    holder.innerHTML = content || '';
    for (const a of holder.querySelectorAll('a')) {
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
    }
    return holder.innerHTML;
  }

  function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>'"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[ch]));
  }

  function descend() {
    const item = state.items[state.selected];
    if (!item || item.type === 'card') return;
    let next = null;
    if (item.type === 'secx') next = { type: 'index', title: 'Complete SecurityX Index' };
    if (item.type === 'domain') next = { type: 'domain', domain: item.domain, title: item.domain };
    if (item.type === 'objective') next = { type: 'objective', domain: item.domain, objective: item.objective, title: item.objective };
    if (item.type === 'subdomain') next = { type: 'subdomain', domain: item.domain, objective: item.objective, subdomain: item.subdomain, title: item.subdomain };
    if (item.type === 'topic') next = { type: 'topic', domain: item.domain, objective: item.objective, subdomain: item.subdomain, topic: item.topic, title: item.topic };
    if (item.type === 'acronyms') next = { type: 'acronyms', title: 'Acronyms' };
    if (item.type === 'acronym-letter') next = { type: 'acronym-letter', letter: item.letter, title: item.title };
    if (!next) return;
    state.scopes.push(next);
    state.selected = 0;
    state.depth = 0;
    render();
  }

  function ascend() {
    if (state.scopes.length <= 1) return;
    state.scopes.pop();
    state.selected = 0;
    state.depth = 0;
    render();
  }

  function resetHome() {
    state.scopes = [{ type: 'root', title: 'SecX' }];
    state.selected = 0;
    state.depth = 0;
    render();
  }

  function move(direction) {
    const scope = currentScope();
    if (!state.items.length) return;
    if (scope.type === 'root') return moveRoot(direction);

    const n = state.items.length;
    const cols = state.cols;
    const rows = Math.ceil(n / cols);
    let row = Math.floor(state.selected / cols);
    let col = state.selected % cols;
    const dr = direction === 'up' ? -1 : direction === 'down' ? 1 : 0;
    const dc = direction === 'left' ? -1 : direction === 'right' ? 1 : 0;

    for (let tries = 0; tries < Math.max(rows, cols) + 2; tries += 1) {
      row = (row + dr + rows) % rows;
      col = (col + dc + cols) % cols;
      const candidate = row * cols + col;
      if (candidate < n && candidate !== state.selected) {
        state.selected = candidate;
        state.depth = 0;
        render();
        return;
      }
    }
  }

  function moveRoot(direction) {
    const current = state.items[state.selected];
    const coords = new Map(state.items.map((item, i) => [`${item.col},${item.row}`, i]));
    const delta = { left: [-1, 0], right: [1, 0], up: [0, -1], down: [0, 1] }[direction];
    let col = current.col;
    let row = current.row;
    for (let i = 0; i < 3; i += 1) {
      col = ((col - 1 + delta[0] + 3) % 3) + 1;
      row = ((row - 1 + delta[1] + 3) % 3) + 1;
      const hit = coords.get(`${col},${row}`);
      if (hit != null && hit !== state.selected) {
        state.selected = hit;
        state.depth = 0;
        render();
        return;
      }
    }
    const center = state.items.findIndex(x => x.type === 'secx');
    if (center >= 0 && center !== state.selected) {
      state.selected = center;
      state.depth = 0;
      render();
    }
  }

  function deepen() {
    const item = state.items[state.selected];
    if (!item) return;
    const max = item.type === 'card' ? 8 : 4;
    state.depth = (state.depth + 1) % (max + 1);
    renderDetail();
  }

  function openSearch() {
    state.searchMatches = [];
    state.searchSelected = 0;
    els.searchInput.value = '';
    els.searchResults.innerHTML = '<div class="search-result"><b>Search all 1,156 cards</b><small>Type a concept, objective, acronym, or tool name.</small></div>';
    els.searchDialog.showModal();
    requestAnimationFrame(() => els.searchInput.focus());
  }

  function search(query) {
    const q = query.trim().toLowerCase();
    if (!q) {
      state.searchMatches = [];
      renderSearch();
      return;
    }
    state.searchMatches = state.cards
      .map(card => ({ card, haystack: [card.front, card.topic, card.subdomain, card.objective, card.domain, ...(card.tags || [])].join(' ').toLowerCase() }))
      .filter(x => x.haystack.includes(q))
      .slice(0, 30)
      .map(x => x.card);
    state.searchSelected = 0;
    renderSearch();
  }

  function renderSearch() {
    if (!state.searchMatches.length) {
      els.searchResults.innerHTML = '<div class="search-result"><b>No matches yet</b><small>Try another term.</small></div>';
      return;
    }
    els.searchResults.innerHTML = state.searchMatches.map((c, i) => `
      <div class="search-result ${i === state.searchSelected ? 'active' : ''}" data-search-index="${i}">
        <b>${escapeHtml(c.topic || c.front)}</b>
        <small>${escapeHtml(c.objective)} · ${escapeHtml(c.subdomain || c.domain)} · ${escapeHtml(c.card_type)}</small>
      </div>`).join('');
  }

  function jumpToCard(card) {
    if (!card) return;
    if (card.objective === 'Acronyms') {
      const letter = (card.topic || card.front).trim().charAt(0).toUpperCase();
      state.scopes = [
        { type: 'root', title: 'SecX' },
        { type: 'index', title: 'Complete SecurityX Index' },
        { type: 'acronyms', title: 'Acronyms' },
        { type: 'acronym-letter', letter, title: `${letter} Acronyms` }
      ];
    } else {
      state.scopes = [
        { type: 'root', title: 'SecX' },
        { type: 'domain', domain: card.domain, title: card.domain },
        { type: 'objective', domain: card.domain, objective: card.objective, title: card.objective },
        { type: 'subdomain', domain: card.domain, objective: card.objective, subdomain: card.subdomain, title: card.subdomain },
        { type: 'topic', domain: card.domain, objective: card.objective, subdomain: card.subdomain, topic: card.topic, title: card.topic }
      ];
    }
    state.items = itemsForScope(currentScope());
    const idx = state.items.findIndex(item => item.type === 'card' && item.card.id === card.id);
    state.selected = idx >= 0 ? idx : 0;
    state.depth = 0;
    els.searchDialog.close();
    render();
  }

  document.addEventListener('keydown', event => {
    if (els.searchDialog.open) return;
    const key = event.key;
    if (['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Enter','Escape',' ','Home','/'].includes(key)) event.preventDefault();
    if (key === 'ArrowLeft') move('left');
    else if (key === 'ArrowRight') move('right');
    else if (key === 'ArrowUp') move('up');
    else if (key === 'ArrowDown') move('down');
    else if (key === 'Enter') descend();
    else if (key === 'Escape') ascend();
    else if (key === ' ') deepen();
    else if (key === 'Home') resetHome();
    else if (key === '/') openSearch();
  });

  els.searchInput.addEventListener('input', () => search(els.searchInput.value));
  els.searchDialog.addEventListener('keydown', event => {
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault();
      if (!state.searchMatches.length) return;
      const step = event.key === 'ArrowDown' ? 1 : -1;
      state.searchSelected = (state.searchSelected + step + state.searchMatches.length) % state.searchMatches.length;
      renderSearch();
      els.searchResults.querySelector('.active')?.scrollIntoView({ block: 'nearest' });
    } else if (event.key === 'Enter' && state.searchMatches.length) {
      event.preventDefault();
      jumpToCard(state.searchMatches[state.searchSelected]);
    }
  });
  els.searchResults.addEventListener('click', event => {
    const row = event.target.closest('[data-search-index]');
    if (!row) return;
    jumpToCard(state.searchMatches[Number(row.dataset.searchIndex)]);
  });

  loadDeck()
    .then(() => render())
    .catch(error => {
      els.status.textContent = 'Prototype data load failed';
      els.levelTitle.textContent = 'Could not load SecurityX deck';
      els.levelIntro.textContent = error.message;
      console.error(error);
    });
})();
