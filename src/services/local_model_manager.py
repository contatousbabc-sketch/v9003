#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.2 - Local Model Manager UNIVERSAL
Gerenciador INTELIGENTE para trabalhar com TODOS os 28 módulos do sistema
Gera relatórios COMPLETOS adaptando-se automaticamente ao contexto
"""

import os
import logging
import json
import time
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)

class LocalModelManager:
    """Gerenciador UNIVERSAL de modelos locais para inferência de IA"""
    
    def __init__(self):
        """Inicializa o gerenciador universal de modelos locais"""
        self.project_root = Path(__file__).parent.parent.parent
        
        # Verifica múltiplos diretórios possíveis para modelos
        possible_model_dirs = [
            self.project_root / "src" / "model",
            self.project_root / "model", 
            self.project_root / "models",
            Path.home() / ".cache" / "huggingface" / "transformers"
        ]
        
        self.model_dir = None
        for model_dir in possible_model_dirs:
            try:
                model_dir.mkdir(parents=True, exist_ok=True)
                if self.model_dir is None:
                    self.model_dir = model_dir
                
                model_files = list(model_dir.glob("*.gguf")) + list(model_dir.glob("*.safetensors")) + list(model_dir.glob("*.bin"))
                if model_files:
                    self.model_dir = model_dir
                    logger.info(f"📁 Modelos encontrados em: {model_dir}")
                    break
            except Exception as e:
                logger.warning(f"⚠️ Não foi possível criar diretório {model_dir}: {e}")
                continue
        
        if self.model_dir is None:
            self.model_dir = self.project_root / "src" / "model"
            self.model_dir.mkdir(exist_ok=True)
            
        logger.info(f"📁 Diretório de modelos: {self.model_dir}")
        
        # Backends disponíveis
        self.backends = {
            'llama_cpp': None,
            'transformers': None,
            'ctransformers': None
        }
        
        # Modelo carregado atualmente
        self.current_model = None
        self.current_backend = None
        self.model_info = {}
        
        # ⚡ CONFIGURAÇÕES UNIVERSAIS OTIMIZADAS
        self.default_config = {
            'max_tokens': 16384,  # Tokens para relatórios longos
            'temperature': 0.75,
            'top_p': 0.92,
            'top_k': 45,
            'repeat_penalty': 1.18,
            'context_length': 16384,
            'n_threads': os.cpu_count() or 4,
            'n_gpu_layers': -1,
            'min_length': 500,
            'length_penalty': 1.2,
        }
        
        # 📚 TEMPLATES UNIVERSAIS POR TIPO DE ANÁLISE
        self.analysis_templates = {
            # ANÁLISES DE MERCADO E PÚBLICO
            'market_analysis': {
                'system_prompt': """Você é um analista de mercado especializado em análises profundas e detalhadas.
                
INSTRUÇÕES CRÍTICAS:
- Gere análises COMPLETAS com NO MÍNIMO 1200 palavras
- Use dados concretos e estatísticas quando disponíveis
- Organize em seções claras: Visão Geral, Análise Detalhada, Tendências, Oportunidades, Riscos, Recomendações
- Desenvolva cada ponto com profundidade
- Inclua insights acionáveis
- NUNCA termine abruptamente - sempre conclua com síntese estratégica

FORMATO OBRIGATÓRIO:
1. Executive Summary (3-4 parágrafos)
2. Análise de Mercado Detalhada (múltiplas seções)
3. Segmentação e Personas
4. Análise Competitiva
5. Oportunidades e Gaps
6. Riscos e Desafios
7. Estratégias Recomendadas
8. Conclusão e Próximos Passos""",
                'min_words': 1200,
                'sections': ['executive_summary', 'analise_mercado', 'segmentacao', 'competicao', 'oportunidades', 'riscos', 'estrategias', 'conclusao']
            },
            
            # PERFIS E AVATARES
            'persona_generation': {
                'system_prompt': """Você é um especialista em psicologia do consumidor e criação de personas detalhadas.

INSTRUÇÕES CRÍTICAS:
- Crie perfis COMPLETOS e REALISTAS com NO MÍNIMO 1000 palavras
- Base-se EXCLUSIVAMENTE nos dados fornecidos
- Desenvolva perfil demográfico, psicológico, comportamental e digital
- Inclua histórias pessoais envolventes
- Descreva um dia típico na vida
- Mapeie jornada do cliente completa
- Identifique dores profundas e objetivos reais
- NUNCA invente dados - use apenas informações fornecidas

ESTRUTURA OBRIGATÓRIA:
1. Perfil Demográfico Completo
2. Análise Psicológica Profunda (valores, medos, desejos)
3. Comportamento Digital e Offline
4. Dores e Objetivos Específicos
5. História Pessoal Detalhada
6. Dia na Vida (hora a hora)
7. Jornada do Cliente
8. Estratégias de Abordagem Personalizadas""",
                'min_words': 1000,
                'sections': ['demografico', 'psicologico', 'comportamento', 'dores_objetivos', 'historia', 'dia_vida', 'jornada', 'estrategias']
            },
            
            # ANÁLISES TÉCNICAS
            'technical_analysis': {
                'system_prompt': """Você é um especialista técnico que cria documentação completa e precisa.

