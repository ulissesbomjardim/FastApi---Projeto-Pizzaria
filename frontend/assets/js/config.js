// ===== CONFIGURATION ===== 
const CONFIG = {
    // API Configuration
    API: {
        BASE_URL: window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'http://localhost:8000',
        ENDPOINTS: {
            // Authentication
            LOGIN: '/auth/login',
            REGISTER: '/auth/register',
            REFRESH: '/auth/refresh',
            
            // Items/Menu
            ITEMS: '/items/list-items',
            ITEMS_PUBLIC: '/items/menu',
            CATEGORIES: '/items/categories',
            SEARCH: '/items/search',
            
            // Orders
            ORDERS: '/orders',
            CREATE_ORDER: '/orders/create-order',
            MY_ORDERS: '/orders/my-orders',
            
            // Users
            USERS: '/users',
            ME: '/users/me'
        },
        TIMEOUT: 10000, // 10 seconds
        RETRY_ATTEMPTS: 3
    },
    
    // UI Configuration
    UI: {
        LOADING_DELAY: 1500, // Loading screen duration
        NOTIFICATION_DURATION: 5000, // 5 seconds
        SCROLL_OFFSET: 80, // Navbar height offset for smooth scroll
        DEBOUNCE_DELAY: 300, // Search debounce
        ANIMATION_DURATION: 300
    },
    
    // Cart Configuration
    CART: {
        MAX_QUANTITY: 99,
        MIN_QUANTITY: 1,
        STORAGE_KEY: 'hashtag_pizzaria_cart',
        EXPIRY_HOURS: 24
    },
    
    // Auth Configuration
    AUTH: {
        TOKEN_KEY: 'hashtag_pizzaria_token',
        REFRESH_KEY: 'hashtag_pizzaria_refresh',
        USER_KEY: 'hashtag_pizzaria_user',
        TOKEN_EXPIRY_BUFFER: 300 // 5 minutes buffer before token expires
    },
    
    // Menu Configuration
    MENU: {
        ITEMS_PER_PAGE: 12,
        DEFAULT_CATEGORY: 'all',
        IMAGE_PLACEHOLDER: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" fill="%23333"/><text x="100" y="100" text-anchor="middle" dy="0.3em" fill="%23666" font-size="14">Sem Imagem</text></svg>'
    },
    
    // Validation Rules
    VALIDATION: {
        PASSWORD_MIN_LENGTH: 8,
        USERNAME_MIN_LENGTH: 3,
        PHONE_PATTERN: /^\(\d{2}\)\s\d{4,5}-\d{4}$/,
        EMAIL_PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    },
    
    // Error Messages
    ERRORS: {
        NETWORK: 'Erro de conexão com o servidor. Verifique sua internet e tente novamente.',
        TIMEOUT: 'A requisição demorou muito para responder. Tente novamente.',
        UNAUTHORIZED: 'Email ou senha incorretos. Verifique suas credenciais.',
        FORBIDDEN: 'Você não tem permissão para realizar esta ação.',
        NOT_FOUND: 'Recurso não encontrado.',
        SERVER_ERROR: 'Erro interno do servidor. Tente novamente em alguns instantes.',
        VALIDATION: 'Por favor, verifique os dados fornecidos.',
        UNKNOWN: 'Ocorreu um erro inesperado. Tente novamente.'
    },
    
    // Success Messages
    SUCCESS: {
        LOGIN: 'Login realizado com sucesso!',
        REGISTER: 'Cadastro realizado com sucesso!',
        LOGOUT: 'Logout realizado com sucesso!',
        CART_ADD: 'Item adicionado ao carrinho!',
        CART_REMOVE: 'Item removido do carrinho!',
        CART_UPDATE: 'Carrinho atualizado!',
        ORDER_CREATED: 'Pedido criado com sucesso!',
        CONTACT_SENT: 'Mensagem enviada com sucesso!'
    },
    
    // Development flags
    DEV: {
        ENABLE_LOGS: true,
        MOCK_API: false,
        SHOW_DEBUG_INFO: true
    }
};

