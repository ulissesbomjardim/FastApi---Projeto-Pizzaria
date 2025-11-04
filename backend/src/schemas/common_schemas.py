"""
Schemas para respostas padrão da API
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """Schema para resposta simples com mensagem"""

    message: str = Field(..., description='Mensagem de resposta')
    success: bool = Field(default=True, description='Se a operação foi bem-sucedida')
    timestamp: datetime = Field(default_factory=datetime.now, description='Timestamp da resposta')


class ErrorResponse(BaseModel):
    """Schema para resposta de erro"""

    error: str = Field(..., description='Tipo do erro')
    message: str = Field(..., description='Mensagem de erro')
    details: Optional[Dict[str, Any]] = Field(None, description='Detalhes adicionais do erro')
    timestamp: datetime = Field(default_factory=datetime.now, description='Timestamp do erro')
    success: bool = Field(default=False, description='Sempre False para erros')


class ValidationErrorResponse(BaseModel):
    """Schema para erros de validação"""

    error: str = Field(default='validation_error', description='Tipo do erro')
    message: str = Field(..., description='Mensagem de erro principal')
    validation_errors: List[Dict[str, Any]] = Field(..., description='Lista de erros de validação')
    timestamp: datetime = Field(default_factory=datetime.now, description='Timestamp do erro')
    success: bool = Field(default=False, description='Sempre False para erros')


class PaginationMeta(BaseModel):
    """Schema para metadados de paginação"""

    current_page: int = Field(..., description='Página atual')
    per_page: int = Field(..., description='Itens por página')
    total_items: int = Field(..., description='Total de itens')
    total_pages: int = Field(..., description='Total de páginas')
    has_next: bool = Field(..., description='Se há próxima página')
    has_previous: bool = Field(..., description='Se há página anterior')


class PaginatedResponse(BaseModel):
    """Schema genérico para respostas paginadas"""

    data: List[Any] = Field(..., description='Lista de dados')
    meta: PaginationMeta = Field(..., description='Metadados de paginação')
    success: bool = Field(default=True, description='Se a operação foi bem-sucedida')
    timestamp: datetime = Field(default_factory=datetime.now, description='Timestamp da resposta')


class HealthCheckResponse(BaseModel):
    """Schema para health check da API"""

    status: str = Field(..., description='Status da API')
    version: str = Field(..., description='Versão da API')
    database: str = Field(..., description='Status do banco de dados')
    uptime: str = Field(..., description='Tempo de atividade')
    timestamp: datetime = Field(default_factory=datetime.now, description='Timestamp da verificação')


class SearchFilters(BaseModel):
    """Schema para filtros de busca"""

    query: Optional[str] = Field(None, min_length=1, max_length=100, description='Termo de busca')
    category: Optional[str] = Field(None, description='Filtrar por categoria')
    status: Optional[str] = Field(None, description='Filtrar por status')
    date_from: Optional[datetime] = Field(None, description='Data inicial')
    date_to: Optional[datetime] = Field(None, description='Data final')
    min_price: Optional[float] = Field(None, ge=0, description='Preço mínimo')
    max_price: Optional[float] = Field(None, ge=0, description='Preço máximo')
    is_available: Optional[bool] = Field(None, description='Se está disponível')


class PaginationParams(BaseModel):
    """Schema para parâmetros de paginação"""

    page: int = Field(default=1, ge=1, description='Número da página')
    per_page: int = Field(default=20, ge=1, le=100, description='Itens por página')
    sort_by: Optional[str] = Field(None, description='Campo para ordenação')
    sort_order: Optional[str] = Field(default='asc', pattern='^(asc|desc)$', description='Ordem da ordenação')


class BulkOperationRequest(BaseModel):
    """Schema para operações em lote"""

    ids: List[int] = Field(..., min_items=1, description='Lista de IDs para operação')
    operation: str = Field(..., description='Tipo de operação')
    parameters: Optional[Dict[str, Any]] = Field(None, description='Parâmetros da operação')


class BulkOperationResponse(BaseModel):
    """Schema para resposta de operação em lote"""

    operation: str = Field(..., description='Tipo de operação executada')
    total_requested: int = Field(..., description='Total de itens solicitados')
    successful: int = Field(..., description='Itens processados com sucesso')
    failed: int = Field(..., description='Itens que falharam')
    errors: Optional[List[Dict[str, Any]]] = Field(None, description='Lista de erros ocorridos')
    success: bool = Field(..., description='Se a operação geral foi bem-sucedida')
    timestamp: datetime = Field(default_factory=datetime.now, description='Timestamp da operação')


class StatisticsResponse(BaseModel):
    """Schema para resposta de estatísticas"""

    period: str = Field(..., description='Período das estatísticas')
    metrics: Dict[str, Union[int, float, str]] = Field(..., description='Métricas calculadas')
    charts: Optional[Dict[str, List[Dict]]] = Field(None, description='Dados para gráficos')
    timestamp: datetime = Field(default_factory=datetime.now, description='Timestamp das estatísticas')


class FileUploadResponse(BaseModel):
    """Schema para resposta de upload de arquivo"""

    filename: str = Field(..., description='Nome do arquivo')
    file_size: int = Field(..., description='Tamanho do arquivo em bytes')
    file_type: str = Field(..., description='Tipo do arquivo')
    file_url: str = Field(..., description='URL de acesso ao arquivo')
    upload_timestamp: datetime = Field(default_factory=datetime.now, description='Timestamp do upload')
    success: bool = Field(default=True, description='Se o upload foi bem-sucedido')


class ExportRequest(BaseModel):
    """Schema para solicitação de exportação"""

    format: str = Field(..., pattern='^(csv|xlsx|pdf)$', description='Formato de exportação')
    filters: Optional[SearchFilters] = Field(None, description='Filtros para exportação')
    fields: Optional[List[str]] = Field(None, description='Campos específicos para exportar')
    include_headers: bool = Field(default=True, description='Incluir cabeçalhos')


class ExportResponse(BaseModel):
    """Schema para resposta de exportação"""

    export_id: str = Field(..., description='ID único da exportação')
    format: str = Field(..., description='Formato da exportação')
    status: str = Field(..., description='Status da exportação')
    file_url: Optional[str] = Field(None, description='URL do arquivo (quando pronto)')
    created_at: datetime = Field(default_factory=datetime.now, description='Data de criação')
    expires_at: Optional[datetime] = Field(None, description='Data de expiração do arquivo')


# Schemas para configurações do sistema
class SystemConfigResponse(BaseModel):
    """Schema para configurações do sistema"""

    delivery_fee: float = Field(..., description='Taxa de entrega padrão')
    min_order_value: float = Field(..., description='Valor mínimo do pedido')
    max_delivery_distance: int = Field(..., description='Distância máxima de entrega (km)')
    average_preparation_time: int = Field(..., description='Tempo médio de preparo (min)')
    working_hours: Dict[str, Dict[str, str]] = Field(..., description='Horários de funcionamento')
    payment_methods: List[str] = Field(..., description='Métodos de pagamento aceitos')
    is_accepting_orders: bool = Field(..., description='Se está aceitando pedidos')


class NotificationResponse(BaseModel):
    """Schema para notificações"""

    id: int = Field(..., description='ID da notificação')
    title: str = Field(..., description='Título da notificação')
    message: str = Field(..., description='Mensagem da notificação')
    type: str = Field(..., description='Tipo da notificação')
    is_read: bool = Field(..., description='Se foi lida')
    created_at: datetime = Field(..., description='Data de criação')
    user_id: Optional[int] = Field(None, description='ID do usuário (se específica)')

    class Config:
        from_attributes = True
