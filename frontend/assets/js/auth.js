// ===== AUTHENTICATION SERVICE =====
class AuthService {
    constructor() {
        this.user = null;
        this.isAuthenticated = false;
        this.listeners = [];
        
        this.init();
        Utils.log('Auth Service initialized');
    }
    
    init() {
        // Wait for AuthManager to be ready if available
        if (window.AuthManager) {
            window.AuthManager.waitForInit().then(() => {
                this.syncWithAuthManager();
            });
        } else {
            // Fallback to old method
            this.loadFromStorage();
        }
        
        // Listen to auth events
        EventBus.on('auth:login', this.handleLogin.bind(this));
        EventBus.on('auth:logout', this.handleLogout.bind(this));
        EventBus.on('auth:expired', this.handleExpired.bind(this));
        EventBus.on('auth:register', this.handleRegister.bind(this));
        
        // Listen to AuthManager events if available
        if (window.AuthManager) {
            window.AuthManager.on('auth:login', this.handleLogin.bind(this));
            window.AuthManager.on('auth:logout', this.handleLogout.bind(this));
            window.AuthManager.on('auth:token_refreshed', this.handleTokenRefresh.bind(this));
        }
    }
    
    syncWithAuthManager() {
        if (window.AuthManager && window.AuthManager.isLoggedIn()) {
            this.user = window.AuthManager.getUser();
            this.isAuthenticated = true;
            this.updateAdminMenuVisibility();
            Utils.log('User authenticated via AuthManager:', this.user.username);
        } else {
            this.loadFromStorage();
        }
    }
    
    loadFromStorage() {
        // Try multiple keys for compatibility
        let token = Utils.storage.get(CONFIG.AUTH.TOKEN_KEY) ||
                   localStorage.getItem('hashtag_pizzaria_token') ||
                   localStorage.getItem('access_token');
                   
        let user = Utils.storage.get(CONFIG.AUTH.USER_KEY);
        if (!user) {
            const userData = localStorage.getItem('hashtag_pizzaria_user') || 
                           localStorage.getItem('user_data');
            if (userData) {
                try {
                    user = JSON.parse(userData);
                } catch (e) {
                    console.warn('Invalid user data in storage');
                }
            }
        }
        
        if (token && user) {
            this.user = user;
            this.isAuthenticated = true;
            this.updateAdminMenuVisibility();
            Utils.log('User already authenticated:', user.username);
        }
    }
    
    handleLogin(data) {
        this.user = data.user;
        this.isAuthenticated = true;
        this.updateAdminMenuVisibility();
        this.notifyListeners('login', data);
        Utils.log('User logged in:', data.user.username);
    }
    
    handleLogout() {
        this.user = null;
        this.isAuthenticated = false;
        this.updateAdminMenuVisibility();
        this.notifyListeners('logout');
        Utils.log('User logged out');
    }
    
    handleTokenRefresh(data) {
        // Token was refreshed, no need to update UI but log the event
        Utils.log('Token refreshed successfully');
    }
    
    handleExpired() {
        this.user = null;
        this.isAuthenticated = false;
        this.notifyListeners('expired');
        Utils.log('Session expired');
        showNotification('Sessão expirada. Faça login novamente.', 'warning');
    }
    
    handleRegister(data) {
        this.notifyListeners('register', data);
        Utils.log('User registered:', data);
    }
    
    // Add auth state listener
    onAuthChange(callback) {
        this.listeners.push(callback);
        
        // Return unsubscribe function
        return () => {
            this.listeners = this.listeners.filter(cb => cb !== callback);
        };
    }
    
    // Notify all listeners
    notifyListeners(event, data) {
        this.listeners.forEach(callback => {
            try {
                callback(event, data, this.user);
            } catch (error) {
                Utils.error('Auth listener error:', error);
            }
        });
    }
    