// ===== UTILITY FUNCTIONS =====
const Utils = {
    // Logging with environment check
    log: (...args) => {
        if (CONFIG.DEV.ENABLE_LOGS) {
            console.log('[Hashtag Pizzaria]', ...args);
        }
    },
    
    error: (...args) => {
        console.error('[Hashtag Pizzaria Error]', ...args);
    },
    
    warn: (...args) => {
        if (CONFIG.DEV.ENABLE_LOGS) {
            console.warn('[Hashtag Pizzaria Warning]', ...args);
        }
    },
    
    // Format currency
    formatCurrency: (value) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    },
    
    // Format phone number
    formatPhone: (phone) => {
        const cleaned = phone.replace(/\D/g, '');
        if (cleaned.length === 11) {
            return `(${cleaned.slice(0, 2)}) ${cleaned.slice(2, 7)}-${cleaned.slice(7)}`;
        }
        if (cleaned.length === 10) {
            return `(${cleaned.slice(0, 2)}) ${cleaned.slice(2, 6)}-${cleaned.slice(6)}`;
        }
        return phone;
    },
    
    // Validate email
    isValidEmail: (email) => {
        return CONFIG.VALIDATION.EMAIL_PATTERN.test(email);
    },
    
    // Validate phone
    isValidPhone: (phone) => {
        return CONFIG.VALIDATION.PHONE_PATTERN.test(phone);
    },
    
    // Validate password
    isValidPassword: (password) => {
        return password && password.length >= CONFIG.VALIDATION.PASSWORD_MIN_LENGTH;
    },
    
    // Debounce function
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Throttle function
    throttle: (func, limit) => {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    // Generate unique ID
    generateId: () => {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    },
    
    // Local storage with expiry
    storage: {
        set: (key, value, hours = 24) => {
            const item = {
                value: value,
                expiry: Date.now() + (hours * 60 * 60 * 1000)
            };
            localStorage.setItem(key, JSON.stringify(item));
        },
        
        get: (key) => {
            const item = localStorage.getItem(key);
            if (!item) return null;
            
            try {
                const parsed = JSON.parse(item);
                if (Date.now() > parsed.expiry) {
                    localStorage.removeItem(key);
                    return null;
                }
                return parsed.value;
            } catch (e) {
                localStorage.removeItem(key);
                return null;
            }
        },
        
        remove: (key) => {
            localStorage.removeItem(key);
        },
        
        clear: () => {
            localStorage.clear();
        }
    },
    
    // Smooth scroll to element
    scrollTo: (element, offset = CONFIG.UI.SCROLL_OFFSET) => {
        const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
        const offsetPosition = elementPosition - offset;
        
        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    },
    
    // Check if element is in viewport
    isInViewport: (element) => {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    },
    
    // Escape HTML
    escapeHtml: (text) => {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
    
    // Create element with attributes
    createElement: (tag, attributes = {}, children = []) => {
        const element = document.createElement(tag);
        
        Object.entries(attributes).forEach(([key, value]) => {
            if (key === 'className') {
                element.className = value;
            } else if (key === 'innerHTML') {
                element.innerHTML = value;
            } else {
                element.setAttribute(key, value);
            }
        });
        
        children.forEach(child => {
            if (typeof child === 'string') {
                element.appendChild(document.createTextNode(child));
            } else if (child instanceof Node) {
                element.appendChild(child);
            }
        });
        
        return element;
    },
    
    // Copy to clipboard
    copyToClipboard: async (text) => {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                const successful = document.execCommand('copy');
                document.body.removeChild(textArea);
                return successful;
            } catch (err) {
                document.body.removeChild(textArea);
                return false;
            }
        }
    },
    
    // Format date
    formatDate: (date, options = {}) => {
        const defaultOptions = {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            timeZone: 'America/Sao_Paulo'
        };
        
        return new Intl.DateTimeFormat('pt-BR', { ...defaultOptions, ...options }).format(new Date(date));
    },
    
    // Get relative time
    getRelativeTime: (date) => {
        const now = new Date();
        const past = new Date(date);
        const diff = now - past;
        
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (days > 0) return `há ${days} dia${days > 1 ? 's' : ''}`;
        if (hours > 0) return `há ${hours} hora${hours > 1 ? 's' : ''}`;
        if (minutes > 0) return `há ${minutes} minuto${minutes > 1 ? 's' : ''}`;
        return 'agora mesmo';
    },
    
    // Show toast notification
    showToast: (message, type = 'info') => {
        if (window.showNotification) {
            return window.showNotification(message, type);
        } else {
            // Fallback to console if notification system not available
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
};

// ===== GLOBAL EVENT EMITTER =====
class EventEmitter {
    constructor() {
        this.events = {};
    }
    
    on(event, callback) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        this.events[event].push(callback);
        
        // Return unsubscribe function
        return () => {
            this.events[event] = this.events[event].filter(cb => cb !== callback);
        };
    }
    
    emit(event, data) {
        if (this.events[event]) {
            this.events[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    Utils.error('Event callback error:', error);
                }
            });
        }
    }
    
    off(event, callback) {
        if (this.events[event]) {
            this.events[event] = this.events[event].filter(cb => cb !== callback);
        }
    }
    
    once(event, callback) {
        const unsubscribe = this.on(event, (data) => {
            callback(data);
            unsubscribe();
        });
        return unsubscribe;
    }
}

