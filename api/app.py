#!/usr/bin/env python3
"""
Flask API Backend para AI Video GPT Frontend

Este módulo fornece uma API REST para o frontend web do AI Video GPT,
permitindo geração de vídeos através de requisições HTTP.
"""

import os
import uuid
import json
import threading
import time
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, send_file, send_from_directory, render_template_string
from flask_cors import CORS
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename

# Importar sistema de tratamento de erros
from src.utils.error_handler import (
    error_handler, APIError, ValidationAPIError, AuthenticationError,
    NotFoundError, ProcessingError, ServiceUnavailableError, ErrorCode
)
from src.utils.queue_manager import queue_manager

# Importar blueprint de monitoramento
from src.routes.monitoring import monitoring_bp

# Carregar variáveis de ambiente do arquivo .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Will use system environment variables

# Import logging system
from src.utils.logger import setup_logging, get_logger, ai_logger, log_api_request

# Importar módulos do projeto (comentado temporariamente para teste)
# from main import main as generate_video_main
# from examples.basic.generate_tiktok_video import generate_tiktok_video

app = Flask(__name__)
CORS(app)  # Permitir requisições do frontend

# Configurar rate limiting (temporariamente desabilitado)
# limiter = Limiter(
#     key_func=get_remote_address,
#     storage_uri=os.getenv('RATELIMIT_STORAGE_URL', 'memory://'),
#     default_limits=["100 per hour", "20 per minute"]
# )
# limiter.init_app(app)

# Inicializar tratamento de erros
error_handler.init_app(app)

# Registrar blueprint de monitoramento
app.register_blueprint(monitoring_bp)

