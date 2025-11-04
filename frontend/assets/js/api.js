// ===== API SERVICE =====
class ApiService {
    constructor() {
        this.baseURL = CONFIG.API.BASE_URL;
        this.timeout = CONFIG.API.TIMEOUT;
        this.retryAttempts = CONFIG.API.RETRY_ATTEMPTS;
        this.requestInterceptors = [];
        this.responseInterceptors = [];
        
        // Setup default headers
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
        
        Utils.log('API Service initialized');
    }
    
    // Add request interceptor
    addRequestInterceptor(interceptor) {
        this.requestInterceptors.push(interceptor);
    }
    
    // Add response interceptor
    addResponseInterceptor(interceptor) {
        this.responseInterceptors.push(interceptor);
    }
    
    // Get auth token - use AuthManager if available
    getAuthToken() {
        if (window.AuthManager && window.AuthManager.isInitialized) {
            return window.AuthManager.getToken();
        }
        return Utils.storage.get(CONFIG.AUTH.TOKEN_KEY);
    }
    
    // Set auth headers
    setAuthHeaders(headers = {}) {
        const token = this.getAuthToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        return headers;
    }
    
    // Build URL
    buildURL(endpoint, params = {}) {
        const url = new URL(this.baseURL + endpoint);
        Object.entries(params).forEach(([key, value]) => {
            if (value !== null && value !== undefined) {
                url.searchParams.append(key, value);
            }
        });
        return url.toString();
    }
    
    // Create AbortController with timeout
    createAbortController() {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => {
            controller.abort();
        }, this.timeout);
        
        // Clear timeout if request completes
        const originalSignal = controller.signal;
        const clearTimeoutOnComplete = () => {
            clearTimeout(timeoutId);
        };
        
        controller.signal.addEventListener('abort', clearTimeoutOnComplete);
        
