#!/usr/bin/env python3
"""
Módulo de tratamento de erros padronizado

Este módulo fornece classes e funções para tratamento consistente
de erros em toda a aplicação, incluindo logging estruturado e
respostas padronizadas para a API.
"""

import traceback
from typing import Dict, Any, Optional, Union
from enum import Enum
from flask import jsonify, request
from marshmallow import ValidationError

from .logger import get_logger

class ErrorCode(Enum):
    """Códigos de erro padronizados"""
    # Erros de validação (400)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_PARAMETER = "MISSING_PARAMETER"
    
    # Erros de autenticação (401)
    UNAUTHORIZED = "UNAUTHORIZED"
    INVALID_API_KEY = "INVALID_API_KEY"
    
    # Erros de autorização (403)
    FORBIDDEN = "FORBIDDEN"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # Erros de recurso (404)
    NOT_FOUND = "NOT_FOUND"
    JOB_NOT_FOUND = "JOB_NOT_FOUND"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    
    # Erros de conflito (409)
    CONFLICT = "CONFLICT"
    JOB_ALREADY_EXISTS = "JOB_ALREADY_EXISTS"
    
    # Erros de rate limiting (429)
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    
    # Erros de servidor (500)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    
    # Erros de processamento (422)
    PROCESSING_ERROR = "PROCESSING_ERROR"
    VIDEO_GENERATION_ERROR = "VIDEO_GENERATION_ERROR"
    AUDIO_GENERATION_ERROR = "AUDIO_GENERATION_ERROR"
    IMAGE_GENERATION_ERROR = "IMAGE_GENERATION_ERROR"
    
    # Erros de configuração (503)
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    REDIS_UNAVAILABLE = "REDIS_UNAVAILABLE"
    QUEUE_UNAVAILABLE = "QUEUE_UNAVAILABLE"

class APIError(Exception):
    """Exceção base para erros da API"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.correlation_id = correlation_id
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o erro para dicionário"""
        error_dict = {
            "error": {
                "code": self.error_code.value,
                "message": self.message,
                "status_code": self.status_code
            }
        }
        
        if self.details:
            error_dict["error"]["details"] = self.details
            
        if self.correlation_id:
            error_dict["error"]["correlation_id"] = self.correlation_id
            
        return error_dict

class ValidationAPIError(APIError):
    """Erro de validação de entrada"""
    
    def __init__(self, message: str, field_errors: Optional[Dict] = None):
        details = {"field_errors": field_errors} if field_errors else None
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=400,
            details=details
        )

class AuthenticationError(APIError):
    """Erro de autenticação"""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            error_code=ErrorCode.UNAUTHORIZED,
            status_code=401
        )

class AuthorizationError(APIError):
    """Erro de autorização"""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            error_code=ErrorCode.FORBIDDEN,
            status_code=403
        )

class NotFoundError(APIError):
    """Erro de recurso não encontrado"""
    
    def __init__(self, message: str, resource_type: str = "Resource"):
        super().__init__(
            message=message,
            error_code=ErrorCode.NOT_FOUND,
            status_code=404,
            details={"resource_type": resource_type}
        )

class ProcessingError(APIError):
    """Erro de processamento"""
    
    def __init__(self, message: str, process_type: str = "processing"):
        super().__init__(
            message=message,
            error_code=ErrorCode.PROCESSING_ERROR,
            status_code=422,
            details={"process_type": process_type}
        )

class ServiceUnavailableError(APIError):
    """Erro de serviço indisponível"""
    
    def __init__(self, message: str, service_name: str = "service"):
        super().__init__(
            message=message,
            error_code=ErrorCode.SERVICE_UNAVAILABLE,
            status_code=503,
            details={"service_name": service_name}
        )

class ErrorHandler:
    """Classe para tratamento centralizado de erros"""
    
    def __init__(self, app=None):
        self.logger = get_logger("error_handler")
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa o handler de erros com a aplicação Flask"""
        app.register_error_handler(APIError, self.handle_api_error)
        app.register_error_handler(ValidationError, self.handle_validation_error)
        app.register_error_handler(404, self.handle_not_found)
        app.register_error_handler(500, self.handle_internal_error)
        app.register_error_handler(Exception, self.handle_unexpected_error)
    
    def handle_api_error(self, error: APIError):
        """Trata erros da API"""
        self.logger.error(
            f"API Error: {error.error_code.value} - {error.message}",
            extra={
                "error_code": error.error_code.value,
                "status_code": error.status_code,
                "details": error.details,
                "correlation_id": error.correlation_id,
                "endpoint": request.endpoint,
                "method": request.method,
                "url": request.url
            }
        )
        
        return jsonify(error.to_dict()), error.status_code
    
    def handle_validation_error(self, error: ValidationError):
        """Trata erros de validação do Marshmallow"""
        validation_error = ValidationAPIError(
            message="Validation failed",
            field_errors=error.messages
        )
        return self.handle_api_error(validation_error)
    
    def handle_not_found(self, error):
        """Trata erros 404"""
        not_found_error = NotFoundError(
            message="The requested resource was not found",
            resource_type="endpoint"
        )
        return self.handle_api_error(not_found_error)
    
    def handle_internal_error(self, error):
        """Trata erros internos do servidor"""
        self.logger.error(
            f"Internal server error: {str(error)}",
            extra={
                "traceback": traceback.format_exc(),
                "endpoint": request.endpoint,
                "method": request.method,
                "url": request.url
            }
        )
        
        internal_error = APIError(
            message="An internal server error occurred",
            error_code=ErrorCode.INTERNAL_ERROR,
            status_code=500
        )
        return self.handle_api_error(internal_error)
    
    def handle_unexpected_error(self, error: Exception):
        """Trata erros inesperados"""
        self.logger.critical(
            f"Unexpected error: {str(error)}",
            extra={
                "error_type": type(error).__name__,
                "traceback": traceback.format_exc(),
                "endpoint": request.endpoint,
                "method": request.method,
                "url": request.url
            }
        )
        
        unexpected_error = APIError(
            message="An unexpected error occurred",
            error_code=ErrorCode.INTERNAL_ERROR,
            status_code=500
        )
        return self.handle_api_error(unexpected_error)

def create_error_response(
    message: str,
    error_code: ErrorCode,
    status_code: int,
    details: Optional[Dict[str, Any]] = None
) -> tuple:
    """Cria uma resposta de erro padronizada"""
    error = APIError(
        message=message,
        error_code=error_code,
        status_code=status_code,
        details=details
    )
    return jsonify(error.to_dict()), status_code

def safe_execute(func, *args, **kwargs):
    """Executa uma função de forma segura, capturando exceções"""
    logger = get_logger("safe_execute")
    
    try:
        return func(*args, **kwargs)
    except APIError:
        # Re-raise API errors
        raise
    except Exception as e:
        logger.error(
            f"Error in {func.__name__}: {str(e)}",
            extra={"traceback": traceback.format_exc()}
        )
        raise APIError(
            message=f"Error executing {func.__name__}",
            error_code=ErrorCode.INTERNAL_ERROR,
            status_code=500
        )

# Instância global do error handler
error_handler = ErrorHandler()