# ===== MIDDLEWARE DE SEGURANÇA =====
@app.after_request
def add_security_headers(response):
    """Adicionar cabeçalhos de segurança a todas as respostas"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    # Não adicionar HSTS em desenvolvimento
    if not app.debug:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

@app.errorhandler(401)
def unauthorized(error):
    """Handler customizado para erros 401"""
    return jsonify({
        'error': 'Não autorizado',
        'code': 'UNAUTHORIZED',
        'message': 'API key é obrigatória para este endpoint'
    }), 401

@app.errorhandler(429)
def rate_limit_exceeded(error):
    """Handler para limite de taxa excedido (caso implementado futuramente)"""
    rate_limit_error = APIError(
        message='Muitas requisições. Tente novamente mais tarde.',
        error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
        status_code=429,
        details={'retry_after': getattr(error, 'retry_after', None)}
    )
    return jsonify(rate_limit_error.to_dict()), 429

# Configurações
UPLOAD_FOLDER = 'outputs'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Configurações de segurança
API_KEY = os.getenv('API_KEY', 'ai-video-gpt-default-key-2025')  # Chave padrão para desenvolvimento
REQUIRE_API_KEY = os.getenv('REQUIRE_API_KEY', 'true').lower() == 'true'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Armazenamento em memória para jobs (em produção, usar Redis ou banco de dados)
jobs = {}
video_results = {}

# ===== MIDDLEWARE DE AUTENTICAÇÃO =====

def require_api_key(f):
    """
    Decorator para exigir autenticação via API key em endpoints protegidos.
    
    A API key deve ser fornecida no header 'X-API-Key' ou como parâmetro 
    'api_key' na query string ou corpo da requisição.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Permitir bypass da autenticação se REQUIRE_API_KEY=false
        if not REQUIRE_API_KEY:
            return f(*args, **kwargs)
            
        # Obter API key do header, query params ou body
        api_key = None
        
        # Verificar header X-API-Key
        api_key = request.headers.get('X-API-Key')
        
        # Verificar query parameter
        if not api_key:
            api_key = request.args.get('api_key')
            
        # Verificar no corpo da requisição (JSON)
        if not api_key and request.is_json:
            data = request.get_json(silent=True)
            if data:
                api_key = data.get('api_key')
        
        # Validar API key
        if not api_key:
            return jsonify({
                'error': 'API key é obrigatória',
                'code': 'MISSING_API_KEY',
                'message': 'Forneça a API key no header X-API-Key, parâmetro api_key, ou no corpo da requisição'
            }), 401
        
        if api_key != API_KEY:
            return jsonify({
                'error': 'API key inválida',
                'code': 'INVALID_API_KEY',
                'message': 'A API key fornecida não é válida'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def check_api_key_optional():
    """
    Função auxiliar para verificar se a API key é válida quando fornecida,
    mas não exige sua presença (para endpoints públicos)
    """
    if not REQUIRE_API_KEY:
        return True
        
    api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
    if request.is_json:
        data = request.get_json(silent=True)
        if data:
            api_key = api_key or data.get('api_key')
    
    return not api_key or api_key == API_KEY

class VideoGenerationJob:
    """Classe para gerenciar jobs de geração de vídeo"""
    
    def __init__(self, job_id, script, image_prompts, voice_provider='auto', voice_type='narrator', 
                 language='pt', video_format='standard', effects_preset='professional', enable_effects=True, image_preset=None):
        self.job_id = job_id
        self.script = script
        self.image_prompts = image_prompts
        self.voice_provider = voice_provider
        self.voice_type = voice_type
        self.language = language
        self.video_format = video_format
        self.effects_preset = effects_preset
        self.enable_effects = enable_effects
        self.image_preset = image_preset
        self.status = 'pending'
        self.progress = 0
        self.current_step = 'Iniciando...'
        self.error_message = None
        self.video_path = None
        self.created_at = datetime.now()
        
    def to_dict(self):
        return {
            'job_id': self.job_id,
            'status': self.status,
            'progress': self.progress,
            'current_step': self.current_step,
            'error_message': self.error_message,
            'video_path': self.video_path,
            'image_preset': self.image_preset,
            'created_at': self.created_at.isoformat()
        }

def update_job_progress(job_id, progress, step, status='running'):
    """Atualizar progresso do job"""
    logger = get_logger("job.progress")
    if job_id in jobs:
        jobs[job_id].progress = progress
        jobs[job_id].current_step = step
        jobs[job_id].status = status
        logger.info(f"Job progress updated: {step}", extra={'extra_data': {'job_id': job_id, 'progress': progress, 'status': status}})

def generate_video_async(job_id):
    """Função para gerar vídeo de forma assíncrona"""
    logger = get_logger("video.generation.async")
    
    # Set correlation ID for this job
    with ai_logger.correlation_context(job_id):
        try:
            job = jobs[job_id]
            logger.info(f"Starting async video generation for job {job_id}")
            
            # Verificar se GEMINI_API_KEY está configurada
            if not os.getenv('GEMINI_API_KEY'):
                job.status = 'error'
                job.error_message = 'GEMINI_API_KEY não configurada'
                logger.error("GEMINI_API_KEY not configured for job", extra={'extra_data': {'job_id': job_id}})
                return
            
            # Criar diretório de saída se não existir
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            # Importar módulos necessários
            import sys
            sys.path.append('.')
            from src.core.scriptgen import generate_script
            from src.utils.prompt import scene_prompts
            from src.core.imagegen import generate_images_from_prompts
            from src.core.voice import tts_scenes
            from src.core.subtitle import generate_subtitles
            from src.core.assemble import assemble_video
            import datetime
            import json
            
            # Atualizar progresso inicial
            update_job_progress(job_id, 5, 'Iniciando geração...')
            
            # Gerar ID único para o vídeo
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            # Limpar caracteres especiais do script para nome de diretório
            import re
            script_preview = re.sub(r'[^a-zA-Z0-9_]', '_', job.script.replace(' ', '_').replace('\n', '_').lower())[:20]
            video_id = f"{job.video_format}_{script_preview}_{timestamp}"
            video_output_dir = os.path.join("outputs", "videos", video_id)
            logger.info(f"Generated video ID: {video_id}", extra={'extra_data': {'video_id': video_id, 'output_dir': video_output_dir}})
            
            # Criar diretórios de saída
            os.makedirs(video_output_dir, exist_ok=True)
            os.makedirs(os.path.join(video_output_dir, "images"), exist_ok=True)
            os.makedirs(os.path.join(video_output_dir, "audio"), exist_ok=True)
            os.makedirs(os.path.join(video_output_dir, "subtitles"), exist_ok=True)
            logger.info("Output directories created successfully")
            
            # Passo 1: Processar script fornecido pelo usuário
            update_job_progress(job_id, 15, 'Processando script...')
            logger.info("Starting script processing step")
            
            # Importar parser de script personalizado
            from src.parsers.script_parser import parse_custom_script
            
            script_data = parse_custom_script(job.script)
            if not script_data:
                job.status = 'error'
                job.error_message = 'Falha no processamento do script fornecido'
                logger.error("Script processing failed", extra={'extra_data': {'job_id': job_id}})
                return
            
            logger.info("Script processed successfully")
            
            # Salvar script processado
            script_path = os.path.join(video_output_dir, "script.json")
            with open(script_path, "w", encoding="utf-8") as f:
                json.dump(script_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Script saved to: {script_path}")
            
            # Passo 2: Processar prompts de imagem fornecidos
            update_job_progress(job_id, 25, 'Processando prompts de imagem...')
            logger.info("Starting image prompts processing")
            
            # Importar parser de prompts de imagem
            from src.parsers.image_prompts_parser import parse_image_prompts
            
            prompts = parse_image_prompts(job.image_prompts)
            if not prompts:
                job.status = 'error'
                job.error_message = 'Falha no processamento dos prompts de imagem'
                logger.error("Image prompts processing failed", extra={'extra_data': {'job_id': job_id}})
                return
            
            logger.info(f"Image prompts processed successfully: {len(prompts)} prompts")
            
            # Passo 3: Gerar imagens
            update_job_progress(job_id, 40, 'Gerando imagens...')
            logger.info("Starting image generation")
            image_output_dir = os.path.join(video_output_dir, "images")
            image_paths = generate_images_from_prompts(prompts, image_output_dir, image_preset=getattr(job, 'image_preset', None))
            if not image_paths:
                job.status = 'error'
                job.error_message = 'Falha na geração de imagens'
                logger.error("Image generation failed", extra={'extra_data': {'job_id': job_id}})
                return
            
            logger.info(f"Images generated successfully: {len(image_paths)} images")
            
            # Passo 4: Gerar áudio
            update_job_progress(job_id, 60, 'Criando áudio...')
            logger.info("Starting audio generation", extra={'extra_data': {'voice_provider': job.voice_provider, 'voice_type': job.voice_type}})
            audio_output_dir = os.path.join(video_output_dir, "audio")
            audio_paths = tts_scenes(
                script_data, 
                audio_output_dir,
                provider=job.voice_provider,
                voice_type=job.voice_type,
                language=job.language
            )
            if not audio_paths:
                job.status = 'error'
                job.error_message = 'Falha na geração de áudio'
                logger.error("Audio generation failed", extra={'extra_data': {'job_id': job_id}})
                return
            
            logger.info(f"Audio generated successfully: {len(audio_paths)} files")
            
            # Passo 5: Gerar legendas usando roteiro (sem transcrição)
            update_job_progress(job_id, 75, 'Gerando legendas...')
            logger.info("Starting subtitle generation")
            subtitle_output_dir = os.path.join(video_output_dir, "subtitles")
            
            # Usar sincronização baseada no roteiro para maior precisão
            from src.core.subtitle import generate_subtitles_from_script_sync
            subtitle_path = generate_subtitles_from_script_sync(
                script_path, 
                audio_paths, 
                subtitle_output_dir, 
                style_name="modern"
            )
            
            if not subtitle_path:
                job.status = 'error'
                job.error_message = 'Falha na geração de legendas'
                logger.error("Subtitle generation failed", extra={'extra_data': {'job_id': job_id}})
                return
            
            logger.info(f"Subtitles generated successfully: {subtitle_path}")
            
            # Passo 6: Montar vídeo final com efeitos visuais
            update_job_progress(job_id, 90, 'Montando vídeo final com efeitos visuais...')
            logger.info("Starting video assembly", extra={'extra_data': {'effects_preset': job.effects_preset, 'enable_effects': job.enable_effects}})
            final_video_path = os.path.join(video_output_dir, f"{video_id}.mp4")
            video_path = assemble_video(
                image_paths, 
                audio_paths, 
                subtitle_path, 
                final_video_path, 
                subtitle_style="modern",
                effects_preset=job.effects_preset,
                enable_effects=job.enable_effects
            )
            
            if video_path and os.path.exists(video_path):
                job.video_path = video_path
                update_job_progress(job_id, 100, 'Vídeo gerado com sucesso!', 'completed')
                logger.info(f"Video generation completed successfully: {video_path}")
            else:
                job.status = 'error'
                job.error_message = 'Falha na montagem do vídeo final'
                logger.error("Video assembly failed")
                    
        except Exception as e:
            job.status = 'error'
            job.error_message = f'Erro inesperado: {str(e)}'
            logger.error(f"Unexpected error in video generation: {str(e)}", exc_info=True)

@app.route('/api/health', methods=['GET'])
@log_api_request
def health_check():
    """Endpoint de verificação de saúde da API (público)"""
    try:
        health_status = {
            'status': 'healthy',
            'message': 'AI Video GPT API está funcionando',
            'timestamp': datetime.now().isoformat(),
            'authentication_required': REQUIRE_API_KEY,
            'version': '1.0.0',
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'services': {
                'redis': {
                    'available': queue_manager.use_redis,
                    'status': 'connected' if queue_manager.use_redis else 'unavailable'
                },
                'queue': {
                    'length': queue_manager.get_queue_length() if queue_manager.use_redis else 0,
                    'failed_jobs': queue_manager.get_failed_job_count() if queue_manager.use_redis else 0
                }
            },
            'system': {
                'disk_space': get_disk_usage(),
                'memory_usage': get_memory_usage()
            }
        }
        
        # Verificar se há problemas críticos
        if not queue_manager.use_redis:
            health_status['status'] = 'degraded'
            health_status['warnings'] = ['Redis not available - using in-memory storage']
        
        # Verificar espaço em disco
        disk_usage = get_disk_usage()
        if disk_usage > 90:
            health_status['status'] = 'unhealthy'
            health_status['errors'] = health_status.get('errors', [])
            health_status['errors'].append(f'Low disk space: {disk_usage}% used')
        elif disk_usage > 80:
            health_status['status'] = 'degraded'
            health_status['warnings'] = health_status.get('warnings', [])
            health_status['warnings'].append(f'High disk usage: {disk_usage}% used')
        
        status_code = 200
        if health_status['status'] == 'degraded':
            status_code = 200  # Still OK but with warnings
        elif health_status['status'] == 'unhealthy':
            status_code = 503  # Service unavailable
        
        return jsonify(health_status), status_code
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 503

def get_disk_usage():
    """Obter uso do disco em porcentagem"""
    try:
        import shutil
        total, used, free = shutil.disk_usage('.')
        return round((used / total) * 100, 2)
    except:
        return 0

def get_memory_usage():
    """Obter uso de memória em porcentagem"""
    try:
        import psutil
        return psutil.virtual_memory().percent
    except ImportError:
        return 0
    except:
        return 0

@app.route('/api/generate-video', methods=['POST'])
# @limiter.limit("5 per minute")
@require_api_key
@log_api_request
def generate_video_endpoint():
    """Endpoint para iniciar geração de vídeo usando sistema de filas"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        if not data:
            raise ValidationAPIError("Request body is required")
            
        required_fields = ['script', 'image_prompts']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            raise ValidationAPIError(
                f"Missing required fields: {', '.join(missing_fields)}",
                field_errors={field: "This field is required" for field in missing_fields}
            )
        
        # Extrair e validar parâmetros
        script = data['script'].strip()
        image_prompts = data['image_prompts'].strip()
        
        if len(script) < 50:
            raise ValidationAPIError(
                "Script must have at least 50 characters",
                field_errors={"script": "Script is too short"}
            )
        
        if len(image_prompts) < 50:
            raise ValidationAPIError(
                "Image prompts must have at least 50 characters",
                field_errors={"image_prompts": "Image prompts are too short"}
            )
        
        voice_provider = data.get('voice_provider', 'auto')
        voice_type = data.get('voice_type', 'narrator')
        language = data.get('language', 'pt')
        video_format = data.get('video_format', 'standard')
        effects_preset = data.get('effects_preset', 'professional')
        enable_effects = data.get('enable_effects', True)
        image_preset = data.get('image_preset', None)
        
        # Validar parâmetros
        valid_providers = ['auto', 'elevenlabs', 'gtts']
        valid_types = ['narrator', 'male', 'female', 'child']
        valid_languages = ['pt', 'en', 'es', 'fr']
        valid_formats = ['standard', 'tiktok']
        valid_effects_presets = ['professional', 'cinematic', 'dynamic', 'subtle', 'none']
        valid_image_presets = ['3d_cartoon', 'realistic', 'anime', 'digital_art', None]
        
        if voice_provider not in valid_providers:
            raise ValidationAPIError(
                f"Invalid voice provider. Use: {', '.join(valid_providers)}",
                field_errors={"voice_provider": "Invalid voice provider"}
            )
        
        if voice_type not in valid_types:
            raise ValidationAPIError(
                f"Invalid voice type. Use: {', '.join(valid_types)}",
                field_errors={"voice_type": "Invalid voice type"}
            )
        
        if language not in valid_languages:
            raise ValidationAPIError(
                f"Invalid language. Use: {', '.join(valid_languages)}",
                field_errors={"language": "Invalid language"}
            )
        
        if video_format not in valid_formats:
            raise ValidationAPIError(
                f"Invalid video format. Use: {', '.join(valid_formats)}",
                field_errors={"video_format": "Invalid video format"}
            )
        
        if effects_preset not in valid_effects_presets:
            raise ValidationAPIError(
                f"Invalid effects preset. Use: {', '.join(valid_effects_presets)}",
                field_errors={"effects_preset": "Invalid effects preset"}
            )
        
        if image_preset not in valid_image_presets:
            raise ValidationAPIError(
                f"Invalid image preset. Use: {', '.join([p for p in valid_image_presets if p is not None])} or leave empty",
                field_errors={"image_preset": "Invalid image preset"}
            )
        
        # Verificar GEMINI API key
        if not os.getenv('GEMINI_API_KEY'):
            raise ServiceUnavailableError(
                "GEMINI_API_KEY not configured on server",
                service_name="gemini_api"
            )
        
        # Criar job usando o queue manager
        try:
            job_id = queue_manager.create_job(
                script=script,
                image_prompts=image_prompts,
                voice_provider=voice_provider,
                voice_type=voice_type,
                language=language,
                video_format=video_format,
                effects_preset=effects_preset,
                enable_effects=enable_effects,
                image_preset=image_preset
            )
        except Exception as e:
            raise ServiceUnavailableError(
                "Failed to create video generation job",
                service_name="queue_manager"
            )
        
        # Enfileirar job para processamento
        try:
            queue_manager.queue_job(job_id)
        except Exception as e:
            raise ServiceUnavailableError(
                "Failed to queue video generation job",
                service_name="job_queue"
            )
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Video generation job created and queued successfully',
            'status_url': f'/api/status/{job_id}',
            'queue_info': {
                'using_redis': queue_manager.use_redis,
                'queue_length': queue_manager.get_queue_length() if queue_manager.use_redis else None
            }
        }), 202
        
    except (ValidationAPIError, ServiceUnavailableError):
        # Re-raise API errors to be handled by error handler
        raise
    except Exception as e:
        # Convert unexpected errors to API errors
        raise APIError(
            message="An unexpected error occurred while creating video generation job",
            error_code=ErrorCode.INTERNAL_ERROR,
            status_code=500,
            details={"original_error": str(e)}
        )

@app.route('/api/status/<job_id>', methods=['GET'])
# @limiter.limit("30 per minute")
@require_api_key
@log_api_request
def get_job_status(job_id):
    """Endpoint para verificar status do job usando queue manager"""
    try:
        # Buscar job no queue manager
        job = queue_manager.get_job(job_id)
        
        if not job:
            raise NotFoundError(
                f"Job {job_id} not found",
                resource_type="video_job"
            )
        
        response = {
            'job_id': job_id,
            'status': job.status.value,
            'progress': job.progress,
            'current_step': job.current_step,
            'created_at': job.created_at.isoformat(),
            'updated_at': job.updated_at.isoformat() if job.updated_at else None,
            'queue_info': {
                'using_redis': queue_manager.use_redis,
                'position_in_queue': queue_manager.get_job_position(job_id) if queue_manager.use_redis else None
            }
        }
        
        if job.status.value == 'completed' and job.video_path:
            response['video_path'] = job.video_path
            response['download_url'] = f'/api/download/{job_id}'
        
        if job.status.value == 'failed' and job.error_message:
            response['error'] = job.error_message
        
        return jsonify(response)
        
    except NotFoundError:
        # Re-raise API errors to be handled by error handler
        raise
    except Exception as e:
        # Convert unexpected errors to API errors
        raise APIError(
            message="An unexpected error occurred while retrieving job status",
            error_code=ErrorCode.INTERNAL_ERROR,
            status_code=500,
            details={"job_id": job_id, "original_error": str(e)}
        )

@app.route('/api/download/<job_id>', methods=['GET'])
# @limiter.limit("10 per minute")
@require_api_key
@log_api_request
def download_video(job_id):
    """Endpoint para download do vídeo usando queue manager"""
    try:
        # Buscar job no queue manager
        job = queue_manager.get_job(job_id)
        
        if not job:
            raise NotFoundError(
                f"Job {job_id} not found",
                resource_type="video_job"
            )
        
        if job.status.value != 'completed':
            raise ProcessingError(
                f"Video is not ready yet. Current status: {job.status.value}",
                process_type="video_generation"
            )
        
        if not job.video_path:
            raise ProcessingError(
                "Video file path not available",
                process_type="video_generation"
            )
        
        if not os.path.exists(job.video_path):
            raise NotFoundError(
                "Video file not found on disk",
                resource_type="video_file"
            )
        
        # Enviar arquivo
        filename = f"ai_video_{job_id[:8]}.mp4"
        return send_file(
            job.video_path,
            as_attachment=True,
            download_name=filename,
            mimetype='video/mp4'
        )
        
    except (NotFoundError, ProcessingError):
        # Re-raise API errors to be handled by error handler
        raise
    except Exception as e:
        # Convert unexpected errors to API errors
        raise APIError(
            message="An unexpected error occurred while downloading video",
            error_code=ErrorCode.INTERNAL_ERROR,
            status_code=500,
            details={"job_id": job_id, "original_error": str(e)}
        )

@app.route('/api/preview/<job_id>', methods=['GET'])
@require_api_key
@log_api_request
def preview_video(job_id):
    """Endpoint para preview/streaming do vídeo gerado"""
    if job_id not in jobs:
        return jsonify({
            'error': 'Job não encontrado',
            'code': 'JOB_NOT_FOUND'
        }), 404
    
    job = jobs[job_id]
    
    if job.status != 'completed':
        return jsonify({
            'error': 'Vídeo ainda não foi gerado',
            'code': 'VIDEO_NOT_READY'
        }), 400
    
    if not job.video_path or not os.path.exists(job.video_path):
        return jsonify({
            'error': 'Arquivo de vídeo não encontrado',
            'code': 'VIDEO_FILE_NOT_FOUND'
        }), 404
    
    # Enviar arquivo para preview (streaming)
    return send_file(
        job.video_path,
        mimetype='video/mp4',
        as_attachment=False
    )

@app.route('/api/jobs', methods=['GET'])
# @limiter.limit("10 per minute")
@require_api_key
@log_api_request
def list_jobs():
    """Endpoint para listar todos os jobs usando queue manager"""
    try:
        # Obter parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)  # Máximo 100 por página
        status_filter = request.args.get('status')
        
        # Buscar jobs no queue manager
        all_jobs = queue_manager.list_jobs()
        
        # Filtrar por status se especificado
        if status_filter:
            all_jobs = [job for job in all_jobs if job.status.value == status_filter]
        
        # Ordenar por data de criação (mais recentes primeiro)
        all_jobs.sort(key=lambda x: x.created_at, reverse=True)
        
        # Aplicar paginação
        total = len(all_jobs)
        start = (page - 1) * per_page
        end = start + per_page
        jobs_page = all_jobs[start:end]
        
        # Converter jobs para formato de resposta
        jobs_list = []
        for job in jobs_page:
            job_info = {
                'job_id': job.job_id,
                'status': job.status.value,
                'progress': job.progress,
                'current_step': job.current_step,
                'created_at': job.created_at.isoformat(),
                'updated_at': job.updated_at.isoformat() if job.updated_at else None,
                'script_preview': job.script[:100] + '...' if len(job.script) > 100 else job.script
            }
            
            if job.status.value == 'completed' and job.video_path:
                job_info['download_url'] = f'/api/download/{job.job_id}'
            
            if job.status.value == 'failed' and job.error:
                job_info['error'] = job.error
            
            jobs_list.append(job_info)
        
        return jsonify({
            'jobs': jobs_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            },
            'queue_info': {
                'using_redis': queue_manager.use_redis,
                'queue_length': queue_manager.get_queue_length() if queue_manager.use_redis else None
            }
        })
        
    except Exception as e:
        # Convert unexpected errors to API errors
        raise APIError(
            message="An unexpected error occurred while listing jobs",
            error_code=ErrorCode.INTERNAL_ERROR,
            status_code=500,
            details={"original_error": str(e)}
        )

@app.route('/api/image-presets', methods=['GET'])
@require_api_key
@log_api_request
def get_image_presets():
    """Obter lista de presets de imagem disponíveis."""
    try:
        from src.parsers.image_prompts_parser import load_image_presets_config
        
        config = load_image_presets_config()
        presets = {}
        
        for preset_key, preset_data in config.get('image_presets', {}).items():
            presets[preset_key] = {
                'name': preset_data.get('name', preset_key),
                'description': preset_data.get('description', '')
            }
        
        return jsonify({
            'success': True,
            'presets': presets
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/auth/validate', methods=['GET', 'POST'])
@require_api_key
@log_api_request
def validate_api_key():
    """Endpoint para validar API key"""
    return jsonify({
        'valid': True,
        'message': 'API key válida',
        'authenticated': True
    })

@app.route('/api/auth/info', methods=['GET'])
@log_api_request
def auth_info():
    """Endpoint público para obter informações sobre autenticação"""
    return jsonify({
        'authentication_required': REQUIRE_API_KEY,
        'api_key_methods': [
            'Header: X-API-Key',
            'Query parameter: api_key',
            'Request body: api_key'
        ],
        'message': 'AI Video GPT API - Autenticação via API Key' if REQUIRE_API_KEY else 'AI Video GPT API - Autenticação desabilitada'
    })

# ===== ROTAS PARA SERVIR O FRONTEND =====

@app.route('/')
def serve_frontend():
    """Servir o frontend principal"""
    return send_from_directory('../src/frontend', 'index.html')

@app.route('/test')
def serve_test():
    """Servir página de teste"""
    return send_from_directory('../src/frontend', 'test.html')

@app.route('/frontend/<path:filename>')
def serve_static(filename):
    """Servir arquivos estáticos do frontend"""
    return send_from_directory('../src/frontend', filename)

if __name__ == '__main__':
    # Setup logging for the Flask app
    setup_logging(log_dir="logs", environment="production", log_level="INFO")
    logger = get_logger("app.main")
    
    # Criar diretório de outputs se não existir
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    logger.info("🚀 Iniciando AI Video GPT API...")
    logger.info(f"📁 Diretório de saída: {os.path.abspath(UPLOAD_FOLDER)}")
    logger.info("🌐 API disponível em: http://localhost:5000")
    logger.info("")
    logger.info("🔒 CONFIGURAÇÕES DE SEGURANÇA:")
    if REQUIRE_API_KEY:
        logger.info(f"   ✅ Autenticação HABILITADA")
        logger.info(f"   🔑 API Key: {API_KEY[:12]}...{API_KEY[-4:] if len(API_KEY) > 16 else API_KEY}")
        logger.info("   📝 Métodos de autenticação:")
        logger.info("      - Header: X-API-Key")
        logger.info("      - Query param: ?api_key=...")
        logger.info("      - Request body: {'api_key': '...'}")
    else:
        logger.warning("   ⚠️  Autenticação DESABILITADA (desenvolvimento)")
        logger.info("   📝 Para habilitar: export REQUIRE_API_KEY=true")
    logger.info("")
    logger.info("📋 ENDPOINTS DISPONÍVEIS:")
    logger.info("   GET  /api/health - Verificação de saúde avançada (público)")
    logger.info("   GET  /api/auth/info - Informações de autenticação (público)")
    logger.info("   POST /api/auth/validate - Validar API key (🔒 protegido)")
    logger.info("   POST /api/generate-video - Gerar vídeo (🔒 protegido)")
    logger.info("   GET  /api/status/<job_id> - Status do job (🔒 protegido)")
    logger.info("   GET  /api/download/<job_id> - Download do vídeo (🔒 protegido)")
    logger.info("   GET  /api/preview/<job_id> - Preview do vídeo (🔒 protegido)")
    logger.info("   GET  /api/jobs - Listar todos os jobs (🔒 protegido)")
    logger.info("   GET  /api/image-presets - Presets de imagem (🔒 protegido)")
    logger.info("")
    
    app.run(debug=True, host='0.0.0.0', port=5000)