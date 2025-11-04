# 🧩 Componentes Frontend

Biblioteca completa de componentes reutilizáveis para a interface da Pizzaria.

## 🎨 Sistema de Design

### Tokens de Design

```css
/* Cores principais */
:root {
  --primary-red: #dc2626;
  --primary-orange: #ea580c;
  --secondary-yellow: #fbbf24;
  --success-green: #16a34a;
  --warning-amber: #f59e0b;
  --error-red: #ef4444;
  --info-blue: #3b82f6;
  
  /* Neutros */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;
  
  /* Tipografia */
  --font-family-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-family-mono: 'JetBrains Mono', 'Fira Code', monospace;
  
  /* Tamanhos de fonte */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;
  
  /* Espaçamentos */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;
  --space-16: 4rem;
  --space-20: 5rem;
  
  /* Bordas */
  --radius-sm: 0.125rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;
  --radius-2xl: 1rem;
  --radius-full: 9999px;
  
  /* Sombras */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  
  /* Animações */
  --transition-fast: 150ms ease-in-out;
  --transition-normal: 250ms ease-in-out;
  --transition-slow: 500ms ease-in-out;
}
```

### Utilitários CSS

```css
/* Layout helpers */
.flex { display: flex; }
.flex-col { flex-direction: column; }
.flex-wrap { flex-wrap: wrap; }
.items-center { align-items: center; }
.justify-center { justify-content: center; }
.justify-between { justify-content: space-between; }
.justify-end { justify-content: flex-end; }

/* Grid system */
.grid { display: grid; }
.grid-cols-1 { grid-template-columns: repeat(1, minmax(0, 1fr)); }
.grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.grid-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }

/* Spacing */
.gap-1 { gap: var(--space-1); }
.gap-2 { gap: var(--space-2); }
.gap-3 { gap: var(--space-3); }
.gap-4 { gap: var(--space-4); }
.gap-6 { gap: var(--space-6); }
.gap-8 { gap: var(--space-8); }

/* Text utilities */
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }
.font-bold { font-weight: 700; }
.font-medium { font-weight: 500; }
.font-normal { font-weight: 400; }

/* Visibility */
.hidden { display: none; }
.visible { visibility: visible; }
.invisible { visibility: hidden; }

/* Responsive helpers */
@media (max-width: 768px) {
  .md\\:hidden { display: none; }
  .md\\:block { display: block; }
  .md\\:flex { display: flex; }
}

@media (max-width: 640px) {
  .sm\\:hidden { display: none; }
  .sm\\:block { display: block; }
  .sm\\:text-center { text-align: center; }
}
```

## 📦 Componentes Base

### Button Component

```html
<!-- Botão primário -->
<button class="btn btn--primary">
  <span class="btn__icon">🍕</span>
  <span class="btn__text">Adicionar Pizza</span>
</button>

<!-- Botão secundário -->
<button class="btn btn--secondary">
  <span class="btn__text">Cancelar</span>
</button>

<!-- Botão de perigo -->
<button class="btn btn--danger">
  <span class="btn__text">Excluir Item</span>
</button>

<!-- Botão desabilitado -->
<button class="btn btn--primary" disabled>
  <span class="btn__spinner" aria-hidden="true"></span>
  <span class="btn__text">Processando...</span>
</button>
```

```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  font-family: var(--font-family-primary);
  font-size: var(--text-sm);
  font-weight: 500;
  line-height: 1.5;
  text-decoration: none;
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  user-select: none;
  white-space: nowrap;
}

.btn:focus {
  outline: 2px solid var(--primary-red);
  outline-offset: 2px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
}

/* Variações */
.btn--primary {
  background-color: var(--primary-red);
  border-color: var(--primary-red);
  color: white;
}

.btn--primary:hover:not(:disabled) {
  background-color: #b91c1c;
  border-color: #b91c1c;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn--secondary {
  background-color: transparent;
  border-color: var(--gray-300);
  color: var(--gray-700);
}

.btn--secondary:hover:not(:disabled) {
  background-color: var(--gray-50);
  border-color: var(--gray-400);
}

.btn--danger {
  background-color: var(--error-red);
  border-color: var(--error-red);
  color: white;
}

.btn--danger:hover:not(:disabled) {
  background-color: #dc2626;
  border-color: #dc2626;
}

/* Tamanhos */
.btn--sm {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-xs);
}

.btn--lg {
  padding: var(--space-4) var(--space-6);
  font-size: var(--text-base);
}

/* Estados */
.btn__spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: var(--radius-full);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

### Input Component

```html
<!-- Input básico -->
<div class="input-group">
  <label class="input-label" for="email">E-mail</label>
  <input 
    class="input" 
    id="email" 
    type="email" 
    placeholder="seu@email.com"
    aria-describedby="email-help"
  >
  <span class="input-help" id="email-help">
    Digite seu e-mail para login
  </span>
