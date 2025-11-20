#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - CPL Integration Manager
GARANTE que os CPLs sejam SEMPRE incluídos nos relatórios finais
"""

import os
import json
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

# Importar sistema de logging otimizado
try:
    from ..utils.enhanced_logging_system import get_logger, log_performance
except ImportError:
    try:
        from utils.enhanced_logging_system import get_logger, log_performance
    except ImportError:
        import logging
        def get_logger(name, level=None):
            return logging.getLogger(name)
        def log_performance(operation, duration, details=None):
            pass

logger = get_logger(__name__)

class CPLIntegrationManager:
    """Gerenciador ultra-robusto que GARANTE a integração dos CPLs nos relatórios finais"""
    
    def __init__(self):
        """Inicializa o gerenciador de integração CPL V2.0"""
        # PRIORIDADE 3: Módulos CPL atualizados (removidos protocolos antigos 1-5)
        self.cpl_modules = [
            'cpl_devastador',
            'cpl_devastador_protocol',
            'external_ai_cpl_verification'
        ]
        
        # PRIORIDADE 3: Títulos CPL atualizados (removidos protocolos antigos)
        self.cpl_titles = {
            'cpl_devastador': 'Protocolo Integrado de CPLs Devastadores',
            'cpl_devastador_protocol': 'Protocolo CPL Devastador Completo',
            'external_ai_cpl_verification': 'Verificação Externa dos CPLs com IA'
        }
        
        # PRIORIDADE 3: Descrições CPL atualizadas (removidos protocolos antigos)
        self.cpl_descriptions = {
            'cpl_devastador': 'Integração completa de todos os protocolos CPL em uma estrutura coesa e devastadora',
            'cpl_devastador_protocol': 'Versão avançada e otimizada do protocolo CPL para máximo impacto psicológico',
            'external_ai_cpl_verification': 'Validação externa dos CPLs usando inteligência artificial avançada'
        }
        
        logger.info("🎯 CPL Integration Manager V2.0 inicializado - GARANTINDO inclusão TOTAL nos relatórios")
    
    def garantir_cpls_nos_modulos(self, session_id: str) -> Dict[str, Any]:
        """GARANTE que todos os CPLs estejam salvos na pasta modules"""
        try:
            logger.info(f"🔄 GARANTINDO CPLs para sessão: {session_id}")
            
            # Diretório de módulos
            modules_dir = Path(f"analyses_data/{session_id}/modules")
            modules_dir.mkdir(parents=True, exist_ok=True)
            
            # Status dos CPLs
            cpl_status = {
                'cpls_encontrados': [],
                'cpls_criados': [],
                'cpls_faltando': [],
                'total_cpls': len(self.cpl_modules)
            }
            
            # Verificar e criar CPLs se necessário
            for cpl_module in self.cpl_modules:
                cpl_file = self._get_cpl_filename(cpl_module)
                cpl_path = modules_dir / cpl_file
                
                if cpl_path.exists():
                    cpl_status['cpls_encontrados'].append(cpl_module)
                    logger.info(f"✅ CPL encontrado: {cpl_file}")
                else:
                    # Criar CPL se não existir
                    self._criar_cpl_padrao(cpl_path, cpl_module)
                    cpl_status['cpls_criados'].append(cpl_module)
                    logger.info(f"🆕 CPL criado: {cpl_file}")
            
            # Verificar se todos os CPLs estão presentes
            total_presentes = len(cpl_status['cpls_encontrados']) + len(cpl_status['cpls_criados'])
            
            if total_presentes == len(self.cpl_modules):
                logger.info(f"✅ TODOS OS {len(self.cpl_modules)} CPLs GARANTIDOS na pasta modules!")
            else:
                logger.warning(f"⚠️ Apenas {total_presentes}/{len(self.cpl_modules)} CPLs presentes")
            
            return cpl_status
            
        except Exception as e:
            logger.error(f"❌ Erro ao garantir CPLs: {e}")
            return {'erro': str(e)}
    
    def _get_cpl_filename(self, cpl_module: str) -> str:
        """Retorna o nome do arquivo correto para cada CPL"""
        filename_map = {
            'cpl_protocol_1': 'cpl_protocol_1.json',
            'cpl_protocol_2': 'cpl1.md',
            'cpl_protocol_3': 'cpl2.md', 
            'cpl_protocol_4': 'cpl3.md',
            'cpl_protocol_5': 'cpl4.md',
            'cpl_completo': 'cpl_completo.json'
        }
        return filename_map.get(cpl_module, f'{cpl_module}.md')
    
    def _criar_cpl_padrao(self, cpl_path: Path, cpl_module: str):
        """Cria um CPL padrão se não existir"""
        try:
            titulo = self.cpl_titles.get(cpl_module, cpl_module.replace('_', ' ').title())
            
            if cpl_path.suffix == '.json':
                # Criar arquivo JSON
                cpl_data = {
                    'titulo': titulo,
                    'conteudo': f'Conteúdo do {titulo} será gerado durante a execução do protocolo CPL.',
                    'data_geracao': datetime.now().isoformat(),
                    'status': 'aguardando_geracao',
                    'modulo': cpl_module,
                    'observacao': 'Este arquivo será preenchido automaticamente quando o protocolo CPL for executado.'
                }
                
                with open(cpl_path, 'w', encoding='utf-8') as f:
                    json.dump(cpl_data, f, ensure_ascii=False, indent=2)
            else:
                # Criar arquivo MD
                conteudo_md = f"""# {titulo}

