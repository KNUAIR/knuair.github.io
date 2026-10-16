document.querySelectorAll('[data-image-comparison]').forEach((comparison) => {
  const range = comparison.querySelector('input[type="range"]');
  if (!range) return;

  const update = () => {
    const split = Number(range.value);
    comparison.style.setProperty('--split', `${split}%`);
    range.setAttribute('aria-valuetext', `${split}% PAN, ${100 - split}% RGB`);
  };

  range.addEventListener('input', update);
  update();
});