        return controller;
    }
    
    // Process request through interceptors
    async processRequest(config) {
        let processedConfig = { ...config };
        
        for (const interceptor of this.requestInterceptors) {
            try {
                processedConfig = await interceptor(processedConfig);
            } catch (error) {
                Utils.error('Request interceptor error:', error);
                throw error;
            }
        }
        
        return processedConfig;
    }
    
    // Process response through interceptors
    async processResponse(response, config) {
        let processedResponse = response;
        
        for (const interceptor of this.responseInterceptors) {
            try {
                processedResponse = await interceptor(processedResponse, config);
            } catch (error) {
                Utils.error('Response interceptor error:', error);
                throw error;
            }
        }
        
        return processedResponse;
    }
    
    // Main request method
    async request(config, attemptNumber = 1) {
        try {
            // Process config through interceptors
            const processedConfig = await this.processRequest(config);
            
            // Setup request
            const controller = this.createAbortController();
            const url = this.buildURL(processedConfig.endpoint, processedConfig.params);
            
            const requestOptions = {
                method: processedConfig.method || 'GET',
                headers: {
                    ...this.defaultHeaders,
                    ...processedConfig.headers
                },
                signal: controller.signal
            };
            
            // Add auth headers if needed
            if (processedConfig.auth !== false) {
                requestOptions.headers = this.setAuthHeaders(requestOptions.headers);
            }
            
            // Add body for non-GET requests
            if (processedConfig.data && processedConfig.method !== 'GET') {
                if (processedConfig.data instanceof FormData) {
                    delete requestOptions.headers['Content-Type']; // Let browser set it
                    requestOptions.body = processedConfig.data;
                } else {
                    requestOptions.body = JSON.stringify(processedConfig.data);
                }
            }
            
            Utils.log(`API Request: ${processedConfig.method || 'GET'} ${url}`);
            Performance.mark(`request-start-${processedConfig.endpoint}`);
            
            // Make request
            const response = await fetch(url, requestOptions);
            
            Performance.measure(
                `request-${processedConfig.endpoint}`, 
                `request-start-${processedConfig.endpoint}`
            );
            
            // Process response
            const processedResponse = await this.processResponse(response, processedConfig);
            
            if (!processedResponse.ok) {
                // Try to extract detailed error message
                let errorMessage = null;
                try {
                    const contentType = processedResponse.headers.get('content-type');
                    if (contentType && contentType.includes('application/json')) {
                        const errorData = await processedResponse.clone().json();
                        errorMessage = errorData.detail || errorData.message || errorData.error;
                    }
                } catch (e) {
                    // Ignore parsing errors
                }
                
                throw new ApiError(processedResponse, 'UNKNOWN', errorMessage);
            }
            
            // Parse response data
            const contentType = processedResponse.headers.get('content-type');
            let data;
            
            if (contentType && contentType.includes('application/json')) {
                data = await processedResponse.json();
            } else {
                data = await processedResponse.text();
            }
            
            Utils.log(`API Response: ${processedConfig.method || 'GET'} ${url}`, data);
            
            return {
                data,
                status: processedResponse.status,
                statusText: processedResponse.statusText,
                headers: processedResponse.headers,
                config: processedConfig
            };
            
        } catch (error) {
            // Handle different error types
            if (error.name === 'AbortError') {
                throw new ApiError(null, 'TIMEOUT', CONFIG.ERRORS.TIMEOUT);
            }
            
            if (error instanceof ApiError) {
                throw error;
            }
            
            // Network errors
            if (!navigator.onLine) {
                throw new ApiError(null, 'NETWORK', 'Sem conexão com a internet');
            }
            
            // Retry logic for certain errors
            if (attemptNumber < this.retryAttempts && this.shouldRetry(error)) {
                Utils.warn(`Retrying request (${attemptNumber}/${this.retryAttempts}):`, config.endpoint);
                await new Promise(resolve => setTimeout(resolve, 1000 * attemptNumber));
                return this.request(config, attemptNumber + 1);
            }
            
            throw new ApiError(null, 'NETWORK', CONFIG.ERRORS.NETWORK);
        }
    }
    
    // Check if should retry request
    shouldRetry(error) {
        // Retry on network errors but not on 4xx client errors
        return !(error.response && error.response.status >= 400 && error.response.status < 500);
    }
    
    // HTTP Methods
    async get(endpoint, params = {}, config = {}) {
        return this.request({
            method: 'GET',
            endpoint,
            params,
            ...config
        });
    }
    
    async post(endpoint, data = {}, config = {}) {
        return this.request({
            method: 'POST',
            endpoint,
            data,
            ...config
        });
    }
    
    async put(endpoint, data = {}, config = {}) {
        return this.request({
            method: 'PUT',
            endpoint,
            data,
            ...config
        });
    }
    
    async patch(endpoint, data = {}, config = {}) {
        return this.request({
            method: 'PATCH',
            endpoint,
            data,
            ...config
        });
    }
    
    async delete(endpoint, config = {}) {
        return this.request({
            method: 'DELETE',
            endpoint,
            ...config
        });
    }
    
    // Authentication methods
    async login(credentials) {
        console.log('🔐 API Service - Login attempt with:', { username: credentials.username });
        
        try {
            // Use JSON endpoint instead of form data
            const response = await this.post(CONFIG.API.ENDPOINTS.LOGIN, {
                email_or_username: credentials.username || credentials.email,
                password: credentials.password
            }, {
                auth: false
            });
            
            console.log('✅ API Service - Login successful:', response.data);
            
            // Use AuthManager if available, otherwise fallback to Utils.storage
            if (window.AuthManager && window.AuthManager.isInitialized) {
                window.AuthManager.setAuthData(
                    response.data.access_token,
                    response.data.refresh_token,
                    response.data.user
                );
                console.log('💾 Auth data saved via AuthManager');
            } else {
                // Fallback storage with multiple keys for compatibility
                if (response.data.access_token) {
                    Utils.storage.set(CONFIG.AUTH.TOKEN_KEY, response.data.access_token);
                    localStorage.setItem('hashtag_pizzaria_token', response.data.access_token);
                    localStorage.setItem('access_token', response.data.access_token);
                    localStorage.setItem('authToken', response.data.access_token);
                    console.log('💾 Tokens saved to localStorage with multiple keys');
                }
                
                if (response.data.refresh_token) {
                    Utils.storage.set(CONFIG.AUTH.REFRESH_KEY, response.data.refresh_token);
                    localStorage.setItem('hashtag_pizzaria_refresh', response.data.refresh_token);
                    localStorage.setItem('refresh_token', response.data.refresh_token);
                }
                
                if (response.data.user) {
                    Utils.storage.set(CONFIG.AUTH.USER_KEY, response.data.user);
                    localStorage.setItem('hashtag_pizzaria_user', JSON.stringify(response.data.user));
                    localStorage.setItem('user_data', JSON.stringify(response.data.user));
                    console.log('👤 User data saved with multiple keys');
                }
            }
            
            EventBus.emit('auth:login', response.data);
            return response;
            
        } catch (error) {
            console.error('❌ API Service - Login failed:', error);
            throw error;
        }
    }
    
    async register(userData) {
        const response = await this.post(CONFIG.API.ENDPOINTS.REGISTER, userData, {
            auth: false
        });
        
        EventBus.emit('auth:register', response.data);
        return response;
    }
    
    async refreshToken() {
        // Use AuthManager if available
        if (window.AuthManager && window.AuthManager.isInitialized) {
            return await window.AuthManager.refreshTokens();
        }
        
        // Fallback to direct refresh
        const refreshToken = Utils.storage.get(CONFIG.AUTH.REFRESH_KEY) ||
                           localStorage.getItem('hashtag_pizzaria_refresh') ||
                           localStorage.getItem('refresh_token');
                           
        if (!refreshToken) {
            throw new ApiError(null, 'UNAUTHORIZED', 'No refresh token available');
        }
        
        const response = await this.post(CONFIG.API.ENDPOINTS.REFRESH, {
            refresh_token: refreshToken
        }, {
            auth: false
        });
        
        // Update tokens with multiple keys
        if (response.data.access_token) {
            Utils.storage.set(CONFIG.AUTH.TOKEN_KEY, response.data.access_token);
            localStorage.setItem('hashtag_pizzaria_token', response.data.access_token);
            localStorage.setItem('access_token', response.data.access_token);
        }
        
        if (response.data.refresh_token) {
            Utils.storage.set(CONFIG.AUTH.REFRESH_KEY, response.data.refresh_token);
            localStorage.setItem('hashtag_pizzaria_refresh', response.data.refresh_token);
            localStorage.setItem('refresh_token', response.data.refresh_token);
        }
        
        return response;
    }
    
    logout() {
        console.log('🚪 API Service logout called');
        
        // Use AuthManager if available
        if (window.AuthManager && window.AuthManager.isInitialized) {
            window.AuthManager.logout();
        } else {
            // Fallback logout - remove all possible keys
            const keysToRemove = [
                CONFIG.AUTH.TOKEN_KEY,
                CONFIG.AUTH.REFRESH_KEY, 
                CONFIG.AUTH.USER_KEY,
                'hashtag_pizzaria_token',
                'hashtag_pizzaria_refresh',
                'hashtag_pizzaria_user',
                'access_token',
                'refresh_token',
                'user_data',
                'currentUser',
                'authToken'
            ];
            
            keysToRemove.forEach(key => {
                Utils.storage.remove(key);
                localStorage.removeItem(key);
                sessionStorage.removeItem(key);
            });
            
            EventBus.emit('auth:logout');
        }
    }
    
    // Menu/Items methods
    async getPublicItems(params = {}) {
        console.log('🔍 Loading menu items from:', CONFIG.API.ENDPOINTS.ITEMS_PUBLIC);
        console.log('📦 Request params:', params);
        try {
            const result = await this.get(CONFIG.API.ENDPOINTS.ITEMS_PUBLIC, params, { auth: false });
            console.log('✅ Menu items loaded:', result);
            return result;
        } catch (error) {
            console.error('❌ Failed to load menu items:', error);
            throw error;
        }
    }
    
    async getItems(params = {}) {
        return this.get(CONFIG.API.ENDPOINTS.ITEMS, params);
    }
    
    async getCategories() {
        return this.get(CONFIG.API.ENDPOINTS.CATEGORIES, {}, { auth: false });
    }
    
    async searchItems(query, params = {}) {
        return this.get(CONFIG.API.ENDPOINTS.SEARCH, { q: query, ...params }, { auth: false });
    }
    
    // Orders methods
    async createOrder(orderData) {
        return this.post(CONFIG.API.ENDPOINTS.CREATE_ORDER, orderData);
    }
    
    async getMyOrders(params = {}) {
        return this.get(CONFIG.API.ENDPOINTS.MY_ORDERS, params);
    }
    
    // User methods
    async getCurrentUser() {
        return this.get(CONFIG.API.ENDPOINTS.ME);
    }
    
    async updateProfile(userData) {
        return this.patch(CONFIG.API.ENDPOINTS.ME, userData);
    }
}