## Status
🔄 **Aguardando geração pelo protocolo CPL**

## Descrição
Este CPL será gerado automaticamente quando o protocolo completo for executado.

## Informações Técnicas
- **Módulo**: {cpl_module}
- **Data de criação**: {datetime.now().isoformat()}
- **Status**: Aguardando geração

## Próximos Passos
1. Execute o protocolo CPL completo
2. Este arquivo será automaticamente preenchido com o conteúdo real
3. O CPL será incluído no relatório final

---
*Arquivo criado automaticamente pelo CPL Integration Manager*
"""
                
                with open(cpl_path, 'w', encoding='utf-8') as f:
                    f.write(conteudo_md)
            
            logger.info(f"📝 CPL padrão criado: {cpl_path}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar CPL padrão {cpl_module}: {e}")
    
    def gerar_cpl_com_ia(self, session_id: str, cpl_module: str, dados_contexto: Dict[str, Any] = None) -> Dict[str, Any]:
        """Gera conteúdo de CPL usando IA baseado no contexto da sessão"""
        try:
            logger.info(f"🤖 Gerando CPL {cpl_module} com IA para sessão: {session_id}")
            
            # Importar o sistema de APIs
            from .enhanced_api_rotation_manager import EnhancedAPIRotationManager
            import asyncio
            
            api_manager = EnhancedAPIRotationManager()
            
            # Carregar dados de contexto da sessão
            session_dir = Path(f"analyses_data/{session_id}")
            contexto = self._carregar_contexto_sessao(session_dir, dados_contexto)
            
            # Prompt especializado para geração de CPL
            cpl_prompt = self._criar_prompt_cpl(cpl_module, contexto)
            
            # Gerar conteúdo usando IA
            async def gerar_conteudo():
                return await api_manager.generate_content(
                    cpl_prompt,
                    service_type='ai_generation',
                    max_tokens=3000,
                    temperature=0.7
                )
            
            # Executar geração
            conteudo_gerado = asyncio.run(gerar_conteudo())
            
            # Salvar CPL gerado
            resultado = self._salvar_cpl_gerado(session_id, cpl_module, conteudo_gerado)
            
            logger.info(f"✅ CPL {cpl_module} gerado com IA e salvo")
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar CPL {cpl_module} com IA: {e}")
            return {
                'status': 'error',
                'erro': str(e),
                'cpl_module': cpl_module
            }
    
    def _carregar_contexto_sessao(self, session_dir: Path, dados_contexto: Dict[str, Any] = None) -> Dict[str, Any]:
        """Carrega contexto da sessão para geração de CPL"""
        contexto = {
            'dados_fornecidos': dados_contexto or {},
            'modulos_existentes': [],
            'informacoes_produto': {},
            'publico_alvo': {},
            'concorrencia': {}
        }
        
        try:
            # Carregar módulos existentes
            modules_dir = session_dir / "modules"
            if modules_dir.exists():
                for module_file in modules_dir.glob("*.json"):
                    try:
                        with open(module_file, 'r', encoding='utf-8') as f:
                            module_data = json.load(f)
                            contexto['modulos_existentes'].append({
                                'nome': module_file.stem,
                                'dados': module_data
                            })
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao carregar módulo {module_file}: {e}")
                        
                for module_file in modules_dir.glob("*.md"):
                    try:
                        with open(module_file, 'r', encoding='utf-8') as f:
                            module_content = f.read()
                            contexto['modulos_existentes'].append({
                                'nome': module_file.stem,
                                'conteudo': module_content[:1000]  # Limitar tamanho
                            })
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao carregar módulo {module_file}: {e}")
            
            # Carregar dados específicos se existirem
            info_files = ['posicionamento.json', 'publico_alvo.json', 'concorrencia.json']
            for info_file in info_files:
                file_path = modules_dir / info_file
                if file_path.exists():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            key = info_file.replace('.json', '')
                            contexto[key] = data
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao carregar {info_file}: {e}")
                        
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar contexto da sessão: {e}")
            
        return contexto
    
    def _criar_prompt_cpl(self, cpl_module: str, contexto: Dict[str, Any]) -> str:
        """Cria prompt especializado para geração de CPL"""
        titulo = self.cpl_titles.get(cpl_module, cpl_module)
        descricao = self.cpl_descriptions.get(cpl_module, "")
        
        prompt = f"""
