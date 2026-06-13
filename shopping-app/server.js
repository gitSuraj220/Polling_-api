const path = require('path');
const express = require('express');
const session = require('express-session');

const { products, categories, discountPercent } = require('./data/products');

const app = express();
const PORT = process.env.PORT || 3000;

// View engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Static assets
app.use(express.static(path.join(__dirname, 'public')));

// Body + session middleware (cart/wishlist live in the session, no DB needed)
app.use(express.urlencoded({ extended: true }));
app.use(
  session({
    secret: 'myntra-inspired-demo-secret',
    resave: false,
    saveUninitialized: true,
  })
);

// Make cart/wishlist counts available to every view
app.use((req, res, next) => {
  req.session.cart = req.session.cart || [];
  req.session.wishlist = req.session.wishlist || [];
  res.locals.cartCount = req.session.cart.reduce((n, i) => n + i.qty, 0);
  res.locals.wishlistCount = req.session.wishlist.length;
  res.locals.categories = categories;
  res.locals.discountPercent = discountPercent;
  res.locals.currentPath = req.path;
  res.locals.activeCategory = '';
  res.locals.q = '';
  next();
});

const findProduct = (id) => products.find((p) => p.id === Number(id));

// ---------- Routes ----------

// Home + product listing (with optional category filter, search and sort)
app.get('/', (req, res) => {
  const { category, q, sort } = req.query;
  let list = [...products];

  if (category) {
    list = list.filter((p) => p.category === category);
  }
  if (q) {
    const term = q.toLowerCase();
    list = list.filter(
      (p) =>
        p.name.toLowerCase().includes(term) ||
        p.brand.toLowerCase().includes(term)
    );
  }
  if (sort === 'price-asc') list.sort((a, b) => a.price - b.price);
  if (sort === 'price-desc') list.sort((a, b) => b.price - a.price);
  if (sort === 'discount') list.sort((a, b) => discountPercent(b) - discountPercent(a));
  if (sort === 'rating') list.sort((a, b) => b.rating - a.rating);

  res.render('index', {
    title: category ? `${category} - Myntra-Inspired` : 'Myntra-Inspired Store',
    products: list,
    activeCategory: category || '',
    q: q || '',
    sort: sort || '',
  });
});

// Product detail
app.get('/product/:id', (req, res) => {
  const product = findProduct(req.params.id);
  if (!product) return res.status(404).render('404', { title: 'Not found' });

  const related = products
    .filter((p) => p.category === product.category && p.id !== product.id)
    .slice(0, 4);

  res.render('product', {
    title: `${product.brand} - ${product.name}`,
    product,
    related,
  });
});

// Cart
app.get('/cart', (req, res) => {
  const items = req.session.cart
    .map((i) => ({ ...findProduct(i.id), qty: i.qty }))
    .filter((i) => i.id);
  const total = items.reduce((sum, i) => sum + i.price * i.qty, 0);
  const mrpTotal = items.reduce((sum, i) => sum + i.mrp * i.qty, 0);
  res.render('cart', {
    title: 'Shopping Bag',
    items,
    total,
    savings: mrpTotal - total,
  });
});

app.post('/cart/add/:id', (req, res) => {
  const product = findProduct(req.params.id);
  if (product) {
    const existing = req.session.cart.find((i) => i.id === product.id);
    if (existing) existing.qty += 1;
    else req.session.cart.push({ id: product.id, qty: 1 });
  }
  res.redirect(req.get('referer') || '/cart');
});

app.post('/cart/remove/:id', (req, res) => {
  req.session.cart = req.session.cart.filter((i) => i.id !== Number(req.params.id));
  res.redirect('/cart');
});

app.post('/cart/update/:id', (req, res) => {
  const item = req.session.cart.find((i) => i.id === Number(req.params.id));
  if (item) {
    const qty = parseInt(req.body.qty, 10);
    if (qty > 0) item.qty = qty;
    else req.session.cart = req.session.cart.filter((i) => i.id !== item.id);
  }
  res.redirect('/cart');
});

// Wishlist
app.get('/wishlist', (req, res) => {
  const items = req.session.wishlist
    .map((id) => findProduct(id))
    .filter(Boolean);
  res.render('wishlist', { title: 'Wishlist', items });
});

app.post('/wishlist/toggle/:id', (req, res) => {
  const id = Number(req.params.id);
  const idx = req.session.wishlist.indexOf(id);
  if (idx > -1) req.session.wishlist.splice(idx, 1);
  else req.session.wishlist.push(id);
  res.redirect(req.get('referer') || '/wishlist');
});

// 404 fallback
app.use((req, res) => {
  res.status(404).render('404', { title: 'Page not found' });
});

app.listen(PORT, () => {
  console.log(`Myntra-inspired storefront running at http://localhost:${PORT}`);
});
