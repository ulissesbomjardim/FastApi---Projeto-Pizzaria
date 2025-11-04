# 🔐 AuthManager - Documentação Técnica

## Visão Geral

O **AuthManager** é o núcleo do sistema de autenticação centralizado da Hashtag Pizzaria. É uma classe JavaScript que gerencia tokens, usuários e comunicação entre páginas de forma unificada.

## 🏗️ Arquitetura da Classe

```javascript
class AuthManager {
    constructor() {
        this.version = '1.0.0';
        this.storagePrefix = 'hashtag_pizzaria_';
        this.isInitialized = false;
        
        // Estado atual
        this.currentUser = null;
        this.currentToken = null;
        this.refreshToken = null;
        this.isAuthenticated = false;
        
        // Sistema de eventos
        this.listeners = new Map();
    }
}
```

## 📦 Propriedades Principais

### Configurações de Storage
```javascript
this.storageKeys = {
    token: [
        'hashtag_pizzaria_token', 
        'access_token', 
        'authToken', 
        'token'
    ],
    refresh: [
        'hashtag_pizzaria_refresh', 
        'refresh_token'
    ],
    user: [
        'hashtag_pizzaria_user', 
        'user_data', 
        'currentUser'
    ],
    lastActivity: 'hashtag_pizzaria_last_activity'
};
```

### Estado da Autenticação
```javascript
// Estado atual do usuário
this.currentUser = {
    id: 1,
    username: "admin",
    email: "admin@pizzaria.com",
    is_admin: true,
    is_active: true
};

// Tokens JWT
this.currentToken = "eyJhbGciOiJIUzI1NiIs...";
this.refreshToken = "eyJhbGciOiJIUzI1NiIs...";

// Status de autenticação
this.isAuthenticated = true;
```

## 🔧 Métodos Principais

### Inicialização
```javascript
init() {
    console.log('🔐 AuthManager v' + this.version + ' initializing...');
    
    // 1. Carregar estado do storage
    this.loadFromStorage();
    
    // 2. Configurar listeners
    this.setupStorageListeners();
    this.setupCrossPageCommunication();
    
    // 3. Configurar auto-refresh
    this.setupTokenRefresh();
    
    // 4. Validar token atual
    this.validateCurrentToken();
    
    this.isInitialized = true;
    this.emit('auth:initialized', {
        isAuthenticated: this.isAuthenticated,
        user: this.currentUser
    });
}
```

### Gerenciamento de Storage
```javascript
// Salvar dados em múltiplas chaves
saveToMultipleKeys(keys, value) {
    keys.forEach(key => {
        localStorage.setItem(key, value);
    });
}

// Buscar valor em múltiplas chaves  
getFromMultipleKeys(keys) {
    for (const key of keys) {
        const value = localStorage.getItem(key) || sessionStorage.getItem(key);
        if (value && value !== 'undefined' && value !== 'null') {
            return value;
        }
    }
    return null;
}

// Remover dados de todas as chaves
removeFromMultipleKeys(keys) {
    keys.forEach(key => {
        localStorage.removeItem(key);
        sessionStorage.removeItem(key);
    });
}
```

### Autenticação
```javascript
async login(credentials) {
    console.log('🔐 Attempting login...');
    
    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email_or_username: credentials.username,
                password: credentials.password
            })
        });
        
        const data = await response.json();
        
        // Salvar dados de autenticação
        this.setAuthData(data.access_token, data.refresh_token, data.user);
        
        // Emitir evento de login
        this.emit('auth:login', data);
        
        return data;
    } catch (error) {
        this.emit('auth:login_failed', error);
        throw error;
    }
}
```

### Refresh de Tokens
```javascript
async refreshTokens() {
    if (!this.refreshToken) {
        console.error('❌ No refresh token available');
        this.logout();
        return false;
    }
    
    try {
        const response = await fetch('/auth/refresh', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                refresh_token: this.refreshToken
            })
        });
        
        const data = await response.json();
        
        // Atualizar tokens
        this.setAuthData(
            data.access_token, 
            data.refresh_token || this.refreshToken, 
            this.currentUser
        );
        
        this.emit('auth:token_refreshed', data);
        return true;
    } catch (error) {
        console.error('❌ Token refresh failed:', error);
        this.logout();
        return false;
    }
}
```

## 🌐 Comunicação Cross-Page

### Configuração de Listeners
```javascript
setupCrossPageCommunication() {
    // Listener para receber solicitações
    window.addEventListener('message', (event) => {
        if (event.data.type === 'AUTH_REQUEST') {
            console.log('📤 Auth data requested by:', event.origin);
            this.sendAuthDataToWindow(event.source);
        } else if (event.data.type === 'AUTH_DATA') {
            console.log('📥 Received auth data from:', event.origin);
            this.receiveAuthData(event.data.payload);
        }
    });
    
    // Solicitar dados da página pai se necessário
    if (window.opener || window.parent !== window) {
        setTimeout(() => {
            this.requestAuthFromParent();
        }, 1000);
    }
}
```

### Envio de Dados
```javascript
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
```

### Recebimento de Dados
```javascript
receiveAuthData(authData) {
    if (authData.token && authData.user && !this.isAuthenticated) {
        console.log('✅ Received valid auth data, updating local state...');
        
        this.setAuthData(
            authData.token, 
            authData.refreshToken, 
            authData.user
        );
        
        this.emit('auth:received_from_parent', authData);
    }
}
```

