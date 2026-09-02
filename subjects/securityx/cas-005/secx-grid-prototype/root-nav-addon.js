(() => {
  'use strict';
  const towardCenter = {
    'Governance, Risk, and Compliance': 'ArrowDown',
    'Security Architecture': 'ArrowLeft',
    'Security Engineering': 'ArrowUp',
    'Security Operations': 'ArrowRight'
  };

  document.addEventListener('keydown', event => {
    if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(event.key)) return;
    const grid = document.querySelector('#grid.root-grid');
    const selected = grid?.querySelector('.tile.selected');
    if (!selected || selected.classList.contains('center')) return;
    const title = selected.querySelector('strong')?.textContent?.trim();
    if (!title || event.key === towardCenter[title]) return;

    event.preventDefault();
    event.stopImmediatePropagation();
    grid.querySelector('.tile.center')?.click();
  }, true);
})();
