console.log('🍕 Menu.js loading...');

// ===== MENU SERVICE =====
class MenuService {
    constructor() {
        console.log('🏗️ MenuService constructor called');
        this.items = [];
        this.categories = [];
        this.filteredItems = [];
        this.currentCategory = 'all';
        this.searchQuery = '';
        this.loading = false;
        this.listeners = [];
        
        this.init();
        Utils.log('Menu Service initialized');
    }
    
    init() {
        // Load menu data
        this.loadMenu();
    }
    
    // Load menu from API or mock data
    async loadMenu() {
        if (this.loading) return;
        
        console.log('🚀 Starting menu load...');
        this.loading = true;
        this.notifyListeners({ type: 'loading', loading: true });
        
        try {
            const response = await api.getPublicItems();
            console.log('📦 API Response:', response);
            
            this.items = Array.isArray(response) ? response : (response.data || []);
            console.log('📋 Processed items:', this.items);
            
            this.categories = this.extractCategories();
            this.filteredItems = [...this.items];
            
            Utils.log('Menu loaded:', this.items.length, 'items');
            console.log('✅ Menu loading complete!');
            this.notifyListeners({ type: 'loaded', items: this.items, categories: this.categories });
            
        } catch (error) {
            console.error('❌ Menu loading failed:', error);
            Utils.error('Failed to load menu:', error);
            // Use mock data as fallback
            console.log('🔄 Falling back to mock data...');
            this.loadMockData();
            this.notifyListeners({ type: 'error', error: error.message });
        } finally {
            this.loading = false;
            this.notifyListeners({ type: 'loading', loading: false });
        }
    }
    
    // Load mock data if API fails
    loadMockData() {
        this.items = [
            {
                id: 1,
                name: "Pizza Margherita",
                description: "Molho de tomate, mussarela, manjericão fresco e azeite de oliva",
                price: 32.90,
                category: "Pizzas Tradicionais",
                image_url: "https://images.unsplash.com/photo-1604382354936-07c5b6f67692?w=400",
                is_available: true
            },
            {
                id: 2,
                name: "Pizza Calabresa",
                description: "Molho de tomate, mussarela, calabresa fatiada e cebola",
                price: 35.90,
                category: "Pizzas Tradicionais",
                image_url: "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400",
                is_available: true
            },
            {
                id: 3,
                name: "Pizza Quatro Queijos",
                description: "Molho de tomate, mussarela, provolone, parmesão e gorgonzola",
                price: 42.90,
                category: "Pizzas Especiais",
                image_url: "https://images.unsplash.com/photo-1571997478779-2adcbbe9ab2f?w=400",
                is_available: true
            },
            {
                id: 4,
                name: "Pizza Pepperoni",
                description: "Molho de tomate, mussarela e pepperoni artesanal",
                price: 38.90,
                category: "Pizzas Tradicionais",
                image_url: "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=400",
                is_available: true
            },
            {
                id: 5,
                name: "Pizza Frango com Catupiry",
                description: "Molho de tomate, mussarela, frango desfiado e catupiry",
                price: 36.90,
                category: "Pizzas Tradicionais",
                image_url: "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400",
                is_available: true
            },
            {
                id: 6,
                name: "Pizza Portuguesa",
                description: "Molho de tomate, mussarela, presunto, ovos, cebola, azeitona e orégano",
                price: 39.90,
                category: "Pizzas Especiais",
                image_url: "https://images.unsplash.com/photo-1590534247854-3de6718609b4?w=400",
                is_available: true
            },
            {
                id: 7,
                name: "Refrigerante 2L",
                description: "Coca-Cola, Guaraná Antarctica ou Fanta",
                price: 8.90,
                category: "Bebidas",
                image_url: "https://images.unsplash.com/photo-1553456558-aff63285bdd1?w=400",
                is_available: true
            },
            {
                id: 8,
                name: "Água 500ml",
                description: "Água mineral natural",
                price: 3.50,
                category: "Bebidas",
                image_url: "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=400",
                is_available: true
            }
        ];
        
        this.categories = this.extractCategories();
        this.filteredItems = [...this.items];
        
        Utils.log('Mock menu data loaded');
    }
    
    // Extract unique categories from items
    extractCategories() {
        const categorySet = new Set();
        this.items.forEach(item => {
            if (item.category) {
                categorySet.add(item.category);
            }
        });
        return Array.from(categorySet).sort();
    }
    
    // Add listener for menu changes
    onMenuChange(callback) {
        this.listeners.push(callback);
        return () => {
            this.listeners = this.listeners.filter(cb => cb !== callback);
        };
    }
    