</div>

<!-- Input com erro -->
<div class="input-group">
  <label class="input-label" for="password">Senha</label>
  <input 
    class="input input--error" 
    id="password" 
    type="password"
    aria-describedby="password-error"
    aria-invalid="true"
  >
  <span class="input-error" id="password-error">
    A senha deve ter pelo menos 8 caracteres
  </span>
</div>

<!-- Input com ícone -->
<div class="input-group">
  <label class="input-label" for="search">Buscar</label>
  <div class="input-wrapper">
    <span class="input-icon" aria-hidden="true">🔍</span>
    <input 
      class="input input--with-icon" 
      id="search" 
      type="search"
      placeholder="Buscar pizzas..."
    >
  </div>
</div>
```

```css
.input-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.input-label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--gray-700);
}

.input {
  padding: var(--space-3) var(--space-4);
  font-family: var(--font-family-primary);
  font-size: var(--text-sm);
  border: 1px solid var(--gray-300);
  border-radius: var(--radius-md);
  background-color: white;
  transition: all var(--transition-fast);
}

.input:focus {
  outline: none;
  border-color: var(--primary-red);
  box-shadow: 0 0 0 3px rgb(220 38 38 / 0.1);
}

.input::placeholder {
  color: var(--gray-400);
}

.input--error {
  border-color: var(--error-red);
}

.input--error:focus {
  border-color: var(--error-red);
  box-shadow: 0 0 0 3px rgb(239 68 68 / 0.1);
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input--with-icon {
  padding-left: 2.5rem;
}

.input-icon {
  position: absolute;
  left: var(--space-3);
  pointer-events: none;
  color: var(--gray-400);
}

.input-help {
  font-size: var(--text-xs);
  color: var(--gray-500);
}

.input-error {
  font-size: var(--text-xs);
  color: var(--error-red);
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.input-error::before {
  content: '⚠️';
}
```

### Card Component

```html
<!-- Card básico -->
<article class="card">
  <header class="card__header">
    <h3 class="card__title">Pizza Margherita</h3>
    <span class="card__badge">Clássica</span>
  </header>
  <div class="card__content">
    <p class="card__description">
      Molho de tomate, mozzarella, manjericão fresco e azeite extra virgem.
    </p>
    <div class="card__price">
      <span class="card__price-value">R$ 32,90</span>
      <span class="card__price-size">Grande</span>
    </div>
  </div>
  <footer class="card__actions">
    <button class="btn btn--secondary btn--sm">Ver Detalhes</button>
    <button class="btn btn--primary btn--sm">Adicionar</button>
  </footer>
</article>

<!-- Card com imagem -->
<article class="card card--image">
  <div class="card__image">
    <img src="pizza-margherita.jpg" alt="Pizza Margherita" loading="lazy">
    <div class="card__image-overlay">
      <button class="btn btn--primary" aria-label="Adicionar Pizza Margherita ao carrinho">
        <span aria-hidden="true">➕</span>
      </button>
    </div>
  </div>
  <div class="card__body">
    <h3 class="card__title">Pizza Margherita</h3>
    <p class="card__description">Clássica italiana com ingredientes frescos</p>
    <div class="card__price">R$ 32,90</div>
  </div>
</article>
```

```css
.card {
  display: flex;
  flex-direction: column;
  background-color: white;
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-fast);
  overflow: hidden;
}

.card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-4) 0;
}

.card__title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--gray-900);
  margin: 0;
}

.card__badge {
  padding: var(--space-1) var(--space-2);
  font-size: var(--text-xs);
  font-weight: 500;
  background-color: var(--primary-orange);
  color: white;
  border-radius: var(--radius-full);
}

.card__content {
  padding: var(--space-3) var(--space-4);
  flex-grow: 1;
}