## 🔄 Auto-Refresh Inteligente

### Configuração do Timer
```javascript
setupTokenRefresh() {
    // Verificar token a cada 5 minutos
    setInterval(() => {
        if (this.isAuthenticated && this.currentToken) {
            this.validateTokenExpiration();
        }
    }, 5 * 60 * 1000);
    
    // Verificar imediatamente se necessário
    if (this.isAuthenticated) {
        setTimeout(() => {
            this.validateTokenExpiration();
        }, 2000);
    }
}
```

### Validação de Token
```javascript
async validateCurrentToken() {
    if (!this.currentToken) return false;
    
    try {
        const response = await fetch('/users/me', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${this.currentToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const userData = await response.json();
            
            // Atualizar dados do usuário se necessário
            if (!this.currentUser || 
                JSON.stringify(this.currentUser) !== JSON.stringify(userData)) {
                this.currentUser = userData;
                this.saveUserData(userData);
            }
            
            console.log('✅ Token validated successfully');
            return true;
        } else if (response.status === 401) {
            console.log('🔄 Token expired, attempting refresh...');
            return await this.refreshTokens();
        }
    } catch (error) {
        console.error('❌ Error validating token:', error);
        return false;
    }
}
```

## 🎭 Sistema de Eventos

### Configuração de Eventos
```javascript
// Adicionar listener
on(event, callback) {
    if (!this.listeners.has(event)) {
        this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
}

// Remover listener
off(event, callback) {
    if (this.listeners.has(event)) {
        const callbacks = this.listeners.get(event);
        const index = callbacks.indexOf(callback);
        if (index > -1) {
            callbacks.splice(index, 1);
        }
    }
}

// Emitir evento
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
    
    // Também emitir como evento DOM
    window.dispatchEvent(
        new CustomEvent(`authManager:${event}`, { detail: data })
    );
}
```

### Eventos Disponíveis
```javascript
// Eventos de autenticação
this.emit('auth:initialized', data);
this.emit('auth:login', data);
this.emit('auth:logout');
this.emit('auth:token_refreshed', data);
this.emit('auth:login_failed', error);
this.emit('auth:received_from_parent', data);

// Eventos de storage
this.emit('auth:storage_changed', {
    key: event.key,
    newValue: event.newValue,
    oldValue: event.oldValue
});
```

## 🔍 Métodos Utilitários

### Verificações de Estado
```javascript
// Verificar se está logado
isLoggedIn() {
    return this.isAuthenticated;
}

// Verificar se é admin
isAdmin() {
    return this.isAuthenticated && 
           this.currentUser && 
           this.currentUser.is_admin === true;
}

// Obter token atual
getToken() {
    return this.currentToken;
}

// Obter dados do usuário
getUser() {
    return this.currentUser;
}
```

### Aguardar Inicialização
```javascript
async waitForInit() {
    if (this.isInitialized) return;
    
    return new Promise((resolve) => {
        this.on('auth:initialized', () => resolve());
    });
}
```

## 📊 Uso em Outras Classes

### Integração com API Service
```javascript
// No api.js
getAuthToken() {
    if (window.AuthManager && window.AuthManager.isInitialized) {
        return window.AuthManager.getToken();
    }
    return Utils.storage.get(CONFIG.AUTH.TOKEN_KEY);
}
```

### Integração com Auth Service
```javascript
// No auth.js
init() {
    if (window.AuthManager) {
        window.AuthManager.waitForInit().then(() => {
            this.syncWithAuthManager();
        });
    }
}

syncWithAuthManager() {
    if (window.AuthManager && window.AuthManager.isLoggedIn()) {
        this.user = window.AuthManager.getUser();
        this.isAuthenticated = true;
    }
}
```

## 🐛 Debug e Logs

### Sistema de Logs
```javascript
// Logs detalhados em desenvolvimento
if (CONFIG?.DEV?.ENABLE_LOGS) {
    console.log('🔐 AuthManager initialized');
    console.log('📦 Storage data loaded');
    console.log('✅ Token validated');
    console.log('🔄 Token refreshed');
}
```

### Monitoramento de Estado
```javascript
// Estado atual sempre disponível
window.AuthManager.getState = function() {
    return {
        version: this.version,
        isInitialized: this.isInitialized,
        isAuthenticated: this.isAuthenticated,
        user: this.currentUser,
        hasToken: !!this.currentToken,
        hasRefreshToken: !!this.refreshToken
    };
};
```

## 🔧 Configuração Avançada

### Customização de Timeouts
```javascript
// Configurar intervalos personalizados
const authManager = new AuthManager();
authManager.config = {
    refreshInterval: 5 * 60 * 1000,  // 5 minutos
    validationDelay: 2000,           // 2 segundos
    retryAttempts: 3                 // 3 tentativas
};
```

### Override de Endpoints
```javascript
// Personalizar URLs da API
authManager.endpoints = {
    login: '/auth/login',
    refresh: '/auth/refresh',
    validate: '/users/me'
};
```

---

**O AuthManager é o coração do sistema de autenticação, fornecendo uma base sólida e extensível para gerenciar autenticação de forma centralizada e robusta.**