    // Login method
    async login(email, password) {
        try {
            // Use AuthManager if available
            if (window.AuthManager && window.AuthManager.isInitialized) {
                const response = await window.AuthManager.login({
                    username: email,
                    password: password
                });
                
                // Sync local state
                this.user = response.user;
                this.isAuthenticated = true;
                this.updateAdminMenuVisibility();
                
                showNotification(CONFIG.SUCCESS.LOGIN, 'success');
                return response;
            } else {
                // Fallback to API
                const credentials = {
                    username: email,
                    password: password
                };
                
                const response = await api.login(credentials);
                showNotification(CONFIG.SUCCESS.LOGIN, 'success');
                return response;
            }
        } catch (error) {
            Utils.error('Login error:', error);
            showNotification(error.message, 'error');
            throw error;
        }
    }
    
    // Register method
    async register(userData) {
        try {
            // Validate data
            this.validateRegistrationData(userData);
            
            const response = await api.register(userData);
            showNotification(CONFIG.SUCCESS.REGISTER, 'success');
            return response;
        } catch (error) {
            Utils.error('Registration error:', error);
            showNotification(error.message, 'error');
            throw error;
        }
    }
    
    // Logout method
    logout() {
        // Use AuthManager if available
        if (window.AuthManager && window.AuthManager.isInitialized) {
            window.AuthManager.logout();
        } else {
            api.logout();
        }
        showNotification(CONFIG.SUCCESS.LOGOUT, 'success');
    }
    
    // Validate registration data
    validateRegistrationData(data) {
        const errors = [];
        
        if (!data.full_name || data.full_name.trim().length < 2) {
            errors.push('Nome completo deve ter pelo menos 2 caracteres');
        }
        
        if (!data.username || data.username.length < CONFIG.VALIDATION.USERNAME_MIN_LENGTH) {
            errors.push(`Nome de usuário deve ter pelo menos ${CONFIG.VALIDATION.USERNAME_MIN_LENGTH} caracteres`);
        }
        
        if (!Utils.isValidEmail(data.email)) {
            errors.push('Email inválido');
        }
        
        if (!Utils.isValidPassword(data.password)) {
            errors.push(`Senha deve ter pelo menos ${CONFIG.VALIDATION.PASSWORD_MIN_LENGTH} caracteres`);
        }
        
        if (data.password !== data.confirm_password) {
            errors.push('Senhas não coincidem');
        }
        
        if (errors.length > 0) {
            throw new Error(errors.join(', '));
        }
    }
    
    // Check if user has permission
    hasPermission(permission) {
        return this.isAuthenticated && this.user && this.user.permissions?.includes(permission);
    }
    
    // Check if user is admin
    isAdmin() {
        return this.isAuthenticated && this.user && this.user.is_admin;
    }
    
    // Update admin menu visibility
    updateAdminMenuVisibility() {
        const adminMenus = document.querySelectorAll('.admin-only');
        adminMenus.forEach(menu => {
            menu.style.display = this.isAdmin() ? 'block' : 'none';
        });
    }
    
    // Get current user
    getCurrentUser() {
        return this.user;
    }
    
    // Check auth status
    checkAuthStatus() {
        return this.isAuthenticated;
    }
    
    // Refresh user data
    async refreshUserData() {
        if (!this.isAuthenticated) return null;
        
        try {
            const response = await api.getCurrentUser();
            this.user = response.data;
            Utils.storage.set(CONFIG.AUTH.USER_KEY, this.user);
            this.notifyListeners('userUpdate', this.user);
            return this.user;
        } catch (error) {
            Utils.error('Failed to refresh user data:', error);
            return null;
        }
    }
}

// ===== AUTH MODAL CONTROLLER =====
class AuthModalController {
    constructor() {
        this.modal = null;
        this.form = null;
        this.currentTab = 'login';
        this.isLoading = false;
        
        this.init();
    }
    