    // Notify listeners
    notifyListeners(data) {
        this.listeners.forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                Utils.error('Menu listener error:', error);
            }
        });
        
        EventBus.emit('menu:change', data);
    }
    
    // Filter items by category
    filterByCategory(category) {
        this.currentCategory = category;
        this.applyFilters();
        
        Utils.log('Menu filtered by category:', category);
        EventBus.emit('menu:categoryChanged', category);
    }
    
    // Search items
    search(query) {
        this.searchQuery = query.toLowerCase().trim();
        this.applyFilters();
        
        Utils.log('Menu searched for:', query);
        EventBus.emit('menu:searched', query);
    }
    
    // Apply current filters
    applyFilters() {
        let filtered = [...this.items];
        
        // Filter by category
        if (this.currentCategory && this.currentCategory !== 'all') {
            filtered = filtered.filter(item => 
                item.category === this.currentCategory
            );
        }
        
        // Filter by search query
        if (this.searchQuery) {
            filtered = filtered.filter(item =>
                item.name.toLowerCase().includes(this.searchQuery) ||
                item.description.toLowerCase().includes(this.searchQuery) ||
                item.category.toLowerCase().includes(this.searchQuery)
            );
        }
        
        // Filter by availability
        filtered = filtered.filter(item => item.is_available);
        
        this.filteredItems = filtered;
        this.notifyListeners({ 
            type: 'filtered', 
            items: this.filteredItems,
            category: this.currentCategory,
            search: this.searchQuery
        });
    }
    
    // Get all items
    getItems() {
        return [...this.items];
    }
    
    // Get filtered items
    getFilteredItems() {
        return [...this.filteredItems];
    }
    
    // Get categories
    getCategories() {
        return [...this.categories];
    }
    
    // Get item by ID
    getItem(itemId) {
        return this.items.find(item => item.id === itemId);
    }
    
    // Refresh menu
    async refresh() {
        await this.loadMenu();
    }
}

// ===== MENU DISPLAY CONTROLLER =====
class MenuDisplayController {
    constructor() {
        this.container = null;
        this.categoriesContainer = null;
        this.searchInput = null;
        this.loadingEl = null;
        
        this.init();
    }
    
    init() {
        this.container = document.getElementById('menu-grid');
        this.categoriesContainer = document.querySelector('.menu-filters');
        this.searchInput = document.getElementById('menu-search');
        this.loadingEl = document.querySelector('.menu-loading');
        
        if (!this.container) {
            Utils.error('Menu container not found');
            return;
        }
        
        this.bindEvents();
        this.setupMenuListener();
        this.setupFilterButtons();
        
        Utils.log('Menu Display Controller initialized');
    }
    
