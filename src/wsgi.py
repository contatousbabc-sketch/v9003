#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - WSGI Entry Point
Ponto de entrada para servidores WSGI de produção (Gunicorn, uWSGI, etc)
"""

import os
import sys
import logging
from pathlib import Path

# Configurar path do projeto
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configurar logging para produção
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/production.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def create_production_app():
    """Cria aplicação Flask otimizada para produção"""
    
    try:
        # Importar função de criação da app
        from run import create_app
        
        # Criar aplicação
        app = create_app()
        
        # Configurações específicas de produção
        app.config.update({
            'DEBUG': False,
            'TESTING': False,
            'ENV': 'production',
            'SECRET_KEY': os.getenv('SECRET_KEY', 'arqv18-enhanced-production-key'),
            'JSON_SORT_KEYS': False,
            'JSONIFY_PRETTYPRINT_REGULAR': False,
            'MAX_CONTENT_LENGTH': 100 * 1024 * 1024,  # 100MB max upload
        })
        
        logger.info("✅ Aplicação Flask configurada para produção")
        return app
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar aplicação de produção: {e}")
        raise

# Criar aplicação para WSGI
application = create_production_app()

# Alias para compatibilidade
app = application

if __name__ == "__main__":
    # Para testes locais
    application.run(host='0.0.0.0', port=12000, debug=False)