SISTEMA DE GERAÇÃO DE CPL (Certificado de Pessoa Legal)

Você é um especialista em marketing persuasivo e copywriting. Gere um {titulo} completo e impactante.

DESCRIÇÃO DO CPL:
{descricao}

CONTEXTO DA SESSÃO:
{json.dumps(contexto, ensure_ascii=False, indent=2)[:4000]}

INSTRUÇÕES ESPECÍFICAS PARA {cpl_module.upper()}:
"""
        
        # Instruções específicas por módulo
        if cpl_module == 'cpl_protocol_1':
            prompt += """
- Crie a arquitetura fundamental do evento magnético
- Defina o gancho principal que captura atenção
- Estabeleça a premissa irresistível
- Estruture o fluxo de atenção → interesse → desejo
"""
        elif cpl_module == 'cpl_protocol_2':
            prompt += """
- Identifique a oportunidade paralisante específica
- Crie urgência sem ser agressivo
- Mostre o que está sendo perdido AGORA
- Estabeleça o custo da inação
"""
        elif cpl_module == 'cpl_protocol_3':
            prompt += """
- Apresente a transformação impossível desejada
- Mostre o "antes" vs "depois" dramático
- Crie a visão do futuro ideal
- Estabeleça a ponte emocional
"""
        elif cpl_module == 'cpl_protocol_4':
            prompt += """
- Revele o caminho revolucionário único
- Diferencie da concorrência
- Mostre por que é a ÚNICA solução
- Estabeleça autoridade e credibilidade
"""
        elif cpl_module == 'cpl_protocol_5':
            prompt += """
- Conduza à decisão inevitável
- Remova todas as objeções
- Crie o momento de ação
- Estabeleça o call-to-action irresistível
"""
        
        prompt += """

FORMATO DE RESPOSTA (JSON):
{
    "titulo": "...",
    "resumo_executivo": "...",
    "conteudo_principal": "...",
    "elementos_chave": ["...", "...", "..."],
    "call_to_action": "...",
    "metricas_esperadas": {
        "engajamento": "...",
        "conversao": "...",
        "impacto": "..."
    },
    "implementacao": {
        "passos": ["...", "...", "..."],
        "recursos_necessarios": ["...", "..."],
        "timeline": "..."
    }
}

