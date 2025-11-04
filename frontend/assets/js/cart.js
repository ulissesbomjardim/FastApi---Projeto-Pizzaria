// ===== CART SERVICE =====
class CartService {
    constructor() {
        this.items = [];
        this.total = 0;
        this.listeners = [];
        
        this.init();
        Utils.log('Cart Service initialized');
    }
    
    init() {
        // Load cart from storage
        this.loadFromStorage();
        this.updateTotal();
        
        // Auto-save to storage when cart changes
        this.onCartChange(() => {
            this.saveToStorage();
        });
    }
    
    // Load cart from local storage
    loadFromStorage() {
        const cartData = Utils.storage.get(CONFIG.CART.STORAGE_KEY);
        if (cartData && Array.isArray(cartData)) {
            this.items = cartData;
            Utils.log('Cart loaded from storage:', this.items.length, 'items');
        }
    }
    
    // Save cart to local storage
    saveToStorage() {
        Utils.storage.set(CONFIG.CART.STORAGE_KEY, this.items, CONFIG.CART.EXPIRY_HOURS);
    }
    
    // Add cart change listener
    onCartChange(callback) {
        this.listeners.push(callback);
        
        // Return unsubscribe function
        return () => {
            this.listeners = this.listeners.filter(cb => cb !== callback);
        };
    }
    
    // Notify listeners of cart changes
    notifyListeners() {
        this.listeners.forEach(callback => {
            try {
                callback(this.items, this.total);
            } catch (error) {
                Utils.error('Cart listener error:', error);
            }
        });
        
        // Emit global event
        EventBus.emit('cart:change', {
            items: this.items,
            total: this.total,
            count: this.getItemCount()
        });
    }
    
    // Add item to cart
    addItem(item, quantity = 1) {
        try {
            // Validate item
            if (!item || !item.id) {
                throw new Error('Item inválido');
            }
            
            // Validate quantity
            if (quantity < CONFIG.CART.MIN_QUANTITY || quantity > CONFIG.CART.MAX_QUANTITY) {
                throw new Error(`Quantidade deve estar entre ${CONFIG.CART.MIN_QUANTITY} e ${CONFIG.CART.MAX_QUANTITY}`);
            }
            
            // Check if item is available
            if (!item.is_available) {
                throw new Error('Item não disponível');
            }
            
            // Check if item already exists in cart
            const existingItem = this.items.find(cartItem => cartItem.id === item.id);
            
            if (existingItem) {
                const newQuantity = existingItem.quantity + quantity;
                if (newQuantity > CONFIG.CART.MAX_QUANTITY) {
                    throw new Error(`Quantidade máxima para este item: ${CONFIG.CART.MAX_QUANTITY}`);
                }
                existingItem.quantity = newQuantity;
            } else {
                // Add new item
                this.items.push({
                    id: item.id,
                    name: item.name,
                    description: item.description,
                    price: item.price,
                    category: item.category,
                    image_url: item.image_url,
                    quantity: quantity,
                    addedAt: Date.now()
                });
            }
            
            this.updateTotal();
            this.notifyListeners();
            
            Utils.log('Item added to cart:', item.name, 'x', quantity);
            showNotification(CONFIG.SUCCESS.CART_ADD, 'success');
            
            return true;
        } catch (error) {
            Utils.error('Failed to add item to cart:', error);
            showNotification(error.message, 'error');
            return false;
        }
    }
    
    // Remove item from cart
    removeItem(itemId) {
        const itemIndex = this.items.findIndex(item => item.id === itemId);
        
        if (itemIndex === -1) {
            showNotification('Item não encontrado no carrinho', 'error');
            return false;
        }
        
        const removedItem = this.items.splice(itemIndex, 1)[0];
        this.updateTotal();
        this.notifyListeners();
        
        Utils.log('Item removed from cart:', removedItem.name);
        showNotification(CONFIG.SUCCESS.CART_REMOVE, 'success');
        
        return true;
    }
    
    // Update item quantity
    updateQuantity(itemId, quantity) {
        try {
            // Validate quantity
            if (quantity < CONFIG.CART.MIN_QUANTITY || quantity > CONFIG.CART.MAX_QUANTITY) {
                throw new Error(`Quantidade deve estar entre ${CONFIG.CART.MIN_QUANTITY} e ${CONFIG.CART.MAX_QUANTITY}`);
            }
            
            const item = this.items.find(item => item.id === itemId);
            if (!item) {
                throw new Error('Item não encontrado no carrinho');
            }
            
            item.quantity = quantity;
            this.updateTotal();
            this.notifyListeners();
            
            Utils.log('Item quantity updated:', item.name, 'x', quantity);
            showNotification(CONFIG.SUCCESS.CART_UPDATE, 'success');
            
            return true;
        } catch (error) {
            Utils.error('Failed to update item quantity:', error);
            showNotification(error.message, 'error');
            return false;
        }
    }
    
