(() => {
  const directory = document.querySelector('.schema-directory');
  const navigation = document.querySelector('.schema-pagination');
  if (!directory || !navigation) return;
  const entries = Array.from(directory.querySelectorAll('.schema-directory__entry'));
  const previous = navigation.querySelector('[data-page="previous"]');
  const next = navigation.querySelector('[data-page="next"]');
  const status = navigation.querySelector('[role="status"]');
  const search = document.querySelector('#schema-search');
  const empty = document.querySelector('.schema-empty');
  const searchPanel = document.querySelector('.schema-search');
  const mobile = window.matchMedia('(max-width: 640px)');
  let page = 0;
  function readLocation() {
    const params = new URLSearchParams(window.location.search);
    search.value = params.get('q') || '';
    const requested = Number(params.get('page') || '1');
    page = Number.isSafeInteger(requested) && requested > 0 ? requested - 1 : 0;
  }
  function render(updateLocation = false) {
    const size = mobile.matches ? 10 : 20;
    const query = search.value.trim().toLocaleLowerCase();
    const matching = entries.filter(entry => entry.querySelector('h3').textContent.toLocaleLowerCase().includes(query) || entry.querySelector('p').textContent.toLocaleLowerCase().includes(query));
    const pages = Math.max(1, Math.ceil(matching.length / size));
    page = Math.min(page, pages - 1);
    const visible = new Set(matching.slice(page * size, (page + 1) * size));
    entries.forEach(entry => { entry.hidden = !visible.has(entry); });
    navigation.hidden = pages <= 1 && !query;
    empty.hidden = matching.length !== 0;
    previous.disabled = page === 0;
    next.disabled = page === pages - 1;
    status.textContent = matching.length ? `Page ${page + 1} of ${pages} · ${matching.length} schemas` : '0 schemas';
    if (updateLocation) {
      const url = new URL(window.location.href);
      if (query) url.searchParams.set('q', search.value.trim()); else url.searchParams.delete('q');
      if (page) url.searchParams.set('page', String(page + 1)); else url.searchParams.delete('page');
      window.history.replaceState(null, '', url);
    }
  }
  function changePage(delta) {
    page += delta;
    render(true);
    directory.querySelector('.schema-directory__entry:not([hidden]) h3 a')?.focus();
  }
  previous.addEventListener('click', () => changePage(-1));
  next.addEventListener('click', () => changePage(1));
  search.addEventListener('input', () => { page = 0; render(true); });
  mobile.addEventListener('change', () => { page = 0; render(true); });
  window.addEventListener('popstate', () => { readLocation(); render(); });
  searchPanel.hidden = false;
  readLocation();
  render();
})();
