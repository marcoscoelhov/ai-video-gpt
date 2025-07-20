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
from flask import Flask, request, jsonify, send_file, send_from_directory, render_template_string
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Carregar variáveis de ambiente do arquivo .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv não instalado. Usando variáveis de ambiente do sistema.")

# Importar módulos do projeto (comentado temporariamente para teste)
# from main import main as generate_video_main
# from examples.basic.generate_tiktok_video import generate_tiktok_video

app = Flask(__name__)
CORS(app)  # Permitir requisições do frontend

# Configurações
UPLOAD_FOLDER = 'outputs'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Armazenamento em memória para jobs (em produção, usar Redis ou banco de dados)
jobs = {}
video_results = {}

class VideoGenerationJob:
    """Classe para gerenciar jobs de geração de vídeo"""
    
    def __init__(self, job_id, script, image_prompts, voice_provider='auto', voice_type='narrator', 
                 language='pt', video_format='standard'):
        self.job_id = job_id
        self.script = script
        self.image_prompts = image_prompts
        self.voice_provider = voice_provider
        self.voice_type = voice_type
        self.language = language
        self.video_format = video_format
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
            'created_at': self.created_at.isoformat()
        }

def update_job_progress(job_id, progress, step, status='running'):
    """Atualizar progresso do job"""
    if job_id in jobs:
        jobs[job_id].progress = progress
        jobs[job_id].current_step = step
        jobs[job_id].status = status

def generate_video_async(job_id):
    """Função para gerar vídeo de forma assíncrona"""
    try:
        job = jobs[job_id]
        
        # Verificar se GEMINI_API_KEY está configurada
        if not os.getenv('GEMINI_API_KEY'):
            job.status = 'error'
            job.error_message = 'GEMINI_API_KEY não configurada'
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
        
        # Criar diretórios de saída
        os.makedirs(video_output_dir, exist_ok=True)
        os.makedirs(os.path.join(video_output_dir, "images"), exist_ok=True)
        os.makedirs(os.path.join(video_output_dir, "audio"), exist_ok=True)
        os.makedirs(os.path.join(video_output_dir, "subtitles"), exist_ok=True)
        
        # Passo 1: Processar script fornecido pelo usuário
        update_job_progress(job_id, 15, 'Processando script...')
        
        # Importar parser de script personalizado
        from src.parsers.script_parser import parse_custom_script
        
        script_data = parse_custom_script(job.script)
        if not script_data:
            job.status = 'error'
            job.error_message = 'Falha no processamento do script fornecido'
            return
        
        # Salvar script processado
        script_path = os.path.join(video_output_dir, "script.json")
        with open(script_path, "w", encoding="utf-8") as f:
            json.dump(script_data, f, indent=2, ensure_ascii=False)
        
        # Passo 2: Processar prompts de imagem fornecidos
        update_job_progress(job_id, 25, 'Processando prompts de imagem...')
        
        # Importar parser de prompts de imagem
        from src.parsers.image_prompts_parser import parse_image_prompts
        
        prompts = parse_image_prompts(job.image_prompts)
        if not prompts:
            job.status = 'error'
            job.error_message = 'Falha no processamento dos prompts de imagem'
            return
        
        # Passo 3: Gerar imagens
        update_job_progress(job_id, 40, 'Gerando imagens...')
        image_output_dir = os.path.join(video_output_dir, "images")
        image_paths = generate_images_from_prompts(prompts, image_output_dir)
        if not image_paths:
            job.status = 'error'
            job.error_message = 'Falha na geração de imagens'
            return
        
        # Passo 4: Gerar áudio
        update_job_progress(job_id, 60, 'Criando áudio...')
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
            return
        
        # Passo 5: Gerar legendas usando roteiro (sem transcrição)
        update_job_progress(job_id, 75, 'Gerando legendas...')
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
            return
        
        # Passo 6: Montar vídeo final
        update_job_progress(job_id, 90, 'Montando vídeo final...')
        final_video_path = os.path.join(video_output_dir, f"{video_id}.mp4")
        video_path = assemble_video(image_paths, audio_paths, subtitle_path, final_video_path, subtitle_style="modern")
        
        if video_path and os.path.exists(video_path):
            job.video_path = video_path
            update_job_progress(job_id, 100, 'Vídeo gerado com sucesso!', 'completed')
        else:
            job.status = 'error'
            job.error_message = 'Falha na montagem do vídeo final'
                
    except Exception as e:
        job.status = 'error'
        job.error_message = f'Erro inesperado: {str(e)}'
        import traceback
        print(f"Erro detalhado: {traceback.format_exc()}")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde da API"""
    return jsonify({
        'status': 'healthy',
        'message': 'AI Video GPT API está funcionando',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/generate-video', methods=['POST'])
def generate_video_endpoint():
    """Endpoint para iniciar geração de vídeo"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['script', 'image_prompts']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'error': f'Campo obrigatório ausente: {field}',
                    'code': f'MISSING_{field.upper()}'
                }), 400
        
        # Extrair e validar parâmetros
        script = data['script'].strip()
        image_prompts = data['image_prompts'].strip()
        
        if len(script) < 50:
            return jsonify({
                'error': 'Script deve ter pelo menos 50 caracteres',
                'code': 'SCRIPT_TOO_SHORT'
            }), 400
        
        if len(image_prompts) < 50:
            return jsonify({
                'error': 'Prompts de imagem devem ter pelo menos 50 caracteres',
                'code': 'IMAGE_PROMPTS_TOO_SHORT'
            }), 400
        
        voice_provider = data.get('voice_provider', 'auto')
        voice_type = data.get('voice_type', 'narrator')
        language = data.get('language', 'pt')
        video_format = data.get('video_format', 'standard')
        
        # Validar parâmetros
        valid_providers = ['auto', 'elevenlabs', 'gtts']
        valid_types = ['narrator', 'male', 'female', 'child']
        valid_languages = ['pt', 'en', 'es', 'fr']
        valid_formats = ['standard', 'tiktok']
        
        if voice_provider not in valid_providers:
            return jsonify({
                'error': f'Provedor de voz inválido. Use: {", ".join(valid_providers)}',
                'code': 'INVALID_VOICE_PROVIDER'
            }), 400
        
        if voice_type not in valid_types:
            return jsonify({
                'error': f'Tipo de voz inválido. Use: {", ".join(valid_types)}',
                'code': 'INVALID_VOICE_TYPE'
            }), 400
        
        if language not in valid_languages:
            return jsonify({
                'error': f'Idioma inválido. Use: {", ".join(valid_languages)}',
                'code': 'INVALID_LANGUAGE'
            }), 400
        
        if video_format not in valid_formats:
            return jsonify({
                'error': f'Formato de vídeo inválido. Use: {", ".join(valid_formats)}',
                'code': 'INVALID_FORMAT'
            }), 400
        
        # Verificar API key
        if not os.getenv('GEMINI_API_KEY'):
            return jsonify({
                'error': 'GEMINI_API_KEY não configurada no servidor',
                'code': 'MISSING_API_KEY'
            }), 500
        
        # Criar job único
        job_id = str(uuid.uuid4())
        job = VideoGenerationJob(
            job_id=job_id,
            script=script,
            image_prompts=image_prompts,
            voice_provider=voice_provider,
            voice_type=voice_type,
            language=language,
            video_format=video_format
        )
        
        jobs[job_id] = job
        
        # Iniciar geração em thread separada
        thread = threading.Thread(target=generate_video_async, args=(job_id,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'job_id': job_id,
            'message': 'Geração de vídeo iniciada',
            'status': 'pending'
        }), 202
        
    except Exception as e:
        return jsonify({
            'error': f'Erro interno do servidor: {str(e)}',
            'code': 'INTERNAL_ERROR'
        }), 500

