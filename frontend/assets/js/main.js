// ===== APPLICATION INITIALIZATION =====
class App {
    constructor() {
        this.initialized = false;
        this.loading = true;
        this.components = {};
        
        this.init();
        Utils.log('Application initialized');
    }
    
    async init() {
        try {
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                await new Promise(resolve => {
                    document.addEventListener('DOMContentLoaded', resolve);
                });
            }
            
            // Initialize core components
            this.initializeComponents();
            this.bindGlobalEvents();
            this.setupNavigation();
            this.setupScrollEffects();
            this.setupPerformanceMonitoring();
            
            // Mark as initialized
            this.initialized = true;
            this.loading = false;
            
            // Hide loading screen
            this.hideLoadingScreen();
            
            // Initial render
            this.render();
            
            Utils.log('Application ready');
            EventBus.emit('app:ready');
            
        } catch (error) {
            Utils.error('Application initialization failed:', error);
            this.handleInitializationError(error);
        }
    }
    
    initializeComponents() {
        // Navigation controller
        this.components.navigation = new NavigationController();
        
        // Scroll manager
        this.components.scrollManager = new ScrollManager();
        
        // Notification system (already initialized)
        this.components.notifications = window.notifications;
        
        // Performance monitor
        this.components.performance = new PerformanceMonitor();
        
        Utils.log('Core components initialized');
    }
    
    bindGlobalEvents() {
        // Window events
        window.addEventListener('resize', Utils.throttle(() => {
            EventBus.emit('window:resize', {
                width: window.innerWidth,
                height: window.innerHeight
            });
        }, 250));
        
        window.addEventListener('scroll', Utils.throttle(() => {
            EventBus.emit('window:scroll', {
                scrollY: window.scrollY,
                scrollX: window.scrollX
            });
        }, 16)); // ~60fps
        
        // Online/offline events
        window.addEventListener('online', () => {
            EventBus.emit('app:online');
            showNotification('Conexão restaurada', 'success');
        });
        
        window.addEventListener('offline', () => {
            EventBus.emit('app:offline');
            showNotification('Sem conexão com a internet', 'warning');
        });
        
        // Before unload (if cart has items)
        window.addEventListener('beforeunload', (e) => {
            if (cart && !cart.isEmpty()) {
                e.preventDefault();
                e.returnValue = 'Você tem itens no carrinho. Deseja realmente sair?';
                return e.returnValue;
            }
        });
        
        // Error handling
        window.addEventListener('error', (e) => {
            Utils.error('Global error:', e.error);
            EventBus.emit('app:error', e.error);
        });
        
        window.addEventListener('unhandledrejection', (e) => {
            Utils.error('Unhandled promise rejection:', e.reason);
            EventBus.emit('app:error', e.reason);
        });
        
        Utils.log('Global events bound');
    }
    
    setupNavigation() {
        // Mobile menu toggle
        const mobileMenuBtn = document.getElementById('mobile-menu-btn');
        const navMenu = document.querySelector('.nav-menu');
        
        mobileMenuBtn?.addEventListener('click', () => {
            navMenu?.classList.toggle('open');
            mobileMenuBtn.classList.toggle('active');
        });
        
        // Close mobile menu on link click
        navMenu?.querySelectorAll('a[href^="#"]').forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('open');
                mobileMenuBtn?.classList.remove('active');
            });
        });
        
        // Close mobile menu on outside click
        document.addEventListener('click', (e) => {
            if (!navMenu?.contains(e.target) && !mobileMenuBtn?.contains(e.target)) {
                navMenu?.classList.remove('open');
                mobileMenuBtn?.classList.remove('active');
            }
        });
    }
    
    setupScrollEffects() {
        // Header scroll effect
        const header = document.querySelector('header');
        if (header) {
            EventBus.on('window:scroll', ({ scrollY }) => {
                if (scrollY > 100) {
                    header.classList.add('scrolled');
                } else {
                    header.classList.remove('scrolled');
                }
            });
        }
        
        // Back to top button
        this.setupBackToTop();
        
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                this.components.scrollManager.scrollToElement(targetId);
            });
        });
    }
    
    setupBackToTop() {
        // Create back to top button
        const backToTop = Utils.createElement('button', {
            id: 'back-to-top',
            className: 'back-to-top-btn',
            innerHTML: '<i class="fas fa-arrow-up"></i>',
            title: 'Voltar ao topo'
        });
        
        document.body.appendChild(backToTop);
        
        // Show/hide based on scroll
        EventBus.on('window:scroll', ({ scrollY }) => {
            if (scrollY > 500) {
                backToTop.classList.add('visible');
            } else {
                backToTop.classList.remove('visible');
            }
        });
        
        // Click handler
        backToTop.addEventListener('click', () => {
            this.components.scrollManager.scrollToTop();
        });
    }
    
    setupPerformanceMonitoring() {
        // Monitor performance metrics
        if ('performance' in window && 'observer' in window.PerformanceObserver.prototype) {
            this.components.performance.start();
        }
        
        // Log performance on page load
        window.addEventListener('load', () => {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                if (perfData) {
                    Utils.log('Page Load Performance:', {
                        loadTime: Math.round(perfData.loadEventEnd - perfData.fetchStart),
                        domReady: Math.round(perfData.domContentLoadedEventEnd - perfData.fetchStart),
                        firstPaint: this.getFirstPaint()
                    });
                }
            }, 0);
        });
    }
    
    getFirstPaint() {
        const paintEntries = performance.getEntriesByType('paint');
        const firstPaint = paintEntries.find(entry => entry.name === 'first-paint');
        return firstPaint ? Math.round(firstPaint.startTime) : null;
    }
    
    hideLoadingScreen() {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.classList.add('fade-out');
            setTimeout(() => {
                loadingScreen.remove();
            }, 500);
        }
    }
    
    render() {
        // Initial render of dynamic content
        EventBus.emit('app:render');
        
        // Update UI based on current state
        this.updateUI();
    }
    
    updateUI() {
        // Update authentication state
        if (auth.checkAuthStatus()) {
            document.body.classList.add('authenticated');
        } else {
            document.body.classList.remove('authenticated');
        }
        
        // Update cart state
        if (cart && !cart.isEmpty()) {
            document.body.classList.add('has-cart-items');
        } else {
            document.body.classList.remove('has-cart-items');
        }
    }
    
    handleInitializationError(error) {
        console.error('App initialization failed:', error);
        
        // Show error message to user
        const errorContainer = Utils.createElement('div', {
            className: 'app-error',
            innerHTML: `
                <div class="error-content">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h2>Erro de Inicialização</h2>
                    <p>Ocorreu um erro ao carregar a aplicação.</p>
                    <button onclick="location.reload()" class="btn btn-primary">
                        <i class="fas fa-redo"></i> Tentar Novamente
                    </button>
                </div>
            `
        });
        
        document.body.innerHTML = '';
        document.body.appendChild(errorContainer);
    }
}

