# 📋 Endpoints Completos

Lista completa de todos os endpoints da API com exemplos detalhados.

!!! info "Base URL"
    Todos os endpoints utilizam a base URL: `http://localhost:8000`

## 🔐 Autenticação

### POST `/auth/register`

Registra um novo usuário no sistema.

**Headers:**
```http
Content-Type: application/json
```

**Body:**
```json
{
  "username": "novo_usuario",
  "email": "usuario@email.com", 
  "password": "MinhaSenh@123",
  "confirm_password": "MinhaSenh@123"
}
```

**Respostas:**

=== "201 - Sucesso"
    ```json
    {
      "message": "Usuário criado com sucesso",
      "user": {
        "id": 2,
        "username": "novo_usuario",
        "email": "usuario@email.com",
        "is_admin": false,
        "is_active": true,
        "created_at": "2023-01-01T12:00:00Z"
      }
    }
    ```

=== "400 - Erro de Validação"
    ```json
    {
      "detail": "Email já cadastrado",
      "error_code": "EMAIL_ALREADY_EXISTS"
    }
    ```

### POST `/auth/login`

Autentica usuário e retorna tokens JWT.

**Body:**
```json
{
  "email_or_username": "admin@pizzaria.com",
  "password": "Admin123!@#"
}
```

**Respostas:**

=== "200 - Sucesso"
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer",
      "expires_in": 900,
      "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@pizzaria.com",
        "is_admin": true,
        "is_active": true
      }
    }
    ```

=== "401 - Credenciais Inválidas"
    ```json
    {
      "detail": "Email ou senha incorretos",
      "error_code": "INVALID_CREDENTIALS"
    }
    ```

### POST `/auth/refresh`

Renova o access token usando refresh token.

**Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### POST `/auth/create-admin` 🔒

Cria um novo administrador. **Requer autenticação de admin.**

**Headers:**
```http
Authorization: Bearer <admin_access_token>
```

**Body:**
```json
{
  "username": "novo_admin",
  "email": "admin@exemplo.com",
  "password": "AdminSenh@123",
  "confirm_password": "AdminSenh@123"
}
```

## 👥 Usuários

### GET `/users/me` 🔒

Retorna informações do usuário autenticado.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Resposta:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@pizzaria.com",
  "is_admin": true,
  "is_active": true,
  "created_at": "2023-01-01T00:00:00Z",
  "orders_count": 5,
  "total_spent": 125.50
}
```

### PUT `/users/me` 🔒

Atualiza informações do usuário autenticado.

**Body:**
```json
{
  "username": "novo_username",
  "email": "novo@email.com"
}
```

### GET `/users/list` 🔒👑

Lista todos os usuários. **Requer admin.**

**Query Parameters:**
- `page` (int): Página (padrão: 1)
- `size` (int): Itens por página (padrão: 10)
- `search` (str): Busca por username ou email
- `is_active` (bool): Filtrar por status ativo

**Exemplo:**
```http
GET /users/list?page=1&size=10&search=admin&is_active=true
```

**Resposta:**
```json
{
  "users": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@pizzaria.com",
      "is_admin": true,
      "is_active": true,
      "created_at": "2023-01-01T00:00:00Z",
      "orders_count": 5,
      "last_login": "2023-01-01T12:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 10,
  "total_pages": 1
}
```

### GET `/users/{user_id}` 🔒👑

Obtém detalhes de um usuário específico. **Requer admin.**

### PATCH `/users/{user_id}/admin` 🔒👑

Altera status de administrador de um usuário. **Requer admin.**

**Body:**
```json
{
  "is_admin": true
}
```

### PATCH `/users/{user_id}/active` 🔒👑

Ativa/desativa um usuário. **Requer admin.**

**Body:**
```json
{
  "is_active": false
}
```

### GET `/users/admin/stats` 🔒👑

Estatísticas gerais de usuários. **Requer admin.**

**Resposta:**
```json
{
  "total_users": 25,
  "active_users": 23,
  "admin_users": 2,
  "new_users_this_month": 5,
  "total_orders": 150,
  "revenue_this_month": 2500.00
}
```

## 🍕 Cardápio

### GET `/items/menu`

Retorna o cardápio público completo.

**Query Parameters:**
- `category` (str): Filtrar por categoria
- `available_only` (bool): Apenas itens disponíveis (padrão: true)
- `search` (str): Buscar por nome ou descrição

**Exemplo:**
```http
GET /items/menu?category=pizza&available_only=true
```

