(() => {
  const current = document.querySelector('#versions [aria-current="page"]');
  const strip = current?.closest('.schema-versions');
  if (!strip) return;
  // Scroll only the version strip, never the page or its anchor destination.
  const stripBox = strip.getBoundingClientRect();
  const currentBox = current.getBoundingClientRect();
  if (currentBox.right > stripBox.right || currentBox.left < stripBox.left) {
    strip.scrollLeft += currentBox.left - stripBox.left - strip.clientWidth / 2 + currentBox.width / 2;
  }
})();