    // Clear cart
    clear() {
        this.items = [];
        this.total = 0;
        this.notifyListeners();
        
        Utils.log('Cart cleared');
        showNotification('Carrinho limpo', 'success');
    }
    
    // Get cart items
    getItems() {
        return [...this.items];
    }
    
    // Get total items count
    getItemCount() {
        return this.items.reduce((count, item) => count + item.quantity, 0);
    }
    
    // Get cart total
    getTotal() {
        return this.total;
    }
    
    // Check if cart is empty
    isEmpty() {
        return this.items.length === 0;
    }
    
    // Update total price
    updateTotal() {
        this.total = this.items.reduce((total, item) => {
            return total + (item.price * item.quantity);
        }, 0);
    }
    
    // Get item by ID
    getItem(itemId) {
        return this.items.find(item => item.id === itemId);
    }
    
    // Check if item is in cart
    hasItem(itemId) {
        return this.items.some(item => item.id === itemId);
    }
    
    // Get cart summary for order
    getOrderSummary() {
        return {
            items: this.items.map(item => ({
                item_id: item.id,
                quantity: item.quantity
            })),
            total: this.total,
            item_count: this.getItemCount()
        };
    }
}

// ===== CART SIDEBAR CONTROLLER =====
class CartSidebarController {
    constructor() {
        this.sidebar = null;
        this.cartItems = null;
        this.cartTotal = null;
        this.cartCount = null;
        this.checkoutBtn = null;
        
        this.init();
    }
    
    init() {
        this.sidebar = document.getElementById('cart-sidebar');
        this.cartItems = document.getElementById('cart-items');
        this.cartTotal = document.getElementById('cart-total');
        this.cartCount = document.getElementById('cart-count');
        this.checkoutBtn = document.getElementById('cart-checkout');
        
        if (!this.sidebar || !this.cartItems) {
            Utils.error('Cart sidebar elements not found');
            return;
        }
        
        this.bindEvents();
        this.render();
        
        // Listen for cart changes
        cart.onCartChange(() => {
            this.render();
        });
        
        Utils.log('Cart Sidebar Controller initialized');
    }
    
    bindEvents() {
        // Open cart button
        const cartBtn = document.getElementById('cart-btn');
        cartBtn?.addEventListener('click', () => this.toggle());
        
        // Close cart button
        const closeBtn = document.getElementById('cart-close');
        closeBtn?.addEventListener('click', () => this.close());
        
        // Close on outside click
        this.sidebar.addEventListener('click', (e) => {
            if (e.target === this.sidebar) {
                this.close();
            }
        });
        
        // Checkout button
        this.checkoutBtn?.addEventListener('click', () => this.handleCheckout());
    }
    
    open() {
        this.sidebar.classList.add('open');
        document.body.style.overflow = 'hidden';
    }
    
    close() {
        this.sidebar.classList.remove('open');
        document.body.style.overflow = '';
    }
    
    toggle() {
        if (this.sidebar.classList.contains('open')) {
            this.close();
        } else {
            this.open();
        }
    }
    
    render() {
        const items = cart.getItems();
        const total = cart.getTotal();
        const count = cart.getItemCount();
        
        // Update cart count in navbar
        if (this.cartCount) {
            this.cartCount.textContent = count;
            this.cartCount.style.display = count > 0 ? 'block' : 'none';
        }
        
        // Update total
        if (this.cartTotal) {
            this.cartTotal.textContent = Utils.formatCurrency(total).replace('R$', '').trim();
        }
        
        // Update checkout button
        if (this.checkoutBtn) {
            this.checkoutBtn.disabled = items.length === 0;
        }
        
        // Render items
        this.renderItems(items);
    }
    
    renderItems(items) {
        if (items.length === 0) {
            this.cartItems.innerHTML = `
                <div class="empty-cart">
                    <i class="fas fa-shopping-cart"></i>
                    <p>Seu carrinho está vazio</p>
                    <span>Adicione itens do nosso cardápio!</span>
                </div>
            `;
            return;
        }
        
        this.cartItems.innerHTML = items.map(item => this.renderCartItem(item)).join('');
        
        // Bind events for cart items
        this.bindItemEvents();
    }
    