// ===== NAVIGATION CONTROLLER =====
class NavigationController {
    constructor() {
        this.activeSection = 'home';
        this.sections = ['home', 'menu', 'about', 'contact'];
        
        this.init();
    }
    
    init() {
        this.setupSectionObserver();
        this.bindNavigationEvents();
        
        Utils.log('Navigation Controller initialized');
    }
    
    setupSectionObserver() {
        // Intersection Observer for section highlighting
        const options = {
            rootMargin: '-50% 0px -50% 0px',
            threshold: 0
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.setActiveSection(entry.target.id);
                }
            });
        }, options);
        
        // Observe all sections
        this.sections.forEach(sectionId => {
            const section = document.getElementById(sectionId);
            if (section) {
                observer.observe(section);
            }
        });
    }
    
    bindNavigationEvents() {
        // Navigation link clicks
        document.querySelectorAll('.nav-link[href^="#"]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                this.navigateToSection(targetId);
            });
        });
    }
    
    setActiveSection(sectionId) {
        if (this.activeSection === sectionId) return;
        
        this.activeSection = sectionId;
        
        // Update navigation links
        document.querySelectorAll('.nav-link').forEach(link => {
            const href = link.getAttribute('href');
            if (href && href.substring(1) === sectionId) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
        
        EventBus.emit('navigation:sectionChanged', sectionId);
        Utils.log('Active section changed:', sectionId);
    }
    
    navigateToSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            app.components.scrollManager.scrollToElement(sectionId);
        }
    }
}

// ===== SCROLL MANAGER =====
class ScrollManager {
    constructor() {
        this.scrolling = false;
        this.init();
    }
    
    init() {
        Utils.log('Scroll Manager initialized');
    }
    
    scrollToElement(elementId, offset = 80) {
        const element = document.getElementById(elementId);
        if (!element) {
            Utils.error('Element not found:', elementId);
            return;
        }
        
        const elementTop = element.offsetTop - offset;
        
        this.scrollTo(elementTop);
    }
    