.card__description {
  color: var(--gray-600);
  font-size: var(--text-sm);
  line-height: 1.6;
  margin-bottom: var(--space-3);
}

.card__price {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.card__price-value {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--primary-red);
}

.card__price-size {
  font-size: var(--text-xs);
  color: var(--gray-500);
  background-color: var(--gray-100);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
}

.card__actions {
  display: flex;
  gap: var(--space-2);
  padding: var(--space-4);
  border-top: 1px solid var(--gray-100);
}

/* Card com imagem */
.card--image {
  max-width: 300px;
}

.card__image {
  position: relative;
  aspect-ratio: 4/3;
  overflow: hidden;
}

.card__image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card__image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, transparent, rgba(0, 0, 0, 0.7));
  display: flex;
  align-items: end;
  justify-content: end;
  padding: var(--space-4);
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.card__image:hover .card__image-overlay {
  opacity: 1;
}

.card__body {
  padding: var(--space-4);
}
```

### Modal Component

```html
<!-- Modal backdrop -->
<div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
  <div class="modal__backdrop" data-modal-close></div>
  <div class="modal__container">
    <!-- Modal header -->
    <header class="modal__header">
      <h2 class="modal__title" id="modal-title">Confirmar Pedido</h2>
      <button class="modal__close" data-modal-close aria-label="Fechar modal">
        <span aria-hidden="true">✕</span>
      </button>
    </header>
    
    <!-- Modal content -->
    <div class="modal__content">
      <p>Tem certeza que deseja finalizar o pedido com os itens selecionados?</p>
      
      <div class="modal__order-summary">
        <div class="order-item">
          <span>2x Pizza Margherita (Grande)</span>
          <span>R$ 65,80</span>
        </div>
        <div class="order-item">
          <span>1x Refrigerante 2L</span>
          <span>R$ 8,90</span>
        </div>
        <hr class="order-divider">
        <div class="order-total">
          <span>Total:</span>
          <span>R$ 74,70</span>
        </div>
      </div>
    </div>
    
    <!-- Modal actions -->
    <footer class="modal__actions">
      <button class="btn btn--secondary" data-modal-close>Cancelar</button>
      <button class="btn btn--primary">Confirmar Pedido</button>
    </footer>
  </div>
</div>
```

```css
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
}

.modal__backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}

.modal__container {
  position: relative;
  background-color: white;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: modalSlideIn var(--transition-normal);
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-1rem) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-6) var(--space-6) 0;
}

.modal__title {
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--gray-900);
  margin: 0;
}

.modal__close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border: none;
  background-color: transparent;
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--gray-500);
  transition: all var(--transition-fast);
}

.modal__close:hover {
  background-color: var(--gray-100);
  color: var(--gray-700);
}

.modal__content {
  padding: var(--space-6);
  overflow-y: auto;
  flex-grow: 1;
}

.modal__actions {
  display: flex;
  gap: var(--space-3);
  padding: 0 var(--space-6) var(--space-6);
}

/* Order summary styles */
.modal__order-summary {
  margin-top: var(--space-4);
  padding: var(--space-4);
  background-color: var(--gray-50);
  border-radius: var(--radius-md);
}

.order-item {
  display: flex;
  justify-content: space-between;
  padding: var(--space-2) 0;
  font-size: var(--text-sm);
}

.order-divider {
  border: none;
  border-top: 1px solid var(--gray-200);
  margin: var(--space-3) 0;
}

.order-total {
  display: flex;
  justify-content: space-between;
  font-weight: 700;
  font-size: var(--text-base);
  color: var(--primary-red);
}
```

## 🚨 Componentes de Feedback

### Alert Component

```html
<!-- Alert de sucesso -->
<div class="alert alert--success" role="alert">
  <span class="alert__icon" aria-hidden="true">✅</span>
  <div class="alert__content">
    <h4 class="alert__title">Pedido confirmado!</h4>
    <p class="alert__message">Seu pedido foi recebido e será preparado em breve.</p>
  </div>
  <button class="alert__close" aria-label="Fechar alerta">
    <span aria-hidden="true">✕</span>
  </button>
</div>

<!-- Alert de erro -->
<div class="alert alert--error" role="alert">
  <span class="alert__icon" aria-hidden="true">❌</span>
  <div class="alert__content">
    <h4 class="alert__title">Erro no pagamento</h4>
    <p class="alert__message">Não foi possível processar o pagamento. Tente novamente.</p>
  </div>
  <button class="alert__close" aria-label="Fechar alerta">
    <span aria-hidden="true">✕</span>
  </button>
