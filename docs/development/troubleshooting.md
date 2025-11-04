# 🔧 Solução de Problemas e Correções

## Problemas Comuns e Soluções

### 1. Erro 422 - Enum de Tamanhos
**Problema:** `Input should be 'pequena', 'media', 'grande'... input: "pequeno"`

**Solução:** Verificar se os valores do frontend correspondem exatamente aos enums do backend:
- `pequena` (não `pequeno`)
- `media` (não `médio`) 
- `grande`, `familia`, `unico`, `350ml`, `500ml`, `1l`, `2l`

### 2. Headers CORS/API
**Problema:** Requests falhando com erro CORS ou 422

**Solução:** Verificar headers obrigatórios:
```javascript
{
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
}
```

### 3. Problemas de Autenticação
**Problema:** Tokens não sincronizando entre páginas

**Solução:** Usar AuthManager centralizado com múltiplas chaves de storage.

### 4. Modal Auto-submit
**Problema:** Modal abre e fecha automaticamente

**Solução:** Implementar controle de estado com `dataset.modalReady`.

### 5. Dados Corrompidos
**Problema:** Pedidos com caracteres especiais causando erro 500

**Solução:** Limpar dados problemáticos do banco ou implementar sanitização.

## Checklist de Debugging

- [ ] Verificar enums no backend vs frontend
- [ ] Confirmar headers das requisições
- [ ] Validar estrutura JSON dos payloads  
- [ ] Testar endpoints via curl
- [ ] Verificar logs do backend
- [ ] Limpar cache do browser (Ctrl+Shift+R)

Para mais detalhes, consulte o arquivo de correções completas.