@app.route('/api/status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Endpoint para verificar status do job"""
    if job_id not in jobs:
        return jsonify({
            'error': 'Job não encontrado',
            'code': 'JOB_NOT_FOUND'
        }), 404
    
    job = jobs[job_id]
    return jsonify(job.to_dict())

@app.route('/api/download/<job_id>', methods=['GET'])
def download_video(job_id):
    """Endpoint para download do vídeo gerado"""
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
    
    # Enviar arquivo
    filename = f"ai_video_{job_id[:8]}.mp4"
    return send_file(
        job.video_path,
        as_attachment=True,
        download_name=filename,
        mimetype='video/mp4'
    )

@app.route('/api/preview/<job_id>', methods=['GET'])
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
def list_jobs():
    """Endpoint para listar todos os jobs (para debug)"""
    return jsonify({
        'jobs': [job.to_dict() for job in jobs.values()],
        'total': len(jobs)
    })

# ===== ROTAS PARA SERVIR O FRONTEND =====

@app.route('/')
def serve_frontend():
    """Servir o frontend principal"""
    return send_from_directory('src/frontend', 'index.html')

@app.route('/test')
def serve_test():
    """Servir página de teste"""
    return send_from_directory('src/frontend', 'test.html')

@app.route('/frontend/<path:filename>')
def serve_static(filename):
    """Servir arquivos estáticos do frontend"""
    return send_from_directory('src/frontend', filename)

if __name__ == '__main__':
    # Criar diretório de outputs se não existir
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    print("🚀 Iniciando AI Video GPT API...")
    print(f"📁 Diretório de saída: {os.path.abspath(UPLOAD_FOLDER)}")
    print("🌐 API disponível em: http://localhost:5000")
    print("📋 Endpoints disponíveis:")
    print("   GET  /api/health - Verificação de saúde")
    print("   POST /api/generate-video - Gerar vídeo")
    print("   GET  /api/status/<job_id> - Status do job")
    print("   GET  /api/download/<job_id> - Download do vídeo")
    print("   GET  /api/jobs - Listar todos os jobs")
    
    app.run(debug=True, host='0.0.0.0', port=5000)