DIRETRIZES:
- Documentação COMPLETA com mínimo de 1500 palavras
- Explicações técnicas detalhadas passo a passo
- Exemplos práticos e casos de uso reais
- Diagramas e fluxogramas em texto quando relevante
- Análise de arquitetura e componentes
- Considerações de segurança, performance e escalabilidade
- Troubleshooting e resolução de problemas
- Best practices e padrões recomendados

ESTRUTURA TÉCNICA:
1. Overview Técnico
2. Arquitetura e Componentes
3. Especificações Detalhadas
4. Implementação Passo a Passo
5. Configurações e Otimizações
6. Segurança e Performance
7. Troubleshooting
8. Manutenção e Evolução""",
                'min_words': 1500,
                'sections': ['overview', 'arquitetura', 'especificacoes', 'implementacao', 'configuracoes', 'seguranca', 'troubleshooting', 'manutencao']
            },
            
            # ESTRATÉGIAS E PLANOS
            'strategy_planning': {
                'system_prompt': """Você é um estrategista de negócios que desenvolve planos detalhados e acionáveis.

REQUISITOS:
- Plano COMPLETO com mínimo de 1300 palavras
- Análise SWOT detalhada
- Objetivos SMART definidos
- Estratégias táticas específicas
- Timeline de implementação
- KPIs e métricas de sucesso
- Budget e recursos necessários
- Gestão de riscos

ESTRUTURA ESTRATÉGICA:
1. Situação Atual e Contexto
2. Análise SWOT Detalhada
3. Objetivos Estratégicos (curto, médio, longo prazo)
4. Estratégias e Táticas Específicas
5. Plano de Ação Detalhado
6. Recursos e Investimentos
7. KPIs e Métricas
8. Gestão de Riscos e Contingências""",
                'min_words': 1300,
                'sections': ['contexto', 'swot', 'objetivos', 'estrategias', 'plano_acao', 'recursos', 'kpis', 'riscos']
            },
            
            # CONTEÚDO E COPYWRITING
            'content_creation': {
                'system_prompt': """Você é um copywriter e estrategista de conteúdo especializado.

INSTRUÇÕES:
- Conteúdo COMPLETO com mínimo de 1000 palavras
- Headlines magnéticas e persuasivas
- Copy focado em dores e desejos
- Estrutura de storytelling
- CTAs específicos e testados
- Gatilhos mentais aplicados corretamente
- Versões A/B quando relevante
- Adaptação para diferentes canais

ESTRUTURA DE CONTEÚDO:
1. Análise do Público e Contexto
2. Estratégia de Mensagem
3. Headlines e Hooks
4. Copy Principal (estruturado)
5. Gatilhos Mentais Aplicados
6. CTAs Específicos
7. Variações para Canais
8. Métricas de Performance Esperadas""",
                'min_words': 1000,
                'sections': ['analise_publico', 'estrategia_mensagem', 'headlines', 'copy', 'gatilhos', 'ctas', 'variacoes', 'metricas']
            },
            
            # ANÁLISE DE DADOS
            'data_analysis': {
                'system_prompt': """Você é um cientista de dados especializado em análises profundas e insights acionáveis.

DIRETRIZES:
- Análise COMPLETA com mínimo de 1100 palavras
- Estatísticas descritivas detalhadas
- Identificação de padrões e tendências
- Correlações e causalidades
- Visualizações recomendadas
- Insights acionáveis
- Recomendações baseadas em dados
- Limitações e considerações

ESTRUTURA DE ANÁLISE:
1. Resumo Executivo dos Dados
2. Estatísticas Descritivas
3. Análise Exploratória
4. Padrões e Tendências Identificados
5. Análise de Correlações
6. Segmentações Relevantes
7. Insights e Descobertas
8. Recomendações Data-Driven""",
                'min_words': 1100,
                'sections': ['resumo', 'estatisticas', 'exploracao', 'padroes', 'correlacoes', 'segmentacoes', 'insights', 'recomendacoes']
            },
            
            # TEMPLATE GENÉRICO (FALLBACK)
            'generic_detailed': {
                'system_prompt': """Você é um especialista que cria análises profundas e detalhadas sobre qualquer assunto.

INSTRUÇÕES UNIVERSAIS:
- Análise COMPLETA com NO MÍNIMO 1000 palavras
- Estruture em seções lógicas e claras
- Desenvolva cada ponto completamente
- Use exemplos práticos e concretos
- Inclua análises de múltiplas perspectivas
- Forneça insights valiosos
- Sempre conclua com síntese e próximos passos
- NUNCA corte a resposta abruptamente