    init() {
        this.modal = document.getElementById('auth-modal');
        this.form = document.getElementById('auth-form');
        
        if (!this.modal || !this.form) {
            // Se estivermos na página admin, não precisa do modal de auth
            if (window.location.pathname.includes('admin.html')) {
                Utils.log('Admin page detected, skipping auth modal initialization');
                return;
            }
            Utils.error('Auth modal elements not found');
            return;
        }
        
        this.bindEvents();
        
        // Initialize with login tab active (disable register fields)
        this.switchTab('login');
        
        Utils.log('Auth Modal Controller initialized');
    }
    
    bindEvents() {
        // Modal close events
        const closeBtn = document.getElementById('auth-close');
        closeBtn?.addEventListener('click', () => this.close());
        
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });
        
        // Tab switching
        const tabs = document.querySelectorAll('.auth-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const tabName = tab.dataset.tab;
                this.switchTab(tabName);
            });
        });
        
        // Form submission
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmit();
        });
        
        // Listen for auth state changes
        auth.onAuthChange((event) => {
            if (event === 'login') {
                this.close();
            }
        });
    }
    
    open(tab = 'login') {
        this.switchTab(tab);
        this.modal.classList.add('open');
        document.body.style.overflow = 'hidden';
        
        // Focus first enabled input
        setTimeout(() => {
            const activeContent = tab === 'login' ? 
                document.getElementById('login-content') : 
                document.getElementById('register-content');
            const firstInput = activeContent.querySelector('input:not([disabled])');
            firstInput?.focus();
        }, 100);
    }
    
    close() {
        this.modal.classList.remove('open');
        document.body.style.overflow = '';
        this.resetForm();
    }
    
    switchTab(tabName) {
        this.currentTab = tabName;
        
        // Update tab buttons
        const tabs = document.querySelectorAll('.auth-tab');
        tabs.forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });
        
        // Update content visibility and disable validation for hidden fields
        const loginContent = document.getElementById('login-content');
        const registerContent = document.getElementById('register-content');
        
        // Verificar se os elementos existem (proteção para página admin)
        if (!loginContent || !registerContent) {
            console.log('Auth modal elements not found - skipping tab switch');
            return;
        }
        
        if (tabName === 'login') {
            loginContent.style.display = 'block';
            registerContent.style.display = 'none';
            
            // Enable validation for login fields
            loginContent.querySelectorAll('input[required]').forEach(input => {
                input.disabled = false;
            });
            
            // Disable validation for register fields
            registerContent.querySelectorAll('input[required]').forEach(input => {
                input.disabled = true;
            });
        } else {
            loginContent.style.display = 'none';
            registerContent.style.display = 'block';
            
            // Disable validation for login fields
            loginContent.querySelectorAll('input[required]').forEach(input => {
                input.disabled = true;
            });
            
            // Enable validation for register fields
            registerContent.querySelectorAll('input[required]').forEach(input => {
                input.disabled = false;
            });
        }
        
        // Update title
        const title = document.getElementById('auth-title');
        title.textContent = tabName === 'login' ? 'Entrar' : 'Cadastrar';
        
        this.resetForm();
    }
    
    async handleSubmit() {
        if (this.isLoading) return;
        
        try {
            this.setLoading(true);
            
            if (this.currentTab === 'login') {
                await this.handleLogin();
            } else {
                await this.handleRegister();
            }
        } catch (error) {
            // Error is already handled by auth service
        } finally {
            this.setLoading(false);
        }
    }
    
    async handleLogin() {
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        
        if (!email || !password) {
            showNotification('Preencha todos os campos', 'error');
            return;
        }
        
        await auth.login(email, password);
    }
    
    async handleRegister() {
        const name = document.getElementById('register-name').value;
        const username = document.getElementById('register-username').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;
        const confirmPassword = document.getElementById('register-confirm').value;
        
        if (!name || !username || !email || !password || !confirmPassword) {
            showNotification('Preencha todos os campos', 'error');
            return;
        }
        
        const userData = {
            full_name: name,
            username: username,
            email: email,
            password: password,
            confirm_password: confirmPassword
        };
        
        await auth.register(userData);
        
        // Switch to login tab after successful registration
        showNotification('Agora você pode fazer login', 'success');
        this.switchTab('login');
    }
    
    setLoading(loading) {
        this.isLoading = loading;
        const submitBtn = this.form.querySelector('button[type="submit"]');
        
        if (loading) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${this.currentTab === 'login' ? 'Entrando...' : 'Cadastrando...'}`;
        } else {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `<i class="fas fa-${this.currentTab === 'login' ? 'sign-in-alt' : 'user-plus'}"></i> ${this.currentTab === 'login' ? 'Entrar' : 'Cadastrar'}`;
        }
    }
    
    resetForm() {
        this.form.reset();
        this.setLoading(false);
    }
}

// ===== USER BUTTON CONTROLLER =====
class UserButtonController {
    constructor() {
        this.userBtn = null;
        this.init();
    }
    
    init() {
        this.userBtn = document.getElementById('user-btn');
        
        if (!this.userBtn) {
            Utils.error('User button not found');
            return;
        }
        
        this.bindEvents();
        this.updateButton();
        
        // Listen for auth changes
        auth.onAuthChange(() => {
            this.updateButton();
        });
        
        Utils.log('User Button Controller initialized');
    }
    
    bindEvents() {
        this.userBtn.addEventListener('click', () => {
            if (auth.checkAuthStatus()) {
                this.showUserMenu();
            } else {
                authModal.open();
            }
        });
    }
    
    updateButton() {
        const icon = this.userBtn.querySelector('i');
        const user = auth.getCurrentUser();
        
        if (auth.checkAuthStatus() && user) {
            icon.className = 'fas fa-user-circle';
            this.userBtn.title = `Olá, ${user.full_name || user.username}`;
        } else {
            icon.className = 'fas fa-user';
            this.userBtn.title = 'Entrar / Cadastrar';
        }
    }
    
    showUserMenu() {
        // Create user menu dynamically
        const existingMenu = document.querySelector('.user-menu');
        if (existingMenu) {
            existingMenu.remove();
        }
        
        const user = auth.getCurrentUser();
        const menu = Utils.createElement('div', { className: 'user-menu' }, [
            Utils.createElement('div', { className: 'user-info' }, [
                Utils.createElement('strong', {}, [user.full_name || user.username]),
                Utils.createElement('small', {}, [user.email])
            ]),
            Utils.createElement('hr'),
            Utils.createElement('ul', { className: 'user-menu-list' }, [
                Utils.createElement('li', {}, [
                    Utils.createElement('button', { 
                        className: 'menu-item profile-btn',
                        innerHTML: '<i class="fas fa-user"></i> Meu Perfil'
                    })
                ]),
                Utils.createElement('li', {}, [
                    Utils.createElement('button', { 
                        className: 'menu-item orders-btn',
                        innerHTML: '<i class="fas fa-shopping-bag"></i> Meus Pedidos'
                    })
                ])
            ]),
            Utils.createElement('hr'),
            Utils.createElement('button', { 
                className: 'menu-item logout-btn',
                innerHTML: '<i class="fas fa-sign-out-alt"></i> Sair'
            })
        ]);
        
        // Position menu
        const rect = this.userBtn.getBoundingClientRect();
        menu.style.position = 'fixed';
        menu.style.top = `${rect.bottom + 10}px`;
        menu.style.right = `${window.innerWidth - rect.right}px`;
        menu.style.zIndex = '2000';
        
        document.body.appendChild(menu);
        
        // Add event listeners
        const profileBtn = menu.querySelector('.profile-btn');
        const ordersBtn = menu.querySelector('.orders-btn');
        
        profileBtn.addEventListener('click', () => {
            this.showProfileModal();
            menu.remove();
        });
        
        ordersBtn.addEventListener('click', () => {
            this.showOrdersModal();
            menu.remove();
        });
        
        menu.querySelector('.logout-btn').addEventListener('click', () => {
            auth.logout();
            menu.remove();
        });
        
        // Close menu when clicking outside
        setTimeout(() => {
            document.addEventListener('click', function closeMenu(e) {
                if (!menu.contains(e.target) && e.target !== this.userBtn) {
                    menu.remove();
                    document.removeEventListener('click', closeMenu);
                }
            });
        }, 0);
    }
    
    async showProfileModal() {
        try {
            const user = auth.getCurrentUser();
            if (!user) return;
            
            // Remove existing modal
            const existingModal = document.querySelector('.profile-modal');
            if (existingModal) {
                existingModal.remove();
            }
            
            const modal = Utils.createElement('div', { className: 'profile-modal modal open' }, [
                Utils.createElement('div', { className: 'modal-content' }, [
                    Utils.createElement('div', { className: 'modal-header' }, [
                        Utils.createElement('h3', {}, ['Meu Perfil']),
                        Utils.createElement('button', { 
                            className: 'modal-close',
                            innerHTML: '<i class="fas fa-times"></i>'
                        })
                    ]),
                    Utils.createElement('div', { className: 'modal-body' }, [
                        Utils.createElement('div', { className: 'profile-info' }, [
                            Utils.createElement('div', { className: 'profile-field' }, [
                                Utils.createElement('label', {}, ['Nome Completo:']),
                                Utils.createElement('span', {}, [user.full_name || user.username])
                            ]),
                            Utils.createElement('div', { className: 'profile-field' }, [
                                Utils.createElement('label', {}, ['Username:']),
                                Utils.createElement('span', {}, [user.username])
                            ]),
                            Utils.createElement('div', { className: 'profile-field' }, [
                                Utils.createElement('label', {}, ['Email:']),
                                Utils.createElement('span', {}, [user.email])
                            ]),
                            Utils.createElement('div', { className: 'profile-field' }, [
                                Utils.createElement('label', {}, ['Tipo de usuário:']),
                                Utils.createElement('span', { 
                                    className: user.is_admin ? 'admin-badge' : 'user-badge'
                                }, [user.is_admin ? 'Administrador' : 'Cliente'])
                            ])
                        ])
                    ])
                ])
            ]);
            
            document.body.appendChild(modal);
            
            // Bind close events
            const closeBtn = modal.querySelector('.modal-close');
            closeBtn.addEventListener('click', () => modal.remove());
            
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.remove();
                }
            });
            
        } catch (error) {
            Utils.error('Error showing profile:', error);
            showNotification('Erro ao carregar perfil', 'error');
        }
    }
    
    async showOrdersModal() {
        try {
            // Remove existing modal
            const existingModal = document.querySelector('.orders-modal');
            if (existingModal) {
                existingModal.remove();
            }
            
            const modal = Utils.createElement('div', { className: 'orders-modal modal open' }, [
                Utils.createElement('div', { className: 'modal-content large-modal' }, [
                    Utils.createElement('div', { className: 'modal-header' }, [
                        Utils.createElement('h3', {}, ['Meus Pedidos']),
                        Utils.createElement('button', { 
                            className: 'modal-close',
                            innerHTML: '<i class="fas fa-times"></i>'
                        })
                    ]),
                    Utils.createElement('div', { className: 'modal-body' }, [
                        Utils.createElement('div', { 
                            className: 'orders-loading',
                            innerHTML: '<i class="fas fa-spinner fa-spin"></i> Carregando pedidos...'
                        })
                    ])
                ])
            ]);
            
            document.body.appendChild(modal);
            
            // Bind close events
            const closeBtn = modal.querySelector('.modal-close');
            closeBtn.addEventListener('click', () => modal.remove());
            
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.remove();
                }
            });
            
            // Load orders
            this.loadUserOrders(modal);
            
        } catch (error) {
            Utils.error('Error showing orders:', error);
            showNotification('Erro ao carregar pedidos', 'error');
        }
    }
    
    async loadUserOrders(modal) {
        try {
            console.log('🔍 Carregando pedidos do usuário...');
            const response = await api.getMyOrders();
            console.log('📦 Resposta da API:', response);
            
            const orders = response.data || [];
            console.log('📋 Pedidos encontrados:', orders.length);
            
            const modalBody = modal.querySelector('.modal-body');
            
            if (orders.length === 0) {
                modalBody.innerHTML = `
                    <div class="empty-orders">
                        <i class="fas fa-shopping-bag"></i>
                        <p>Você ainda não fez nenhum pedido</p>
                        <span>Que tal começar com uma deliciosa pizza?</span>
                        <button class="btn btn-primary" onclick="location.hash='menu'; document.querySelector('.orders-modal').remove();">
                            Ver Cardápio
                        </button>
                    </div>
                `;
                return;
            }
            
            modalBody.innerHTML = `
                <div class="orders-list">
                    ${orders.map(order => this.renderOrderSummary(order)).join('')}
                </div>
            `;
            
        } catch (error) {
            Utils.error('Error loading orders:', error);
            console.error('❌ Detalhes do erro:', {
                message: error.message,
                status: error.status,
                type: error.type,
                response: error.response
            });
            
            const modalBody = modal.querySelector('.modal-body');
            let errorMessage = 'Erro ao carregar pedidos';
            
            if (error.status === 401) {
                errorMessage = 'Sessão expirada. Faça login novamente.';
            } else if (error.status === 404) {
                errorMessage = 'Endpoint de pedidos não encontrado.';
            } else if (error.status >= 500) {
                errorMessage = 'Erro no servidor. Tente novamente mais tarde.';
            } else if (error.type === 'NETWORK') {
                errorMessage = 'Erro de conexão. Verifique sua internet.';
            }
            
            modalBody.innerHTML = `
                <div class="orders-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h4>Problema ao carregar pedidos</h4>
                    <p>${errorMessage}</p>
                    <div class="error-details">
                        <small>Código: ${error.status || 'N/A'} | Tipo: ${error.type || 'Desconhecido'}</small>
                    </div>
                    <div class="error-actions">
                        <button class="btn btn-secondary" onclick="this.closest('.orders-modal').remove()">
                            Fechar
                        </button>
                        <button class="btn btn-primary" onclick="location.reload()">
                            Tentar Novamente
                        </button>
                    </div>
                </div>
            `;
        }
    }
    
    renderOrderSummary(order) {
        const statusClass = this.getStatusClass(order.status);
        const statusText = this.getStatusText(order.status);
        
        return `
            <div class="order-card">
                <div class="order-header">
                    <div class="order-number">#${order.order_number}</div>
                    <div class="order-status ${statusClass}">${statusText}</div>
                </div>
                <div class="order-info">
                    <div class="order-date">
                        ${Utils.formatDate(order.created_at, { 
                            day: '2-digit', 
                            month: '2-digit', 
                            year: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                        })}
                    </div>
                    <div class="order-items-count">
                        ${order.items_count} item${order.items_count > 1 ? 's' : ''}
                    </div>
                    <div class="order-total">
                        ${Utils.formatCurrency(order.total_amount)}
                    </div>
                </div>
            </div>
        `;
    }
    
    getStatusClass(status) {
        const statusMap = {
            'pendente': 'status-pending',
            'confirmado': 'status-confirmed',
            'preparando': 'status-preparing',
            'pronto': 'status-ready',
            'saiu_entrega': 'status-delivery',
            'entregue': 'status-delivered',
            'cancelado': 'status-cancelled'
        };
        return statusMap[status] || 'status-unknown';
    }
    
    getStatusText(status) {
        const statusMap = {
            'pendente': 'Pendente',
            'confirmado': 'Confirmado',
            'preparando': 'Preparando',
            'pronto': 'Pronto',
            'saiu_entrega': 'Saiu para Entrega',
            'entregue': 'Entregue',
            'cancelado': 'Cancelado'
        };
        return statusMap[status] || 'Desconhecido';
    }
}

// ===== INITIALIZE SERVICES =====
const auth = new AuthService();
const authModal = new AuthModalController();
const userButton = new UserButtonController();

// ===== GLOBAL ACCESS =====
window.auth = auth;
window.authModal = authModal;

Utils.log('Authentication system ready');