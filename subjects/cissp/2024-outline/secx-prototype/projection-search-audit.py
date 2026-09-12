#!/usr/bin/env python3
"""Deterministic audit for SecX Source/Coverage/Reviewed-Links projection search."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
errors=[]

def check(ok,msg):
    if not ok: errors.append(msg)

def read(name):
    return (ROOT/name).read_text(encoding='utf-8')

try:
    js=read('projection-search.js')
    relationships=read('relationship-lens.js')
    html=read('next.html')
except OSError as exc:
    print('FAIL secx_projection_search_audit')
    print('-',exc)
    sys.exit(1)

check("kind:'source-projection'" in js,'missing source projection search entries')
check("kind:'coverage-domain-projection'" in js,'missing coverage domain search entries')
check("kind:'coverage-objective-projection'" in js,'missing coverage objective search entries')
check("kind:'relationship-projection'" in js,'missing reviewed relationship projection search entries')
check("sourceHubLayout(item.sourceId" in js,'source search does not route through existing source lens')
check("coverageDomainLayout(item.domainNum" in js,'coverage search does not route through existing coverage lens')
check("coverage:objective:${item.objectiveId}" in js,'coverage objective routing does not use explicit objective id')
check("relationshipHubLayout(item.relationshipId" in js,'relationship search does not route through existing reviewed Links hub')
check("Array.isArray(window.SECX_RELEASED_RELATIONSHIPS)" in js,'relationship search is not derived from the released relationship runtime')
check("relationshipId:r.id" in js,'relationship projection does not preserve stable released relationship id')
check("secx:relationships-ready" in js,'projection search does not wait for relationship-runtime readiness')
check("secx:relationships-ready" in relationships,'relationship lens does not publish runtime readiness after setup')
check("searchIndex.push(item)" in js,'projection entries are not added to existing search index')
check("priorNavigate(item)" in js,'projection search does not preserve existing search routing')
check("searchPaletteBtn" in js,'expanded search has no visible open control for pointer/touch users')
check("searchCloseBtn" in js,'expanded search has no visible close control for pointer/touch users')
check("searchButton.addEventListener('click',()=>{searchOpener=searchButton;openSearch();input?.focus({preventScroll:true})})" in js,'visible Search control does not open palette and synchronously transfer focus to its input')
check("closeButton.addEventListener('click',closeSearchToOpener)" in js,'visible Close control does not use focus-restoring dismissal')
check("setAttribute('role','combobox')" in js,'projection search input does not expose combobox role')
check("setAttribute('aria-controls','searchResults')" in js,'projection search input does not identify its result listbox')
check("setAttribute('aria-expanded'" in js,'projection search input does not expose palette expanded state')
check("aria-activedescendant" in js,'projection search does not expose active result to assistive technology')
check("option.tabIndex=-1" in js,'combobox listbox options remain in the Tab order')
check("e.key!=='Tab'" in js and "e.shiftKey" in js,'search dialog does not implement Tab and Shift+Tab containment')
check("e.key==='Escape'" in js and "closeSearchToOpener()" in js,'search dialog does not support focus-restoring Escape dismissal')
check("searchOpener=document.activeElement" in js,'keyboard-opened search does not remember its opener')
check("searchOpener=null" in js,'search navigation does not clear stale opener state before routing')
check("MutationObserver" in js,'projection search accessibility state is not synchronized with palette/result mutations')
check("localStorage" not in js,'projection search must not read/write learner state')
check("RELATIONSHIP_REVIEW" not in js,'projection search must not access reviewer relationship data')
check("RELEASED_RELATIONSHIPS.json" not in js,'projection search must not directly fetch/read the raw relationship release artifact')
for token in ('similarityScore','levenshtein','fuzzyMatch','cosineSimilarity','semanticDistance','relationshipScore'):
    check(token not in js,f'projection search contains inferred relationship helper: {token}')
check("projection-search.js" in html,'expanded page does not load projection search')
check(html.find("coverage-lens.js") < html.find("projection-search.js"),'projection search must load after coverage lens')
check(html.find("projection-search.js") < html.find("released-relationships.js") < html.find("relationship-lens.js"),'relationship search listener must load before the released relationship runtime/lens')
check("coverage.onload" in html,'projection search load is not gated on coverage-lens completion')

if errors:
    print('FAIL secx_projection_search_audit')
    for e in errors: print('-',e)
    sys.exit(1)
print('PASS secx_projection_search_audit source+coverage+reviewed-links navigation=explicit released-relationships-only existing-search-index-only combobox-a11y=enabled touch-controls=enabled modal-focus=contained visible-open-focus=sync')
