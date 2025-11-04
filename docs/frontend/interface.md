# 🖥️ Interface do Sistema

A interface do Hashtag Pizzaria é desenvolvida com tecnologias web modernas e foco na experiência do usuário.

## 🎨 Design System

### Paleta de Cores

```css
:root {
  /* Cores Principais */
  --primary-color: #d32f2f;      /* Vermelho pizzaria */
  --primary-dark: #b71c1c;       /* Vermelho escuro */
  --primary-light: #ff5722;      /* Laranja vibrante */
  --secondary-color: #ff9800;    /* Laranja secundário */
  --accent-color: #ffc107;       /* Amarelo destaque */
  
  /* Cores de Fundo */
  --background-color: #0a0a0a;   /* Preto principal */
  --surface-color: #1a1a1a;      /* Cinza muito escuro */
  --card-color: #2a2a2a;         /* Cinza escuro */
  
  /* Cores de Texto */
  --text-primary: #ffffff;       /* Branco */
  --text-secondary: #b3b3b3;     /* Cinza claro */
  --text-muted: #666666;         /* Cinza médio */
}
```

### Tipografia

```css
/* Fontes Principais */
--font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-display: 'Poppins', sans-serif;

/* Tamanhos */
--font-xs: 0.75rem;    /* 12px */
--font-sm: 0.875rem;   /* 14px */
--font-base: 1rem;     /* 16px */
--font-lg: 1.125rem;   /* 18px */
--font-xl: 1.25rem;    /* 20px */
--font-2xl: 1.5rem;    /* 24px */
--font-3xl: 2rem;      /* 32px */
```

### Espaçamento

```css
/* Sistema de Grid de 4px */
--space-1: 0.25rem;    /* 4px */
--space-2: 0.5rem;     /* 8px */
--space-3: 0.75rem;    /* 12px */
--space-4: 1rem;       /* 16px */
--space-5: 1.25rem;    /* 20px */
--space-6: 1.5rem;     /* 24px */
--space-8: 2rem;       /* 32px */
--space-10: 2.5rem;    /* 40px */
```

## 📱 Layout Responsivo

### Breakpoints

```css
/* Mobile First */
.container {
  width: 100%;
  padding: 0 1rem;
}

/* Tablet (768px+) */
@media (min-width: 48rem) {
  .container {
    max-width: 48rem;
    padding: 0 2rem;
  }
}

/* Desktop (1024px+) */
@media (min-width: 64rem) {
  .container {
    max-width: 64rem;
  }
}

/* Large Desktop (1280px+) */
@media (min-width: 80rem) {
  .container {
    max-width: 80rem;
  }
}
```

### Grid System

```css
.menu-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-6);
}

@media (max-width: 768px) {
  .menu-grid {
    grid-template-columns: 1fr;
    gap: var(--space-4);
  }
}
```

## 🧩 Componentes Principais

### Header/Navegação

```html
<header class="header">
  <nav class="navbar">
    <div class="container">
      <div class="nav-brand">
        <img src="assets/images/logo.svg" alt="Pizzaria" class="logo">
        <span class="brand-text">Hashtag Pizzaria</span>
      </div>
      
      <ul class="nav-menu">
        <li class="nav-item">
          <a href="#home" class="nav-link">Home</a>
        </li>
        <li class="nav-item">
          <a href="#menu" class="nav-link">Cardápio</a>
        </li>
        <li class="nav-item">
          <a href="#about" class="nav-link">Sobre</a>
        </li>
      </ul>
      
      <div class="nav-actions">
        <button class="cart-btn" id="cart-btn">
          <i class="fas fa-shopping-cart"></i>
          <span class="cart-count">0</span>
        </button>
        <button class="user-btn" id="user-btn">
          <i class="fas fa-user"></i>
        </button>
      </div>
    </div>
  </nav>
</header>
```

### Cards de Menu

```html
<div class="menu-card">
  <div class="card-image">
    <img src="assets/images/pizza.svg" alt="Pizza" class="item-image">
    <div class="card-badge">Disponível</div>
  </div>
  
  <div class="card-content">
    <h3 class="item-name">Pizza Margherita</h3>
    <p class="item-description">
      Molho de tomate, mozzarella e manjericão fresco
    </p>
    <div class="item-details">
      <span class="item-price">R$ 25,90</span>
      <span class="item-time">
        <i class="fas fa-clock"></i> 25 min
      </span>
    </div>
  </div>
  
  <div class="card-actions">
    <button class="btn btn-primary add-to-cart-btn">
      <i class="fas fa-plus"></i>
      Adicionar
    </button>
  </div>
</div>
```

### Filtros de Categoria

```html
<div class="menu-filters">
  <button class="filter-btn active" data-filter="all">
    <i class="fas fa-th"></i>
    Todos
  </button>
  <button class="filter-btn" data-filter="pizza">
    <i class="fas fa-pizza-slice"></i>
    Pizzas
  </button>
  <button class="filter-btn" data-filter="bebida">
    <i class="fas fa-glass-cheers"></i>
    Bebidas
  </button>
  <button class="filter-btn" data-filter="sobremesa">
    <i class="fas fa-ice-cream"></i>
    Sobremesas
  </button>
</div>
```

### Modal de Item