    scrollToTop() {
        this.scrollTo(0);
    }
    
    scrollTo(position, duration = 800) {
        if (this.scrolling) return;
        
        this.scrolling = true;
        const start = window.scrollY;
        const distance = position - start;
        const startTime = performance.now();
        
        const easeInOutCubic = (t) => {
            return t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;
        };
        
        const animation = (currentTime) => {
            const timeElapsed = currentTime - startTime;
            const progress = Math.min(timeElapsed / duration, 1);
            const ease = easeInOutCubic(progress);
            
            window.scrollTo(0, start + distance * ease);
            
            if (progress < 1) {
                requestAnimationFrame(animation);
            } else {
                this.scrolling = false;
            }
        };
        
        requestAnimationFrame(animation);
    }
}

// ===== PERFORMANCE MONITOR =====
class PerformanceMonitor {
    constructor() {
        this.metrics = {};
        this.observers = [];
    }
    
    start() {
        this.observeLCP();
        this.observeFID();
        this.observeCLS();
        
        Utils.log('Performance monitoring started');
    }
    
    observeLCP() {
        // Largest Contentful Paint
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                const lastEntry = entries[entries.length - 1];
                this.metrics.lcp = Math.round(lastEntry.startTime);
                Utils.log('LCP:', this.metrics.lcp + 'ms');
            });
            
            try {
                observer.observe({ entryTypes: ['largest-contentful-paint'] });
                this.observers.push(observer);
            } catch (e) {
                // LCP not supported
            }
        }
    }
    
    observeFID() {
        // First Input Delay
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                entries.forEach(entry => {
                    this.metrics.fid = Math.round(entry.processingStart - entry.startTime);
                    Utils.log('FID:', this.metrics.fid + 'ms');
                });
            });
            
            try {
                observer.observe({ entryTypes: ['first-input'] });
                this.observers.push(observer);
            } catch (e) {
                // FID not supported
            }
        }
    }
    
    observeCLS() {
        // Cumulative Layout Shift
        if ('PerformanceObserver' in window) {
            let clsValue = 0;
            
            const observer = new PerformanceObserver((list) => {
                list.getEntries().forEach(entry => {
                    if (!entry.hadRecentInput) {
                        clsValue += entry.value;
                        this.metrics.cls = Math.round(clsValue * 10000) / 10000;
                        Utils.log('CLS:', this.metrics.cls);
                    }
                });
            });
            
            try {
                observer.observe({ entryTypes: ['layout-shift'] });
                this.observers.push(observer);
            } catch (e) {
                // CLS not supported
            }
        }
    }
    
    getMetrics() {
        return { ...this.metrics };
    }
    
    stop() {
        this.observers.forEach(observer => observer.disconnect());
        this.observers = [];
        Utils.log('Performance monitoring stopped');
    }
}

// ===== GLOBAL EVENT LISTENERS =====
EventBus.on('app:ready', () => {
    // Update UI when app is ready
    if (app && typeof app.updateUI === 'function') {
        app.updateUI();
    }
});

EventBus.on('auth:login', () => {
    if (app && typeof app.updateUI === 'function') {
        app.updateUI();
    }
    showNotification('Login realizado com sucesso!', 'success');
});

EventBus.on('auth:logout', () => {
    if (app && typeof app.updateUI === 'function') {
        app.updateUI();
    }
    showNotification('Logout realizado com sucesso!', 'success');
});

EventBus.on('cart:change', () => {
    if (app && typeof app.updateUI === 'function') {
        app.updateUI();
    }
});

EventBus.on('window:resize', () => {
    // Handle responsive changes
    const isMobile = window.innerWidth <= 768;
    document.body.classList.toggle('mobile', isMobile);
});

EventBus.on('app:error', (error) => {
    // Handle application errors
    Utils.error('Application error:', error);
    showNotification('Ocorreu um erro inesperado', 'error');
});

// ===== INITIALIZATION =====
let app = null;

// Initialize app when script loads
function initializeApp() {
    try {
        app = new App();
        window.app = app; // Make globally accessible
    } catch (error) {
        Utils.error('Failed to initialize app:', error);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

// ===== SERVICE WORKER REGISTRATION =====
if ('serviceWorker' in navigator && CONFIG.ENV === 'production') {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                Utils.log('Service Worker registered:', registration);
            })
            .catch(error => {
                Utils.log('Service Worker registration failed:', error);
            });
    });
}

Utils.log('Main application script loaded');