    setupFilterButtons() {
        if (!this.categoriesContainer) return;
        
        // Bind existing filter buttons
        const filterButtons = this.categoriesContainer.querySelectorAll('.filter-btn');
        filterButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const filter = btn.dataset.filter;
                
                // Map HTML filter values to category names
                let category = filter;
                switch(filter) {
                    case 'pizza':
                        category = 'pizza';
                        break;
                    case 'bebida':
                        category = 'bebida';
                        break;
                    case 'sobremesa':
                        category = 'sobremesa';
                        break;
                    case 'entrada':
                        category = 'entrada';
                        break;
                    case 'promocao':
                        category = 'promocao';
                        break;
                    case 'all':
                    default:
                        category = 'all';
                        break;
                }
                
                // Update filter
                menu.filterByCategory(category);
                
                // Update button states
                filterButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                console.log('🔍 Filter applied:', filter, '→', category);
            });
        });
    }
    
    bindEvents() {
        // Search input
        if (this.searchInput) {
            let searchTimeout;
            this.searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    menu.search(e.target.value);
                }, 300);
            });
        }
        
        // Clear search button
        const clearBtn = document.getElementById('clear-search');
        clearBtn?.addEventListener('click', () => {
            this.searchInput.value = '';
            menu.search('');
        });
    }
    
    setupMenuListener() {
        menu.onMenuChange((data) => {
            switch (data.type) {
                case 'loading':
                    this.toggleLoading(data.loading);
                    break;
                    
                case 'loaded':
                case 'filtered':
                    this.renderItems(data.items);
                    if (data.categories) {
                        this.renderCategories(data.categories);
                    }
                    break;
                    
                case 'error':
                    this.showError(data.error);
                    break;
            }
        });
    }
    
    toggleLoading(loading) {
        if (this.loadingEl) {
            this.loadingEl.style.display = loading ? 'block' : 'none';
        }
        
        if (this.container) {
            this.container.style.opacity = loading ? '0.5' : '1';
        }
    }
    
    renderCategories(categories) {
        if (!this.categoriesContainer) return;
        
        const allCategories = ['all', ...categories];
        
        this.categoriesContainer.innerHTML = allCategories.map(category => `
            <button class="filter-btn ${menu.currentCategory === category ? 'active' : ''}" 
                    data-filter="${category}">
                <i class="fas ${this.getCategoryIcon(category)}"></i>
                ${this.getCategoryLabel(category)}
            </button>
        `).join('');
        
        // Bind category buttons
        this.categoriesContainer.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const category = btn.dataset.filter;
                menu.filterByCategory(category);
                
                // Update active state
                this.categoriesContainer.querySelectorAll('.category-btn').forEach(b => {
                    b.classList.remove('active');
                });
                btn.classList.add('active');
            });
        });
    }
    
    renderItems(items) {
        if (!this.container) return;
        
        if (items.length === 0) {
            this.container.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-search"></i>
                    <h3>Nenhum item encontrado</h3>
                    <p>Tente ajustar sua pesquisa ou categoria</p>
                </div>
            `;
            return;
        }
        
        this.container.innerHTML = items.map(item => this.renderMenuItem(item)).join('');
        
        // Bind item events
        this.bindItemEvents();
    }
    
    renderMenuItem(item) {
        const inCart = cart.hasItem(item.id);
        const cartQuantity = inCart ? cart.getItem(item.id).quantity : 0;
        
        // Mapear categoria para imagem padrão
        const getCategoryImage = (category) => {
            const categoryImages = {
                'pizza': 'assets/images/pizza.svg',
                'bebida': 'assets/images/bebida.svg',
                'sobremesa': 'assets/images/sobremesa.svg',
                'entrada': 'assets/images/entrada.svg',
                'promocao': 'assets/images/promocao.svg'
            };
            const image = categoryImages[category.toLowerCase()] || 'assets/images/todos.svg';
            console.log(`Categoria: ${category} -> Imagem: ${image}`);
            return image;
        };
        
        return `
            <div class="menu-card" data-item-id="${item.id}">
                <div class="menu-card-image">
                    <img src="${getCategoryImage(item.category)}" alt="${item.name}" loading="lazy" class="category-image">
                    ${!item.is_available ? '<div class="unavailable-overlay">Indisponível</div>' : ''}
                </div>
                <div class="menu-card-content">
                    <div class="menu-card-header">
                        <h3 class="menu-card-title">${item.name}</h3>
                        <span class="menu-card-category">${item.category}</span>
                    </div>
                    <p class="menu-card-description">${item.description}</p>
                    <div class="menu-card-footer">
                        <span class="menu-card-price">${Utils.formatCurrency(item.price)}</span>
                        <div class="menu-card-actions">
                            ${item.is_available ? `
                                ${inCart ? `
                                    <div class="quantity-controls">
                                        <button class="quantity-btn decrease" data-action="decrease">
                                            <i class="fas fa-minus"></i>
                                        </button>
                                        <span class="quantity-display">${cartQuantity}</span>
                                        <button class="quantity-btn increase" data-action="increase">
                                            <i class="fas fa-plus"></i>
                                        </button>
                                    </div>
                                ` : `
                                    <button class="add-to-cart-btn" data-action="add">
                                        <i class="fas fa-plus"></i> Adicionar
                                    </button>
                                `}
                            ` : `
                                <button class="add-to-cart-btn" disabled>
                                    Indisponível
                                </button>
                            `}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    bindItemEvents() {
        this.container.querySelectorAll('.menu-card').forEach(card => {
            const itemId = parseInt(card.dataset.itemId);
            const item = menu.getItem(itemId);
            
            if (!item || !item.is_available) return;
            
            // Add to cart button
            const addBtn = card.querySelector('[data-action="add"]');
            addBtn?.addEventListener('click', (e) => {
                e.stopPropagation();
                this.addItemToCart(item);
            });
            
            // Quantity controls
            const increaseBtn = card.querySelector('[data-action="increase"]');
            increaseBtn?.addEventListener('click', (e) => {
                e.stopPropagation();
                const cartItem = cart.getItem(itemId);
                if (cartItem && cartItem.quantity < CONFIG.CART.MAX_QUANTITY) {
                    cart.updateQuantity(itemId, cartItem.quantity + 1);
                }
            });
            
            const decreaseBtn = card.querySelector('[data-action="decrease"]');
            decreaseBtn?.addEventListener('click', (e) => {
                e.stopPropagation();
                const cartItem = cart.getItem(itemId);
                if (cartItem) {
                    if (cartItem.quantity > 1) {
                        cart.updateQuantity(itemId, cartItem.quantity - 1);
                    } else {
                        cart.removeItem(itemId);
                    }
                }
            });
            
            // Card click to show details
            card.addEventListener('click', () => {
                this.showItemDetails(item);
            });
        });
    }
    
    addItemToCart(item, quantity = 1) {
        if (cart.addItem(item, quantity)) {
            // Re-render this specific item to show quantity controls
            const card = this.container.querySelector(`[data-item-id="${item.id}"]`);
            if (card) {
                const updatedHtml = this.renderMenuItem(item);
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = updatedHtml;
                const newCard = tempDiv.firstElementChild;
                
                card.replaceWith(newCard);
                
                // Re-bind events for the new card
                this.bindItemEvents();
            }
        }
    }
    
    showItemDetails(item) {
        const existingModal = document.querySelector('.item-details-modal');
        if (existingModal) {
            existingModal.remove();
        }
        
        const modal = Utils.createElement('div', { className: 'item-details-modal modal open' }, [
            Utils.createElement('div', { className: 'modal-content' }, [
                Utils.createElement('div', { className: 'modal-header' }, [
                    Utils.createElement('h3', {}, [item.name]),
                    Utils.createElement('button', { 
                        className: 'modal-close',
                        innerHTML: '<i class="fas fa-times"></i>'
                    })
                ]),
                Utils.createElement('div', { className: 'modal-body item-details' }, [
                    Utils.createElement('div', { className: 'item-image-large' }, [
                        item.image_url 
                            ? Utils.createElement('img', { src: item.image_url, alt: item.name })
                            : Utils.createElement('i', { className: 'fas fa-utensils' })
                    ]),
                    Utils.createElement('div', { className: 'item-info' }, [
                        Utils.createElement('div', { className: 'item-category' }, [item.category]),
                        Utils.createElement('p', { className: 'item-description-full' }, [item.description]),
                        Utils.createElement('div', { className: 'item-price-large' }, [Utils.formatCurrency(item.price)]),
                        Utils.createElement('div', { className: 'item-actions' }, [
                            item.is_available 
                                ? Utils.createElement('button', {
                                    className: 'btn btn-primary add-item-btn',
                                    innerHTML: '<i class="fas fa-plus"></i> Adicionar ao Carrinho'
                                })
                                : Utils.createElement('button', {
                                    className: 'btn btn-secondary',
                                    disabled: true,
                                    innerHTML: 'Indisponível'
                                })
                        ])
                    ])
                ])
            ])
        ]);
        
        document.body.appendChild(modal);
        
        // Bind events
        const closeBtn = modal.querySelector('.modal-close');
        closeBtn.addEventListener('click', () => modal.remove());
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        const addBtn = modal.querySelector('.add-item-btn');
        addBtn?.addEventListener('click', () => {
            this.addItemToCart(item);
            modal.remove();
        });
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        modal.addEventListener('remove', () => {
            document.body.style.overflow = '';
        });
    }
    
    showError(message) {
        showNotification(`Erro ao carregar cardápio: ${message}`, 'error');
    }
    
    // Helper functions for category display
    getCategoryIcon(category) {
        const icons = {
            'all': 'fa-th',
            'pizza': 'fa-pizza-slice',
            'bebida': 'fa-glass-cheers',
            'sobremesa': 'fa-ice-cream',
            'entrada': 'fa-leaf',
            'promocao': 'fa-percentage'
        };
        return icons[category] || 'fa-utensils';
    }
    
    getCategoryLabel(category) {
        const labels = {
            'all': 'Todos',
            'pizza': 'Pizzas',
            'bebida': 'Bebidas',
            'sobremesa': 'Sobremesas',
            'entrada': 'Entradas',
            'promocao': 'Promoções'
        };
        return labels[category] || category;
    }
}

// ===== CART INTEGRATION =====
// Listen for cart changes to update menu display
EventBus.on('cart:change', () => {
    // Re-render menu items to show updated quantities
    const menuController = window.menuController;
    if (menuController && menu.filteredItems) {
        menuController.renderItems(menu.filteredItems);
    }
});

// ===== INITIALIZE SERVICES =====
const menu = new MenuService();
let menuController;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    menuController = new MenuDisplayController();
    window.menuController = menuController;
});

// ===== GLOBAL ACCESS =====
window.menu = menu;

console.log('✅ Menu.js fully loaded');
Utils.log('Menu system ready');