// ===== API ERROR CLASS =====
class ApiError extends Error {
    constructor(response, type = 'UNKNOWN', message = null) {
        const errorMessage = message || ApiError.getBasicErrorMessage(response, type);
        super(errorMessage);
        
        this.name = 'ApiError';
        this.response = response;
        this.type = type;
        this.status = response?.status;
        this.statusText = response?.statusText;
        
        // Set detailed message asynchronously if response is available
        if (response && !message) {
            this.setDetailedMessage();
        }
    }
    
    async setDetailedMessage() {
        try {
            const detailedMessage = await ApiError.getDetailedErrorMessage(this.response);
            if (detailedMessage && detailedMessage !== this.message) {
                this.message = detailedMessage;
            }
        } catch (e) {
            // Keep original message if detailed extraction fails
        }
    }
    
    static getBasicErrorMessage(response, type) {
        if (response) {
            switch (response.status) {
                case 400:
                    return CONFIG.ERRORS.VALIDATION;
                case 401:
                    return CONFIG.ERRORS.UNAUTHORIZED;
                case 403:
                    return CONFIG.ERRORS.FORBIDDEN;
                case 404:
                    return CONFIG.ERRORS.NOT_FOUND;
                case 422:
                    return 'Dados inválidos fornecidos';
                case 500:
                case 502:
                case 503:
                case 504:
                    return CONFIG.ERRORS.SERVER_ERROR;
                default:
                    return CONFIG.ERRORS.UNKNOWN;
            }
        }
        return CONFIG.ERRORS[type] || CONFIG.ERRORS.UNKNOWN;
    }
    