ESTRUTURA GENÉRICA:
1. Introdução e Contextualização (2-3 parágrafos)
2. Análise Detalhada (múltiplas perspectivas)
3. Descobertas e Insights
4. Implicações Práticas
5. Recomendações Acionáveis
6. Conclusão Completa
7. Próximos Passos""",
                'min_words': 1000,
                'sections': ['introducao', 'analise', 'insights', 'implicacoes', 'recomendacoes', 'conclusao', 'proximos_passos']
            }
        }
        
        # 🎯 DETECÇÃO AUTOMÁTICA DE TIPO DE ANÁLISE
        self.analysis_keywords = {
            'market_analysis': ['mercado', 'market', 'concorrência', 'competition', 'setor', 'indústria', 'industry', 'tendências', 'trends'],
            'persona_generation': ['avatar', 'persona', 'perfil', 'profile', 'cliente', 'customer', 'público', 'audience', 'buyer'],
            'technical_analysis': ['técnico', 'technical', 'arquitetura', 'architecture', 'implementação', 'implementation', 'sistema', 'system', 'código', 'code'],
            'strategy_planning': ['estratégia', 'strategy', 'plano', 'plan', 'planejamento', 'planning', 'objetivos', 'goals', 'kpi', 'roadmap'],
            'content_creation': ['conteúdo', 'content', 'copy', 'texto', 'text', 'mensagem', 'message', 'campanha', 'campaign', 'post'],
            'data_analysis': ['dados', 'data', 'análise', 'analysis', 'estatística', 'statistics', 'métricas', 'metrics', 'relatório', 'report']
        }
        
        # Inicializar backends
        self._initialize_backends()
        
        # Detectar e carregar modelo automaticamente
        self._auto_load_model()
        
        logger.info("🤖 Local Model Manager UNIVERSAL inicializado para 28+ módulos")
    
    def _initialize_backends(self):
        """Inicializa os backends disponíveis"""
        
        self._check_gpu_availability()
        
        try:
            from llama_cpp import Llama
            self.backends['llama_cpp'] = Llama
            logger.info("✅ Backend llama-cpp-python disponível")
        except ImportError:
            logger.warning("⚠️ llama-cpp-python não instalado")
        
        try:
            import transformers
            try:
                import torch
                self.backends['transformers'] = transformers
                logger.info(f"✅ Backend transformers {transformers.__version__} disponível com PyTorch {torch.__version__}")
                if torch.cuda.is_available():
                    logger.info(f"🎮 CUDA disponível: {torch.cuda.get_device_name(0)}")
                else:
                    logger.info("💻 Usando CPU para transformers")
            except ImportError:
                logger.warning("⚠️ transformers instalado mas PyTorch ausente")
        except ImportError:
            logger.warning("⚠️ transformers não instalado")
        
        try:
            from ctransformers import AutoModelForCausalLM
            self.backends['ctransformers'] = AutoModelForCausalLM
            logger.info("✅ Backend ctransformers disponível")
        except ImportError:
            logger.warning("⚠️ ctransformers não instalado")
    
    def _check_gpu_availability(self):
        """Verifica disponibilidade de GPU"""
        try:
            import pynvml
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            logger.info(f"🎮 NVML disponível: {device_count} GPU(s) detectada(s)")
            
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle)
                if isinstance(name, bytes):
                    name = name.decode('utf-8')
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                memory_total = memory_info.total // (1024**3)
                logger.info(f"   GPU {i}: {name} ({memory_total}GB)")
                
        except ImportError:
            logger.warning("⚠️ NVML não disponível")
            try:
                import subprocess
                result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    gpus = result.stdout.strip().split('\n')
                    logger.info(f"🎮 GPU detectada via nvidia-smi: {len(gpus)} dispositivo(s)")
            except Exception:
                logger.warning("⚠️ GPU não detectada - usando apenas CPU")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao verificar GPU: {e}")
    
    def _auto_load_model(self):
        """Detecta e carrega automaticamente um modelo disponível"""
        
        model_files = []
        for pattern in ['*.gguf', '*.safetensors', '*.bin']:
            model_files.extend(list(self.model_dir.glob(pattern)))
        
        if not model_files:
            logger.warning("⚠️ Nenhum modelo encontrado")
            return
        
        gguf_files = [f for f in model_files if f.suffix == '.gguf']
        safetensors_files = [f for f in model_files if f.suffix == '.safetensors']
        bin_files = [f for f in model_files if f.suffix == '.bin']
        
        logger.info(f"📂 Modelos: {len(gguf_files)} GGUF, {len(safetensors_files)} SafeTensors, {len(bin_files)} BIN")
        
        models_to_try = []
        if gguf_files:
            models_to_try.extend([(f, 'gguf') for f in gguf_files])
        if safetensors_files:
            models_to_try.extend([(f, 'safetensors') for f in safetensors_files])
        if bin_files:
            models_to_try.extend([(f, 'bin') for f in bin_files])
        
        for model_path, model_type in models_to_try:
            try:
                file_size = model_path.stat().st_size
                if file_size < 1024:
                    continue
                
                success = False
                if model_type == 'gguf':
                    success = self._load_gguf_model(model_path)
                elif model_type == 'safetensors':
                    success = self._load_safetensors_model(model_path)
                elif model_type == 'bin':
                    success = self._load_bin_model(model_path)
                
                if success:
                    logger.info(f"✅ Modelo carregado: {model_path.name}")
                    return
                    
            except Exception as e:
                logger.warning(f"⚠️ Erro ao carregar {model_path.name}: {e}")
                continue
        
        logger.error("❌ Nenhum modelo pôde ser carregado")
    
    def _load_gguf_model(self, model_path: Path):
        """Carrega modelo GGUF (código similar ao original, mantendo otimizações)"""
        if not self.backends['llama_cpp']:
            return False
        
        try:
            file_size_gb = model_path.stat().st_size / (1024**3)
            
            gpu_layers = 0
            gpu_detected = False
            
            try:
                import torch
                if torch.cuda.is_available():
                    gpu_layers = 45
                    gpu_detected = True
            except:
                pass
            
            if not gpu_detected:
                try:
                    import pynvml
                    pynvml.nvmlInit()
                    if pynvml.nvmlDeviceGetCount() > 0:
                        gpu_layers = 45
                        gpu_detected = True
                except:
                    pass
            
            cpu_count = os.cpu_count() or 4
            
            if file_size_gb < 2:
                n_ctx = 16384 if gpu_detected else 8192
                n_threads = cpu_count if not gpu_detected else min(4, cpu_count)
                n_batch = 2048 if gpu_detected else 1024
            elif file_size_gb < 5:
                n_ctx = 16384 if gpu_detected else 8192
                n_threads = cpu_count if not gpu_detected else min(4, cpu_count)
                n_batch = 1024 if gpu_detected else 512
            else:
                n_ctx = 8192 if gpu_detected else 4096
                n_threads = cpu_count if not gpu_detected else min(2, cpu_count)
                n_batch = 512 if gpu_detected else 256
            
            config = {
                'model_path': str(model_path),
                'n_ctx': n_ctx,
                'n_threads': n_threads,
                'n_gpu_layers': gpu_layers,
                'n_batch': n_batch,
                'verbose': False,
                'use_mmap': True,
                'use_mlock': False,
                'seed': -1,
                'low_vram': False,
                'f16_kv': True,
            }
            
            self.current_model = self.backends['llama_cpp'](**config)
            self.current_backend = 'llama_cpp'
            
            self.model_info = {
                'name': model_path.name,
                'type': 'gguf',
                'backend': 'llama.cpp',
                'size_mb': file_size_gb * 1024,
                'context_length': n_ctx,
                'gpu_layers': gpu_layers,
            }
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar GGUF: {e}")
            return False
    
    def _load_safetensors_model(self, model_path: Path):
        """Carrega SafeTensors (simplificado)"""
        return False  # Implementar se necessário
    
    def _load_bin_model(self, model_path: Path):
        """Carrega BIN (simplificado)"""
        return False  # Implementar se necessário
    
    def is_model_loaded(self) -> bool:
        """Verifica se há um modelo carregado"""
        return self.current_model is not None
    
    def _detect_analysis_type(self, prompt: str, context_data: Dict[str, Any] = None) -> str:
        """
        🎯 DETECÇÃO AUTOMÁTICA do tipo de análise baseada no prompt e contexto
        """
        prompt_lower = prompt.lower()
        
        # Analisa dados de contexto se fornecidos
        if context_data:
            context_str = json.dumps(context_data, ensure_ascii=False).lower()
            prompt_lower += " " + context_str
        
        # Conta matches para cada tipo
        type_scores = {}
        for analysis_type, keywords in self.analysis_keywords.items():
            score = sum(1 for keyword in keywords if keyword in prompt_lower)
            if score > 0:
                type_scores[analysis_type] = score
        
        # Retorna o tipo com mais matches
        if type_scores:
            detected_type = max(type_scores, key=type_scores.get)
            logger.info(f"🎯 Tipo detectado: {detected_type} (score: {type_scores[detected_type]})")
            return detected_type
        
        logger.info("🎯 Tipo genérico detectado (fallback)")
        return 'generic_detailed'
    
    def _build_enhanced_prompt(self, user_prompt: str, analysis_type: str, 
                              context_data: Dict[str, Any] = None, 
                              module_name: str = None) -> str:
        """
        🏗️ CONSTRÓI PROMPT ENRIQUECIDO baseado no tipo e contexto
        """
        template = self.analysis_templates.get(analysis_type, self.analysis_templates['generic_detailed'])
        
        # Monta o prompt completo
        enhanced_parts = [template['system_prompt'], "\n---\n"]
        
        # Adiciona dados de contexto se disponíveis
        if context_data:
            enhanced_parts.append("## DADOS DE CONTEXTO DISPONÍVEIS:\n")
            
            # Extrai informações relevantes do contexto
            for key, value in context_data.items():
                if isinstance(value, (dict, list)):
                    enhanced_parts.append(f"### {key.upper().replace('_', ' ')}:\n")
                    enhanced_parts.append(f"```json\n{json.dumps(value, ensure_ascii=False, indent=2)}\n```\n")
                else:
                    enhanced_parts.append(f"- **{key.replace('_', ' ').title()}**: {value}\n")
            
            enhanced_parts.append("\n---\n")
        
        # Adiciona informações do módulo se fornecidas
        if module_name:
            enhanced_parts.append(f"## MÓDULO ATUAL: {module_name}\n\n")
        
        # Adiciona a tarefa do usuário
        enhanced_parts.append("## TAREFA ESPECÍFICA:\n")
        enhanced_parts.append(user_prompt)
        enhanced_parts.append("\n\n---\n")
        
        # Adiciona lembretes críticos
        min_words = template.get('min_words', 1000)
        sections = template.get('sections', [])
        
        enhanced_parts.append(f"""
