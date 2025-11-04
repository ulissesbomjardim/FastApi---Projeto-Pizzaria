/**
 * 🔐 AuthManager - Sistema Centralizado de Autenticação
 * 
 * Este serviço gerencia autenticação de forma centralizada para todas as páginas
 * do sistema Hashtag Pizzaria. Garante consistência de tokens e dados entre páginas.
 * 
 * Funcionalidades:
 * - Múltiplas chaves de storage para compatibilidade
 * - Comunicação entre páginas/tabs
 * - Auto-refresh de tokens
 * - Persistência robusta
 * - Event system para sincronização
 */

class AuthManager {
    constructor() {
        this.version = '1.0.0';
        this.storagePrefix = 'hashtag_pizzaria_';
        this.isInitialized = false;
        
        // Configurações de storage
        this.storageKeys = {
            token: ['hashtag_pizzaria_token', 'access_token', 'authToken', 'token'],
            refresh: ['hashtag_pizzaria_refresh', 'refresh_token'],
            user: ['hashtag_pizzaria_user', 'user_data', 'currentUser'],
            lastActivity: 'hashtag_pizzaria_last_activity'
        };
        
        // Estado atual
        this.currentUser = null;
        this.currentToken = null;
        this.refreshToken = null;
        this.isAuthenticated = false;
        
        // Listeners para eventos
        this.listeners = new Map();
        
        this.init();
    }
    
    init() {
        console.log('🔐 AuthManager v' + this.version + ' initializing...');
        
        // Carregar estado atual do storage
        this.loadFromStorage();
        
        // Configurar listeners de storage para sincronização entre tabs
        this.setupStorageListeners();
        
        // Configurar comunicação entre páginas
        this.setupCrossPageCommunication();
        
        // Configurar auto-refresh de tokens
        this.setupTokenRefresh();
        
        // Verificar se token está válido
        this.validateCurrentToken();
        
        this.isInitialized = true;
        console.log('✅ AuthManager initialized successfully');
        
        // Emitir evento de inicialização
        this.emit('auth:initialized', {
            isAuthenticated: this.isAuthenticated,
            user: this.currentUser
        });
    }
    
    /**
     * Carrega dados de autenticação do storage
     */
    loadFromStorage() {
        console.log('📦 Loading auth data from storage...');
        
        // Carregar token
        this.currentToken = this.getFromMultipleKeys(this.storageKeys.token);
        
        // Carregar refresh token
        this.refreshToken = this.getFromMultipleKeys(this.storageKeys.refresh);
        
        // Carregar dados do usuário
        const userData = this.getFromMultipleKeys(this.storageKeys.user);
        if (userData) {
            try {
                this.currentUser = typeof userData === 'string' ? JSON.parse(userData) : userData;
            } catch (e) {
                console.warn('⚠️ Invalid user data in storage');
                this.currentUser = null;
            }
        }
        
        // Determinar estado de autenticação
        this.isAuthenticated = !!(this.currentToken && this.currentUser);
        
        console.log('📦 Storage load complete:', {
            hasToken: !!this.currentToken,
            hasUser: !!this.currentUser,
            isAuthenticated: this.isAuthenticated
        });
    }
    
    /**
     * Busca valor em múltiplas chaves de storage
     */
    getFromMultipleKeys(keys) {
        for (const key of keys) {
            const value = localStorage.getItem(key) || sessionStorage.getItem(key);
            if (value && value !== 'undefined' && value !== 'null') {
                return value;
            }
        }
        return null;
    }
    
    /**
     * Salva dados em todas as chaves relevantes
     */
    saveToMultipleKeys(keys, value) {
        keys.forEach(key => {
            localStorage.setItem(key, value);
        });
    }
    
    /**
     * Remove dados de todas as chaves relevantes
     */
    removeFromMultipleKeys(keys) {
        keys.forEach(key => {
            localStorage.removeItem(key);
            sessionStorage.removeItem(key);
        });
    }
    
    /**
     * Configura listeners para sincronização entre tabs
     */
    setupStorageListeners() {
        window.addEventListener('storage', (event) => {
            // Ignorar eventos não relacionados à autenticação
            const authKeys = [...this.storageKeys.token, ...this.storageKeys.user, ...this.storageKeys.refresh];
            if (!authKeys.includes(event.key)) return;
            
            console.log('🔄 Storage changed in another tab:', event.key);
            
            // Recarregar dados
            this.loadFromStorage();
            
            // Emitir evento de mudança
            this.emit('auth:storage_changed', {
                key: event.key,
                newValue: event.newValue,
                oldValue: event.oldValue
            });
        });
    }
    