    static async getDetailedErrorMessage(response) {
        if (response) {
            // Try to get detailed error from response body
            let errorDetail = null;
            try {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const errorData = await response.clone().json();
                    errorDetail = errorData.detail || errorData.message || errorData.error;
                }
            } catch (e) {
                // Ignore parsing errors
            }
            
            switch (response.status) {
                case 400:
                    return errorDetail || CONFIG.ERRORS.VALIDATION;
                case 401:
                    return errorDetail || CONFIG.ERRORS.UNAUTHORIZED;
                case 403:
                    return errorDetail || CONFIG.ERRORS.FORBIDDEN;
                case 404:
                    return errorDetail || CONFIG.ERRORS.NOT_FOUND;
                case 422:
                    return errorDetail || 'Dados inválidos fornecidos';
                case 500:
                case 502:
                case 503:
                case 504:
                    return errorDetail || CONFIG.ERRORS.SERVER_ERROR;
                default:
                    return CONFIG.ERRORS.UNKNOWN;
            }
        }
        
        return CONFIG.ERRORS[type] || CONFIG.ERRORS.UNKNOWN;
    }
}

// ===== API INSTANCE =====
const api = new ApiService();

// ===== REQUEST INTERCEPTORS =====
// Add request ID for tracking
api.addRequestInterceptor(async (config) => {
    config.requestId = Utils.generateId();
    config.timestamp = Date.now();
    return config;
});

// ===== RESPONSE INTERCEPTORS =====
// Handle authentication errors
api.addResponseInterceptor(async (response, config) => {
    if (response.status === 401 && config.endpoint !== CONFIG.API.ENDPOINTS.LOGIN) {
        // Try to refresh token
        try {
            await api.refreshToken();
            // Retry original request
            return api.request(config);
        } catch (refreshError) {
            // Refresh failed, logout user
            api.logout();
            EventBus.emit('auth:expired');
            throw new ApiError(response, 'UNAUTHORIZED');
        }
    }
    
    return response;
});

