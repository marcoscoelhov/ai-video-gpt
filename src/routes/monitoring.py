from flask import Blueprint, render_template, jsonify, request
from src.utils.monitoring import metrics_collector
from src.utils.cache import cache_manager
import logging

logger = logging.getLogger(__name__)

# Blueprint para rotas de monitoramento
monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/monitoring')


@monitoring_bp.route('/')
def dashboard():
    """Página principal do dashboard de monitoramento"""
    return render_template('monitoring/dashboard.html')


@monitoring_bp.route('/api/health')
def health_check():
    """Endpoint para verificação de saúde do sistema"""
    try:
        health_data = metrics_collector.get_system_health()
        return jsonify({
            'status': 'success',
            'data': health_data
        })
    except Exception as e:
        logger.error(f"Erro ao obter dados de saúde: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@monitoring_bp.route('/api/metrics')
def get_metrics():
    """Endpoint para obter métricas do sistema"""
    try:
        hours = request.args.get('hours', 1, type=int)
        
        # Obter métricas do sistema
        system_metrics = metrics_collector.get_system_metrics_history(hours)
        
        # Obter estatísticas de API
        api_stats = metrics_collector.get_api_statistics(hours)
        
        # Obter tendências de performance
        performance_trends = metrics_collector.get_performance_trends(hours)
        
        return jsonify({
            'status': 'success',
            'data': {
                'system_metrics': system_metrics,
                'api_statistics': api_stats,
                'performance_trends': performance_trends
            }
        })
    except Exception as e:
        logger.error(f"Erro ao obter métricas: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@monitoring_bp.route('/api/cache-stats')
def get_cache_stats():
    """Endpoint para obter estatísticas do cache"""
    try:
        cache_stats = cache_manager.get_stats()
        return jsonify({
            'status': 'success',
            'data': cache_stats
        })
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do cache: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@monitoring_bp.route('/api/clear-cache', methods=['POST'])
def clear_cache():
    """Endpoint para limpar o cache"""
    try:
        cache_manager.clear()
        return jsonify({
            'status': 'success',
            'message': 'Cache limpo com sucesso'
        })
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@monitoring_bp.route('/api/system-info')
def get_system_info():
    """Endpoint para obter informações do sistema"""
    try:
        import platform
        import psutil
        from datetime import datetime
        
        # Informações básicas do sistema
        system_info = {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'disk_total_gb': round(psutil.disk_usage('/').total / (1024**3), 2),
            'uptime': str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())),
            'process_count': len(psutil.pids())
        }
        
        return jsonify({
            'status': 'success',
            'data': system_info
        })
    except Exception as e:
        logger.error(f"Erro ao obter informações do sistema: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@monitoring_bp.route('/api/alerts')
def get_alerts():
    """Endpoint para obter alertas do sistema"""
    try:
        alerts = []
        health_data = metrics_collector.get_system_health()
        
        # Verificar alertas baseados na saúde do sistema
        if health_data.get('cpu_percent', 0) > 80:
            alerts.append({
                'type': 'warning',
                'message': f"Alto uso de CPU: {health_data['cpu_percent']:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
        
        if health_data.get('memory_percent', 0) > 85:
            alerts.append({
                'type': 'warning',
                'message': f"Alto uso de memória: {health_data['memory_percent']:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
        
        if health_data.get('disk_percent', 0) > 90:
            alerts.append({
                'type': 'critical',
                'message': f"Espaço em disco baixo: {health_data['disk_percent']:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
        
        # Verificar alertas de API
        api_stats = metrics_collector.get_api_statistics(1)
        if api_stats.get('error_rate', 0) > 10:
            alerts.append({
                'type': 'warning',
                'message': f"Alta taxa de erro na API: {api_stats['error_rate']:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
        
        return jsonify({
            'status': 'success',
            'data': alerts
        })
    except Exception as e:
        logger.error(f"Erro ao obter alertas: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500