</div>

<!-- Alert de aviso -->
<div class="alert alert--warning" role="alert">
  <span class="alert__icon" aria-hidden="true">⚠️</span>
  <div class="alert__content">
    <h4 class="alert__title">Atenção</h4>
    <p class="alert__message">Alguns itens estão em falta. Deseja continuar?</p>
  </div>
</div>
```

```css
.alert {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-4);
  border: 1px solid;
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
}

.alert__icon {
  font-size: var(--text-lg);
  flex-shrink: 0;
}

.alert__content {
  flex-grow: 1;
}

.alert__title {
  font-size: var(--text-sm);
  font-weight: 600;
  margin: 0 0 var(--space-1) 0;
}

.alert__message {
  font-size: var(--text-sm);
  margin: 0;
  line-height: 1.5;
}

.alert__close {
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--space-1);
  border-radius: var(--radius-sm);
  color: inherit;
  opacity: 0.7;
  transition: opacity var(--transition-fast);
  flex-shrink: 0;
}

.alert__close:hover {
  opacity: 1;
}

/* Variações */
.alert--success {
  background-color: #f0fdf4;
  border-color: #16a34a;
  color: #166534;
}

.alert--error {
  background-color: #fef2f2;
  border-color: #ef4444;
  color: #991b1b;
}

.alert--warning {
  background-color: #fffbeb;
  border-color: #f59e0b;
  color: #92400e;
}

.alert--info {
  background-color: #eff6ff;
  border-color: #3b82f6;
  color: #1e40af;
}
```

### Loading States

```html
<!-- Loading spinner -->
<div class="loading-spinner" aria-label="Carregando...">
  <div class="spinner"></div>
  <span class="loading-text">Carregando menu...</span>
</div>

<!-- Skeleton loading -->
<div class="skeleton-card">
  <div class="skeleton skeleton--image"></div>
  <div class="skeleton-content">
    <div class="skeleton skeleton--title"></div>
    <div class="skeleton skeleton--text"></div>
    <div class="skeleton skeleton--text skeleton--text-short"></div>
  </div>
</div>

<!-- Loading button -->
<button class="btn btn--primary" disabled>
  <span class="btn__spinner"></span>
  <span>Processando...</span>
</button>
```

```css
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-4);
  padding: var(--space-8);
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid var(--gray-200);
  border-top: 3px solid var(--primary-red);
  border-radius: var(--radius-full);
  animation: spin 1s linear infinite;
}

.loading-text {
  font-size: var(--text-sm);
  color: var(--gray-600);
}

/* Skeleton loading */
.skeleton-card {
  background-color: white;
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  box-shadow: var(--shadow-sm);
}

.skeleton {
  background: linear-gradient(
    90deg,
    var(--gray-200) 25%,
    var(--gray-100) 50%,
    var(--gray-200) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 2s infinite;
  border-radius: var(--radius-sm);
}

.skeleton--image {
  width: 100%;
  height: 200px;
  margin-bottom: var(--space-3);
  border-radius: var(--radius-md);
}

.skeleton--title {
  height: 1.25rem;
  width: 70%;
  margin-bottom: var(--space-2);
}

.skeleton--text {
  height: 0.875rem;
  width: 100%;
  margin-bottom: var(--space-2);
}

.skeleton--text-short {
  width: 60%;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}
```

## 📱 Componentes Responsivos

### Navigation Component

```html
<nav class="navbar" role="navigation" aria-label="Navegação principal">
  <div class="navbar__container">
    <!-- Logo -->
    <div class="navbar__brand">
      <a href="/" class="navbar__logo">
        <span class="navbar__logo-icon">🍕</span>
        <span class="navbar__logo-text">Pizzaria</span>
      </a>
    </div>
    
    <!-- Desktop menu -->
    <div class="navbar__menu" id="navbar-menu">
      <ul class="navbar__nav">
        <li class="navbar__item">
          <a href="#menu" class="navbar__link">Cardápio</a>
        </li>
        <li class="navbar__item">
          <a href="#about" class="navbar__link">Sobre</a>
        </li>
        <li class="navbar__item">
          <a href="#contact" class="navbar__link">Contato</a>
        </li>
      </ul>
      
      <div class="navbar__actions">
        <button class="navbar__cart" aria-label="Carrinho de compras">
          <span class="navbar__cart-icon">🛒</span>
          <span class="navbar__cart-badge">3</span>
        </button>
        <button class="btn btn--primary">Entrar</button>
      </div>
    </div>
    
    <!-- Mobile toggle -->
    <button 
      class="navbar__toggle" 
      aria-expanded="false"
      aria-controls="navbar-menu"
      aria-label="Abrir menu de navegação"
    >
      <span class="navbar__toggle-line"></span>
      <span class="navbar__toggle-line"></span>
      <span class="navbar__toggle-line"></span>
    </button>
  </div>
</nav>
```

```css
.navbar {
  background-color: white;
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar__container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-6);
  max-width: 1200px;
  margin: 0 auto;
}