// ===== MOCK API FOR DEVELOPMENT =====
const MockAPI = {
    enabled: CONFIG.DEV.MOCK_API,
    
    // Mock data
    mockItems: [
        {
            id: 1,
            name: "Pizza Margherita",
            description: "Molho de tomate, mussarela, manjericão fresco e azeite",
            price: 35.90,
            category: "pizza",
            is_available: true,
            image_url: null
        },
        {
            id: 2,
            name: "Pizza Pepperoni",
            description: "Molho de tomate, mussarela e pepperoni",
            price: 39.90,
            category: "pizza",
            is_available: true,
            image_url: null
        },
        {
            id: 3,
            name: "Coca-Cola 2L",
            description: "Refrigerante Coca-Cola 2 litros",
            price: 8.50,
            category: "bebida",
            is_available: true,
            image_url: null
        },
        {
            id: 4,
            name: "Pudim de Leite",
            description: "Pudim tradicional de leite condensado",
            price: 12.90,
            category: "sobremesa",
            is_available: true,
            image_url: null
        }
    ],
    
    mockCategories: [
        { name: "pizza", count: 8 },
        { name: "bebida", count: 5 },
        { name: "sobremesa", count: 3 }
    ],
    
    // Mock responses
    getPublicItems: (params) => {
        let items = [...MockAPI.mockItems];
        
        if (params.category && params.category !== 'all') {
            items = items.filter(item => item.category === params.category);
        }
        
        if (params.available_only !== false) {
            items = items.filter(item => item.is_available);
        }
        
        return Promise.resolve({
            data: {
                items: items,
                total: items.length,
                page: 1,
                pages: 1
            }
        });
    },
    
    getCategories: () => {
        return Promise.resolve({
            data: {
                categories: MockAPI.mockCategories
            }
        });
    },
    
    searchItems: (query) => {
        const items = MockAPI.mockItems.filter(item =>
            item.name.toLowerCase().includes(query.toLowerCase()) ||
            item.description.toLowerCase().includes(query.toLowerCase())
        );
        
        return Promise.resolve({
            data: {
                items: items,
                total: items.length,
                query: query
            }
        });
    },
    
    // Mock orders data
    mockOrders: [
        {
            id: 1,
            order_number: "PED-12345678",
            customer_name: "Admin User",
            status: "entregue",
            total_amount: 47.80,
            created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 dias atrás
            items_count: 2
        },
        {
            id: 2,
            order_number: "PED-87654321",
            customer_name: "Admin User",
            status: "preparando",
            total_amount: 35.90,
            created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(), // 1 dia atrás
            items_count: 1
        },
        {
            id: 3,
            order_number: "PED-11223344",
            customer_name: "Admin User",
            status: "pendente",
            total_amount: 65.70,
            created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 horas atrás
            items_count: 3
        }
    ],
    
    getMyOrders: (params) => {
        return Promise.resolve({
            data: MockAPI.mockOrders
        });
    },
    
    login: (credentials) => {
        return Promise.resolve({
            data: {
                access_token: 'mock_token_123',
                refresh_token: 'mock_refresh_123',
                user: {
                    id: 1,
                    username: 'admin',
                    email: 'admin@pizzaria.com',
                    full_name: 'Administrador',
                    is_admin: true
                }
            }
        });
    },
    
    createOrder: (orderData) => {
        const newOrder = {
            id: Date.now(),
            order_number: `PED-${Math.random().toString(36).substr(2, 8).toUpperCase()}`,
            customer_name: orderData.customer_name,
            status: 'pendente',
            total_amount: 45.90, // mock total
            created_at: new Date().toISOString(),
            items_count: orderData.items.length
        };
        
        MockAPI.mockOrders.unshift(newOrder);
        
        return Promise.resolve({
            data: newOrder
        });
    }
};

// Override API methods if mock is enabled
if (MockAPI.enabled) {
    Utils.warn('Mock API enabled - using fake data');
    
    api.getPublicItems = MockAPI.getPublicItems;
    api.getCategories = MockAPI.getCategories;
    api.searchItems = (query, params) => MockAPI.searchItems(query);
    api.getMyOrders = MockAPI.getMyOrders;
    // api.login = MockAPI.login; // Desabilitado - usar API real
    // api.createOrder = MockAPI.createOrder; // Desabilitado - usar API real
}

// ===== EXPORT =====
window.api = api;
window.ApiError = ApiError;

Utils.log('API Service ready');