## REQUISITOS OBRIGATÓRIOS:
✓ Mínimo de {min_words} palavras
✓ Seções obrigatórias: {', '.join(sections)}
✓ Análise COMPLETA e DETALHADA
✓ Exemplos práticos e concretos
✓ Insights acionáveis
✓ NUNCA termine abruptamente
✓ Sempre conclua com síntese estratégica

## COMECE AGORA A ANÁLISE COMPLETA:
""")
        
        return "".join(enhanced_parts)
    
    def generate_for_module(self, 
                           module_name: str,
                           task_description: str,
                           context_data: Dict[str, Any] = None,
                           analysis_type: str = None,
                           **kwargs) -> str:
        """
        🎯 MÉTODO PRINCIPAL para gerar conteúdo para qualquer módulo
        
        Args:
            module_name: Nome do módulo (ex: 'avatar_generation', 'market_analysis')
            task_description: Descrição da tarefa específica
            context_data: Dados de contexto do módulo (sessão, etapas anteriores, etc)
            analysis_type: Tipo forçado de análise (opcional)
            **kwargs: Parâmetros adicionais de geração
        
        Returns:
            Análise completa gerada
        """
        
        if not self.is_model_loaded():
            raise RuntimeError("❌ Nenhum modelo local carregado")
        
        logger.info(f"🎯 Gerando para módulo: {module_name}")
        
        # Detecta tipo de análise automaticamente se não fornecido
        if not analysis_type:
            analysis_type = self._detect_analysis_type(task_description, context_data)
        
        # Constrói prompt enriquecido
        enhanced_prompt = self._build_enhanced_prompt(
            task_description,
            analysis_type,
            context_data,
            module_name
        )
        
        logger.info(f"📝 Prompt construído: {len(enhanced_prompt)} caracteres")
        logger.info(f"🎯 Tipo de análise: {analysis_type}")
        
        # Configura parâmetros otimizados
        config = {**self.default_config, **kwargs}
        
        # Ajustes específicos por tipo
        template = self.analysis_templates[analysis_type]
        config['max_tokens'] = max(config.get('max_tokens', 16384), template.get('min_words', 1000) * 2)
        
        # Gera conteúdo
        try:
            if self.current_backend == 'llama_cpp':
                return self._generate_llama_cpp(enhanced_prompt, config, report_mode=True)
            elif self.current_backend == 'transformers':
                return self._generate_transformers(enhanced_prompt, config, report_mode=True)
            else:
                raise RuntimeError(f"Backend não suportado: {self.current_backend}")
        except Exception as e:
            logger.error(f"❌ Erro na geração: {e}")
            raise
    
    def generate_text(self, prompt: str, report_mode: bool = True, **kwargs) -> str:
        """Método legado mantido para compatibilidade"""
        return self.generate_for_module(
            module_name="legacy",
            task_description=prompt,
            context_data=None,
            **kwargs
        )
    
    def _generate_llama_cpp(self, prompt: str, config: Dict, report_mode: bool = False) -> str:
        """⚡ Geração OTIMIZADA com llama-cpp"""
        
        start_time = time.time()
        max_tokens = config.get('max_tokens', 16384)
        
        stop_tokens = ["<|im_end|>", "<|endoftext|>", "### User:", "### Human:"]
        
        generation_params = {
            'max_tokens': max_tokens,
            'temperature': config.get('temperature', 0.75),
            'top_p': config.get('top_p', 0.92),
            'top_k': config.get('top_k', 45),
            'repeat_penalty': config.get('repeat_penalty', 1.18),
            'stop': stop_tokens,
            'echo': False,
            'stream': False,
        }
        
        logger.info(f"🎯 Gerando: max_tokens={max_tokens}, temp={generation_params['temperature']}")
        
        try:
            response = self.current_model(prompt, **generation_params)
            
            if isinstance(response, dict):
                if 'choices' in response and len(response['choices']) > 0:
                    generated_text = response['choices'][0].get('text', '').strip()
                else:
                    generated_text = ""
            else:
                generated_text = str(response).strip()
            
            # Validação inteligente
            min_expected = 400 if report_mode else 100
            
            if len(generated_text) < min_expected:
                logger.warning(f"⚠️ Resposta curta ({len(generated_text)} chars), aplicando recuperação...")
                
                for attempt in range(3):
                    logger.info(f"🔄 Tentativa {attempt + 1}/3...")
                    
                    retry_params = generation_params.copy()
                    retry_params['max_tokens'] = max_tokens * (2 + attempt)
                    retry_params['temperature'] = 0.8 + (attempt * 0.05)
                    retry_params['repeat_penalty'] = max(1.1, 1.18 - (attempt * 0.03))
                    retry_params['stop'] = ["<|im_end|>"]
                    
                    extended_prompt = f"{prompt}\n\n[CRÍTICO: Forneça uma resposta COMPLETA e DETALHADA de no mínimo 800 palavras. Desenvolva completamente todos os pontos.]"
                    
                    response = self.current_model(extended_prompt, **retry_params)
                    
                    if isinstance(response, dict) and 'choices' in response:
                        generated_text = response['choices'][0].get('text', '').strip()
                    else:
                        generated_text = str(response).strip()
                    
                    if len(generated_text) >= min_expected:
                        logger.info(f"✅ Recuperação bem-sucedida: {len(generated_text)} chars")
                        break
                
                if len(generated_text) < min_expected:
                    logger.warning("⚠️ Última tentativa com parâmetros máximos...")
                    
                    max_params = {
                        'max_tokens': max_tokens * 4,
                        'temperature': 0.9,
                        'top_p': 0.98,
                        'top_k': 60,
                        'repeat_penalty': 1.1,
                        'stop': ["<|endoftext|>"],
                        'echo': False
                    }
                    
                    final_prompt = f"""INSTRUÇÕES ABSOLUTAS: Você DEVE fornecer uma resposta COMPLETA, DETALHADA e LONGA.