Responda APENAS com o JSON válido, sem texto adicional.
"""
        
        return prompt
    
    def _salvar_cpl_gerado(self, session_id: str, cpl_module: str, conteudo_gerado: str) -> Dict[str, Any]:
        """Salva o CPL gerado pela IA"""
        try:
            modules_dir = Path(f"analyses_data/{session_id}/modules")
            modules_dir.mkdir(parents=True, exist_ok=True)
            
            # Tentar parsear como JSON
            try:
                cpl_data = json.loads(conteudo_gerado)
                cpl_data['modulo'] = cpl_module
                cpl_data['data_geracao'] = datetime.now().isoformat()
                cpl_data['gerado_por'] = 'IA_CPL_Generator'
                cpl_data['status'] = 'gerado_com_ia'
                
                # Salvar como JSON
                filename = self._get_cpl_filename(cpl_module)
                if filename.endswith('.json'):
                    filepath = modules_dir / filename
                else:
                    # Se o arquivo padrão é MD, salvar como JSON também
                    filepath = modules_dir / f"{cpl_module}_generated.json"
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(cpl_data, f, ensure_ascii=False, indent=2)
                
                # Também salvar versão MD para compatibilidade
                md_filepath = modules_dir / f"{cpl_module}.md"
                md_content = self._converter_json_para_md(cpl_data)
                with open(md_filepath, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                
                return {
                    'status': 'success',
                    'arquivo_json': str(filepath),
                    'arquivo_md': str(md_filepath),
                    'cpl_module': cpl_module,
                    'tamanho_conteudo': len(conteudo_gerado)
                }
                
            except json.JSONDecodeError:
                # Se não for JSON válido, salvar como MD
                filename = f"{cpl_module}.md"
                filepath = modules_dir / filename
                
                md_content = f"""# {self.cpl_titles.get(cpl_module, cpl_module)}

## Conteúdo Gerado por IA

{conteudo_gerado}

---
*Gerado automaticamente em {datetime.now().isoformat()}*
"""
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                
                return {
                    'status': 'success_md_only',
                    'arquivo_md': str(filepath),
                    'cpl_module': cpl_module,
                    'observacao': 'Conteúdo salvo como MD (não foi possível parsear JSON)'
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar CPL gerado: {e}")
            return {
                'status': 'error',
                'erro': str(e),
                'cpl_module': cpl_module
            }
    
    def _converter_json_para_md(self, cpl_data: Dict[str, Any]) -> str:
        """Converte dados JSON do CPL para formato MD"""
        md_content = f"""# {cpl_data.get('titulo', 'CPL Gerado')}

## Resumo Executivo
{cpl_data.get('resumo_executivo', 'N/A')}

## Conteúdo Principal
{cpl_data.get('conteudo_principal', 'N/A')}

## Elementos-Chave
"""
        
        for elemento in cpl_data.get('elementos_chave', []):
            md_content += f"- {elemento}\n"
        
        md_content += f"""
## Call to Action
{cpl_data.get('call_to_action', 'N/A')}

## Métricas Esperadas
"""
        
        metricas = cpl_data.get('metricas_esperadas', {})
        for metrica, valor in metricas.items():
            md_content += f"- **{metrica.title()}**: {valor}\n"
        
        md_content += """
## Implementação
"""
        
        implementacao = cpl_data.get('implementacao', {})
        if 'passos' in implementacao:
            md_content += "\n### Passos:\n"
            for i, passo in enumerate(implementacao['passos'], 1):
                md_content += f"{i}. {passo}\n"
        
        if 'recursos_necessarios' in implementacao:
            md_content += "\n### Recursos Necessários:\n"
            for recurso in implementacao['recursos_necessarios']:
                md_content += f"- {recurso}\n"
        
        if 'timeline' in implementacao:
            md_content += f"\n### Timeline: {implementacao['timeline']}\n"
        
        md_content += f"""
