/**
 * Script de validação do sistema de autenticação
 * Executa testes automatizados para verificar se tudo está funcionando
 */

console.log('🧪 Iniciando testes do sistema de autenticação...');

// Teste 1: Verificar se AuthManager está carregado
function testAuthManager() {
    console.log('\n1️⃣ Testando AuthManager...');
    
    if (window.AuthManager) {
        console.log('✅ AuthManager encontrado');
        console.log('   - Versão:', window.AuthManager.version);
        console.log('   - Inicializado:', window.AuthManager.isInitialized);
        console.log('   - Autenticado:', window.AuthManager.isLoggedIn());
        
        if (window.AuthManager.isLoggedIn()) {
            const user = window.AuthManager.getUser();
            console.log('   - Usuário:', user?.username);
            console.log('   - Admin:', user?.is_admin);
        }
        
        return true;
    } else {
        console.log('❌ AuthManager não encontrado');
        return false;
    }
}

// Teste 2: Verificar localStorage
function testLocalStorage() {
    console.log('\n2️⃣ Testando localStorage...');
    
    const keys = [
        'hashtag_pizzaria_token',
        'hashtag_pizzaria_user',
        'hashtag_pizzaria_refresh',
        'access_token',
        'user_data',
        'refresh_token'
    ];
    
    let found = 0;
    keys.forEach(key => {
        const value = localStorage.getItem(key);
        if (value) {
            console.log(`   ✅ ${key}: ${key.includes('token') ? 'TOKEN_FOUND' : 'DATA_FOUND'}`);
            found++;
        } else {
            console.log(`   ❌ ${key}: não encontrado`);
        }
    });
    
    console.log(`   📊 Total encontrado: ${found}/${keys.length}`);
    return found > 0;
}

// Teste 3: Verificar API Service
function testApiService() {
    console.log('\n3️⃣ Testando API Service...');
    
    if (window.api) {
        console.log('✅ API Service encontrado');
        
        // Testar token
        const token = window.api.getAuthToken();
        if (token) {
            console.log('   ✅ Token disponível:', token.substring(0, 20) + '...');
        } else {
            console.log('   ❌ Token não disponível');
        }
        
        return !!token;
    } else {
        console.log('❌ API Service não encontrado');
        return false;
    }
}

// Teste 4: Verificar Auth Service
function testAuthService() {
    console.log('\n4️⃣ Testando Auth Service...');
    
    if (window.auth) {
        console.log('✅ Auth Service encontrado');
        console.log('   - Autenticado:', window.auth.isAuthenticated);
        console.log('   - É admin:', window.auth.isAdmin());
        
        const user = window.auth.getCurrentUser();
        if (user) {
            console.log('   - Usuário atual:', user.username);
        }
        
        return window.auth.isAuthenticated;
    } else {
        console.log('❌ Auth Service não encontrado');
        return false;
    }
}

// Teste 5: Verificar AdminPanel (apenas se estivermos na página admin)
function testAdminPanel() {
    const isAdminPage = window.location.pathname.includes('admin.html');
    
    console.log('\n5️⃣ Testando AdminPanel...');
    console.log('   - Página admin:', isAdminPage);
    
    if (isAdminPage) {
        if (window.AdminPanel) {
            console.log('   ✅ Classe AdminPanel encontrada');
        } else {
            console.log('   ❌ Classe AdminPanel não encontrada');
        }
        
        if (window.adminPanel) {
            console.log('   ✅ Instância adminPanel encontrada');
            return true;
        } else {
            console.log('   ❌ Instância adminPanel não encontrada');
            return false;
        }
    } else {
        console.log('   ℹ️ Não é página admin, pulando teste');
        return true;
    }
}

// Executar todos os testes
async function runAllTests() {
    console.log('🚀 Executando bateria de testes...');
    
    await new Promise(resolve => setTimeout(resolve, 2000)); // Aguardar carregamento
    
    const results = {
        authManager: testAuthManager(),
        localStorage: testLocalStorage(),
        apiService: testApiService(),
        authService: testAuthService(),
        adminPanel: testAdminPanel()
    };
    
    console.log('\n📊 RESULTADOS DOS TESTES:');
    console.log('================================');
    
    Object.entries(results).forEach(([test, passed]) => {
        console.log(`${passed ? '✅' : '❌'} ${test}: ${passed ? 'PASSOU' : 'FALHOU'}`);
    });
    
    const passedCount = Object.values(results).filter(Boolean).length;
    const totalCount = Object.keys(results).length;
    
    console.log('================================');
    console.log(`📈 RESUMO: ${passedCount}/${totalCount} testes passaram`);
    
    if (passedCount === totalCount) {
        console.log('🎉 TODOS OS TESTES PASSARAM! Sistema funcionando corretamente.');
    } else {
        console.log('⚠️ Alguns testes falharam. Verifique os logs acima.');
    }
    
    return results;
}

// Auto-executar se estivermos em desenvolvimento
if (window.CONFIG?.DEV?.ENABLE_LOGS) {
    window.runAuthTests = runAllTests;
    
    // Executar testes automaticamente após 3 segundos
    setTimeout(() => {
        console.log('🤖 Auto-executando testes...');
        runAllTests();
    }, 3000);
}

console.log('✅ Script de validação carregado. Execute window.runAuthTests() para testar manualmente.');