Mínimo obrigatório: 1000 palavras. NÃO pare até completar toda a análise com todas as seções.

{prompt}

INICIE AGORA A RESPOSTA COMPLETA (mínimo 1000 palavras):"""
                    
                    response = self.current_model(final_prompt, **max_params)
                    
                    if isinstance(response, dict) and 'choices' in response:
                        generated_text = response['choices'][0].get('text', '').strip()
                    else:
                        generated_text = str(response).strip()
                
        except Exception as e:
            logger.error(f"❌ Erro na geração: {e}")
            
            try:
                logger.info("🔄 Fallback minimalista...")
                simple_params = {
                    'max_tokens': 4096,
                    'temperature': 0.7,
                    'stop': ["<|im_end|>"],
                    'echo': False
                }
                response = self.current_model(prompt, **simple_params)
                
                if isinstance(response, dict) and 'choices' in response:
                    generated_text = response['choices'][0].get('text', '').strip()
                else:
                    generated_text = str(response).strip()
                    
            except Exception as e2:
                logger.error(f"❌ Fallback falhou: {e2}")
                generated_text = "ERRO: Não foi possível gerar resposta. Verifique os logs."
        
        generation_time = time.time() - start_time
        word_count = len(generated_text.split())
        char_count = len(generated_text)
        tokens_per_second = word_count / generation_time if generation_time > 0 else 0
        
        logger.info(f"🤖 Gerado: {char_count} chars, {word_count} palavras")
        logger.info(f"⏱️ Tempo: {generation_time:.2f}s ({tokens_per_second:.1f} tokens/s)")
        
        if report_mode:
            if word_count < 500:
                logger.warning(f"⚠️ ATENÇÃO: Apenas {word_count} palavras (esperado: 800+)")
            elif word_count < 800:
                logger.info(f"ℹ️ {word_count} palavras (bom, mas poderia ser mais completo)")
            else:
                logger.info(f"✅ Resposta completa com {word_count} palavras")
        
        generated_text = self._post_process_text(generated_text, report_mode)
        
        return generated_text
    
    def _generate_transformers(self, prompt: str, config: Dict, report_mode: bool = False) -> str:
        """⚡ Geração com transformers (simplificado para o exemplo)"""
        
        logger.info("🔒 Transformers backend não implementado completamente neste exemplo")
        return "Geração via transformers não disponível. Use llama.cpp (GGUF)."
    
    def _post_process_text(self, text: str, report_mode: bool = False) -> str:
        """🧹 Pós-processamento inteligente"""
        
        if not text:
            return text
        
        # Remove espaços extras
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove repetições de linhas
        lines = text.split('\n')
        cleaned_lines = []
        last_line = None
        
        for line in lines:
            line = line.strip()
            if line and line != last_line:
                cleaned_lines.append(line)
                last_line = line
            elif not line:
                cleaned_lines.append('')
        
        text = '\n'.join(cleaned_lines)
        
        # Remove artefatos
        artifacts = [
            'Human:', 'User:', 'Assistant:', 'AI:',
            '<|im_end|>', '<|endoftext|>',
            '[INST]', '[/INST]',
            '### System:', '### User:', '### Assistant:'
        ]
        
        for artifact in artifacts:
            text = text.replace(artifact, '')
        
        text = text.strip()
        
        # Garante pontuação final para relatórios
        if report_mode and text:
            last_sentence = text.split('.')[-1].strip()
            if len(last_sentence) > 100 and not any(text.endswith(end) for end in ['.', '!', '?', ':', ';']):
                text += '.'
        
        return text
    
    def chat_completion(self, messages: List[Dict[str, str]], 
                       module_name: str = None,
                       context_data: Dict[str, Any] = None,
                       **kwargs) -> str:
        """
        🎯 Chat completion compatível com módulos
        """
        
        prompt = self._messages_to_prompt(messages)
        
        # Detecta automaticamente tipo de análise
        last_message = messages[-1].get('content', '') if messages else ''
        analysis_type = self._detect_analysis_type(last_message, context_data)
        
        logger.info(f"💬 Chat completion: {len(prompt)} chars, tipo: {analysis_type}")
        
        if module_name:
            return self.generate_for_module(
                module_name=module_name,
                task_description=prompt,
                context_data=context_data,
                analysis_type=analysis_type,
                **kwargs
            )
        else:
            return self.generate_text(prompt, report_mode=True, **kwargs)
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Converte mensagens para prompt"""
        
        prompt_parts = []
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'system':
                prompt_parts.append(f"### System:\n{content}\n")
            elif role == 'user':
                prompt_parts.append(f"### User:\n{content}\n")
            elif role == 'assistant':
                prompt_parts.append(f"### Assistant:\n{content}\n")
        
        prompt_parts.append("### Assistant:\n")
        
        return "\n".join(prompt_parts)
    
    def generate_structured_analysis(self,
                                    module_name: str,
                                    analysis_sections: List[str],
                                    context_data: Dict[str, Any],
                                    **kwargs) -> Dict[str, str]:
        """
        🎯 Gera análise ESTRUTURADA por seções
        
        Útil quando você precisa de cada seção separadamente
        """
        
        logger.info(f"📊 Gerando análise estruturada: {len(analysis_sections)} seções")
        
        results = {}
        
        for section in analysis_sections:
            logger.info(f"📝 Gerando seção: {section}")
            
            section_prompt = f"""
## SEÇÃO ESPECÍFICA: {section.upper().replace('_', ' ')}

Baseado nos dados de contexto fornecidos, desenvolva COMPLETAMENTE esta seção.
Mínimo: 300 palavras para esta seção específica.

Seção: {section.replace('_', ' ').title()}
"""
            
            section_result = self.generate_for_module(
                module_name=module_name,
                task_description=section_prompt,
                context_data=context_data,
                **kwargs
            )
            
            results[section] = section_result
            logger.info(f"✅ Seção '{section}' concluída: {len(section_result.split())} palavras")
        
        logger.info(f"✅ Análise estruturada completa: {len(results)} seções geradas")
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações do modelo carregado"""
        return self.model_info.copy()
    
    def get_available_analysis_types(self) -> List[str]:
        """Retorna tipos de análise disponíveis"""
        return list(self.analysis_templates.keys())
    
    def get_analysis_template_info(self, analysis_type: str) -> Dict[str, Any]:
        """Retorna informações sobre um template específico"""
        template = self.analysis_templates.get(analysis_type)
        if template:
            return {
                'type': analysis_type,
                'min_words': template.get('min_words', 1000),
                'sections': template.get('sections', []),
                'system_prompt_preview': template['system_prompt'][:200] + '...'
            }
        return {}
    
    def benchmark_module(self, module_name: str, 
                        test_prompt: str = None,
                        context_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        🏁 Testa performance para um módulo específico
        """
        
        if not self.is_model_loaded():
            return {'error': 'Nenhum modelo carregado'}
        
        if test_prompt is None:
            test_prompt = f"Crie uma análise detalhada e completa para o módulo {module_name}"
        
        logger.info(f"🏁 Benchmark para módulo: {module_name}")
        
        start_time = time.time()
        
        try:
            result = self.generate_for_module(
                module_name=module_name,
                task_description=test_prompt,
                context_data=context_data or {}
            )
            
            generation_time = time.time() - start_time
            word_count = len(result.split())
            char_count = len(result)
            
            return {
                'success': True,
                'module': module_name,
                'generation_time_seconds': round(generation_time, 2),
                'words_generated': word_count,
                'characters_generated': char_count,
                'words_per_second': round(word_count / generation_time, 2) if generation_time > 0 else 0,
                'model_info': self.model_info,
                'preview': result[:300] + '...' if len(result) > 300 else result
            }
            
        except Exception as e:
            return {
                'success': False,
                'module': module_name,
                'error': str(e),
                'generation_time_seconds': time.time() - start_time
            }