**Resposta:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Pizza Margherita",
      "description": "Molho de tomate, mozzarella e manjericão fresco",
      "price": 25.90,
      "category": "pizza",
      "image_url": null,
      "is_available": true,
      "preparation_time": 25
    }
  ],
  "categories": ["pizza", "bebida", "sobremesa", "entrada", "promocao"],
  "total_items": 23
}
```

### GET `/items/categories`

Lista todas as categorias disponíveis.

**Resposta:**
```json
{
  "categories": [
    {
      "name": "pizza",
      "display_name": "Pizzas",
      "icon": "fa-pizza-slice",
      "items_count": 9
    },
    {
      "name": "bebida", 
      "display_name": "Bebidas",
      "icon": "fa-glass-cheers",
      "items_count": 6
    }
  ]
}
```

### GET `/items/search`

Busca itens do cardápio por termo.

**Query Parameters:**
- `q` (str): Termo de busca (obrigatório)
- `category` (str): Filtrar por categoria
- `min_price` (float): Preço mínimo
- `max_price` (float): Preço máximo

### GET `/items/{item_id}/public`

Detalhes públicos de um item específico.

**Resposta:**
```json
{
  "id": 1,
  "name": "Pizza Margherita",
  "description": "Molho de tomate, mozzarella e manjericão fresco",
  "price": 25.90,
  "category": "pizza",
  "image_url": null,
  "is_available": true,
  "preparation_time": 25,
  "ingredients": ["Molho de tomate", "Mozzarella", "Manjericão"],
  "nutritional_info": {
    "calories": 250,
    "proteins": 12,
    "carbs": 30,
    "fats": 8
  }
}
```

### POST `/items/create-item` 🔒👑

Cria um novo item no cardápio. **Requer admin.**

**Body:**
```json
{
  "name": "Pizza Quattro Stagioni",
  "description": "Pizza dividida em quatro sabores",
  "price": 32.90,
  "category": "pizza",
  "image_url": "https://exemplo.com/pizza.jpg",
  "is_available": true,
  "preparation_time": 30
}
```

### PUT `/items/edit-item/{item_id}` 🔒👑

Edita um item existente. **Requer admin.**

### DELETE `/items/delete-item/{item_id}` 🔒👑

Remove um item do cardápio. **Requer admin.**

### PATCH `/items/toggle-availability/{item_id}` 🔒👑

Alterna disponibilidade de um item. **Requer admin.**

## 🛒 Pedidos

### POST `/orders/create-order` 🔒

Cria um novo pedido.

**Body:**
```json
{
  "items": [
    {
      "item_id": 1,
      "quantity": 2,
      "observations": "Sem cebola"
    },
    {
      "item_id": 5,
      "quantity": 1,
      "observations": ""
    }
  ],
  "delivery_address": "Rua das Flores, 123",
  "phone": "(11) 99999-9999",
  "observations": "Tocar campainha"
}
```

**Resposta:**
```json
{
  "id": 15,
  "user_id": 1,
  "status": "pendente",
  "total": 51.80,
  "estimated_time": 35,
  "delivery_address": "Rua das Flores, 123",
  "phone": "(11) 99999-9999",
  "observations": "Tocar campainha",
  "created_at": "2023-01-01T12:00:00Z",
  "items": [
    {
      "id": 25,
      "item_id": 1,
      "item_name": "Pizza Margherita",
      "quantity": 2,
      "unit_price": 25.90,
      "subtotal": 51.80,
      "observations": "Sem cebola"
    }
  ]
}
```

### GET `/orders/my-orders` 🔒

Lista pedidos do usuário autenticado.

**Query Parameters:**
- `status` (str): Filtrar por status
- `page` (int): Página
- `size` (int): Itens por página

### GET `/orders/{order_id}` 🔒

Detalhes de um pedido específico.

### PATCH `/orders/{order_id}/status` 🔒👑

Atualiza status de um pedido. **Requer admin.**

**Body:**
```json
{
  "status": "em_preparo"
}
```

!!! info "Status Disponíveis"
    - `pendente` - Pedido recebido
    - `confirmado` - Pedido confirmado
    - `em_preparo` - Em preparação
    - `saiu_entrega` - Saiu para entrega
    - `entregue` - Entregue
    - `cancelado` - Cancelado

### DELETE `/orders/{order_id}/cancel` 🔒

Cancela um pedido (apenas se pendente).

### POST `/orders/{order_id}/add-item` 🔒

Adiciona item a um pedido existente.

**Body:**
```json
{
  "item_id": 3,
  "quantity": 1,
  "observations": "Bem quente"
}
```

### DELETE `/orders/{order_id}/remove-item` 🔒

Remove item de um pedido.

**Query Parameters:**
- `order_item_id` (int): ID do item no pedido

**Exemplo:**
```http
DELETE /orders/15/remove-item?order_item_id=25
```

## 📊 Códigos de Status HTTP

| Código | Significado | Uso |
|--------|-------------|-----|
| 200 | OK | Operação bem-sucedida |
| 201 | Created | Recurso criado |
| 204 | No Content | Operação sem retorno |
| 400 | Bad Request | Dados inválidos |
| 401 | Unauthorized | Token inválido/expirado |
| 403 | Forbidden | Sem permissão |
| 404 | Not Found | Recurso não encontrado |
| 422 | Unprocessable Entity | Erro de validação |
| 500 | Internal Server Error | Erro interno |

## 🔧 Headers Padrão

### Requisições Autenticadas

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Respostas da API

```http
Content-Type: application/json
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-Response-Time: 125ms
```

## 📝 Exemplos com cURL

### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_username": "admin@pizzaria.com",
    "password": "Admin123!@#"
  }'
```

### Criar Pedido
```bash
curl -X POST "http://localhost:8000/orders/create-order" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [{"item_id": 1, "quantity": 2}],
    "delivery_address": "Rua das Flores, 123",
    "phone": "(11) 99999-9999"
  }'
```

### Listar Cardápio
```bash
curl "http://localhost:8000/items/menu?category=pizza"
```