    /**
     * Configura comunicação entre páginas/windows
     */
    setupCrossPageCommunication() {
        // Listener para receber solicitações de dados de auth
        window.addEventListener('message', (event) => {
            if (event.data.type === 'AUTH_REQUEST') {
                console.log('📤 Auth data requested by:', event.origin);
                this.sendAuthDataToWindow(event.source);
            } else if (event.data.type === 'AUTH_DATA') {
                console.log('📥 Received auth data from:', event.origin);
                this.receiveAuthData(event.data.payload);
            }
        });
        
        // Solicitar dados de auth da página pai (se houver)
        if (window.opener || window.parent !== window) {
            setTimeout(() => {
                this.requestAuthFromParent();
            }, 1000);
        }
    }
    
    /**
     * Envia dados de auth para uma janela específica
     */
    sendAuthDataToWindow(targetWindow) {
        if (this.isAuthenticated) {
            try {
                targetWindow.postMessage({
                    type: 'AUTH_DATA',
                    payload: {
                        token: this.currentToken,
                        refreshToken: this.refreshToken,
                        user: this.currentUser,
                        timestamp: Date.now()
                    }
                }, '*');
                console.log('📤 Auth data sent successfully');
            } catch (e) {
                console.warn('⚠️ Could not send auth data:', e);
            }
        }
    }
    
    /**
     * Solicita dados de auth da página pai
     */
    requestAuthFromParent() {
        if (!this.isAuthenticated) {
            console.log('📥 Requesting auth data from parent...');
            
            try {
                if (window.opener) {
                    window.opener.postMessage({ type: 'AUTH_REQUEST' }, '*');
                }
                if (window.parent !== window) {
                    window.parent.postMessage({ type: 'AUTH_REQUEST' }, '*');
                }
            } catch (e) {
                console.log('⚠️ Could not request auth from parent:', e);
            }
        }
    }
    
    /**
     * Recebe e processa dados de auth de outra página
     */
    receiveAuthData(authData) {
        if (authData.token && authData.user && !this.isAuthenticated) {
            console.log('✅ Received valid auth data, updating local state...');
            
            this.setAuthData(authData.token, authData.refreshToken, authData.user);
            
            this.emit('auth:received_from_parent', authData);
        }
    }
    
    /**
     * Configura auto-refresh de tokens
     */
    setupTokenRefresh() {
        // Verificar token a cada 5 minutos
        setInterval(() => {
            if (this.isAuthenticated && this.currentToken) {
                this.validateTokenExpiration();
            }
        }, 5 * 60 * 1000);
        
        // Verificar imediatamente se token está próximo do vencimento
        if (this.isAuthenticated) {
            setTimeout(() => {
                this.validateTokenExpiration();
            }, 2000);
        }
    }
    