# Instância global
local_model_manager = LocalModelManager()

def get_local_model_manager() -> LocalModelManager:
    """Retorna a instância global do gerenciador"""
    return local_model_manager

def is_local_model_available() -> bool:
    """Verifica se há um modelo disponível"""
    return local_model_manager.is_model_loaded()

# 🎯 FUNÇÕES DE CONVENIÊNCIA PARA CADA TIPO DE MÓDULO

def generate_market_analysis(task: str, context: Dict[str, Any] = None, **kwargs) -> str:
    """Gera análise de mercado completa"""
    return local_model_manager.generate_for_module(
        module_name='market_analysis',
        task_description=task,
        context_data=context,
        analysis_type='market_analysis',
        **kwargs
    )

def generate_persona_profile(task: str, context: Dict[str, Any] = None, **kwargs) -> str:
    """Gera perfil de persona/avatar completo"""
    return local_model_manager.generate_for_module(
        module_name='persona_generation',
        task_description=task,
        context_data=context,
        analysis_type='persona_generation',
        **kwargs
    )

def generate_technical_documentation(task: str, context: Dict[str, Any] = None, **kwargs) -> str:
    """Gera documentação técnica completa"""
    return local_model_manager.generate_for_module(
        module_name='technical_analysis',
        task_description=task,
        context_data=context,
        analysis_type='technical_analysis',
        **kwargs
    )