// Global event emitter instance
window.EventBus = new EventEmitter();

// ===== PERFORMANCE MONITORING =====
const Performance = {
    marks: new Map(),
    
    mark(name) {
        this.marks.set(name, performance.now());
        Utils.log(`Performance mark: ${name}`);
    },
    
    measure(name, startMark) {
        const startTime = this.marks.get(startMark);
        if (startTime) {
            const duration = performance.now() - startTime;
            Utils.log(`Performance measure: ${name} took ${duration.toFixed(2)}ms`);
            return duration;
        }
        return null;
    }
};

// ===== NOTIFICATION SYSTEM =====
function showNotification(message, type = 'info', duration = 5000) {
    // Ensure we have a message
    if (!message || message.trim() === '') {
        message = type === 'success' ? 'Operação realizada com sucesso!' : 
                  type === 'error' ? 'Ocorreu um erro. Tente novamente.' :
                  type === 'warning' ? 'Atenção!' :
                  'Notificação';
    }
    
    // Truncate very long messages
    if (message.length > 200) {
        message = message.substring(0, 197) + '...';
    }
    
    // Log notification for debugging
    Utils.log(`Notification [${type}]: ${message}`);
    
    // Create notification element
    const notification = Utils.createElement('div', {
        className: `notification notification-${type}`,
        innerHTML: `
            <div class="notification-content">
                <div class="notification-icon">
                    <i class="fas fa-${getNotificationIcon(type)}"></i>
                </div>
                <div class="notification-text">
                    <span class="notification-message">${message}</span>
                </div>
                <button class="notification-close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `
    });
    
    // Add to page
    document.body.appendChild(notification);
    
    // Debug: Log the notification element
    console.log('Notification created:', {
        message: message,
        type: type,
        element: notification,
        innerHTML: notification.innerHTML
    });
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('show');
        console.log('Notification shown:', notification.classList);
    }, 100);
    
    // Auto hide after duration
    const hideTimeout = setTimeout(() => {
        hideNotification(notification);
    }, duration);
    
    // Close button handler
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        clearTimeout(hideTimeout);
        hideNotification(notification);
    });
    
    // Click to close
    notification.addEventListener('click', () => {
        clearTimeout(hideTimeout);
        hideNotification(notification);
    });
    
    return notification;
}

function hideNotification(notification) {
    notification.classList.add('hide');
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 300);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// ===== SCROLL FUNCTIONS =====
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (!element) {
        Utils.error('Section not found:', sectionId);
        return;
    }
    
    const offset = 80; // Account for fixed header
    const elementTop = element.offsetTop - offset;
    
    window.scrollTo({
        top: elementTop,
        behavior: 'smooth'
    });
}

// ===== EXPORT GLOBALS =====
window.CONFIG = CONFIG;
window.Utils = Utils;
window.Performance = Performance;
window.showNotification = showNotification;
window.scrollToSection = scrollToSection;

// ===== INITIALIZATION =====
Utils.log('Configuration loaded successfully');
Performance.mark('app-start');