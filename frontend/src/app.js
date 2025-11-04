// Frontend JavaScript for Pizzaria App
const API_BASE_URL = 'http://localhost:8000';

class PizzariaApp {
    constructor() {
        this.statusElement = document.getElementById('status');
        this.init();
    }

    init() {
        console.log('Pizzaria Frontend initialized');
        this.setupEventListeners();
        this.checkBackendConnection();
    }

    setupEventListeners() {
        // Add event listeners for frontend interactions
        document.addEventListener('DOMContentLoaded', () => {
            console.log('DOM fully loaded');
        });
    }

    async checkBackendConnection() {
        try {
            this.updateStatus('Conectando ao backend...', 'loading');
            
            // Try to connect to backend
            const response = await fetch(`${API_BASE_URL}/docs`);
            
            if (response.ok) {
                this.updateStatus('✅ Backend conectado com sucesso!', 'success');
                console.log('Backend connection successful');
            } else {
                throw new Error('Backend responded with error');
            }
        } catch (error) {
            this.updateStatus('❌ Backend não disponível. Verifique se o servidor está rodando.', 'error');
            console.log('Backend not available:', error);
        }
    }

    updateStatus(message, type) {
        this.statusElement.textContent = message;
        this.statusElement.className = `status-${type}`;
    }

    // Future methods for pizza management will go here
    async loadPizzas() {
        // Implementation for loading pizzas from backend
    }

    async addPizza(pizzaData) {
        // Implementation for adding new pizza
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PizzariaApp();
});