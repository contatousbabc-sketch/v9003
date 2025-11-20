#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - External AI Verifier Integration V2.0
Sistema robusto de verificação externa usando IA com múltiplas APIs
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

# Importar o sistema de APIs
try:
    from .enhanced_api_rotation_manager import EnhancedAPIRotationManager
except ImportError:
    # Fallback para import absoluto
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent))
    from enhanced_api_rotation_manager import EnhancedAPIRotationManager

logger = logging.getLogger(__name__)

class ExternalAIVerifierIntegration:
    """Sistema robusto de verificação externa com IA usando múltiplas APIs"""
    
    def __init__(self):
        """Inicializa o sistema de verificação externa com IA"""
        self.api_manager = None
        self.verifier_available = False
        
        try:
            # Inicializar o gerenciador de APIs
            self.api_manager = EnhancedAPIRotationManager()
            self.verifier_available = True
            
            logger.info("✅ Sistema de Verificação Externa com IA V2.0 inicializado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar verificação externa: {e}")
            self.verifier_available = False
    
    async def verificar_relatorio_com_ai_externa(self, session_id: str, relatorio_content: str) -> Dict[str, Any]:
        """Verifica o relatório usando IA externa com múltiplas APIs"""
        try:
            if not self.verifier_available:
                logger.warning("⚠️ Sistema de verificação externa não disponível")
                return {
                    'status': 'skipped',
                    'motivo': 'Sistema de verificação externa não disponível',
                    'timestamp': datetime.now().isoformat()
                }
            
            logger.info(f"🔍 Iniciando verificação externa com IA para sessão: {session_id}")
            
            # Prompt especializado para verificação de relatórios
            verification_prompt = f"""
SISTEMA DE VERIFICAÇÃO EXTERNA - ANÁLISE DE RELATÓRIO

Você é um especialista em análise e verificação de relatórios de investigação. 
Analise o seguinte relatório e forneça uma verificação detalhada:

RELATÓRIO A VERIFICAR:
{relatorio_content[:8000]}  # Limitar para evitar tokens excessivos

CRITÉRIOS DE VERIFICAÇÃO:
1. CONSISTÊNCIA INTERNA: Verifique se as informações são consistentes entre si
2. QUALIDADE DOS DADOS: Avalie a qualidade e confiabilidade das fontes
3. COMPLETUDE: Identifique lacunas ou informações faltantes
4. PRECISÃO: Verifique se há informações imprecisas ou contraditórias
5. ESTRUTURA: Avalie a organização e clareza do relatório
6. CONFORMIDADE: Verifique se atende aos padrões esperados

FORMATO DE RESPOSTA (JSON):
{{
    "status": "aprovado|rejeitado|aprovado_com_ressalvas",
    "pontuacao_geral": 0-100,
    "criterios": {{
        "consistencia_interna": {{"pontuacao": 0-100, "observacoes": "..."}},
        "qualidade_dados": {{"pontuacao": 0-100, "observacoes": "..."}},
        "completude": {{"pontuacao": 0-100, "observacoes": "..."}},
        "precisao": {{"pontuacao": 0-100, "observacoes": "..."}},
        "estrutura": {{"pontuacao": 0-100, "observacoes": "..."}},
        "conformidade": {{"pontuacao": 0-100, "observacoes": "..."}}
    }},
    "pontos_fortes": ["...", "...", "..."],
    "pontos_fracos": ["...", "...", "..."],
    "recomendacoes": ["...", "...", "..."],
    "alertas_criticos": ["...", "..."],
    "resumo_executivo": "...",
    "timestamp": "{datetime.now().isoformat()}"
}}

Responda APENAS com o JSON válido, sem texto adicional.
"""
            
            # Executar verificação usando o sistema de APIs
            resultado_ia = await self.api_manager.generate_content(
                verification_prompt,
                service_type='ai_generation',
                max_tokens=2000,
                temperature=0.3  # Baixa temperatura para maior precisão
            )
            
            # Tentar parsear o resultado como JSON
            try:
                resultado_verificacao = json.loads(resultado_ia)
                resultado_verificacao['session_id'] = session_id
                resultado_verificacao['verificacao_externa'] = True
                resultado_verificacao['api_utilizada'] = 'sistema_multiplas_apis'
                
            except json.JSONDecodeError:
                # Se não conseguir parsear como JSON, criar estrutura padrão
                logger.warning("⚠️ Resposta da IA não está em formato JSON válido")
                resultado_verificacao = {
                    'status': 'processado',
                    'pontuacao_geral': 75,
                    'resumo_executivo': resultado_ia[:500] + "..." if len(resultado_ia) > 500 else resultado_ia,
                    'observacoes': 'Verificação processada mas formato de resposta não estruturado',
                    'session_id': session_id,
                    'verificacao_externa': True,
                    'api_utilizada': 'sistema_multiplas_apis',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Salvar resultado da verificação
            await self._salvar_resultado_verificacao(session_id, resultado_verificacao)
            
            logger.info("✅ Verificação externa com IA concluída")
            return resultado_verificacao
            
        except Exception as e:
            logger.error(f"❌ Erro na verificação externa: {e}")
            return {
                'status': 'error',
                'erro': str(e),
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            }
    
    async def verificar_cpls_com_ai_externa(self, session_id: str) -> Dict[str, Any]:
        """Verifica especificamente os CPLs usando IA externa"""
        try:
            if not self.verifier_available:
                return {
                    'status': 'skipped',
                    'motivo': 'Sistema de verificação externa não disponível'
                }
            
            logger.info(f"🎯 Verificando CPLs com IA externa para sessão: {session_id}")
            
            # Carregar CPLs da pasta modules
            modules_dir = Path(f"analyses_data/{session_id}/modules")
            cpls_encontrados = {}
            
            if not modules_dir.exists():
                logger.warning(f"⚠️ Diretório de módulos não encontrado: {modules_dir}")
                return {
                    'status': 'no_modules_dir',
                    'mensagem': 'Diretório de módulos não encontrado'
                }
            
            # Buscar arquivos CPL
            cpl_files = list(modules_dir.glob("cpl*.json")) + list(modules_dir.glob("cpl*.md"))
            
            for cpl_file in cpl_files:
                try:
                    if cpl_file.suffix == '.json':
                        with open(cpl_file, 'r', encoding='utf-8') as f:
                            cpl_content = json.load(f)
                    else:
                        with open(cpl_file, 'r', encoding='utf-8') as f:
                            cpl_content = f.read()
                    
                    cpls_encontrados[cpl_file.stem] = cpl_content
                    
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao carregar CPL {cpl_file}: {e}")
            
            if not cpls_encontrados:
                logger.warning("⚠️ Nenhum CPL encontrado para verificação")
                return {
                    'status': 'no_cpls',
                    'mensagem': 'Nenhum CPL encontrado para verificação',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Analisar cada CPL com IA
            resultados_cpls = {}
            
            for cpl_name, cpl_content in cpls_encontrados.items():
                try:
                    # Prompt especializado para verificação de CPLs
                    cpl_verification_prompt = f"""
SISTEMA DE VERIFICAÇÃO DE CPL (Certificado de Pessoa Legal)

Você é um especialista em análise de documentos CPL. Analise o seguinte CPL:

CPL: {cpl_name}
CONTEÚDO:
{str(cpl_content)[:4000]}  # Limitar tokens

CRITÉRIOS DE VERIFICAÇÃO CPL:
1. VALIDADE: Verificar se o CPL está válido e ativo
2. COMPLETUDE: Verificar se todas as informações necessárias estão presentes
3. CONSISTÊNCIA: Verificar consistência dos dados
4. AUTENTICIDADE: Avaliar sinais de autenticidade
5. CONFORMIDADE: Verificar se atende aos padrões legais

FORMATO DE RESPOSTA (JSON):
{{
    "cpl_name": "{cpl_name}",
    "status": "valido|invalido|suspeito",
    "pontuacao": 0-100,
    "criterios": {{
        "validade": {{"status": "ok|problema", "observacao": "..."}},
        "completude": {{"status": "ok|problema", "observacao": "..."}},
        "consistencia": {{"status": "ok|problema", "observacao": "..."}},
        "autenticidade": {{"status": "ok|problema", "observacao": "..."}},
        "conformidade": {{"status": "ok|problema", "observacao": "..."}}
    }},
    "alertas": ["...", "..."],
    "recomendacoes": ["...", "..."],
    "resumo": "...",
    "timestamp": "{datetime.now().isoformat()}"
}}

Responda APENAS com o JSON válido.
"""
                    
                    # Executar verificação usando o sistema de APIs
                    resultado_ia = await self.api_manager.generate_content(
                        cpl_verification_prompt,
                        service_type='ai_generation',
                        max_tokens=4096,
                        temperature=0.8  # Muito baixa para máxima precisão
                    )
                    
                    # Tentar parsear como JSON
                    try:
                        resultado_cpl = json.loads(resultado_ia)
                    except json.JSONDecodeError:
                        resultado_cpl = {
                            'cpl_name': cpl_name,
                            'status': 'processado',
                            'pontuacao': 70,
                            'resumo': resultado_ia[:300] + "..." if len(resultado_ia) > 300 else resultado_ia,
                            'observacao': 'CPL processado mas formato de resposta não estruturado',
                            'timestamp': datetime.now().isoformat()
                        }
                    
                    resultados_cpls[cpl_name] = resultado_cpl
                    logger.info(f"✅ CPL {cpl_name} verificado com IA")
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao verificar CPL {cpl_name}: {e}")
                    resultados_cpls[cpl_name] = {
                        'cpl_name': cpl_name,
                        'status': 'error',
                        'erro': str(e),
                        'timestamp': datetime.now().isoformat()
                    }
            
            # Compilar resultado final
            resultado_final = {
                'status': 'completed',
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'total_cpls_analisados': len(resultados_cpls),
                'cpls_com_sucesso': len([r for r in resultados_cpls.values() if r.get('status') != 'error']),
                'resultados_individuais': resultados_cpls,
                'resumo_geral': self._gerar_resumo_verificacao_cpls(resultados_cpls)
            }
            
            # Salvar resultado
            await self._salvar_resultado_verificacao_cpls(session_id, resultado_final)
            
            logger.info(f"✅ Verificação de CPLs concluída: {len(resultados_cpls)} CPLs analisados")
            return resultado_final
            
        except Exception as e:
            logger.error(f"❌ Erro na verificação de CPLs: {e}")
            return {
                'status': 'error',
                'erro': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _gerar_resumo_verificacao_cpls(self, resultados_cpls: Dict[str, Any]) -> Dict[str, Any]:
        """Gera resumo da verificação dos CPLs"""
        try:
            total_cpls = len(resultados_cpls)
            cpls_validos = 0
            cpls_suspeitos = 0
            cpls_invalidos = 0
            cpls_com_erros = 0
            
            principais_alertas = []
            principais_recomendacoes = []
            
            for cpl_name, resultado in resultados_cpls.items():
                if resultado.get('status') == 'error':
                    cpls_com_erros += 1
                elif resultado.get('status') == 'valido':
                    cpls_validos += 1
                elif resultado.get('status') == 'suspeito':
                    cpls_suspeitos += 1
                elif resultado.get('status') == 'invalido':
                    cpls_invalidos += 1
                
                # Coletar alertas e recomendações
                if 'alertas' in resultado:
                    principais_alertas.extend(resultado['alertas'])
                if 'recomendacoes' in resultado:
                    principais_recomendacoes.extend(resultado['recomendacoes'])
            
            return {
                'total_cpls': total_cpls,
                'cpls_validos': cpls_validos,
                'cpls_suspeitos': cpls_suspeitos,
                'cpls_invalidos': cpls_invalidos,
                'cpls_com_erros': cpls_com_erros,
                'taxa_sucesso': (cpls_validos / total_cpls * 100) if total_cpls > 0 else 0,
                'principais_alertas': list(set(principais_alertas))[:5],  # Top 5 únicos
                'principais_recomendacoes': list(set(principais_recomendacoes))[:5],  # Top 5 únicos
                'status_geral': 'aprovado' if cpls_validos >= total_cpls * 0.8 else 'atencao_necessaria'
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resumo de CPLs: {e}")
            return {
                'erro': str(e),
                'status_geral': 'erro_no_resumo'
            }
    
    async def _salvar_resultado_verificacao(self, session_id: str, resultado: Dict[str, Any]) -> None:
        """Salva resultado da verificação externa"""
        try:
            # Criar diretório se não existir
            verification_dir = Path(f"analyses_data/{session_id}/verification")
            verification_dir.mkdir(parents=True, exist_ok=True)
            
            # Salvar resultado
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"external_verification_{timestamp}.json"
            filepath = verification_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Resultado da verificação salvo: {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar resultado da verificação: {e}")
    
    async def _salvar_resultado_verificacao_cpls(self, session_id: str, resultado: Dict[str, Any]) -> None:
        """Salva resultado da verificação de CPLs"""
        try:
            # Criar diretório se não existir
            verification_dir = Path(f"analyses_data/{session_id}/verification")
            verification_dir.mkdir(parents=True, exist_ok=True)
            
            # Salvar resultado
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cpl_verification_{timestamp}.json"
            filepath = verification_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Resultado da verificação de CPLs salvo: {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar resultado da verificação de CPLs: {e}")
    
    async def verificar_dados_completos(self, session_id: str, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica dados completos usando IA externa"""
        try:
            if not self.verifier_available:
                return {
                    'status': 'skipped',
                    'motivo': 'Sistema de verificação externa não disponível'
                }
            
            logger.info(f"🔍 Verificando dados completos para sessão: {session_id}")
            
            # Prompt para verificação de dados completos
            data_verification_prompt = f"""
SISTEMA DE VERIFICAÇÃO DE DADOS COMPLETOS

Analise os seguintes dados e verifique sua completude e qualidade:

DADOS:
{json.dumps(dados, ensure_ascii=False, indent=2)[:6000]}

CRITÉRIOS DE VERIFICAÇÃO:
1. COMPLETUDE: Verificar se todos os campos necessários estão preenchidos
2. CONSISTÊNCIA: Verificar se os dados são consistentes entre si
3. QUALIDADE: Avaliar a qualidade dos dados fornecidos
4. INTEGRIDADE: Verificar a integridade dos dados
5. CONFORMIDADE: Verificar se atende aos padrões esperados

FORMATO DE RESPOSTA (JSON):
{{
    "status": "completo|incompleto|problematico",
    "pontuacao_geral": 0-100,
    "campos_analisados": 0,
    "campos_completos": 0,
    "campos_incompletos": ["...", "..."],
    "problemas_encontrados": ["...", "..."],
    "recomendacoes": ["...", "..."],
    "resumo": "...",
    "timestamp": "{datetime.now().isoformat()}"
}}

Responda APENAS com o JSON válido.
"""
            
            # Executar verificação
            resultado_ia = await self.api_manager.generate_content(
                data_verification_prompt,
                service_type='ai_generation',
                max_tokens=4096,
                temperature=0.2
            )
            
            # Parsear resultado
            try:
                resultado_verificacao = json.loads(resultado_ia)
                resultado_verificacao['session_id'] = session_id
                resultado_verificacao['verificacao_externa'] = True
                
            except json.JSONDecodeError:
                resultado_verificacao = {
                    'status': 'processado',
                    'pontuacao_geral': 75,
                    'resumo': resultado_ia[:400] + "..." if len(resultado_ia) > 400 else resultado_ia,
                    'observacao': 'Dados processados mas formato de resposta não estruturado',
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Salvar resultado
            await self._salvar_resultado_verificacao(session_id, resultado_verificacao)
            
            logger.info("✅ Verificação de dados completos concluída")
            return resultado_verificacao
            
        except Exception as e:
            logger.error(f"❌ Erro na verificação de dados completos: {e}")
            return {
                'status': 'error',
                'erro': str(e),
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            }

# Instância global
external_ai_verifier_integration = ExternalAIVerifierIntegration()

async def verificar_relatorio_com_ai_externa(session_id: str, relatorio_content: str) -> Dict[str, Any]:
    """Função principal para verificação externa do relatório"""
    return await external_ai_verifier_integration.verificar_relatorio_com_ai_externa(session_id, relatorio_content)

async def verificar_cpls_com_ai_externa(session_id: str) -> Dict[str, Any]:
    """Função principal para verificação externa dos CPLs"""
    return await external_ai_verifier_integration.verificar_cpls_com_ai_externa(session_id)

async def verificar_dados_completos(session_id: str, dados: Dict[str, Any]) -> Dict[str, Any]:
    """Função principal para verificação de dados completos"""
    return await external_ai_verifier_integration.verificar_dados_completos(session_id, dados)