    renderCartItem(item) {
        const itemTotal = item.price * item.quantity;
        
        return `
            <div class="cart-item" data-item-id="${item.id}">
                <div class="cart-item-image">
                    ${item.image_url 
                        ? `<img src="${item.image_url}" alt="${item.name}">`
                        : '<i class="fas fa-utensils"></i>'
                    }
                </div>
                <div class="cart-item-info">
                    <div class="cart-item-name" title="${item.name}">${item.name}</div>
                    <div class="cart-item-price">${Utils.formatCurrency(itemTotal)}</div>
                    <div class="cart-item-controls">
                        <button class="quantity-btn decrease-btn" data-action="decrease">
                            <i class="fas fa-minus"></i>
                        </button>
                        <span class="quantity-display">${item.quantity}</span>
                        <button class="quantity-btn increase-btn" data-action="increase">
                            <i class="fas fa-plus"></i>
                        </button>
                        <button class="remove-item-btn" data-action="remove" title="Remover item">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    bindItemEvents() {
        this.cartItems.querySelectorAll('.cart-item').forEach(itemEl => {
            const itemId = parseInt(itemEl.dataset.itemId);
            
            // Quantity controls
            itemEl.addEventListener('click', (e) => {
                e.stopPropagation();
                
                const action = e.target.closest('[data-action]')?.dataset.action;
                if (!action) return;
                
                const item = cart.getItem(itemId);
                if (!item) return;
                
                switch (action) {
                    case 'increase':
                        if (item.quantity < CONFIG.CART.MAX_QUANTITY) {
                            cart.updateQuantity(itemId, item.quantity + 1);
                        } else {
                            showNotification(`Quantidade máxima: ${CONFIG.CART.MAX_QUANTITY}`, 'warning');
                        }
                        break;
                    
                    case 'decrease':
                        if (item.quantity > CONFIG.CART.MIN_QUANTITY) {
                            cart.updateQuantity(itemId, item.quantity - 1);
                        } else {
                            cart.removeItem(itemId);
                        }
                        break;
                    
                    case 'remove':
                        cart.removeItem(itemId);
                        break;
                }
            });
        });
    }
    
    async handleCheckout() {
        if (!auth.checkAuthStatus()) {
            showNotification('Faça login para finalizar seu pedido', 'warning');
            authModal.open();
            return;
        }
        
        if (cart.isEmpty()) {
            showNotification('Seu carrinho está vazio', 'warning');
            return;
        }
        
        try {
            // For now, just show a simple form
            this.showCheckoutForm();
        } catch (error) {
            Utils.error('Checkout error:', error);
            showNotification('Erro ao finalizar pedido', 'error');
        }
    }
    
    showCheckoutForm() {
        const existingForm = document.querySelector('.checkout-form');
        if (existingForm) {
            existingForm.remove();
        }
        
        const form = Utils.createElement('div', { className: 'checkout-form modal open' }, [
            Utils.createElement('div', { className: 'modal-content' }, [
                Utils.createElement('div', { className: 'modal-header' }, [
                    Utils.createElement('h3', {}, ['Finalizar Pedido']),
                    Utils.createElement('button', { 
                        className: 'modal-close',
                        innerHTML: '<i class="fas fa-times"></i>'
                    })
                ]),
                Utils.createElement('div', { className: 'modal-body' }, [
                    Utils.createElement('form', { id: 'checkout-form' }, [
                        Utils.createElement('div', { className: 'form-group' }, [
                            Utils.createElement('input', {
                                type: 'text',
                                placeholder: 'Nome completo',
                                required: true,
                                id: 'customer-name'
                            })
                        ]),
                        Utils.createElement('div', { className: 'form-group' }, [
                            Utils.createElement('input', {
                                type: 'tel',
                                placeholder: '(11) 99999-9999',
                                required: true,
                                id: 'customer-phone',
                                maxlength: '15'
                            })
                        ]),
                        Utils.createElement('div', { className: 'form-group' }, [
                            Utils.createElement('textarea', {
                                placeholder: 'Endereço completo',
                                required: true,
                                rows: 3,
                                id: 'customer-address'
                            })
                        ]),
                        Utils.createElement('div', { className: 'form-group' }, [
                            Utils.createElement('select', { 
                                required: true,
                                id: 'payment-method'
                            }, [
                                Utils.createElement('option', { value: '' }, ['Forma de pagamento']),
                                Utils.createElement('option', { value: 'pix' }, ['PIX']),
                                Utils.createElement('option', { value: 'cartao_credito' }, ['Cartão de Crédito']),
                                Utils.createElement('option', { value: 'cartao_debito' }, ['Cartão de Débito']),
                                Utils.createElement('option', { value: 'dinheiro' }, ['Dinheiro']),
                                Utils.createElement('option', { value: 'vale_refeicao' }, ['Vale Refeição'])
                            ])
                        ]),
                        Utils.createElement('div', { className: 'checkout-summary' }, [
                            Utils.createElement('div', { className: 'summary-line' }, [
                                Utils.createElement('span', {}, ['Total']),
                                Utils.createElement('strong', {}, [Utils.formatCurrency(cart.getTotal())])
                            ])
                        ]),
                        Utils.createElement('button', {
                            type: 'submit',
                            className: 'btn btn-primary',
                            innerHTML: '<i class="fas fa-check"></i> Confirmar Pedido'
                        })
                    ])
                ])
            ])
        ]);
        
        document.body.appendChild(form);
        
        // Bind events
        const closeBtn = form.querySelector('.modal-close');
        closeBtn.addEventListener('click', () => form.remove());
        
        form.addEventListener('click', (e) => {
            if (e.target === form) {
                form.remove();
            }
        });
        
        const checkoutForm = form.querySelector('#checkout-form');
        checkoutForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.processOrder(checkoutForm, form);
        });
        
        // Add phone formatting
        const phoneInput = form.querySelector('#customer-phone');
        phoneInput.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 11) {
                value = value.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
            } else if (value.length >= 7) {
                value = value.replace(/(\d{2})(\d{4})(\d{0,4})/, '($1) $2-$3');
            } else if (value.length >= 3) {
                value = value.replace(/(\d{2})(\d{0,5})/, '($1) $2');
            }
            e.target.value = value;
        });

        // Focus first input
        setTimeout(() => {
            form.querySelector('input').focus();
        }, 100);
    }
    
    async processOrder(form, modal) {
        try {
            const formData = new FormData(form);
            const customerAddress = formData.get('customer-address') || document.getElementById('customer-address').value;
            const customerPhone = formData.get('customer-phone') || document.getElementById('customer-phone').value;
            
            // Format phone number
            const formatPhone = (phone) => {
                if (!phone) return phone;
                // Remove all non-digits
                const digits = phone.replace(/\D/g, '');
                // Format as (XX) XXXXX-XXXX
                if (digits.length === 11) {
                    return `(${digits.slice(0,2)}) ${digits.slice(2,7)}-${digits.slice(7)}`;
                }
                return phone;
            };
            
            const orderData = {
                customer_name: formData.get('customer-name') || document.getElementById('customer-name').value,
                customer_phone: formatPhone(customerPhone),
                is_delivery: true, // Assumindo que sempre é entrega por enquanto
                delivery_address: customerAddress ? {
                    street: customerAddress,
                    number: "S/N",         // Número da casa/apt
                    neighborhood: "Centro", // Valor padrão por enquanto
                    city: "São Paulo",      // Valor padrão por enquanto
                    state: "SP",           // Valor padrão por enquanto
                    zip_code: "01000-000", // Valor padrão por enquanto
                    complement: null
                } : null,
                payment_method: formData.get('payment-method') || document.getElementById('payment-method').value,
                observations: null,
                items: cart.getOrderSummary().items.map(item => ({
                    item_id: item.item_id,
                    quantity: item.quantity,
                    observations: null
                }))
            };
            
            // Basic validation
            if (!orderData.customer_name || !orderData.customer_phone || !orderData.payment_method) {
                showNotification('Preencha todos os campos obrigatórios', 'error');
                return;
            }
            
            // Validate delivery address if is_delivery is true
            if (orderData.is_delivery && !orderData.delivery_address?.street) {
                showNotification('Endereço de entrega é obrigatório', 'error');
                return;
            }
            
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';
            
            const response = await api.createOrder(orderData);
            
            // Success
            showNotification(CONFIG.SUCCESS.ORDER_CREATED, 'success');
            cart.clear();
            modal.remove();
            this.close();
            
            Utils.log('Order created successfully:', response.data);
            
        } catch (error) {
            Utils.error('Order creation failed:', error);
            showNotification(error.message, 'error');
            
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-check"></i> Confirmar Pedido';
        }
    }
}

// ===== INITIALIZE SERVICES =====
const cart = new CartService();
const cartSidebar = new CartSidebarController();

// ===== GLOBAL ACCESS =====
window.cart = cart;

Utils.log('Cart system ready');