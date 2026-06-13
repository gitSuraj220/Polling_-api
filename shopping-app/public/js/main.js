// Lightweight client-side enhancement for the storefront.
document.addEventListener('click', function (e) {
  // Size selection on the product detail page.
  if (e.target.classList.contains('size-pill')) {
    document.querySelectorAll('.size-pill').forEach((b) => b.classList.remove('sel'));
    e.target.classList.add('sel');
  }
});
