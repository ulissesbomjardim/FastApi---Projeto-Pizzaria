// ===================================
// 🔧 PAINEL ADMINISTRATIVO JS
// ===================================

class AdminPanel {
    constructor() {
        console.log('AdminPanel constructor called');
        this.currentView = 'dashboard';
        this.orders = [];
        this.items = [];
        this.stats = {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkAdminAccess();
    }

    setupEventListeners() {
        // Navegação entre seções com proteção contra cliques automáticos
        let lastNavigationTime = 0;
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('admin-nav-btn')) {
                const now = Date.now();
                
                // Impedir cliques muito rápidos (menos de 1 segundo)
                if (now - lastNavigationTime < 1000) {
                    console.log('🚫 Navigation blocked - too fast (potential auto-click)');
                    e.preventDefault();
                    e.stopPropagation();
                    return;
                }
                
                lastNavigationTime = now;
                const view = e.target.dataset.view;
                console.log('🔄 Navigation to:', view);
                this.switchView(view);
            }

            // Botões de ação
            if (e.target.classList.contains('action-btn')) {
                this.handleActionClick(e.target);
            }

            // Fechar modais
            if (e.target.classList.contains('modal-close') || e.target.classList.contains('admin-modal')) {
                this.closeModal();
            }
        });

        // Formulário de item
        document.addEventListener('submit', (e) => {
            if (e.target.id === 'itemForm') {
                console.log('📋 Form submit event detected:', e);
                console.log('📋 Modal ready status:', e.target.dataset.modalReady);
                
                // Só processar se o modal estiver marcado como pronto
                if (e.target.dataset.modalReady === 'true') {
                    console.log('📋 Processing form submit...');
                    e.preventDefault();
                    this.handleItemSubmit(e.target);
                } else {
                    console.log('📋 Form submit ignored - modal not ready');
                    e.preventDefault();
                }
            }
        });

        // Atualização de status de pedido
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('status-select')) {
                this.updateOrderStatus(e.target);
            }
        });
    }

    async checkAdminAccess() {
        // Verificar se há token antes de carregar o dashboard
        const token = localStorage.getItem('hashtag_pizzaria_token') || localStorage.getItem('access_token');
        
        if (!token) {
            console.log('AdminPanel: No token found, dashboard not loaded');
            return;
        }
        
        console.log('AdminPanel initialized with token, loading dashboard...');
        this.loadDashboard();
    }

    switchView(view) {
        // Atualizar navegação
        document.querySelectorAll('.admin-nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-view="${view}"]`).classList.add('active');

        this.currentView = view;

        // Carregar conteúdo
        switch (view) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'orders':
                this.loadOrders();
                break;
            case 'items':
                this.loadItems();
                break;
        }
    }

    async loadDashboard() {
        try {
            console.log('📊 loadDashboard() started');
            const content = document.getElementById('adminContent');
            console.log('📍 Dashboard content element:', content ? 'Found' : 'NOT FOUND', content);
            
            content.innerHTML = `
                <div class="loading">
                    Carregando estatísticas...
                </div>
            `;

            console.log('📡 Fetching dashboard stats...');
            // Carregar estatísticas
            const stats = await this.fetchStats();
            console.log('📊 Dashboard stats received:', stats);
            
            // Verificar se stats foi carregado corretamente
            if (!stats) {
                throw new Error('Não foi possível carregar as estatísticas');
            }
            
            content.innerHTML = `
                <h2><i class="fas fa-chart-bar"></i> Dashboard Administrativo</h2>
                
                <div class="admin-stats">
                    <div class="stat-card revenue">
                        <h3 class="stat-value">R$ ${parseFloat(stats.total_revenue || 0).toFixed(2)}</h3>
                        <p class="stat-label">Receita Total</p>
                        <i class="fas fa-dollar-sign stat-icon"></i>
                    </div>
                    
                    <div class="stat-card orders">
                        <h3 class="stat-value">${stats.total_orders}</h3>
                        <p class="stat-label">Total de Pedidos</p>
                        <i class="fas fa-shopping-cart stat-icon"></i>
                    </div>
                    
                    <div class="stat-card pending">
                        <h3 class="stat-value">${stats.orders_by_status.find(item => item.status === 'pendente')?.count || 0}</h3>
                        <p class="stat-label">Pedidos Pendentes</p>
                        <i class="fas fa-clock stat-icon"></i>
                    </div>
                    
                    <div class="stat-card completed">
                        <h3 class="stat-value">${stats.orders_by_status.find(item => item.status === 'entregue')?.count || 0}</h3>
                        <p class="stat-label">Pedidos Entregues</p>
                        <i class="fas fa-check-circle stat-icon"></i>
                    </div>
                </div>

                <div class="admin-table-container">
                    <h3><i class="fas fa-list"></i> Resumo por Status</h3>
                    <table class="admin-table">
                        <thead>
                            <tr>
                                <th>Status</th>
                                <th>Quantidade</th>
                                <th>Percentual</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${stats.orders_by_status.map(({status, count}) => {
                                const percentage = ((count / stats.total_orders) * 100).toFixed(1);
                                return `
                                    <tr>
                                        <td><span class="status-badge status-${status}">${this.formatStatus(status)}</span></td>
                                        <td>${count}</td>
                                        <td>${percentage}%</td>
                                    </tr>
                                `;
                            }).join('')}
                        </tbody>
                    </table>
                </div>
            `;

            console.log('📝 Setting dashboard HTML content...');
            console.log('✅ Dashboard loaded successfully');

        } catch (error) {
            console.error('Erro ao carregar dashboard:', error);
            document.getElementById('adminContent').innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Erro ao carregar dashboard</h3>
                    <p>Não foi possível carregar as estatísticas.</p>
                </div>
            `;
        }
    }

    async loadOrders() {
        try {
            console.log('📋 loadOrders() started');
            const content = document.getElementById('adminContent');
            console.log('📍 Content element:', content ? 'Found' : 'NOT FOUND', content);
            content.innerHTML = `
                <div class="loading">
                    Carregando pedidos...
                </div>
            `;

            const orders = await this.fetchAllOrders();
            this.orders = orders;

            content.innerHTML = `
                <h2><i class="fas fa-list-alt"></i> Gerenciar Pedidos</h2>
                
                <div class="admin-filters">
                    <div class="filters-row">
                        <div class="filter-group">
                            <label>Status</label>
                            <select id="statusFilter">
                                <option value="">Todos os status</option>
                                <option value="pendente">Pendente</option>
                                <option value="confirmado">Confirmado</option>
                                <option value="preparando">Preparando</option>
                                <option value="pronto">Pronto</option>
                                <option value="saiu_entrega">Saiu para entrega</option>
                                <option value="entregue">Entregue</option>
                                <option value="cancelado">Cancelado</option>
                            </select>
                        </div>
                        
                        <div class="filter-group">
                            <label>Buscar</label>
                            <input type="text" id="searchOrder" placeholder="Número do pedido ou cliente...">
                        </div>
                        
                        <button class="btn-filter" onclick="adminPanel.filterOrders()">
                            <i class="fas fa-search"></i> Filtrar
                        </button>
                    </div>
                </div>

                <div class="admin-table-container">
                    <table class="admin-table">
                        <thead>
                            <tr>
                                <th>Pedido</th>
                                <th>Cliente</th>
                                <th>Total</th>
                                <th>Status</th>
                                <th>Data</th>
                                <th>Ações</th>
                            </tr>
                        </thead>
                        <tbody id="ordersTableBody">
                            ${this.renderOrdersTable(orders)}
                        </tbody>
                    </table>
                </div>
            `;

            // Adicionar event listeners para filtros
            document.getElementById('statusFilter').addEventListener('change', () => this.filterOrders());
            document.getElementById('searchOrder').addEventListener('input', () => this.filterOrders());

        } catch (error) {
            console.error('Erro ao carregar pedidos:', error);
            document.getElementById('adminContent').innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Erro ao carregar pedidos</h3>
                    <p>Não foi possível carregar a lista de pedidos.</p>
                </div>
            `;
        }
    }

    async loadItems() {
        try {
            console.log('🍕 loadItems() started');
            const content = document.getElementById('adminContent');
            console.log('📍 Content element:', content ? 'Found' : 'NOT FOUND', content);
            content.innerHTML = `
                <div class="loading">
                    Carregando itens...
                </div>
            `;

            console.log('📡 Fetching items from API...');
            const items = await this.fetchAllItems();
            console.log('📊 Items received:', items?.length || 0, items);
            this.items = items;

            console.log('🎨 Rendering items HTML...');
            const htmlContent = `
                <h2><i class="fas fa-utensils"></i> Gerenciar Cardápio</h2>
                
                <div class="admin-filters">
                    <div class="filters-row">
                        <div class="filter-group">
                            <label>Categoria</label>
                            <select id="categoryFilter">
                                <option value="">Todas as categorias</option>
                                <option value="pizza">Pizza</option>
                                <option value="bebida">Bebida</option>
                                <option value="sobremesa">Sobremesa</option>
                                <option value="entrada">Entrada</option>
                                <option value="promocao">Promoção</option>
                            </select>
                        </div>
                        
                        <div class="filter-group">
                            <label>Disponibilidade</label>
                            <select id="availabilityFilter">
                                <option value="">Todos</option>
                                <option value="true">Disponíveis</option>
                                <option value="false">Indisponíveis</option>
                            </select>
                        </div>
                        
                        <div class="filter-group">
                            <label>Buscar</label>
                            <input type="text" id="searchItem" placeholder="Nome do item...">
                        </div>
                        
                        <button class="btn-filter" onclick="adminPanel.filterItems()">
                            <i class="fas fa-search"></i> Filtrar
                        </button>
                        
                        <button class="btn-primary" onclick="window.adminPanel.showAddItemModal()">
                            <i class="fas fa-plus"></i> Novo Item
                        </button>
                    </div>
                </div>

                <div class="admin-table-container">
                    <table class="admin-table">
                        <thead>
                            <tr>
                                <th>Nome</th>
                                <th>Categoria</th>
                                <th>Preço</th>
                                <th>Disponível</th>
                                <th>Tempo Preparo</th>
                                <th>Ações</th>
                            </tr>
                        </thead>
                        <tbody id="itemsTableBody">
                            ${this.renderItemsTable(items)}
                        </tbody>
                    </table>
                </div>
            `;

            console.log('📝 Setting HTML content, length:', htmlContent.length);
            content.innerHTML = htmlContent;
            console.log('✅ HTML content set successfully');

            // Adicionar event listeners para filtros
            document.getElementById('categoryFilter').addEventListener('change', () => this.filterItems());
            document.getElementById('availabilityFilter').addEventListener('change', () => this.filterItems());
            document.getElementById('searchItem').addEventListener('input', () => this.filterItems());

        } catch (error) {
            console.error('Erro ao carregar itens:', error);
            document.getElementById('adminContent').innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Erro ao carregar itens</h3>
                    <p>Não foi possível carregar o cardápio.</p>
                </div>
            `;
        }
    }

    renderOrdersTable(orders) {
        console.log('📋 renderOrdersTable called with:', orders?.length || 0, 'orders');
        if (!orders || orders.length === 0) {
            return `
                <tr>
                    <td colspan="6" style="text-align: center; padding: 40px;">
                        <i class="fas fa-inbox" style="font-size: 3rem; color: #ccc; display: block; margin-bottom: 15px;"></i>
                        Nenhum pedido encontrado
                    </td>
                </tr>
            `;
        }

        return orders.map(order => `
            <tr>
                <td><strong>${order.order_number}</strong></td>
                <td>${order.customer_name}</td>
                <td>R$ ${parseFloat(order.total_amount || 0).toFixed(2)}</td>
                <td>
                    <select class="status-select" data-order-id="${order.id}">
                        <option value="pendente" ${order.status === 'pendente' ? 'selected' : ''}>Pendente</option>
                        <option value="confirmado" ${order.status === 'confirmado' ? 'selected' : ''}>Confirmado</option>
                        <option value="preparando" ${order.status === 'preparando' ? 'selected' : ''}>Preparando</option>
                        <option value="pronto" ${order.status === 'pronto' ? 'selected' : ''}>Pronto</option>
                        <option value="saiu_entrega" ${order.status === 'saiu_entrega' ? 'selected' : ''}>Saiu para entrega</option>
                        <option value="entregue" ${order.status === 'entregue' ? 'selected' : ''}>Entregue</option>
                        <option value="cancelado" ${order.status === 'cancelado' ? 'selected' : ''}>Cancelado</option>
                    </select>
                </td>
                <td>${new Date(order.created_at).toLocaleDateString('pt-BR')}</td>
                <td>
                    <div class="action-buttons">
                        <button class="action-btn view" data-action="view-order" data-id="${order.id}">
                            <i class="fas fa-eye"></i> Ver
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    renderItemsTable(items) {
        console.log('🔧 renderItemsTable called with:', items?.length || 0, 'items');
        if (!items || items.length === 0) {
            return `
                <tr>
                    <td colspan="6" style="text-align: center; padding: 40px;">
                        <i class="fas fa-utensils" style="font-size: 3rem; color: #ccc; display: block; margin-bottom: 15px;"></i>
                        Nenhum item encontrado
                    </td>
                </tr>
            `;
        }

        return items.map(item => `
            <tr>
                <td><strong>${item.name}</strong></td>
                <td><span class="status-badge status-${item.category}">${this.formatCategory(item.category)}</span></td>
                <td>R$ ${parseFloat(item.price || 0).toFixed(2)}</td>
                <td>
                    <span class="status-badge ${item.is_available ? 'status-entregue' : 'status-cancelado'}">
                        ${item.is_available ? 'Sim' : 'Não'}
                    </span>
                </td>
                <td>${item.preparation_time || '-'} min</td>
                <td>
                    <div class="action-buttons">
                        <button class="action-btn edit" data-action="edit-item" data-id="${item.id}">
                            <i class="fas fa-edit"></i> Editar
                        </button>
                        <button class="action-btn toggle" data-action="toggle-item" data-id="${item.id}">
                            <i class="fas fa-power-off"></i> ${item.is_available ? 'Desativar' : 'Ativar'}
                        </button>
                        <button class="action-btn delete" data-action="delete-item" data-id="${item.id}">
                            <i class="fas fa-trash"></i> Deletar
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    formatStatus(status) {
        const statusMap = {
            'pendente': 'Pendente',
            'confirmado': 'Confirmado',
            'preparando': 'Preparando',
            'pronto': 'Pronto',
            'saiu_entrega': 'Saiu para Entrega',
            'entregue': 'Entregue',
            'cancelado': 'Cancelado'
        };
        return statusMap[status] || status;
    }

    formatCategory(category) {
        const categoryMap = {
            'pizza': 'Pizza',
            'bebida': 'Bebida',
            'sobremesa': 'Sobremesa',
            'entrada': 'Entrada',
            'promocao': 'Promoção'
        };
        return categoryMap[category] || category;
    }

    async handleActionClick(btn) {
        const action = btn.dataset.action;
        const id = parseInt(btn.dataset.id);

        try {
            console.log(`🔧 Action clicked: ${action}, ID: ${id}`);
            switch (action) {
                case 'view-order':
                    await this.viewOrder(id);
                    break;
                case 'edit-item':
                    console.log(`📝 Editing item: ${id}`);
                    await this.editItem(id);
                    break;
                case 'toggle-item':
                    await this.toggleItem(id);
                    break;
                case 'delete-item':
                    await this.deleteItem(id);
                    break;
                default:
                    console.log(`❓ Unknown action: ${action}`);
            }
        } catch (error) {
            console.error(`Erro na ação ${action}:`, error);
            showNotification('Erro ao executar ação', 'error');
        }
    }

    async updateOrderStatus(select) {
        const orderId = select.dataset.orderId;
        const newStatus = select.value;
        const originalStatus = select.dataset.originalStatus || select.options[select.selectedIndex].defaultSelected;

        try {
            const api = window.apiService || this.getApiService();
            const response = await api.patch(`/orders/${orderId}/status?new_status=${newStatus}`);
            
            if (response.ok) {
                showNotification(`Status do pedido atualizado para: ${this.formatStatus(newStatus)}`, 'success');
                select.dataset.originalStatus = newStatus;
            } else {
                throw new Error('Erro ao atualizar status');
            }
        } catch (error) {
            console.error('Erro ao atualizar status do pedido:', error);
            showNotification('Erro ao atualizar status do pedido', 'error');
            // Reverter seleção
            select.value = originalStatus;
        }
    }

    async viewOrder(orderId) {
        try {
            console.log('📋 Viewing order:', orderId);
            const api = window.apiService || this.getApiService();
            
            // ✅ Buscar pedido completo com itens do endpoint específico
            console.log('🔍 Fetching complete order data from /orders/' + orderId);
            const response = await api.get(`/orders/${orderId}`);
            
            if (!response.ok) {
                throw new Error(`Erro ao buscar pedido: ${response.status}`);
            }
            
            const order = await response.json();
            console.log('📊 Complete order data received:', order);
            console.log('🍕 Order items:', order.items);
            console.log('📊 Items length:', order.items?.length);
            console.log('💰 Subtotal:', order.subtotal);
            console.log('🚚 Delivery fee:', order.delivery_fee);
            console.log('💵 Total:', order.total_amount);
            
            if (!order) {
                throw new Error('Pedido não encontrado');
            }
            
            const modalHtml = `
                <div class="admin-modal show">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h3 class="modal-title">
                                <i class="fas fa-receipt"></i> Detalhes do Pedido ${order.order_number}
                            </h3>
                            <button class="modal-close">&times;</button>
                        </div>
                        <div class="modal-body">
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Cliente:</label>
                                    <p><strong>${order.customer_name || order.user?.name || 'Cliente não identificado'}</strong></p>
                                </div>
                                <div class="form-group">
                                    <label>Telefone:</label>
                                    <p>${order.customer_phone || order.user?.phone || 'Não informado'}</p>
                                </div>
                                <div class="form-group">
                                    <label>Status:</label>
                                    <span class="status-badge status-${order.status || 'pendente'}">${this.formatStatus(order.status || 'pendente')}</span>
                                </div>
                                <div class="form-group">
                                    <label>Tipo:</label>
                                    <p>${order.is_delivery !== undefined ? (order.is_delivery ? 'Delivery' : 'Retirada') : 'Não informado'}</p>
                                </div>
                            </div>

                            ${(order.delivery_address && order.delivery_address.street) ? `
                                <div class="form-section">
                                    <h3>Endereço de Entrega</h3>
                                    <p>${order.delivery_address.street || 'Rua não informada'}, ${order.delivery_address.number || 'S/N'}</p>
                                    <p>${order.delivery_address.district || 'Bairro não informado'} - ${order.delivery_address.city || 'Cidade não informada'}</p>
                                    ${order.delivery_address.complement ? `<p>Complemento: ${order.delivery_address.complement}</p>` : ''}
                                </div>
                            ` : (order.is_delivery ? '<div class="form-section"><h3>Endereço de Entrega</h3><p>Endereço não informado</p></div>' : '')}

                            <div class="form-section">
                                <h3>Itens do Pedido</h3>
                                <div class="admin-table-container">
                                    <table class="admin-table">
                                        <thead>
                                            <tr>
                                                <th>Item</th>
                                                <th>Qtd</th>
                                                <th>Preço Unit.</th>
                                                <th>Subtotal</th>
                                                <th>Obs.</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${(order.items && Array.isArray(order.items) && order.items.length > 0) ? 
                                                order.items.map(item => `
                                                    <tr>
                                                        <td>${item.item?.name || item.name || 'Item não identificado'}</td>
                                                        <td>${item.quantity || 0}</td>
                                                        <td>R$ ${parseFloat(item.unit_price || item.price || 0).toFixed(2)}</td>
                                                        <td>R$ ${parseFloat(item.subtotal || (parseFloat(item.quantity || 0) * parseFloat(item.unit_price || item.price || 0)) || 0).toFixed(2)}</td>
                                                        <td>${item.observations || item.obs || '-'}</td>
                                                    </tr>
                                                `).join('') 
                                                : '<tr><td colspan="5" style="text-align: center;">Nenhum item encontrado</td></tr>'
                                            }
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            <div class="form-section">
                                <div class="form-row">
                                    <div class="form-group">
                                        <label>Subtotal:</label>
                                        <p><strong>R$ ${parseFloat(order.subtotal || 0).toFixed(2)}</strong></p>
                                    </div>
                                    <div class="form-group">
                                        <label>Taxa de Entrega:</label>
                                        <p><strong>R$ ${parseFloat(order.delivery_fee || 0).toFixed(2)}</strong></p>
                                    </div>
                                    <div class="form-group">
                                        <label>Total:</label>
                                        <p><strong style="font-size: 1.2rem; color: #28a745;">R$ ${parseFloat(order.total_amount || order.total || 0).toFixed(2)}</strong></p>
                                    </div>
                                </div>
                            </div>

                            ${order.observations ? `
                                <div class="form-section">
                                    <h3>Observações</h3>
                                    <p>${order.observations}</p>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', modalHtml);

        } catch (error) {
            console.error('Erro ao visualizar pedido:', error);
            showNotification('Erro ao carregar detalhes do pedido', 'error');
        }
    }

    showAddItemModal() {
        console.log('🆕 showAddItemModal() called - opening new item modal');
        this.showItemModal();
    }

    async editItem(itemId) {
        console.log(`🔧 editItem called with ID: ${itemId}`);
        try {
            const api = window.apiService || this.getApiService();
            console.log(`📡 Fetching item data for ID: ${itemId}`);
            const response = await api.get(`/items/get-item/${itemId}`);
            console.log(`📨 API response status: ${response.status}`);
            const item = await response.json();
            console.log(`📊 Item data received:`, item);
            console.log(`🖼️ Opening modal for item: ${item.name}`);
            this.showItemModal(item);
        } catch (error) {
            console.error('Erro ao carregar item:', error);
            showNotification('Erro ao carregar item para edição', 'error');
        }
    }

    showItemModal(item = null) {
        console.log(`🖼️ showItemModal called with item:`, item);
        const isEditing = !!item;
        const modalTitle = isEditing ? 'Editar Item' : 'Novo Item';
        console.log(`📝 Modal title: ${modalTitle}, isEditing: ${isEditing}`);

        const modalHtml = `
            <div class="admin-modal show">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3 class="modal-title">
                            <i class="fas fa-utensils"></i> ${modalTitle}
                        </h3>
                        <button class="modal-close">&times;</button>
                    </div>
                    <div class="modal-body">
                        <form id="itemForm">
                            <input type="hidden" id="itemId" value="${item ? item.id : ''}">
                            
                            <div class="form-section">
                                <h3>Informações Básicas</h3>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="itemName">Nome do Item *</label>
                                        <input type="text" id="itemName" required value="${item ? item.name : ''}" placeholder="Ex: Pizza Margherita">
                                    </div>
                                    <div class="form-group">
                                        <label for="itemCategory">Categoria *</label>
                                        <select id="itemCategory" required>
                                            <option value="">Selecione uma categoria</option>
                                            <option value="pizza" ${item && item.category === 'pizza' ? 'selected' : ''}>Pizza</option>
                                            <option value="bebida" ${item && item.category === 'bebida' ? 'selected' : ''}>Bebida</option>
                                            <option value="sobremesa" ${item && item.category === 'sobremesa' ? 'selected' : ''}>Sobremesa</option>
                                            <option value="entrada" ${item && item.category === 'entrada' ? 'selected' : ''}>Entrada</option>
                                            <option value="promocao" ${item && item.category === 'promocao' ? 'selected' : ''}>Promoção</option>
                                        </select>
                                    </div>
                                </div>
                                
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="itemPrice">Preço (R$) *</label>
                                        <input type="number" id="itemPrice" step="0.01" min="0" required value="${item ? item.price : ''}" placeholder="0.00">
                                    </div>
                                    <div class="form-group">
                                        <label for="itemSize">Tamanho</label>
                                        <select id="itemSize">
                                            <option value="pequena" ${item && item.size === 'pequena' ? 'selected' : ''}>Pequena</option>
                                            <option value="media" ${item && item.size === 'media' ? 'selected' : ''}>Média</option>
                                            <option value="grande" ${item && item.size === 'grande' ? 'selected' : ''}>Grande</option>
                                            <option value="familia" ${item && item.size === 'familia' ? 'selected' : ''}>Família</option>
                                            <option value="unico" ${item && item.size === 'unico' ? 'selected' : ''}>Único</option>
                                            <option value="350ml" ${item && item.size === '350ml' ? 'selected' : ''}>350ml</option>
                                            <option value="500ml" ${item && item.size === '500ml' ? 'selected' : ''}>500ml</option>
                                            <option value="1l" ${item && item.size === '1l' ? 'selected' : ''}>1L</option>
                                            <option value="2l" ${item && item.size === '2l' ? 'selected' : ''}>2L</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div class="form-section">
                                <h3>Detalhes</h3>
                                <div class="form-group">
                                    <label for="itemDescription">Descrição</label>
                                    <textarea id="itemDescription" placeholder="Descreva o item...">${item ? item.description : ''}</textarea>
                                </div>
                                
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="itemPrepTime">Tempo de Preparo (min)</label>
                                        <input type="number" id="itemPrepTime" min="1" value="${item ? item.preparation_time : '20'}" placeholder="20">
                                    </div>
                                    <div class="form-group">
                                        <label for="itemCalories">Calorias</label>
                                        <input type="number" id="itemCalories" min="0" value="${item ? item.calories || '' : ''}" placeholder="0">
                                    </div>
                                </div>
                                
                                <div class="form-group">
                                    <label for="itemImage">URL da Imagem</label>
                                    <input type="url" id="itemImage" value="${item ? item.image_url || '' : ''}" placeholder="https://exemplo.com/imagem.jpg">
                                </div>
                            </div>

                            <div class="form-section">
                                <h3>Ingredientes e Alérgenos</h3>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="itemIngredients">Ingredientes (separados por vírgula)</label>
                                        <textarea id="itemIngredients" placeholder="molho de tomate, queijo mussarela, manjericão...">${item && item.ingredients ? (Array.isArray(item.ingredients) ? item.ingredients.join(', ') : item.ingredients) : ''}</textarea>
                                    </div>
                                    <div class="form-group">
                                        <label for="itemAllergens">Alérgenos (separados por vírgula)</label>
                                        <textarea id="itemAllergens" placeholder="glúten, lactose, ovos...">${item && item.allergens ? (Array.isArray(item.allergens) ? item.allergens.join(', ') : item.allergens) : ''}</textarea>
                                    </div>
                                </div>
                            </div>

                            <div class="checkbox-group">
                                <input type="checkbox" id="itemAvailable" ${item ? (item.is_available ? 'checked' : '') : 'checked'}>
                                <label for="itemAvailable">Item disponível para venda</label>
                            </div>

                            <div class="form-buttons">
                                <button type="button" class="btn-secondary modal-close">Cancelar</button>
                                <button type="submit" class="btn-primary">
                                    <i class="fas fa-save"></i> ${isEditing ? 'Atualizar' : 'Salvar'} Item
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Configurar eventos do modal após inserção
        const modal = document.querySelector('.admin-modal.show');
        const closeButtons = modal.querySelectorAll('.modal-close');
        
        // Event listeners para fechar modal
        closeButtons.forEach(btn => {
            btn.addEventListener('click', () => this.closeModal());
        });
        
        // Marcar que o modal foi aberto (para controle de submits)
        const form = document.getElementById('itemForm');
        if (form) {
            form.dataset.modalReady = 'true';
            console.log('� Modal form marked as ready');
        }
        
        console.log('🖼️ Modal setup complete');
    }

    async handleItemSubmit(form) {
        try {
            const formData = new FormData(form);
            const itemId = document.getElementById('itemId').value;
            const isEditing = !!itemId;

            // Debug dos elementos do formulário
            console.log('🔍 Debug form elements:');
            console.log('- itemName:', document.getElementById('itemName')?.value);
            console.log('- itemCategory:', document.getElementById('itemCategory')?.value);
            console.log('- itemSize:', document.getElementById('itemSize')?.value);
            console.log('- itemPrice:', document.getElementById('itemPrice')?.value);

            const itemData = {
                name: formData.get('itemName') || document.getElementById('itemName').value,
                category: document.getElementById('itemCategory').value,
                size: document.getElementById('itemSize').value,
                price: parseFloat(document.getElementById('itemPrice').value),
                description: document.getElementById('itemDescription').value,
                preparation_time: parseInt(document.getElementById('itemPrepTime').value) || 20,
                calories: parseInt(document.getElementById('itemCalories').value) || null,
                image_url: document.getElementById('itemImage').value || null,
                ingredients: document.getElementById('itemIngredients').value.trim() || null,
                allergens: document.getElementById('itemAllergens').value.trim() || null,
                is_available: document.getElementById('itemAvailable').checked
            };

            // Validações básicas
            if (!itemData.name || !itemData.name.trim()) {
                throw new Error('Nome do item é obrigatório');
            }
            if (!itemData.category) {
                throw new Error('Categoria é obrigatória');
            }
            if (!itemData.size) {
                throw new Error('Tamanho é obrigatório');
            }
            if (!itemData.price || itemData.price <= 0) {
                throw new Error('Preço deve ser maior que zero');
            }

            console.log('📦 Dados do item a serem enviados:', JSON.stringify(itemData, null, 2));
            console.log('📦 Dados brutos:', itemData);

            const api = window.apiService || this.getApiService();
            const endpoint = isEditing ? `/items/edit-item/${itemId}` : '/items/create-item';
            const method = isEditing ? 'PUT' : 'POST';
            
            console.log(`🌐 Fazendo ${method} para: ${endpoint}`);
            console.log('🔑 Headers que serão enviados:', api.getHeaders ? api.getHeaders() : 'N/A');
            
            let response;
            if (isEditing) {
                response = await api.put(`/items/edit-item/${itemId}`, itemData);
            } else {
                response = await api.post('/items/create-item', itemData);
            }

            if (response.ok) {
                showNotification(
                    `Item ${isEditing ? 'atualizado' : 'criado'} com sucesso!`, 
                    'success'
                );
                this.closeModal();
                this.loadItems(); // Recarregar lista
            } else {
                const errorText = await response.text();
                console.error('❌ Resposta do servidor (texto):', errorText);
                
                let errorData;
                try {
                    errorData = JSON.parse(errorText);
                } catch (e) {
                    errorData = { detail: errorText };
                }
                
                console.error('❌ Erro da API (parsed):', errorData);
                console.error('❌ Status da resposta:', response.status);
                console.error('❌ Headers da resposta:', [...response.headers.entries()]);
                
                throw new Error(`Erro ao ${isEditing ? 'atualizar' : 'criar'} item: ${JSON.stringify(errorData.detail || errorData)}`);
            }

        } catch (error) {
            console.error('Erro ao salvar item:', error);
            showNotification('Erro ao salvar item', 'error');
        }
    }

    async toggleItem(itemId) {
        try {
            const api = window.apiService || this.getApiService();
            const response = await api.put(`/items/toggle-availability/${itemId}`);
            
            if (response.ok) {
                const result = await response.json();
                showNotification(
                    `Item ${result.is_available ? 'ativado' : 'desativado'} com sucesso!`, 
                    'success'
                );
                this.loadItems(); // Recarregar lista
            } else {
                throw new Error('Erro ao alterar disponibilidade');
            }
        } catch (error) {
            console.error('Erro ao alterar disponibilidade:', error);
            showNotification('Erro ao alterar disponibilidade do item', 'error');
        }
    }

    async deleteItem(itemId) {
        if (!confirm('Tem certeza que deseja deletar este item? Esta ação não pode ser desfeita.')) {
            return;
        }

        try {
            const api = window.apiService || this.getApiService();
            const response = await api.delete(`/items/delete-item/${itemId}`);
            
            if (response.ok) {
                const result = await response.json();
                showNotification(result.message, 'success');
                this.loadItems(); // Recarregar lista
            } else {
                throw new Error('Erro ao deletar item');
            }
        } catch (error) {
            console.error('Erro ao deletar item:', error);
            showNotification('Erro ao deletar item', 'error');
        }
    }

    filterOrders() {
        const statusFilter = document.getElementById('statusFilter').value;
        const searchFilter = document.getElementById('searchOrder').value.toLowerCase();

        let filteredOrders = this.orders;

        if (statusFilter) {
            filteredOrders = filteredOrders.filter(order => order.status === statusFilter);
        }

        if (searchFilter) {
            filteredOrders = filteredOrders.filter(order => 
                order.order_number.toLowerCase().includes(searchFilter) ||
                order.customer_name.toLowerCase().includes(searchFilter)
            );
        }

        document.getElementById('ordersTableBody').innerHTML = this.renderOrdersTable(filteredOrders);
    }

    filterItems() {
        const categoryFilter = document.getElementById('categoryFilter').value;
        const availabilityFilter = document.getElementById('availabilityFilter').value;
        const searchFilter = document.getElementById('searchItem').value.toLowerCase();

        let filteredItems = this.items;

        if (categoryFilter) {
            filteredItems = filteredItems.filter(item => item.category === categoryFilter);
        }

        if (availabilityFilter !== '') {
            const isAvailable = availabilityFilter === 'true';
            filteredItems = filteredItems.filter(item => item.is_available === isAvailable);
        }

        if (searchFilter) {
            filteredItems = filteredItems.filter(item => 
                item.name.toLowerCase().includes(searchFilter) ||
                (item.description && item.description.toLowerCase().includes(searchFilter))
            );
        }

        document.getElementById('itemsTableBody').innerHTML = this.renderItemsTable(filteredItems);
    }

    closeModal() {
        const modal = document.querySelector('.admin-modal');
        if (modal) {
            modal.remove();
        }
    }

    // API calls usando fetch direto como fallback
    async fetchStats() {
        try {
            console.log('📊 fetchStats() started');
            const api = window.apiService || this.getApiService();
            console.log('📡 API service for stats:', api ? 'Found' : 'NOT FOUND');
            
            const response = await api.get('/orders/admin/stats');
            console.log('📨 Stats API response status:', response.status);
            
            if (!response.ok) {
                console.error('❌ Failed to fetch stats:', response.status);
                return null;
            }
            
            const data = await response.json();
            console.log('📊 Stats data:', data);
            return data;
        } catch (error) {
            console.error('❌ Error fetching stats:', error);
            return null;
        }
    }

    async fetchAllOrders() {
        try {
            console.log('📋 fetchAllOrders() started');
            const api = window.apiService || this.getApiService();
            console.log('📡 API service:', api ? 'Found' : 'Not found');
            
            const response = await api.get('/orders/admin/all-orders?limit=100');
            console.log('📨 API response status:', response.status);
            
            const data = await response.json();
            console.log('📊 Orders received:', data?.length || 0, data);
            return data;
        } catch (error) {
            console.error('❌ fetchAllOrders() error:', error);
            throw error;
        }
    }

    async fetchAllItems() {
        try {
            console.log('🔌 fetchAllItems() started');
            const api = window.apiService || this.getApiService();
            console.log('📡 API service:', api ? 'Found' : 'Not found');
            
            const response = await api.get('/items/list-items?available_only=false&limit=200');
            console.log('📨 API response status:', response.status);
            
            const data = await response.json();
            console.log('📊 API response data:', data);
            return data;
        } catch (error) {
            console.error('❌ fetchAllItems() error:', error);
            throw error;
        }
    }

    // Fallback API service se apiService não estiver disponível
    getApiService() {
        const baseURL = CONFIG?.API?.BASE_URL || 'http://172.25.132.243:8000';
        
        return {
            async get(endpoint) {
                let token = localStorage.getItem('hashtag_pizzaria_token') || localStorage.getItem('access_token');
                console.log('AdminPanel - Token debug:', token ? 'Token exists (' + token.substring(0, 20) + '...)' : 'No token found');
                
                const makeRequest = async (authToken) => {
                    return await fetch(`${baseURL}${endpoint}`, {
                        method: 'GET',
                        headers: {
                            'Authorization': `Bearer ${authToken}`,
                            'Content-Type': 'application/json'
                        }
                    });
                };

                let response = await makeRequest(token);
                
                // Se retornar 401, tentar refresh do token
                if (response.status === 401 && window.refreshAuthToken) {
                    console.log('Token expired, attempting refresh...');
                    const newToken = await window.refreshAuthToken();
                    if (newToken) {
                        response = await makeRequest(newToken);
                    }
                }
                
                return response;
            },
            async post(endpoint, data) {
                let token = localStorage.getItem('hashtag_pizzaria_token') || localStorage.getItem('access_token');
                
                const makeRequest = async (authToken) => {
                    return await fetch(`${baseURL}${endpoint}`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${authToken}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    });
                };

                let response = await makeRequest(token);
                
                if (response.status === 401 && window.refreshAuthToken) {
                    const newToken = await window.refreshAuthToken();
                    if (newToken) {
                        response = await makeRequest(newToken);
                    }
                }
                
                return response;
            },
            async put(endpoint, data) {
                let token = localStorage.getItem('hashtag_pizzaria_token') || localStorage.getItem('access_token');
                
                const makeRequest = async (authToken) => {
                    return await fetch(`${baseURL}${endpoint}`, {
                        method: 'PUT',
                        headers: {
                            'Authorization': `Bearer ${authToken}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    });
                };

                let response = await makeRequest(token);
                
                // Se retornar 401, tentar refresh do token
                if (response.status === 401 && window.refreshAuthToken) {
                    console.log('Token expired, attempting refresh...');
                    const newToken = await window.refreshAuthToken();
                    if (newToken) {
                        response = await makeRequest(newToken);
                    }
                }
                
                return response;
            },
            async patch(endpoint, data) {
                let token = localStorage.getItem('hashtag_pizzaria_token') || localStorage.getItem('access_token');
                
                const makeRequest = async (authToken) => {
                    return await fetch(`${baseURL}${endpoint}`, {
                        method: 'PATCH',
                        headers: {
                            'Authorization': `Bearer ${authToken}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    });
                };

                let response = await makeRequest(token);
                
                // Se retornar 401, tentar refresh do token
                if (response.status === 401 && window.refreshAuthToken) {
                    console.log('Token expired, attempting refresh...');
                    const newToken = await window.refreshAuthToken();
                    if (newToken) {
                        response = await makeRequest(newToken);
                    }
                }
                
                return response;
            },
            async delete(endpoint) {
                let token = localStorage.getItem('hashtag_pizzaria_token') || localStorage.getItem('access_token');
                
                const makeRequest = async (authToken) => {
                    return await fetch(`${baseURL}${endpoint}`, {
                        method: 'DELETE',
                        headers: {
                            'Authorization': `Bearer ${authToken}`,
                            'Content-Type': 'application/json'
                        }
                    });
                };

                let response = await makeRequest(token);
                
                // Se retornar 401, tentar refresh do token
                if (response.status === 401 && window.refreshAuthToken) {
                    console.log('Token expired, attempting refresh...');
                    const newToken = await window.refreshAuthToken();
                    if (newToken) {
                        response = await makeRequest(newToken);
                    }
                }
                
                return response;
            }
        };
    }
}

// Função para obter informações do usuário
async function getUserInfo() {
    try {
        const token = localStorage.getItem('access_token');
        const baseURL = CONFIG?.API?.BASE_URL || 'http://172.25.132.243:8000';
        
        const response = await fetch(`${baseURL}/users/me`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Erro ao obter informações do usuário:', error);
        return null;
    }
}

// Inicializar painel admin quando a página carregar
let adminPanel;

// Função para garantir que CONFIG está disponível
function ensureConfig() {
    if (typeof CONFIG === 'undefined') {
        window.CONFIG = {
            API: {
                BASE_URL: 'http://172.25.132.243:8000'
            }
        };
    }
}

// Função para garantir que showNotification está disponível
function ensureNotification() {
    if (typeof showNotification === 'undefined') {
        window.showNotification = function(message, type = 'info') {
            console.log(`[${type.toUpperCase()}] ${message}`);
            
            // Criar notificação visual simples
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: ${type === 'error' ? '#dc3545' : type === 'success' ? '#28a745' : '#007bff'};
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                z-index: 10000;
                max-width: 300px;
                font-size: 14px;
            `;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 4000);
        };
    }
}

// Expor AdminPanel globalmente para testes
window.AdminPanel = AdminPanel;

document.addEventListener('DOMContentLoaded', () => {
    // Garantir que dependências essenciais estão disponíveis
    ensureConfig();
    ensureNotification();
    
    // AdminPanel será inicializado manualmente apenas após login bem-sucedido
    console.log('AdminPanel script loaded, waiting for manual initialization...');
});