.navbar__brand {
  flex-shrink: 0;
}

.navbar__logo {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  text-decoration: none;
  color: var(--gray-900);
}

.navbar__logo-icon {
  font-size: var(--text-2xl);
}

.navbar__logo-text {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--primary-red);
}

.navbar__menu {
  display: flex;
  align-items: center;
  gap: var(--space-8);
}

.navbar__nav {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: var(--space-6);
}

.navbar__link {
  color: var(--gray-700);
  text-decoration: none;
  font-weight: 500;
  transition: color var(--transition-fast);
}

.navbar__link:hover {
  color: var(--primary-red);
}

.navbar__actions {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.navbar__cart {
  position: relative;
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--space-2);
  border-radius: var(--radius-md);
  transition: background-color var(--transition-fast);
}

.navbar__cart:hover {
  background-color: var(--gray-100);
}

.navbar__cart-icon {
  font-size: var(--text-xl);
}

.navbar__cart-badge {
  position: absolute;
  top: 0;
  right: 0;
  background-color: var(--primary-red);
  color: white;
  font-size: var(--text-xs);
  font-weight: 600;
  padding: var(--space-1);
  min-width: 1.25rem;
  height: 1.25rem;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
}

.navbar__toggle {
  display: none;
  flex-direction: column;
  gap: 4px;
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--space-2);
}

.navbar__toggle-line {
  width: 24px;
  height: 2px;
  background-color: var(--gray-700);
  transition: all var(--transition-fast);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .navbar__menu {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background-color: white;
    flex-direction: column;
    align-items: stretch;
    gap: 0;
    box-shadow: var(--shadow-md);
    max-height: 0;
    overflow: hidden;
    transition: max-height var(--transition-normal);
  }

  .navbar__menu.navbar__menu--open {
    max-height: 400px;
  }

  .navbar__nav {
    flex-direction: column;
    gap: 0;
    padding: var(--space-4);
  }

  .navbar__item {
    padding: var(--space-3) 0;
    border-bottom: 1px solid var(--gray-200);
  }

  .navbar__actions {
    padding: var(--space-4);
    border-top: 1px solid var(--gray-200);
  }

  .navbar__toggle {
    display: flex;
  }

  .navbar__toggle[aria-expanded="true"] .navbar__toggle-line:nth-child(1) {
    transform: translateY(6px) rotate(45deg);
  }

  .navbar__toggle[aria-expanded="true"] .navbar__toggle-line:nth-child(2) {
    opacity: 0;
  }

  .navbar__toggle[aria-expanded="true"] .navbar__toggle-line:nth-child(3) {
    transform: translateY(-6px) rotate(-45deg);
  }
}
```

## 🛠️ JavaScript dos Componentes

### Component Manager

```javascript
// components/ComponentManager.js
class ComponentManager {
  constructor() {
    this.components = new Map();
    this.init();
  }

  init() {
    // Auto-initialize components on DOM load
    document.addEventListener('DOMContentLoaded', () => {
      this.initializeAll();
    });
  }

  register(name, componentClass) {
    this.components.set(name, componentClass);
  }

  initializeAll() {
    // Initialize all registered components
    for (const [name, ComponentClass] of this.components) {
      const elements = document.querySelectorAll(`[data-component="${name}"]`);
      elements.forEach(element => {
        if (!element._component) {
          element._component = new ComponentClass(element);
        }
      });
    }
  }

