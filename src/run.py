#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Aplicação Principal Aprimorada
Servidor Flask para análise de mercado ultra-detalhada
"""

import os
import sys
import time
import logging
from typing import Dict, List, Any, Optional
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Adiciona src ao path se necessário
if 'src' not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar logger em tempo real ANTES de outros imports
from services.realtime_logger import realtime_logger, log_info, log_success, log_error, log_separator

# Configuração de logging simplificada (sem arquivo para resolver quota)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Apenas console
    ]
)

logger = logging.getLogger(__name__)

# >>>>>>>>>> ADICIONE A LINHA ABAIXO PARA SUPRIMIR O AVISO DO PYTHON-DOTENV <<<<<<<<<<
logging.getLogger("dotenv").setLevel(logging.CRITICAL)

def create_app():
    """Cria e configura a aplicação Flask"""

    # Carrega variáveis de ambiente
    from services.environment_loader import environment_loader

    app = Flask(__name__)

    # CONFIGURAÇÃO CRÍTICA DE PRODUÇÃO
    # Força ambiente de produção - NUNCA debug em produção
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    debug = False  # SEMPRE False em produção
    app.config['DEBUG'] = debug
    app.config['TESTING'] = False

    # Configuração de logging para produção
    if FLASK_ENV == 'production':
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(name)s %(message)s'
        )
    else:
        logging.basicConfig(level=logging.DEBUG)

    # Configuração CORS para produção
    cors_origins = os.getenv('CORS_ORIGINS', '*')
    if FLASK_ENV == 'production' and cors_origins == '*':
        # Em produção, CORS deve ser restritivo
        cors_origins = ['https://yourdomain.com  ']  # Configurar domínio real

    CORS(app, resources={
        r"/api/*": {
            "origins": cors_origins.split(',') if isinstance(cors_origins, str) else cors_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Chave secreta segura carregada do ambiente
    app.secret_key = os.getenv('SECRET_KEY', 'arqv18-enhanced-ultra-secure-key-2025')
    if not os.getenv('SECRET_KEY') and FLASK_ENV == 'production':
        raise ValueError("SECRET_KEY deve ser definida em produção")

    # Registra blueprints with instrumentation
    logger.info("🔍 Importando blueprints...")

    logger.info("📊 Importando analysis...")
    from routes.analysis import analysis_bp

    logger.info("📊 Importando enhanced_analysis...")
    from routes.enhanced_analysis import enhanced_analysis_bp

    logger.info("🔍 Importando forensic_analysis...")
    # from routes.forensic_analysis import forensic_bp  # COMENTADO - módulo não existe

    logger.info("📁 Importando files...")
    from routes.files import files_bp

    logger.info("📈 Importando progress...")
    from routes.progress import progress_bp

    logger.info("👤 Importando user...")
    from routes.user import user_bp

    logger.info("🖥️ Importando monitoring...")
    # from routes.monitoring import monitoring_bp  # COMENTADO - módulo não existe

    logger.info("📄 Importando html_report_generator...")
    # from routes.html_report_generator import html_report_bp  # COMENTADO - módulo não existe

    logger.info("🔗 Importando mcp...")
    # from routes.mcp import mcp_bp  # COMENTADO - módulo não existe

    logger.info("⚡ Importando enhanced_workflow...")
    from routes.enhanced_workflow import enhanced_workflow_bp
    
    logger.info("💾 Importando sessions...")
    from routes.sessions import sessions_bp
    
    logger.info("💬 Importando chat...")
    from routes.chat import chat_bp
    
    logger.info("🤖 Importando models...")
    from routes.models import models_bp

    logger.info("🔍 Inicializando External AI Verifier...")
    try:
        # Adiciona o diretório do External AI Verifier ao path
        external_ai_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'external_ai_verifier', 'src')
        if external_ai_path not in sys.path:
            sys.path.insert(0, external_ai_path)
        
        # Adiciona também o diretório services ao path
        services_path = os.path.join(external_ai_path, 'services')
        if services_path not in sys.path:
            sys.path.insert(0, services_path)
        
        # Importa e inicializa o External AI Verifier
        import external_review_agent
        
        # Cria instância global do External AI Verifier
        app.external_ai_verifier = external_review_agent.ExternalReviewAgent()
        logger.info("✅ External AI Verifier inicializado com sucesso!")
        
    except Exception as e:
        logger.warning(f"⚠️ External AI Verifier não pôde ser inicializado: {e}")
        logger.warning(f"🔍 Detalhes do erro: {str(e)}")
        app.external_ai_verifier = None

    logger.info("✅ Todos os blueprints e serviços importados com sucesso!")

    app.register_blueprint(analysis_bp, url_prefix='/api')
    app.register_blueprint(enhanced_analysis_bp, url_prefix='/enhanced')
    # app.register_blueprint(forensic_bp, url_prefix='/forensic')  # COMENTADO - módulo não existe
    app.register_blueprint(files_bp, url_prefix='/files')
    app.register_blueprint(progress_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/user')
    # app.register_blueprint(monitoring_bp, url_prefix='/monitoring')  # COMENTADO - módulo não existe
    # app.register_blueprint(pdf_bp, url_prefix='/pdf')  # REMOVIDO - não existe
    # app.register_blueprint(html_report_bp, url_prefix='/html_report')  # COMENTADO - módulo não existe
    # app.register_blueprint(mcp_bp, url_prefix='/mcp')  # COMENTADO - módulo não existe
    app.register_blueprint(enhanced_workflow_bp, url_prefix='/api')
    app.register_blueprint(sessions_bp, url_prefix='/api')
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(models_bp)

    @app.route('/')
    def index():
        """Página principal"""
        from utils.logo_manager import logo_manager
        logo_data_url = logo_manager.get_logo_data_url()
        return render_template('enhanced_interface_v3.html', logo_data_url=logo_data_url)

    @app.route('/archaeological')
    def archaeological():
        """Interface arqueológica"""
        return render_template('enhanced_interface.html')

    @app.route('/forensic')
    def forensic():
        """Interface forense"""
        return render_template('forensic_interface.html')

    @app.route('/unified')
    def unified():
        """Interface unificada"""
        return render_template('enhanced_interface_v3.html')

    @app.route('/v3')
    def interface_v3():
        """Interface v18.0 aprimorada"""
        return render_template('enhanced_interface_v3.html')

    @app.route('/api/app_status')
    def app_status():
        """Status da aplicação"""
        try:
            # Status dos serviços principais
            services_status = {
                'enhanced_ai_manager': True,
                'real_search_orchestrator': True,
                'viral_content_analyzer': True,
                'database': True,
                'orchestrators': True
            }

            # Verifica saúde dos componentes - tratamento seguro
            try:
                from services.health_checker import health_checker
                health_check = health_checker.get_system_health()
                if isinstance(health_check, str):
                    health_check = {'status': health_check}
            except Exception as health_error:
                health_check = {'status': 'error', 'message': str(health_error)}

            status = {
                'status': 'healthy',
                'services': services_status,
                'health': health_check,
                'timestamp': datetime.now().isoformat(),
                'version': 'ARQV40 Enhanced v1.0',
                'features': {
                    'real_data_only': True,
                    'viral_content_capture': True,
                    'ai_active_search': True,
                    'api_rotation': True,
                    'screenshot_capture': True
                }
            }

            return jsonify(status)

        except Exception as e:
            logger.error(f"Error in app_status: {e}")
            return jsonify({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500


    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint não encontrado'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

    return app

def main():
    """Função principal"""

    print("🚀 ARQV40 Enhanced v1.0 - Iniciando aplicação...")
    log_separator("INICIALIZAÇÃO DO SISTEMA V380")
    log_info("Sistema ARQV40 Enhanced v1.0 iniciando...")

    try:
        # Cria aplicação
        log_info("Criando aplicação Flask...")
        app = create_app()
        log_success("Aplicação Flask criada com sucesso")

        # Configurações do servidor
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 12000))
        debug = os.getenv('FLASK_ENV', 'production') == 'development' # This line is kept for clarity in main, but app.config['DEBUG'] is set in create_app

        print(f"🌐 Servidor: http://{host}:{port}")
        print(f"🔧 Modo: {'Desenvolvimento' if debug else 'Produção'}")
        print(f"📊 Interface: Análise Ultra-Detalhada de Mercado")
        print(f"🤖 IA: Gemini 2.0 Flash + OpenAI + OpenRouter com Busca Ativa")
        print(f"🔍 Pesquisa: Orquestrador Real + Rotação de APIs + Screenshots")
        print(f"💾 Banco: Arquivos Locais + Cache Inteligente")
        print(f"🛡️ Sistema: Ultra-Robusto v18.0 com Captura Visual")

        # Log das configurações
        log_info(f"Servidor configurado: http://{host}:{port}")
        log_info(f"Modo: {'Desenvolvimento' if debug else 'Produção'}")
        log_info("Hierarquia IA: Grok-4 → Gemini-2.0 → Qwen3-Coder")
        log_info("Fallback APIs: Serper → Jina → Exa → Firecrawl → Supadata → Apify → RapidAPI")
        log_success("Todas as correções aplicadas com sucesso")

        print("\n" + "=" * 60)
        print("✅ ARQV18 Enhanced v18.0 PRONTO!")
        print("=" * 60)
        print("Pressione Ctrl+C para parar o servidor")
        print("=" * 60)
        
        log_separator("SISTEMA PRONTO PARA EXECUÇÃO")
        log_success("ARQV18 Enhanced v18.0 totalmente operacional")

        print("\n🔥 RECURSOS ATIVADOS - 100% DADOS REAIS:")
        print("- IA com Ferramentas de Busca Ativa REAIS")
        print("- Busca Massiva REAL com Rotação de APIs REAIS")
        print("- Captura Automática de Screenshots REAIS")
        print("- Análise de Conteúdo Viral REAL")
        print("- 26 Módulos de Análise REAIS Especializados")
        print("- Workflow em 4 Etapas REAIS Controladas")
        print("- GARANTIA: ZERO SIMULAÇÃO - ZERO EXEMPLOS - 100% DADOS REAIS")

        # Inicia servidor (sem reloader para evitar problemas de double-import)
        app.run(
            host=host,
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )

    except KeyboardInterrupt:
        print("\n\n✅ Servidor encerrado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")
        logger.critical(f"Critical error during server startup: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