def generate_strategy_plan(task: str, context: Dict[str, Any] = None, **kwargs) -> str:
    """Gera plano estratégico completo"""
    return local_model_manager.generate_for_module(
        module_name='strategy_planning',
        task_description=task,
        context_data=context,
        analysis_type='strategy_planning',
        **kwargs
    )

def generate_content_copy(task: str, context: Dict[str, Any] = None, **kwargs) -> str:
    """Gera copy e conteúdo completo"""
    return local_model_manager.generate_for_module(
        module_name='content_creation',
        task_description=task,
        context_data=context,
        analysis_type='content_creation',
        **kwargs
    )

def generate_data_report(task: str, context: Dict[str, Any] = None, **kwargs) -> str:
    """Gera relatório de análise de dados completo"""
    return local_model_manager.generate_for_module(
        module_name='data_analysis',
        task_description=task,
        context_data=context,
        analysis_type='data_analysis',
        **kwargs
    )

def generate_for_any_module(module_name: str, task: str, context: Dict[str, Any] = None, **kwargs) -> str:
    """Função genérica para qualquer módulo"""
    return local_model_manager.generate_for_module(
        module_name=module_name,
        task_description=task,
        context_data=context,
        **kwargs
    )

# 🎯 EXEMPLO DE USO COM MÚLTIPLOS MÓDULOS
if __name__ == "__main__":
    print("=" * 80)
    print("LOCAL MODEL MANAGER UNIVERSAL - SISTEMA MULTI-MÓDULOS")
    print("=" * 80)
    
    manager = get_local_model_manager()
    
    if not manager.is_model_loaded():
        print("❌ Nenhum modelo carregado. Coloque um modelo .gguf na pasta src/model/")
        exit(1)
    
    print("\n📊 INFORMAÇÕES DO MODELO:")
    print(f"   Nome: {manager.model_info.get('name', 'N/A')}")
    print(f"   Tipo: {manager.model_info.get('type', 'N/A')}")
    print(f"   Backend: {manager.model_info.get('backend', 'N/A')}")
    print(f"   Contexto: {manager.model_info.get('context_length', 'N/A')}")
    print(f"   GPU Layers: {manager.model_info.get('gpu_layers', 0)}")
    
    print("\n🎯 TIPOS DE ANÁLISE DISPONÍVEIS:")
    for i, analysis_type in enumerate(manager.get_available_analysis_types(), 1):
        info = manager.get_analysis_template_info(analysis_type)
        print(f"   {i}. {analysis_type}")
        print(f"      → Mínimo: {info.get('min_words', 0)} palavras")
        print(f"      → Seções: {len(info.get('sections', []))}")
    
    print("\n" + "=" * 80)
    print("EXEMPLO 1: GERAÇÃO PARA MÓDULO DE AVATARES")
    print("=" * 80)
    
    # Simula dados de contexto do módulo de avatares
    avatar_context = {
        'session_id': 'test_001',
        'etapa1_data': {
            'publico_alvo': {
                'faixas_etarias': ['30-45', '45-55'],
                'localizacoes': ['São Paulo', 'Rio de Janeiro'],
                'profissoes': ['Empreendedor', 'Consultor'],
                'renda': {'min': 5000, 'max': 20000}
            }
        },
        'etapa2_data': {
            'pesquisa_mercado': {
                'dores_principais': ['Falta de clientes', 'Baixa conversão'],
                'desejos_principais': ['Crescimento', 'Reconhecimento']
            }
        }
    }
    
    print("\n📝 Gerando perfil de avatar completo...")
    print("   (Isso pode levar alguns segundos...)\n")
    
    try:
        avatar_profile = generate_persona_profile(
            task="Crie um perfil COMPLETO e DETALHADO de avatar baseado nos dados fornecidos",
            context=avatar_context
        )
        
        word_count = len(avatar_profile.split())
        print(f"\n✅ PERFIL GERADO COM SUCESSO!")
        print(f"   Palavras: {word_count}")
        print(f"   Caracteres: {len(avatar_profile)}")
        print(f"\n📄 PREVIEW (primeiras 500 caracteres):")
        print("   " + "-" * 76)
        preview_lines = avatar_profile[:500].split('\n')
        for line in preview_lines:
            print(f"   {line}")
        print("   ...")
        print("   " + "-" * 76)
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
    
    print("\n" + "=" * 80)
    print("EXEMPLO 2: GERAÇÃO PARA MÓDULO DE ANÁLISE DE MERCADO")
    print("=" * 80)
    
    market_context = {
        'nicho': 'Marketing Digital para Médicos',
        'concorrentes': ['Empresa A', 'Empresa B', 'Empresa C'],
        'ticket_medio': 3500,
        'tamanho_mercado': 'R$ 50 milhões/ano'
    }
    
    print("\n📊 Gerando análise de mercado...\n")
    
    try:
        market_analysis = generate_market_analysis(
            task="Faça uma análise COMPLETA do mercado de marketing digital para médicos",
            context=market_context
        )
        
        word_count = len(market_analysis.split())
        print(f"\n✅ ANÁLISE GERADA COM SUCESSO!")
        print(f"   Palavras: {word_count}")
        print(f"   Caracteres: {len(market_analysis)}")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
    
    print("\n" + "=" * 80)
    print("🎯 COMO USAR EM SEUS 28 MÓDULOS:")
    print("=" * 80)
    print("""
    # Para qualquer módulo, basta chamar:
    
    resultado = generate_for_any_module(
        module_name='seu_modulo',
        task='Descrição da tarefa',
        context={
            'dados_etapa_anterior': {...},
            'session_id': 'xxx',
            'qualquer_outro_dado': {...}
        }
    )
    
    # Ou use as funções específicas:
    - generate_market_analysis()
    - generate_persona_profile()
    - generate_technical_documentation()
    - generate_strategy_plan()
    - generate_content_copy()
    - generate_data_report()
    
    # O sistema detecta AUTOMATICAMENTE o tipo de análise
    # e aplica o template correto com prompts otimizados!
    """)
    
    print("\n✅ LOCAL MODEL MANAGER UNIVERSAL PRONTO PARA USO!")
    print("=" * 80)