    /**
     * Valida se o token atual ainda é válido
     */
    async validateCurrentToken() {
        if (!this.currentToken) return false;
        
        try {
            const baseURL = window.CONFIG?.API?.BASE_URL || 'http://172.25.132.243:8000';
            const response = await fetch(`${baseURL}/users/me`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.currentToken}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const userData = await response.json();
                
                // Atualizar dados do usuário se necessário
                if (!this.currentUser || JSON.stringify(this.currentUser) !== JSON.stringify(userData)) {
                    this.currentUser = userData;
                    this.saveUserData(userData);
                }
                
                console.log('✅ Token validated successfully');
                return true;
            } else if (response.status === 401) {
                console.log('🔄 Token expired, attempting refresh...');
                return await this.refreshTokens();
            } else {
                console.warn('⚠️ Token validation failed:', response.status);
                return false;
            }
        } catch (error) {
            console.error('❌ Error validating token:', error);
            return false;
        }
    }
    
    /**
     * Verifica se o token está próximo do vencimento e renova se necessário
     */
    async validateTokenExpiration() {
        // Se não tiver refresh token, não pode renovar
        if (!this.refreshToken) return;
        
        // Tentar renovar token se estiver próximo do vencimento (implementação simples)
        try {
            const isValid = await this.validateCurrentToken();
            if (!isValid) {
                console.log('🔄 Token invalid, attempting refresh...');
                await this.refreshTokens();
            }
        } catch (error) {
            console.error('❌ Error in token expiration check:', error);
        }
    }
    
    /**
     * Renova tokens usando refresh token
     */
    async refreshTokens() {
        if (!this.refreshToken) {
            console.error('❌ No refresh token available');
            this.logout();
            return false;
        }
        
        try {
            const baseURL = window.CONFIG?.API?.BASE_URL || 'http://172.25.132.243:8000';
            const response = await fetch(`${baseURL}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    refresh_token: this.refreshToken
                })
            });
            
            if (!response.ok) {
                throw new Error(`Token refresh failed: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('✅ Token refreshed successfully');
            
            // Atualizar tokens
            this.setAuthData(data.access_token, data.refresh_token || this.refreshToken, this.currentUser);
            
            this.emit('auth:token_refreshed', data);
            return true;
            
        } catch (error) {
            console.error('❌ Token refresh failed:', error);
            this.logout();
            return false;
        }
    }
    
    /**
     * Realiza login
     */
    async login(credentials) {
        console.log('🔐 Attempting login...');
        
        try {
            const baseURL = window.CONFIG?.API?.BASE_URL || 'http://172.25.132.243:8000';
            const response = await fetch(`${baseURL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email_or_username: credentials.username || credentials.email,
                    password: credentials.password
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Login failed: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('✅ Login successful');
            
            // Salvar dados de autenticação
            this.setAuthData(data.access_token, data.refresh_token, data.user);
            
            // Emitir evento de login
            this.emit('auth:login', data);
            
            return data;
            
        } catch (error) {
            console.error('❌ Login failed:', error);
            this.emit('auth:login_failed', error);
            throw error;
        }
    }
    
    /**
     * Define dados de autenticação e salva no storage
     */
    setAuthData(token, refreshToken, user) {
        this.currentToken = token;
        this.refreshToken = refreshToken;
        this.currentUser = user;
        this.isAuthenticated = !!(token && user);
        
        // Salvar no storage com todas as chaves
        if (token) {
            this.saveToMultipleKeys(this.storageKeys.token, token);
        }
        
        if (refreshToken) {
            this.saveToMultipleKeys(this.storageKeys.refresh, refreshToken);
        }
        
        if (user) {
            this.saveUserData(user);
        }
        
        // Marcar última atividade
        localStorage.setItem(this.storageKeys.lastActivity, Date.now().toString());
        
        console.log('💾 Auth data saved successfully');
    }
    
    /**
     * Salva dados do usuário no storage
     */
    saveUserData(user) {
        const userString = JSON.stringify(user);
        this.saveToMultipleKeys(this.storageKeys.user, userString);
    }
    
    /**
     * Realiza logout
     */
    logout() {
        console.log('🚪 Logging out...');
        
        // Limpar estado
        this.currentToken = null;
        this.refreshToken = null;
        this.currentUser = null;
        this.isAuthenticated = false;
        
        // Limpar storage
        this.removeFromMultipleKeys(this.storageKeys.token);
        this.removeFromMultipleKeys(this.storageKeys.refresh);
        this.removeFromMultipleKeys(this.storageKeys.user);
        localStorage.removeItem(this.storageKeys.lastActivity);
        
        // Emitir evento de logout
        this.emit('auth:logout');
        
        console.log('✅ Logout completed');
    }
    
    /**
     * Verifica se usuário é admin
     */
    isAdmin() {
        return this.isAuthenticated && this.currentUser && this.currentUser.is_admin === true;
    }
    
    /**
     * Obtém token atual
     */
    getToken() {
        return this.currentToken;
    }
    
    /**
     * Obtém dados do usuário atual
     */
    getUser() {
        return this.currentUser;
    }
    
    /**
     * Verifica se está autenticado
     */
    isLoggedIn() {
        return this.isAuthenticated;
    }
    
    /**
     * Sistema de eventos
     */
    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }
    
    off(event, callback) {
        if (this.listeners.has(event)) {
            const callbacks = this.listeners.get(event);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        }
    }
    
    emit(event, data) {
        if (this.listeners.has(event)) {
            this.listeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error('Error in event callback:', error);
                }
            });
        }
        
        // Também emitir como evento DOM para compatibilidade
        window.dispatchEvent(new CustomEvent(`authManager:${event}`, { detail: data }));
    }
    
    /**
     * Aguarda inicialização se ainda não foi inicializado
     */
    async waitForInit() {
        if (this.isInitialized) return;
        
        return new Promise((resolve) => {
            this.on('auth:initialized', () => resolve());
        });
    }
}

// Criar instância global
window.AuthManager = window.AuthManager || new AuthManager();

// Compatibilidade - exportar para uso em módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthManager;
}

console.log('🔐 AuthManager script loaded');