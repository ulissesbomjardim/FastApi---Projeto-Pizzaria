"""
Schemas para autenticação e gestão de usuários
"""
import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    """Schema base para usuário"""

    email: EmailStr = Field(..., description='Email do usuário')
    username: str = Field(..., min_length=3, max_length=50, description='Nome de usuário')

    @validator('username')
    def validate_username(cls, v):
        """Validar formato do username"""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username deve conter apenas letras, números e underscore')
        return v.lower()


class UserCreate(UserBase):
    """Schema para criação de usuário"""

    password: str = Field(..., min_length=8, max_length=100, description='Senha do usuário (mínimo 8 caracteres)')
    confirm_password: str = Field(..., description='Confirmação da senha')

    @validator('password')
    def validate_password(cls, v):
        """Validar força da senha"""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Senha deve conter pelo menos uma letra maiúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('Senha deve conter pelo menos uma letra minúscula')
        if not re.search(r'\d', v):
            raise ValueError('Senha deve conter pelo menos um número')
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', v):
            raise ValueError('Senha deve conter pelo menos um caractere especial')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Verificar se as senhas coincidem"""
        if 'password' in values and v != values['password']:
            raise ValueError('Senhas não coincidem')
        return v


class UserUpdate(BaseModel):
    """Schema para atualização de usuário"""

    email: Optional[EmailStr] = Field(None, description='Novo email')
    username: Optional[str] = Field(None, min_length=3, max_length=50, description='Novo username')
    is_active: Optional[bool] = Field(None, description='Status ativo do usuário')


class UserResponse(UserBase):
    """Schema para resposta de usuário (sem senha)"""

    id: int = Field(..., description='ID único do usuário')
    is_active: bool = Field(..., description='Se o usuário está ativo')
    is_admin: bool = Field(..., description='Se o usuário é administrador')
    created_at: datetime = Field(..., description='Data de criação')
    updated_at: datetime = Field(..., description='Data da última atualização')

    class Config:
        from_attributes = True  # Para compatibilidade com SQLAlchemy


class UserLogin(BaseModel):
    """Schema para login de usuário"""

    email_or_username: str = Field(..., description='Email ou username para login')
    password: str = Field(..., description='Senha do usuário')


class TokenData(BaseModel):
    """Schema para dados do token JWT"""

    user_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Schema para requisição de refresh token"""

    refresh_token: str = Field(..., description='Token de renovação JWT')


class Token(BaseModel):
    """Schema para resposta de token"""

    access_token: str = Field(..., description='Token de acesso JWT')
    refresh_token: str = Field(..., description='Token de renovação JWT')
    token_type: str = Field(default='bearer', description='Tipo do token')
    expires_in: int = Field(..., description='Tempo de expiração do access token em segundos')
    refresh_expires_in: int = Field(..., description='Tempo de expiração do refresh token em segundos')
    user: UserResponse = Field(..., description='Dados do usuário autenticado')


class RefreshTokenResponse(BaseModel):
    """Schema para resposta de refresh token"""

    access_token: str = Field(..., description='Novo token de acesso JWT')
    refresh_token: str = Field(..., description='Novo token de renovação JWT')
    token_type: str = Field(default='bearer', description='Tipo do token')
    expires_in: int = Field(..., description='Tempo de expiração do access token em segundos')
    refresh_expires_in: int = Field(..., description='Tempo de expiração do refresh token em segundos')


class PasswordChange(BaseModel):
    """Schema para mudança de senha"""

    current_password: str = Field(..., description='Senha atual')
    new_password: str = Field(..., min_length=8, max_length=100, description='Nova senha')
    confirm_new_password: str = Field(..., description='Confirmação da nova senha')

    @validator('new_password')
    def validate_new_password(cls, v):
        """Validar força da nova senha"""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Nova senha deve conter pelo menos uma letra maiúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('Nova senha deve conter pelo menos uma letra minúscula')
        if not re.search(r'\d', v):
            raise ValueError('Nova senha deve conter pelo menos um número')
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', v):
            raise ValueError('Nova senha deve conter pelo menos um caractere especial')
        return v

    @validator('confirm_new_password')
    def passwords_match(cls, v, values):
        """Verificar se as novas senhas coincidem"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Novas senhas não coincidem')
        return v


class PasswordReset(BaseModel):
    """Schema para reset de senha"""

    email: EmailStr = Field(..., description='Email para reset de senha')


class PasswordResetConfirm(BaseModel):
    """Schema para confirmação de reset de senha"""

    token: str = Field(..., description='Token de reset recebido por email')
    new_password: str = Field(..., min_length=8, max_length=100, description='Nova senha')
    confirm_password: str = Field(..., description='Confirmação da nova senha')

    @validator('new_password')
    def validate_password(cls, v):
        """Validar força da senha"""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Senha deve conter pelo menos uma letra maiúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('Senha deve conter pelo menos uma letra minúscula')
        if not re.search(r'\d', v):
            raise ValueError('Senha deve conter pelo menos um número')
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', v):
            raise ValueError('Senha deve conter pelo menos um caractere especial')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Verificar se as senhas coincidem"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Senhas não coincidem')
        return v