```html
<div class="modal" id="item-modal">
  <div class="modal-backdrop"></div>
  <div class="modal-content">
    <div class="modal-header">
      <h2 class="modal-title">Pizza Margherita</h2>
      <button class="modal-close">
        <i class="fas fa-times"></i>
      </button>
    </div>
    
    <div class="modal-body">
      <img src="assets/images/pizza.svg" alt="Pizza" class="modal-image">
      <p class="modal-description">
        Molho de tomate, mozzarella e manjericão fresco
      </p>
      <div class="modal-price">R$ 25,90</div>
      
      <div class="quantity-selector">
        <label for="quantity">Quantidade:</label>
        <div class="quantity-controls">
          <button class="quantity-btn" data-action="decrease">-</button>
          <input type="number" id="quantity" value="1" min="1" max="10">
          <button class="quantity-btn" data-action="increase">+</button>
        </div>
      </div>
      
      <div class="observations">
        <label for="observations">Observações:</label>
        <textarea id="observations" placeholder="Ex: sem cebola"></textarea>
      </div>
    </div>
    
    <div class="modal-footer">
      <button class="btn btn-secondary cancel-btn">Cancelar</button>
      <button class="btn btn-primary add-item-btn">
        Adicionar - R$ 25,90
      </button>
    </div>
  </div>
</div>
```

### Carrinho de Compras

```html
<div class="cart-sidebar" id="cart-sidebar">
  <div class="cart-header">
    <h3>Seu Pedido</h3>
    <button class="cart-close">
      <i class="fas fa-times"></i>
    </button>
  </div>
  
  <div class="cart-items">
    <div class="cart-item">
      <div class="item-info">
        <h4>Pizza Margherita</h4>
        <p>Sem cebola</p>
      </div>
      <div class="item-controls">
        <div class="quantity-controls">
          <button class="quantity-btn">-</button>
          <span class="quantity">2</span>
          <button class="quantity-btn">+</button>
        </div>
        <span class="item-total">R$ 51,80</span>
        <button class="remove-item">
          <i class="fas fa-trash"></i>
        </button>
      </div>
    </div>
  </div>
  
  <div class="cart-summary">
    <div class="summary-line">
      <span>Subtotal:</span>
      <span>R$ 51,80</span>
    </div>
    <div class="summary-line">
      <span>Taxa de entrega:</span>
      <span>R$ 5,00</span>
    </div>
    <div class="summary-total">
      <span>Total:</span>
      <span>R$ 56,80</span>
    </div>
  </div>
  
  <div class="cart-actions">
    <button class="btn btn-primary checkout-btn">
      Finalizar Pedido
    </button>
  </div>
</div>
```

## 🎭 Estados da Interface

### Loading States

```css
.loading-skeleton {
  background: linear-gradient(
    90deg,
    var(--card-color) 25%,
    var(--surface-color) 50%,
    var(--card-color) 75%
  );
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

### Empty States

```html
<div class="empty-state">
  <img src="assets/images/empty-cart.svg" alt="Carrinho vazio" class="empty-icon">
  <h3>Seu carrinho está vazio</h3>
  <p>Adicione itens deliciosos do nosso cardápio!</p>
  <button class="btn btn-primary">Ver Cardápio</button>
</div>
```

### Error States

```html
<div class="error-state">
  <i class="fas fa-exclamation-triangle error-icon"></i>
  <h3>Ops! Algo deu errado</h3>
  <p>Não conseguimos carregar o cardápio. Tente novamente.</p>
  <button class="btn btn-secondary retry-btn">Tentar Novamente</button>
</div>
```

## 🔔 Sistema de Notificações

### Toast Notifications

```html
<div class="toast toast-success" role="alert">
  <div class="toast-icon">
    <i class="fas fa-check-circle"></i>
  </div>
  <div class="toast-content">
    <div class="toast-title">Sucesso!</div>
    <div class="toast-message">Item adicionado ao carrinho</div>
  </div>
  <button class="toast-close">
    <i class="fas fa-times"></i>
  </button>
</div>
```

### Variações de Toast

```css
.toast-success { border-left-color: #22c55e; }
.toast-error { border-left-color: #ef4444; }
.toast-warning { border-left-color: #f59e0b; }
.toast-info { border-left-color: #3b82f6; }
```

## 📊 Feedback Visual

### Botões com Estados

```css
.btn {
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(211, 47, 47, 0.3);
}

.btn:active {
  transform: translateY(0);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}
```

### Animações de Micro-interação

```css
.menu-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.menu-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.add-to-cart-btn {
  position: relative;
}

.add-to-cart-btn.adding::after {
  content: '';
  position: absolute;
  width: 20px;
  height: 20px;
  border: 2px solid transparent;
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

## 🎯 Acessibilidade

### ARIA Labels

```html
<button class="cart-btn" aria-label="Carrinho de compras com 3 itens">
  <i class="fas fa-shopping-cart" aria-hidden="true"></i>
  <span class="cart-count" aria-live="polite">3</span>
</button>

<div class="menu-filters" role="tablist">
  <button class="filter-btn" role="tab" aria-selected="true">
    Todos
  </button>
</div>
```

### Navegação por Teclado

```css
.filter-btn:focus,
.btn:focus,
.nav-link:focus {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

.menu-card:focus-within {
  outline: 2px solid var(--primary-color);
}
```

### Alto Contraste

```css
@media (prefers-contrast: high) {
  :root {
    --text-primary: #ffffff;
    --background-color: #000000;
    --primary-color: #ff0000;
  }
}

@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```