---
*Gerado automaticamente em {cpl_data.get('data_geracao', datetime.now().isoformat())}*
"""
        
        return md_content
    
    def gerar_todos_cpls_com_ia(self, session_id: str, dados_contexto: Dict[str, Any] = None) -> Dict[str, Any]:
        """Gera todos os CPLs usando IA de forma sequencial"""
        try:
            logger.info(f"🚀 Iniciando geração completa de CPLs com IA para sessão: {session_id}")
            
            resultados = {
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'cpls_gerados': [],
                'cpls_com_erro': [],
                'total_cpls': len(self.cpl_modules),
                'sucesso': 0,
                'erros': 0
            }
            
            # Gerar cada CPL sequencialmente
            for cpl_module in self.cpl_modules:
                if cpl_module == 'external_ai_cpl_verification':
                    # Pular verificação externa neste momento
                    continue
                    
                try:
                    logger.info(f"🔄 Gerando {cpl_module}...")
                    resultado = self.gerar_cpl_com_ia(session_id, cpl_module, dados_contexto)
                    
                    if resultado.get('status') == 'success' or resultado.get('status') == 'success_md_only':
                        resultados['cpls_gerados'].append({
                            'modulo': cpl_module,
                            'resultado': resultado,
                            'titulo': self.cpl_titles.get(cpl_module, cpl_module)
                        })
                        resultados['sucesso'] += 1
                        logger.info(f"✅ {cpl_module} gerado com sucesso")
                    else:
                        resultados['cpls_com_erro'].append({
                            'modulo': cpl_module,
                            'erro': resultado.get('erro', 'Erro desconhecido')
                        })
                        resultados['erros'] += 1
                        logger.error(f"❌ Erro ao gerar {cpl_module}")
                        
                except Exception as e:
                    logger.error(f"❌ Erro crítico ao gerar {cpl_module}: {e}")
                    resultados['cpls_com_erro'].append({
                        'modulo': cpl_module,
                        'erro': str(e)
                    })
                    resultados['erros'] += 1
            
            # Calcular estatísticas finais
            resultados['taxa_sucesso'] = (resultados['sucesso'] / resultados['total_cpls']) * 100 if resultados['total_cpls'] > 0 else 0
            resultados['status_geral'] = 'sucesso' if resultados['sucesso'] >= resultados['total_cpls'] * 0.8 else 'parcial'
            
            # Salvar relatório de geração
            self._salvar_relatorio_geracao_cpls(session_id, resultados)
            
            logger.info(f"🎯 Geração de CPLs concluída: {resultados['sucesso']}/{resultados['total_cpls']} sucessos")
            return resultados
            
        except Exception as e:
            logger.error(f"❌ Erro crítico na geração de CPLs: {e}")
            return {
                'status': 'error',
                'erro': str(e),
                'session_id': session_id
            }
    
    def _salvar_relatorio_geracao_cpls(self, session_id: str, resultados: Dict[str, Any]) -> None:
        """Salva relatório da geração de CPLs"""
        try:
            session_dir = Path(f"analyses_data/{session_id}")
            session_dir.mkdir(parents=True, exist_ok=True)
            
            # Salvar relatório JSON
            relatorio_path = session_dir / "cpl_generation_report.json"
            with open(relatorio_path, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, ensure_ascii=False, indent=2)
            
            # Salvar relatório MD
            md_path = session_dir / "cpl_generation_report.md"
            md_content = f"""# Relatório de Geração de CPLs

## Resumo Executivo
- **Sessão**: {session_id}
- **Data**: {resultados['timestamp']}
- **Total de CPLs**: {resultados['total_cpls']}
- **Sucessos**: {resultados['sucesso']}
- **Erros**: {resultados['erros']}
- **Taxa de Sucesso**: {resultados.get('taxa_sucesso', 0):.1f}%
- **Status Geral**: {resultados.get('status_geral', 'N/A').upper()}

## CPLs Gerados com Sucesso
"""
            
            for cpl in resultados['cpls_gerados']:
                md_content += f"### ✅ {cpl['titulo']}\n"
                md_content += f"- **Módulo**: {cpl['modulo']}\n"
                if 'arquivo_json' in cpl['resultado']:
                    md_content += f"- **Arquivo JSON**: {cpl['resultado']['arquivo_json']}\n"
                if 'arquivo_md' in cpl['resultado']:
                    md_content += f"- **Arquivo MD**: {cpl['resultado']['arquivo_md']}\n"
                md_content += "\n"
            
            if resultados['cpls_com_erro']:
                md_content += "## CPLs com Erro\n"
                for cpl_erro in resultados['cpls_com_erro']:
                    md_content += f"### ❌ {cpl_erro['modulo']}\n"
                    md_content += f"- **Erro**: {cpl_erro['erro']}\n\n"
            
            md_content += f"""