  create(name, element, options = {}) {
    const ComponentClass = this.components.get(name);
    if (!ComponentClass) {
      console.warn(`Component "${name}" not found`);
      return null;
    }
    return new ComponentClass(element, options);
  }
}

// Global component manager instance
window.ComponentManager = new ComponentManager();
```

### Modal Component JS

```javascript
// components/Modal.js
class Modal {
  constructor(element, options = {}) {
    this.element = element;
    this.options = {
      closeOnBackdrop: true,
      closeOnEscape: true,
      autoFocus: true,
      ...options
    };

    this.isOpen = false;
    this.init();
  }

  init() {
    // Bind close events
    const closeButtons = this.element.querySelectorAll('[data-modal-close]');
    closeButtons.forEach(button => {
      button.addEventListener('click', () => this.close());
    });

    // Close on backdrop click
    if (this.options.closeOnBackdrop) {
      this.element.addEventListener('click', (e) => {
        if (e.target === this.element) {
          this.close();
        }
      });
    }

    // Close on escape key
    if (this.options.closeOnEscape) {
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && this.isOpen) {
          this.close();
        }
      });
    }
  }

  open() {
    if (this.isOpen) return;

    this.isOpen = true;
    this.element.style.display = 'flex';
    document.body.style.overflow = 'hidden';

    // Focus management
    if (this.options.autoFocus) {
      const focusableElements = this.element.querySelectorAll(
        'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
      );
      
      if (focusableElements.length > 0) {
        focusableElements[0].focus();
      }
    }

    // Dispatch custom event
    this.element.dispatchEvent(new CustomEvent('modal:open', {
      detail: { modal: this }
    }));
  }

  close() {
    if (!this.isOpen) return;

    this.isOpen = false;
    this.element.style.display = 'none';
    document.body.style.overflow = '';

    // Dispatch custom event
    this.element.dispatchEvent(new CustomEvent('modal:close', {
      detail: { modal: this }
    }));
  }

  toggle() {
    this.isOpen ? this.close() : this.open();
  }

  static create(content, options = {}) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = content;
    document.body.appendChild(modal);

    return new Modal(modal, options);
  }
}

// Register component
ComponentManager.register('modal', Modal);
```

### Alert Component JS

```javascript
// components/Alert.js
class Alert {
  constructor(element, options = {}) {
    this.element = element;
    this.options = {
      autoClose: false,
      autoCloseDelay: 5000,
      ...options
    };

    this.init();
  }

  init() {
    // Handle close button
    const closeButton = this.element.querySelector('.alert__close');
    if (closeButton) {
      closeButton.addEventListener('click', () => this.close());
    }

    // Auto close
    if (this.options.autoClose) {
      setTimeout(() => this.close(), this.options.autoCloseDelay);
    }
  }

  close() {
    this.element.style.animation = 'alertSlideOut 300ms ease-in-out forwards';
    setTimeout(() => {
      if (this.element.parentNode) {
        this.element.parentNode.removeChild(this.element);
      }
    }, 300);

    // Dispatch custom event
    this.element.dispatchEvent(new CustomEvent('alert:close', {
      detail: { alert: this }
    }));
  }

  static create(type, title, message, container = document.body) {
    const alert = document.createElement('div');
    alert.className = `alert alert--${type}`;
    alert.innerHTML = `
      <span class="alert__icon" aria-hidden="true">${this.getIcon(type)}</span>
      <div class="alert__content">
        <h4 class="alert__title">${title}</h4>
        <p class="alert__message">${message}</p>
      </div>
      <button class="alert__close" aria-label="Fechar alerta">
        <span aria-hidden="true">✕</span>
      </button>
    `;

    container.appendChild(alert);
    return new Alert(alert, { autoClose: true });
  }

  static getIcon(type) {
    const icons = {
      success: '✅',
      error: '❌',
      warning: '⚠️',
      info: 'ℹ️'
    };
    return icons[type] || icons.info;
  }
}

// Add CSS animation
const style = document.createElement('style');
style.textContent = `
  @keyframes alertSlideOut {
    to {
      opacity: 0;
      transform: translateX(100%);
    }
  }
`;
document.head.appendChild(style);

// Register component
ComponentManager.register('alert', Alert);
```

Este sistema completo de componentes fornece uma base sólida e reutilizável para toda a interface da Pizzaria, seguindo as melhores práticas de acessibilidade, responsividade e manutenibilidade.