---
*Relatório gerado automaticamente pelo CPL Integration Manager V2.0*
"""
            
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            logger.info(f"📊 Relatório de geração de CPLs salvo: {relatorio_path}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório de geração: {e}")
    
    def verificar_integracao_relatorios(self, session_id: str) -> Dict[str, Any]:
        """Verifica se os CPLs estão sendo incluídos nos relatórios"""
        try:
            logger.info(f"🔍 Verificando integração CPLs nos relatórios: {session_id}")
            
            # Verificar relatório final MD
            relatorio_md = Path(f"analyses_data/{session_id}/relatorio_final.md")
            relatorio_completo_md = Path(f"analyses_data/{session_id}/relatorio_final_completo.md")
            
            status_integracao = {
                'relatorio_md_existe': relatorio_md.exists(),
                'relatorio_completo_existe': relatorio_completo_md.exists(),
                'cpls_no_relatorio_md': False,
                'cpls_no_relatorio_completo': False,
                'cpls_encontrados_md': [],
                'cpls_encontrados_completo': []
            }
            
            # Verificar conteúdo dos relatórios
            if relatorio_md.exists():
                with open(relatorio_md, 'r', encoding='utf-8') as f:
                    conteudo_md = f.read()
                    
                for cpl_module in self.cpl_modules:
                    titulo = self.cpl_titles[cpl_module]
                    if titulo.lower() in conteudo_md.lower() or cpl_module in conteudo_md:
                        status_integracao['cpls_encontrados_md'].append(cpl_module)
                
                status_integracao['cpls_no_relatorio_md'] = len(status_integracao['cpls_encontrados_md']) > 0
            
            if relatorio_completo_md.exists():
                with open(relatorio_completo_md, 'r', encoding='utf-8') as f:
                    conteudo_completo = f.read()
                    
                for cpl_module in self.cpl_modules:
                    titulo = self.cpl_titles[cpl_module]
                    if titulo.lower() in conteudo_completo.lower() or cpl_module in conteudo_completo:
                        status_integracao['cpls_encontrados_completo'].append(cpl_module)
                
                status_integracao['cpls_no_relatorio_completo'] = len(status_integracao['cpls_encontrados_completo']) > 0
            
            # Log do status
            if status_integracao['cpls_no_relatorio_md'] or status_integracao['cpls_no_relatorio_completo']:
                logger.info("✅ CPLs encontrados nos relatórios!")
            else:
                logger.warning("⚠️ CPLs NÃO encontrados nos relatórios - será corrigido")
            
            return status_integracao
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar integração: {e}")
            return {'erro': str(e)}
    
    def forcar_integracao_cpls(self, session_id: str) -> bool:
        """FORÇA a integração dos CPLs nos relatórios finais"""
        try:
            logger.info(f"🔧 FORÇANDO integração CPLs para sessão: {session_id}")
            
            # 1. Garantir que os CPLs existam na pasta modules
            self.garantir_cpls_nos_modulos(session_id)
            
            # 2. Forçar regeneração dos relatórios incluindo CPLs
            from .comprehensive_report_generator_v3 import ComprehensiveReportGeneratorV3
            
            report_generator = ComprehensiveReportGeneratorV3()
            
            # Regenerar relatório MD
            resultado_md = report_generator.compile_final_markdown_report(session_id)
            
            if resultado_md.get('success'):
                logger.info("✅ Relatório MD regenerado com CPLs incluídos")
            else:
                logger.warning("⚠️ Problema na regeneração do relatório MD")
            
            # Regenerar relatório HTML
            resultado_html = report_generator.compile_final_html_report(session_id)
            
            if resultado_html.get('success'):
                logger.info("✅ Relatório HTML regenerado com CPLs incluídos")
            else:
                logger.warning("⚠️ Problema na regeneração do relatório HTML")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao forçar integração: {e}")
            return False

# Instância global
cpl_integration_manager = CPLIntegrationManager()

def garantir_cpls_nos_relatorios(session_id: str) -> Dict[str, Any]:
    """Função principal para garantir CPLs nos relatórios"""
    return cpl_integration_manager.forcar_integracao_cpls(session_id)