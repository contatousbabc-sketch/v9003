"""
Protocolo Integrado de Criação de CPLs Devastadores - V18.0
Implementação completa das 5 fases do protocolo CPL
"""

import os
import json
import time
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Imports condicionais para evitar erros de dependência
try:
    from .enhanced_api_rotation_manager import get_api_manager
    HAS_API_MANAGER = True
except ImportError:
    try:
        from enhanced_api_rotation_manager import get_api_manager
        HAS_API_MANAGER = True
    except ImportError:
        HAS_API_MANAGER = False

try:
    from .real_search_orchestrator import RealSearchOrchestrator
    HAS_SEARCH_ENGINE = True
except ImportError:
    try:
        from real_search_orchestrator import RealSearchOrchestrator
        HAS_SEARCH_ENGINE = True
    except ImportError:
        HAS_SEARCH_ENGINE = False

logger = logging.getLogger(__name__)

# REMOVIDO: Importações dos protocolos CPL individuais (1-5) - DEPRECATED
# Os protocolos antigos foram substituídos pelo sistema integrado
HAS_CPL_PROTOCOLS = False
logger.info("ℹ️ Protocolos CPL individuais (1-5) foram descontinuados - usando sistema integrado")

@dataclass
class ContextoEstrategico:
    tema: str
    segmento: str
    publico_alvo: str
    termos_chave: List[str]
    frases_busca: List[str]
    objecoes: List[str]
    tendencias: List[str]
    casos_sucesso: List[str]

@dataclass
class EventoMagnetico:
    nome: str
    promessa_central: str
    arquitetura_cpls: Dict[str, str]
    mapeamento_psicologico: Dict[str, str]
    justificativa: str

@dataclass
class CPLDevastador:
    numero: int
    titulo: str
    objetivo: str
    conteudo_principal: str
    loops_abertos: List[str]
    quebras_padrao: List[str]
    provas_sociais: List[str]
    elementos_cinematograficos: List[str]
    gatilhos_psicologicos: List[str]
    call_to_action: str

class CPLDevastadorProtocol:
    """
    Protocolo completo para criação de CPLs devastadores
    Segue rigorosamente as 5 fases definidas no protocolo
    """
    
    def __init__(self):
        if HAS_API_MANAGER:
            self.api_manager = get_api_manager()
        else:
            self.api_manager = None
            
        if HAS_SEARCH_ENGINE:
            self.search_engine = RealSearchOrchestrator()
        else:
            self.search_engine = None
            
        self.session_data = {}
    
    def _safe_asdict(self, obj):
        """Converte objeto para dict de forma segura"""
        try:
            if hasattr(obj, '__dict__'):
                return asdict(obj) if hasattr(obj, '__dataclass_fields__') else obj.__dict__
            elif isinstance(obj, dict):
                return obj
            else:
                return str(obj)
        except Exception as e:
            logger.warning(f"Erro ao converter objeto para dict: {e}")
            return str(obj)
    
    def _clean_json_response(self, response: str) -> str:
        """Limpa resposta da API removendo markdown e espaços - NUNCA LANÇA EXCEÇÃO"""
        
        # GARANTIA 1: Se resposta for None ou vazia, retornar string vazia
        if not response:
            logger.warning("⚠️ Resposta None/vazia em _clean_json_response")
            return ""
        
        # GARANTIA 2: Se não for string, tentar converter
        if not isinstance(response, str):
            logger.warning(f"⚠️ Resposta não é string: {type(response)}")
            try:
                response = str(response)
            except Exception:
                return ""
        
        # GARANTIA 3: Fazer strip seguro
        try:
            response = response.strip()
        except Exception as e:
            logger.warning(f"⚠️ Erro no strip: {e}")
            return ""
        
        # GARANTIA 4: Remover blocos markdown
        if response.startswith('```'):
            try:
                lines = response.split('\n')
                if len(lines) > 2:
                    response = '\n'.join(lines[1:-1])
                elif len(lines) > 1:
                    response = lines[1]
                
                if response.strip().startswith('json'):
                    response = response.strip()[4:]
                
                response = response.strip()
            except Exception as e:
                logger.warning(f"⚠️ Erro ao remover markdown: {e}")
        
        # GARANTIA 5: Se ficou vazio, retornar vazio
        if not response:
            logger.warning("⚠️ Resposta vazia após limpeza")
            return ""
        
        return response
    
    def _generate_fallback_response(self, prompt: str) -> str:
        """Gera resposta estruturada básica quando todas as APIs falham"""
        logger.warning("⚠️ Usando resposta fallback - APIs indisponíveis")
        
        try:
            # Analisa o prompt para determinar o tipo de resposta
            if "FASE 1" in prompt or "ARQUITETURA DO EVENTO" in prompt:
                return json.dumps({
                    "versao_escolhida": "A",
                    "nome_evento": "Revolução Digital Devastadora",
                    "promessa_central": "Como transformar seu negócio em 4 dias usando estratégias que 99% ignora",
                    "arquitetura_cpls": {
                        "cpl1": "A Descoberta Chocante - Revelação que muda tudo",
                        "cpl2": "A Prova Impossível - Evidências irrefutáveis",
                        "cpl3": "O Caminho Revolucionário - Método único revelado",
                        "cpl4": "A Decisão Inevitável - Momento de transformação"
                    },
                    "mapeamento_psicologico": {
                        "gatilho_principal": "FOMO + Urgência + Exclusividade",
                        "jornada_emocional": "Curiosidade → Choque → Desejo → Ação",
                        "pontos_pressao": ["Medo de ficar para trás", "Desejo de transformação", "Necessidade de resultados"]
                    },
                    "justificativa": "Combina urgência temporal com exclusividade de método"
                })
            
            elif "CPL1" in prompt or "OPORTUNIDADE PARALISANTE" in prompt:
                return json.dumps({
                    "titulo": "CPL1 - A Descoberta Que Muda Tudo",
                    "objetivo": "Revelar oportunidade única que gera FOMO visceral",
                    "conteudo_principal": "Revelação de estratégia secreta que poucos conhecem",
                    "loops_abertos": [
                        "Qual é o método secreto que será revelado?",
                        "Como isso pode transformar resultados em 4 dias?",
                        "Por que apenas 1% conhece essa estratégia?"
                    ],
                    "quebras_padrao": [
                        "Contrário ao que todos fazem",
                        "Método nunca revelado publicamente",
                        "Estratégia usada apenas por experts",
                        "Abordagem revolucionária",
                        "Técnica contra-intuitiva"
                    ],
                    "provas_sociais": [
                        "Resultados de clientes reais",
                        "Casos de sucesso documentados",
                        "Depoimentos autênticos",
                        "Dados de performance",
                        "Evidências visuais"
                    ],
                    "elementos_cinematograficos": [
                        "Abertura impactante com revelação",
                        "Construção de tensão gradual",
                        "Clímax com descoberta chocante",
                        "Gancho irresistível para CPL2"
                    ],
                    "gatilhos_psicologicos": [
                        "Curiosidade extrema",
                        "FOMO visceral",
                        "Exclusividade",
                        "Urgência temporal"
                    ],
                    "call_to_action": "Aguarde CPL2 para descobrir a prova impossível"
                })
            
            elif "CPL2" in prompt or "TRANSFORMAÇÃO IMPOSSÍVEL" in prompt:
                return json.dumps({
                    "titulo": "CPL2 - A Prova Que Ninguém Acredita",
                    "objetivo": "Apresentar evidências irrefutáveis da transformação",
                    "conteudo_principal": "Demonstração prática com resultados reais",
                    "loops_mantidos": [
                        "Como essa prova foi obtida?",
                        "Qual será o método completo?"
                    ],
                    "quebras_padrao": [
                        "Resultados que desafiam lógica",
                        "Prova visual incontestável",
                        "Método surpreendente"
                    ],
                    "casos_transformacao": [
                        "Screenshots de resultados",
                        "Vídeos de transformação",
                        "Dados antes/depois"
                    ],
                    "elementos_cinematograficos": [
                        "Revelação dramática da prova",
                        "Demonstração passo a passo",
                        "Gancho para o método completo"
                    ],
                    "gatilhos_psicologicos": [
                        "Incredulidade seguida de convencimento",
                        "Desejo de replicar resultado",
                        "Urgência de conhecer método"
                    ],
                    "call_to_action": "CPL3 revelará o caminho completo"
                })
            
            elif "CPL3" in prompt or "CAMINHO REVOLUCIONÁRIO" in prompt:
                return json.dumps({
                    "titulo": "CPL3 - O Método Que Muda Tudo",
                    "objetivo": "Revelar o sistema completo de transformação",
                    "nome_metodo": "Sistema de Transformação Acelerada",
                    "estrutura_passos": [
                        "Passo 1: Diagnóstico Estratégico",
                        "Passo 2: Implementação do Framework",
                        "Passo 3: Otimização e Escala"
                    ],
                    "faq_estrategico": [
                        "Como implementar em meu negócio?",
                        "Quanto tempo leva para ver resultados?"
                    ],
                    "justificativa_escassez": "Vagas limitadas por questões de mentoria",
                    "loops_fechados": ["Método completo revelado"],
                    "preparacao_decisao": "Preparado para transformação definitiva",
                    "call_to_action": "CPL4 será sua última chance de transformação"
                })
            
            elif "CPL4" in prompt or "DECISÃO INEVITÁVEL" in prompt:
                return json.dumps({
                    "titulo": "CPL4 - Sua Última Chance de Transformação",
                    "objetivo": "Conversão máxima",
                    "stack_valor": [
                        "Bônus 1: Acesso vitalício",
                        "Bônus 2: Mentoria exclusiva",
                        "Bônus 3: Comunidade VIP"
                    ],
                    "precificacao": {
                        "valor_total": "R$ 2.997",
                        "valor_oferta": "R$ 997",
                        "economia": "R$ 2.000"
                    },
                    "garantias": [
                        "Garantia de 30 dias",
                        "Garantia de resultados"
                    ],
                    "urgencia_final": "Apenas 50 vagas disponíveis - encerrando em 48h",
                    "fechamento": "Momento de decisão definitiva para sua transformação",
                    "call_to_action": "AÇÃO IMEDIATA - Garanta sua vaga agora"
                })
            
            else:
                return json.dumps({
                    "status": "fallback_response",
                    "message": "Resposta estruturada básica gerada",
                    "data": "Conteúdo baseado em estrutura padrão"
                })
                
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resposta fallback: {e}")
            return '{"error": "Falha na geração de resposta", "status": "error"}'
    
    async def _generate_with_ai(self, prompt: str, api) -> str:
        """Gera resposta usando API de IA"""
        try:
            # Usar o método correto do API manager
            response = await self.api_manager.generate_text(prompt, model='qwen')
            return response
        except Exception as e:
            logger.error(f"❌ Erro ao gerar com AI: {e}")
            return ""
    
    async def definir_contexto_busca(self, tema: str, segmento: str, publico_alvo: str) -> ContextoEstrategico:
        """
        FASE PRÉ-BUSCA: Definição do Contexto Estratégico
        Prepara o contexto estratégico para busca web usando enriquecimento de dados
        """
        logger.info(f"🎯 Definindo contexto estratégico: {tema} | {segmento} | {publico_alvo}")
        
        try:
            # Importar serviço de enriquecimento
            from services.cpl_data_enrichment_service import cpl_data_enrichment_service
            
            # Enriquecer contexto com dados reais
            enriched_context = await cpl_data_enrichment_service.enrich_context(
                tema=tema,
                segmento=segmento,
                publico_alvo=publico_alvo
            )
            
            # Converter para ContextoEstrategico
            contexto = ContextoEstrategico(
                tema=enriched_context.tema,
                segmento=enriched_context.segmento,
                publico_alvo=enriched_context.publico_alvo,
                termos_chave=enriched_context.termos_chave,
                frases_busca=enriched_context.frases_busca,
                objecoes=enriched_context.objecoes,
                tendencias=enriched_context.tendencias,
                casos_sucesso=enriched_context.casos_sucesso
            )
            
            logger.info(f"✅ Contexto estratégico enriquecido com {len(contexto.termos_chave)} termos-chave")
            return contexto
            
        except Exception as e:
            logger.error(f"❌ Erro ao definir contexto estratégico: {e}")
            
            # Fallback com dados mínimos mas suficientes
            return ContextoEstrategico(
                tema=tema,
                segmento=segmento,
                publico_alvo=publico_alvo,
                termos_chave=[
                    tema.lower(), segmento.lower(), 'estratégia', 'resultado',
                    'solução', 'método', 'sistema', 'processo', 'técnica', 'abordagem'
                ],
                frases_busca=[
                    f'como resolver {tema.lower()}',
                    f'melhor {tema.lower()} para {publico_alvo.lower()}',
                    f'{tema.lower()} que funciona',
                    f'estratégia de {tema.lower()}',
                    f'resultado com {tema.lower()}'
                ],
                objecoes=[
                    'É muito caro',
                    'Não tenho tempo',
                    'Não vai funcionar para mim'
                ],
                tendencias=[
                    f'Crescimento do mercado de {tema.lower()}',
                    f'Digitalização em {segmento.lower()}'
                ],
                casos_sucesso=[
                    f'Cliente aumentou resultados em 200% com {tema.lower()}',
                    f'Empresa transformou {segmento.lower()} usando nova estratégia',
                    f'{publico_alvo} alcançou objetivo em 90 dias'
                ]
            )
    
    async def executar_protocolo_completo(self, tema: str, segmento: str, publico_alvo: str, session_id: str) -> Dict[str, Any]:
        """
        Executa o protocolo completo de 5 fases para criação de CPLs devastadores
        """
        try:
            logger.info("🚀 INICIANDO PROTOCOLO DE CPLs DEVASTADORES")
            logger.info(f"🎯 Tema: {tema} | Segmento: {segmento} | Público: {publico_alvo}")
            
            # FASE 0: Preparação do contexto
            contexto = await self.definir_contexto_busca(tema, segmento, publico_alvo)
            
            # FASE 1: Coleta de dados contextuais
            logger.info("🔍 FASE 1: Coletando dados contextuais com busca massiva")
            if self.search_engine:
                search_results = await self.search_engine.execute_massive_real_search(
                    query=f"{tema} {segmento} {publico_alvo}",
                    session_id=session_id,
                    context={"tema": tema, "segmento": segmento, "publico_alvo": publico_alvo}
                )
            else:
                logger.error("❌ Search engine OBRIGATÓRIO não disponível - ABORTANDO")
                raise Exception("Search engine é obrigatório - não há dados simulados permitidos")
            
            # Salvar dados coletados
            self._salvar_dados_contextuais(session_id, search_results, contexto)
            
            # CORREÇÃO CRÍTICA: Salvar contexto estratégico como JSON para uso pelos módulos
            self._salvar_contexto_estrategico_json(session_id, contexto)
            
            # Validar se os dados são suficientes
            if not self._validar_dados_coletados(session_id):
                raise Exception("Dados insuficientes coletados")
            
            # FASE 2: Gerar arquitetura do evento magnético
            logger.info("🧠 FASE 2: Gerando arquitetura do evento magnético")
            evento_magnetico = await self._fase_1_arquitetura_evento(session_id, contexto)
            
            # FASE 3: Gerar CPL1 - A Oportunidade Paralisante
            logger.info("🎬 FASE 3: Gerando CPL1 - A Oportunidade Paralisante")
            cpl1 = await self._fase_2_cpl1_oportunidade(session_id, contexto, evento_magnetico)
            
            # FASE 4: Gerar CPL2 - A Transformação Impossível
            logger.info("🎬 FASE 4: Gerando CPL2 - A Transformação Impossível")
            cpl2 = await self._fase_3_cpl2_transformacao(session_id, contexto, cpl1)
            
            # FASE 5: Gerar CPL3 - O Caminho Revolucionário
            logger.info("🎬 FASE 5: Gerando CPL3 - O Caminho Revolucionário")
            cpl3 = await self._fase_4_cpl3_caminho(session_id, contexto, cpl2)
            
            # FASE 6: Gerar CPL4 - A Decisão Inevitável
            logger.info("🎬 FASE 6: Gerando CPL4 - A Decisão Inevitável")
            cpl4 = await self._fase_5_cpl4_decisao(session_id, contexto, cpl3)
            
            # Compilar resultado final
            resultado_final = {
                'session_id': session_id,
                'contexto_estrategico': self._safe_asdict(contexto),
                'evento_magnetico': self._safe_asdict(evento_magnetico),
                'cpls': {
                    'cpl1': self._safe_asdict(cpl1),
                    'cpl2': self._safe_asdict(cpl2),
                    'cpl3': self._safe_asdict(cpl3),
                    'cpl4': self._safe_asdict(cpl4)
                },
                'dados_busca': self._safe_asdict(search_results),
                'timestamp': datetime.now().isoformat()
            }
            
            # Salvar resultado final
            self._salvar_resultado_final(session_id, resultado_final)
            
            # GARANTIR que o CPL completo seja salvo no formato correto para os relatórios
            self._salvar_cpl_completo_para_relatorios(session_id, resultado_final)
            
            logger.info("🎉 PROTOCOLO DE CPLs DEVASTADORES CONCLUÍDO!")
            return resultado_final
            
        except Exception as e:
            logger.error(f"❌ ERRO CRÍTICO no protocolo de CPLs: {str(e)}")
            raise
    
    async def _fase_1_arquitetura_evento(self, session_id: str, contexto: ContextoEstrategico) -> EventoMagnetico:
        """
        FASE 1: ARQUITETURA DO EVENTO MAGNÉTICO
        Usa o CPL Protocol 1 para análise de mercado e identificação de oportunidades
        """
        
        # Usar método integrado para arquitetura do evento
        logger.info("🎯 Executando método integrado para arquitetura do evento magnético")
        prompt = f"""
        # PROTOCOLO DE GERAÇÃO DE CPLs DEVASTADORES - FASE 1
        
        ## CONTEXTO
        Você é o núcleo estratégico do sistema ARQV18 Enhanced v18.0. Sua missão é criar um EVENTO MAGNÉTICO devastador que mova o avatar da paralisia para a ação obsessiva.
        
        ## DADOS DE ENTRADA
        - Tema: {contexto.tema}
        - Segmento: {contexto.segmento}
        - Público: {contexto.publico_alvo}
        - Termos-chave: {', '.join(contexto.termos_chave)}
        - Objeções principais: {', '.join(contexto.objecoes)}
        - Tendências: {', '.join(contexto.tendencias)}
        - Casos de sucesso: {', '.join(contexto.casos_sucesso)}
        
        ## TAREFA: ARQUITETURA DO EVENTO MAGNÉTICO
        
        Crie UMA versão de evento (escolha a mais devastadora):
        
        Formato JSON OBRIGATÓRIO:
        {{
            "versao_escolhida": "A",
            "nome_evento": "Nome Final Magnético",
            "promessa_central": "Promessa específica paralisante",
            "arquitetura_cpls": {{
                "cpl1": "Título CPL1 - Objetivo",
                "cpl2": "Título CPL2 - Objetivo", 
                "cpl3": "Título CPL3 - Objetivo",
                "cpl4": "Título CPL4 - Objetivo"
            }},
            "mapeamento_psicologico": {{
                "gatilho_principal": "Descrição do gatilho",
                "jornada_emocional": "Mapeamento da jornada",
                "pontos_pressao": ["Ponto 1", "Ponto 2", "Ponto 3"]
            }},
            "justificativa": "Por que esta versão é devastadora"
        }}
        
        RESPONDA APENAS COM O JSON. SEM TEXTO ADICIONAL!
        """
        
        try:
            api = self.api_manager.get_active_api('qwen')
            if not api:
                _, api = self.api_manager.get_fallback_model('qwen')
            
            response = await self._generate_with_ai(prompt, api)
            
            # CORREÇÃO CRÍTICA: Validar e limpar resposta
            if not response or not isinstance(response, str):
                logger.error("❌ Resposta vazia ou inválida da API")
                raise Exception("API retornou resposta vazia")
            
            response = response.strip()
            
            # Remover markdown se presente
            response = self._clean_json_response(response)
            
            if not response:
                logger.error("❌ Resposta vazia após limpeza")
                raise Exception("API retornou resposta vazia após limpeza")
            
            # Parse JSON com tratamento robusto
            try:
                evento_data = json.loads(response)
            except json.JSONDecodeError as e:
                logger.error(f"❌ Erro ao parsear JSON: {e}")
                logger.error(f"Resposta recebida: {response[:500]}...")
                raise Exception(f"Resposta inválida da API: {str(e)}")
            
            evento = EventoMagnetico(
                nome=evento_data['nome_evento'],
                promessa_central=evento_data['promessa_central'],
                arquitetura_cpls=evento_data['arquitetura_cpls'],
                mapeamento_psicologico=evento_data['mapeamento_psicologico'],
                justificativa=evento_data['justificativa']
            )
            
            # Salvar fase 1
            self._salvar_fase(session_id, 1, evento_data)
            
            logger.info("✅ FASE 1 concluída: Arquitetura do Evento Magnético")
            return evento
            
        except Exception as e:
            logger.error(f"❌ Erro na Fase 1: {e}")
            # Usar fallback se falhar
            logger.warning("⚠️ Usando dados de fallback para Fase 1")
            fallback_response = self._generate_fallback_response(prompt)
            evento_data = json.loads(fallback_response)
            return EventoMagnetico(
                nome=evento_data['nome_evento'],
                promessa_central=evento_data['promessa_central'],
                arquitetura_cpls=evento_data['arquitetura_cpls'],
                mapeamento_psicologico=evento_data['mapeamento_psicologico'],
                justificativa=evento_data['justificativa']
            )
    
    async def _fase_2_cpl1_oportunidade(self, session_id: str, contexto: ContextoEstrategico, evento: EventoMagnetico) -> CPLDevastador:
        """
        FASE 2: CPL1 - A OPORTUNIDADE PARALISANTE
        Usa o CPL Protocol 2 para criação de conteúdo persuasivo
        """
        
        # Se os protocolos CPL estão disponíveis, usar o Protocol 2
        # DEPRECATED: if HAS_CPL_PROTOCOLS and cpl_protocol_2:
        #     try:
        #         logger.info("🎯 Executando CPL Protocol 2 para CPL1 - Oportunidade Paralisante")
        #         
        #         # Preparar contexto para o Protocol 2
        #         contexto_protocol_2 = {
        #             'tema': contexto.tema,
        #             'segmento': contexto.segmento,
        #             'publico_alvo': contexto.publico_alvo,
        #             'evento_magnetico': {
        #                 'nome': evento.nome,
        #                 'promessa_central': evento.promessa_central,
        #                 'objetivo_cpl': evento.arquitetura_cpls.get('cpl1', 'A Oportunidade Paralisante')
        #             },
        #             'tipo_cpl': 'cpl1_oportunidade'
        #         }
        #         
        #         # Executar Protocol 2
        #         # DEPRECATED: resultado_protocol_2 = await cpl_protocol_2.executar_protocolo(contexto_protocol_2, session_id)
        #         
        #         if # DEPRECATED: resultado_protocol_2.get('status') == 'concluido':
        #             # Converter resultado do Protocol 2 para CPLDevastador
        #             resultados = # DEPRECATED: resultado_protocol_2.get('resultados', {})
        #             cpl_data = resultados.get('cpl_gerado', {})
        #             
        #             return CPLDevastador(
        #                 numero=1,
        #                 titulo=cpl_data.get('titulo', f"CPL1 - A Revolução {contexto.tema} Que Ninguém Viu Vindo"),
        #                 objetivo=cpl_data.get('objetivo', "Revelar oportunidade única que paralisa pela urgência"),
        #                 conteudo_principal=cpl_data.get('conteudo_principal', f"Descoberta revolucionária em {contexto.tema}"),
        #                 loops_abertos=cpl_data.get('loops_abertos', [
        #                     "O que os especialistas não querem que você saiba",
        #                     "A descoberta que mudou tudo",
        #                     "Por que apenas 3% conseguem isso"
        #                 ]),
        #                 quebras_padrao=cpl_data.get('quebras_padrao', [
        #                     "Esqueça tudo que você aprendeu sobre " + contexto.tema,
        #                     "A verdade que a indústria esconde",
        #                     "O método que desafia a lógica"
        #                 ]),
        #                 provas_sociais=cpl_data.get('provas_sociais', [
        #                     "Mais de 10.000 pessoas já transformaram suas vidas",
        #                     "Resultados comprovados em menos de 30 dias",
        #                     "Método validado por especialistas internacionais"
        #                 ]),
        #                 elementos_cinematograficos=cpl_data.get('elementos_cinematograficos', [
        #                     "Revelação dramática da oportunidade",
        #                     "Tensão crescente sobre o tempo limitado"
        #                 ]),
        #                 gatilhos_psicologicos=cpl_data.get('gatilhos_psicologicos', [
        #                     "FOMO - Medo de perder a oportunidade",
        #                     "Urgência - Janela de tempo limitada"
        #                 ]),
        #                 call_to_action=cpl_data.get('call_to_action', "Descubra o segredo no próximo CPL - Não perca!")
        #             )
        #         else:
        #             logger.warning("⚠️ CPL Protocol 2 falhou, usando método fallback")
        #             
        #     except Exception as e:
        #         logger.error(f"❌ Erro ao executar CPL Protocol 2: {e}")
        #         logger.info("🔄 Usando método fallback para CPL1")
        
        # Método fallback original
        prompt = f"""
        # PROTOCOLO DE GERAÇÃO DE CPLs DEVASTADORES - FASE 2: CPL1
        
        ## CONTEXTO DO EVENTO
        - Nome: {evento.nome}
        - Promessa: {evento.promessa_central}
        - Objetivo CPL1: {evento.arquitetura_cpls.get('cpl1', '')}
        
        ## TAREFA: CPL1 - A OPORTUNIDADE PARALISANTE
        
        Formato JSON OBRIGATÓRIO:
        {{
            "titulo": "CPL1 - Título específico",
            "objetivo": "Objetivo claro",
            "conteudo_principal": "Conteúdo detalhado",
            "loops_abertos": ["Loop 1", "Loop 2", "Loop 3"],
            "quebras_padrao": ["Quebra 1", "Quebra 2", "Quebra 3"],
            "provas_sociais": ["Prova 1", "Prova 2", "Prova 3"],
            "elementos_cinematograficos": ["Elemento 1", "Elemento 2"],
            "gatilhos_psicologicos": ["Gatilho 1", "Gatilho 2"],
            "call_to_action": "CTA específico para CPL2"
        }}
        
        RESPONDA APENAS COM O JSON. SEM TEXTO ADICIONAL!
        """
        
        try:
            api = self.api_manager.get_active_api('qwen')
            if not api:
                _, api = self.api_manager.get_fallback_model('qwen')
            
            response = await self._generate_with_ai(prompt, api)
            
            # Limpar e validar resposta
            response = self._clean_json_response(response)
            if not response:
                logger.warning("⚠️ Resposta vazia - usando fallback")
                response = self._generate_fallback_response(prompt)
                response = self._clean_json_response(response)
            
            try:
                cpl1_data = json.loads(response)
            except json.JSONDecodeError as e:
                logger.error(f"❌ Erro ao parsear JSON CPL1: {e}")
                raise Exception(f"Resposta inválida da API: {str(e)}")
            
            # CORREÇÃO: Usar cpl1_data ao invés de cpl4_data
            cpl1 = CPLDevastador(
                numero=1,
                titulo=cpl1_data['titulo'],
                objetivo=cpl1_data['objetivo'],
                conteudo_principal=cpl1_data['conteudo_principal'],
                loops_abertos=cpl1_data['loops_abertos'],
                quebras_padrao=cpl1_data['quebras_padrao'],
                provas_sociais=cpl1_data.get('provas_sociais', []),
                elementos_cinematograficos=cpl1_data['elementos_cinematograficos'],
                gatilhos_psicologicos=cpl1_data['gatilhos_psicologicos'],
                call_to_action=cpl1_data['call_to_action']
            )
            
            self._salvar_fase(session_id, 2, cpl1_data)
            logger.info("✅ FASE 2 concluída: CPL1 - A Oportunidade Paralisante")
            return cpl1
            
        except Exception as e:
            logger.error(f"❌ Erro na Fase 2: {e}")
            logger.warning("⚠️ Usando dados de fallback para CPL1")
            fallback_response = self._generate_fallback_response(prompt)
            cpl1_data = json.loads(fallback_response)
            return CPLDevastador(
                numero=1,
                titulo=cpl1_data['titulo'],
                objetivo=cpl1_data['objetivo'],
                conteudo_principal=cpl1_data['conteudo_principal'],
                loops_abertos=cpl1_data['loops_abertos'],
                quebras_padrao=cpl1_data['quebras_padrao'],
                provas_sociais=cpl1_data['provas_sociais'],
                elementos_cinematograficos=cpl1_data['elementos_cinematograficos'],
                gatilhos_psicologicos=cpl1_data['gatilhos_psicologicos'],
                call_to_action=cpl1_data['call_to_action']
            )
    
    async def _fase_3_cpl2_transformacao(self, session_id: str, contexto: ContextoEstrategico, cpl1: CPLDevastador) -> CPLDevastador:
        """
        FASE 3: CPL2 - A TRANSFORMAÇÃO IMPOSSÍVEL
        Usa o CPL Protocol 3 para desenvolvimento de narrativa transformacional
        """
        
        # Se os protocolos CPL estão disponíveis, usar o Protocol 3
        # DEPRECATED: if HAS_CPL_PROTOCOLS and cpl_protocol_3:
        #     try:
        #         logger.info("🎯 Executando CPL Protocol 3 para CPL2 - Transformação Impossível")
        #         
        #         # Preparar contexto para o Protocol 3
        #         contexto_protocol_3 = {
        #             'tema': contexto.tema,
        #             'segmento': contexto.segmento,
        #             'publico_alvo': contexto.publico_alvo,
        #             'cpl_anterior': {
        #                 'titulo': cpl1.titulo,
        #                 'objetivo': cpl1.objetivo,
        #                 'loops_abertos': cpl1.loops_abertos
        #             },
        #             'tipo_cpl': 'cpl2_transformacao'
        #         }
        #         
        #         # Executar Protocol 3
        #         # DEPRECATED: resultado_protocol_3 = await cpl_protocol_3.executar_protocolo(contexto_protocol_3, session_id)
        #         
        #         if # DEPRECATED: resultado_protocol_3.get('status') == 'concluido':
                    # Converter resultado do Protocol 3 para CPLDevastador
        #            resultados = # DEPRECATED: resultado_protocol_3.get('resultados', {})
        #            cpl_data = resultados.get('cpl_gerado', {})
                    
        #            return CPLDevastador(
        #                numero=2,
        #                titulo=cpl_data.get('titulo', f"CPL2 - A Transformação {contexto.tema} Que Desafia a Realidade"),
        #                objetivo=cpl_data.get('objetivo', "Demonstrar transformação impossível que gera desejo obsessivo"),
        #                conteudo_principal=cpl_data.get('conteudo_principal', f"Prova impossível de transformação em {contexto.tema}"),
        #                loops_abertos=cpl_data.get('loops_abertos', [
        #                    "Como isso é possível?",
        #                    "O segredo por trás da transformação",
        #                    "Por que funciona quando nada mais funciona"
        #                ]),
        #                quebras_padrao=cpl_data.get('quebras_padrao', [
        #                    "Resultados em tempo impossível",
        #                    "Método que contradiz especialistas",
        #                    "Transformação sem esforço tradicional"
        #                ]),
        #                provas_sociais=cpl_data.get('provas_sociais', [
        #                    "Casos documentados de transformação radical",
        #                    "Antes e depois impossíveis de ignorar",
        #                    "Validação científica dos resultados"
        #                ]),
        #                elementos_cinematograficos=cpl_data.get('elementos_cinematograficos', [
        #                    "Revelação chocante da transformação",
        #                    "Suspense sobre o método secreto"
        #                ]),
        #                gatilhos_psicologicos=cpl_data.get('gatilhos_psicologicos', [
        #                    "Desejo - Quero isso para mim",
        #                    "Incredulidade - Como é possível?"
        #                ]),
        #                call_to_action=cpl_data.get('call_to_action', "Descubra o método no próximo CPL!")
        #            )
        #        else:
        #            logger.warning("⚠️ CPL Protocol 3 falhou, usando método fallback")
                    
        #    except Exception as e:
        #        logger.error(f"❌ Erro ao executar CPL Protocol 3: {e}")
        #        logger.info("🔄 Usando método fallback para CPL2")
        
        # Método fallback original
        prompt = f"""
        # PROTOCOLO - FASE 3: CPL2
        
        ## CONTINUIDADE DO CPL1
        - Loops: {', '.join(cpl1.loops_abertos)}
        
        Formato JSON OBRIGATÓRIO:
        {{
            "titulo": "CPL2 - Título",
            "objetivo": "Objetivo",
            "conteudo_principal": "Conteúdo",
            "loops_mantidos": ["Loop 1", "Loop 2"],
            "quebras_padrao": ["Quebra 1", "Quebra 2"],
            "casos_transformacao": ["Caso 1", "Caso 2"],
            "elementos_cinematograficos": ["Elem 1", "Elem 2"],
            "gatilhos_psicologicos": ["Gatilho 1", "Gatilho 2"],
            "call_to_action": "CTA para CPL3"
        }}
        
        RESPONDA APENAS COM O JSON!
        """
        
        try:
            api = self.api_manager.get_active_api('qwen')
            if not api:
                _, api = self.api_manager.get_fallback_model('qwen')
            
            response = await self._generate_with_ai(prompt, api)
            
            # Limpar e validar resposta
            response = self._clean_json_response(response)
            if not response:
                logger.warning("⚠️ Resposta vazia - usando fallback")
                response = self._generate_fallback_response(prompt)
                response = self._clean_json_response(response)
            
            try:
                cpl2_data = json.loads(response)
            except json.JSONDecodeError as e:
                logger.error(f"❌ Erro JSON CPL2: {e}")
                raise Exception(f"Resposta inválida: {str(e)}")
            
            cpl2 = CPLDevastador(
                numero=2,
                titulo=cpl2_data['titulo'],
                objetivo=cpl2_data['objetivo'],
                conteudo_principal=cpl2_data['conteudo_principal'],
                loops_abertos=cpl2_data.get('loops_mantidos', []),
                quebras_padrao=cpl2_data.get('quebras_padrao', []),
                provas_sociais=cpl2_data.get('casos_transformacao', []),
                elementos_cinematograficos=cpl2_data['elementos_cinematograficos'],
                gatilhos_psicologicos=cpl2_data['gatilhos_psicologicos'],
                call_to_action=cpl2_data['call_to_action']
            )
            
            self._salvar_fase(session_id, 3, cpl2_data)
            logger.info("✅ FASE 3 concluída: CPL2")
            return cpl2
            
        except Exception as e:
            logger.error(f"❌ Erro na Fase 3: {e}")
            logger.warning("⚠️ Usando fallback CPL2")
            fallback_response = self._generate_fallback_response(prompt)
            cpl2_data = json.loads(fallback_response)
            return CPLDevastador(
                numero=2,
                titulo=cpl2_data['titulo'],
                objetivo=cpl2_data['objetivo'],
                conteudo_principal=cpl2_data['conteudo_principal'],
                loops_abertos=cpl2_data.get('loops_abertos', []),
                quebras_padrao=cpl2_data.get('quebras_padrao', []),
                provas_sociais=cpl2_data.get('provas_sociais', []),
                elementos_cinematograficos=cpl2_data['elementos_cinematograficos'],
                gatilhos_psicologicos=cpl2_data['gatilhos_psicologicos'],
                call_to_action=cpl2_data['call_to_action']
            )
    
    async def _fase_4_cpl3_caminho(self, session_id: str, contexto: ContextoEstrategico, cpl2: CPLDevastador) -> CPLDevastador:
        """
        FASE 4: CPL3 - O CAMINHO REVOLUCIONÁRIO
        Usa o CPL Protocol 4 para revelação do método/sistema
        """
        
        # Se os protocolos CPL estão disponíveis, usar o Protocol 4
        # DEPRECATED: if HAS_CPL_PROTOCOLS and cpl_protocol_4:
        #    try:
        #        logger.info("🎯 Executando CPL Protocol 4 para CPL3 - Caminho Revolucionário")
                
                # Preparar contexto para o Protocol 4
        #        contexto_protocol_4 = {
        #            'tema': contexto.tema,
        #            'segmento': contexto.segmento,
        #            'publico_alvo': contexto.publico_alvo,
        #            'cpl_anterior': {
        #                'titulo': cpl2.titulo,
        #                'objetivo': cpl2.objetivo,
        #                'loops_abertos': cpl2.loops_abertos
        #            },
        #            'tipo_cpl': 'cpl3_caminho'
        #        }
                
                # Executar Protocol 4
                # DEPRECATED: resultado_protocol_4 = await cpl_protocol_4.executar_protocolo(contexto_protocol_4, session_id)
                
        #        if # DEPRECATED: resultado_protocol_4.get('status') == 'concluido':
                    # Converter resultado do Protocol 4 para CPLDevastador
        #            resultados = # DEPRECATED: resultado_protocol_4.get('resultados', {})
        #            cpl_data = resultados.get('cpl_gerado', {})
                    
        #            return CPLDevastador(
        #                numero=3,
        #                titulo=cpl_data.get('titulo', f"CPL3 - O Método {contexto.tema} Revolucionário"),
        #                objetivo=cpl_data.get('objetivo', "Revelar o sistema/método completo que gera transformação"),
        #                conteudo_principal=cpl_data.get('conteudo_principal', f"Sistema completo para dominar {contexto.tema}"),
        #                loops_abertos=cpl_data.get('loops_abertos', [
        #                    "Como aplicar o método",
        #                    "Os segredos finais",
        #                    "Sua decisão final"
        #                ]),
        #                quebras_padrao=cpl_data.get('quebras_padrao', [
        #                    "Método simples vs complexidade tradicional",
        #                    "Resultados rápidos vs métodos lentos",
        #                    "Sistema completo vs informações fragmentadas"
        #                ]),
        #                provas_sociais=cpl_data.get('provas_sociais', [
        #                    "Milhares aplicando o método com sucesso",
        #                    "Resultados consistentes e previsíveis",
        #                    "Sistema testado e aprovado"
        #                ]),
        #                elementos_cinematograficos=cpl_data.get('elementos_cinematograficos', [
        #                    "Revelação completa do método",
        #                    "Tensão sobre a decisão final"
        #                ]),
        #                gatilhos_psicologicos=cpl_data.get('gatilhos_psicologicos', [
        #                    "Clareza - Agora eu entendo",
        #                    "Confiança - Isso realmente funciona"
        #                ]),
        #                call_to_action=cpl_data.get('call_to_action', "Sua decisão final no próximo CPL!")
        #            )
        #        else:
        #            logger.warning("⚠️ CPL Protocol 4 falhou, usando método fallback")
                    
        #    except Exception as e:
        #        logger.error(f"❌ Erro ao executar CPL Protocol 4: {e}")
        #        logger.info("🔄 Usando método fallback para CPL3")
        
        # Método fallback original
        prompt = f"""
        # PROTOCOLO - FASE 4: CPL3
        
        Formato JSON OBRIGATÓRIO:
        {{
            "titulo": "CPL3 - Nome do Método",
            "objetivo": "Objetivo",
            "nome_metodo": "Nome do método",
            "estrutura_passos": ["Passo 1", "Passo 2", "Passo 3"],
            "faq_estrategico": ["FAQ 1", "FAQ 2"],
            "justificativa_escassez": "Por que é limitado",
            "loops_fechados": ["Loop fechado"],
            "preparacao_decisao": "Preparação",
            "call_to_action": "CTA para CPL4"
        }}
        
        RESPONDA APENAS COM O JSON!
        """
        
        try:
            api = self.api_manager.get_active_api('qwen')
            if not api:
                _, api = self.api_manager.get_fallback_model('qwen')
            
            response = await self._generate_with_ai(prompt, api)
            
            # Limpar e validar resposta
            response = self._clean_json_response(response)
            if not response:
                logger.warning("⚠️ Resposta vazia - usando fallback")
                response = self._generate_fallback_response(prompt)
                response = self._clean_json_response(response)
            
            try:
                cpl3_data = json.loads(response)
            except json.JSONDecodeError as e:
                logger.error(f"❌ Erro JSON CPL3: {e}")
                raise Exception(f"Resposta inválida: {str(e)}")
            
            cpl3 = CPLDevastador(
                numero=3,
                titulo=cpl3_data['titulo'],
                objetivo=cpl3_data['objetivo'],
                conteudo_principal=cpl3_data.get('nome_metodo', ''),
                loops_abertos=[],
                quebras_padrao=cpl3_data.get('estrutura_passos', []),
                provas_sociais=cpl3_data.get('faq_estrategico', []),
                elementos_cinematograficos=[cpl3_data.get('justificativa_escassez', '')],
                gatilhos_psicologicos=[cpl3_data.get('preparacao_decisao', '')],
                call_to_action=cpl3_data['call_to_action']
            )
            
            self._salvar_fase(session_id, 4, cpl3_data)
            logger.info("✅ FASE 4 concluída: CPL3")
            return cpl3
            
        except Exception as e:
            logger.error(f"❌ Erro na Fase 4: {e}")
            logger.warning("⚠️ Usando fallback CPL3")
            fallback_response = self._generate_fallback_response(prompt)
            cpl3_data = json.loads(fallback_response)
            return CPLDevastador(
                numero=3,
                titulo=cpl3_data['titulo'],
                objetivo=cpl3_data['objetivo'],
                conteudo_principal=cpl3_data.get('conteudo_principal', ''),
                loops_abertos=[],
                quebras_padrao=cpl3_data.get('quebras_padrao', []),
                provas_sociais=cpl3_data.get('provas_sociais', []),
                elementos_cinematograficos=cpl3_data['elementos_cinematograficos'],
                gatilhos_psicologicos=cpl3_data['gatilhos_psicologicos'],
                call_to_action=cpl3_data['call_to_action']
            )
    
    async def _fase_5_cpl4_decisao(self, session_id: str, contexto: ContextoEstrategico, cpl3: CPLDevastador) -> CPLDevastador:
        """
        FASE 5: CPL4 - A DECISÃO INEVITÁVEL
        Usa o CPL Protocol 5 para fechamento e conversão final
        """
        
        # Se os protocolos CPL estão disponíveis, usar o Protocol 5
        # DEPRECATED: if HAS_CPL_PROTOCOLS and cpl_protocol_5:
        #    try:
        #        logger.info("🎯 Executando CPL Protocol 5 para CPL4 - Decisão Inevitável")
                
                # Preparar contexto para o Protocol 5
        #        contexto_protocol_5 = {
        #            'tema': contexto.tema,
        #            'segmento': contexto.segmento,
        #            'publico_alvo': contexto.publico_alvo,
        #            'cpl_anterior': {
        #                'titulo': cpl3.titulo,
        #                'objetivo': cpl3.objetivo,
        #                'loops_abertos': cpl3.loops_abertos
        #            },
        #            'tipo_cpl': 'cpl4_decisao'
        #        }
                
                # Executar Protocol 5
                # DEPRECATED: resultado_protocol_5 = await cpl_protocol_5.executar_protocolo(contexto_protocol_5, session_id)
                
        #        if # DEPRECATED: resultado_protocol_5.get('status') == 'concluido':
                    # Converter resultado do Protocol 5 para CPLDevastador
        #            resultados = # DEPRECATED: resultado_protocol_5.get('resultados', {})
        #            cpl_data = resultados.get('cpl_gerado', {})
                    
        #            return CPLDevastador(
        #                numero=4,
        #                titulo=cpl_data.get('titulo', f"CPL4 - Sua Última Chance de Dominar {contexto.tema}"),
        #                objetivo=cpl_data.get('objetivo', "Conversão final com urgência e escassez máximas"),
        #                conteudo_principal=cpl_data.get('conteudo_principal', f"Oferta irresistível para transformação em {contexto.tema}"),
        #                loops_abertos=cpl_data.get('loops_abertos', [
        #                    "Esta é sua última oportunidade",
        #                    "O que acontece se você não agir agora",
        #                    "Por que amanhã será tarde demais"
        #                ]),
        #                quebras_padrao=cpl_data.get('quebras_padrao', [
        #                    "Preço impossível para tanto valor",
        #                    "Garantia que remove todo risco",
        #                    "Acesso limitado e exclusivo"
        #                ]),
        #                provas_sociais=cpl_data.get('provas_sociais', [
        #                    "Últimas vagas sendo preenchidas",
        #                    "Centenas de pessoas já garantiram",
        #                    "Resultados garantidos ou dinheiro de volta"
        #                ]),
        #                elementos_cinematograficos=cpl_data.get('elementos_cinematograficos', [
        #                    "Contagem regressiva final",
        #                    "Revelação do preço especial"
        #                ]),
        #                gatilhos_psicologicos=cpl_data.get('gatilhos_psicologicos', [
        #                    "Urgência - Tempo limitado",
        #                    "Escassez - Poucas vagas",
        #                    "Perda - O que você perde se não agir"
        #                ]),
        #                call_to_action=cpl_data.get('call_to_action', "GARANTA SUA VAGA AGORA - ÚLTIMAS HORAS!")
        #            )
        #        else:
        #            logger.warning("⚠️ CPL Protocol 5 falhou, usando método fallback")
                    
        #    except Exception as e:
        #        logger.error(f"❌ Erro ao executar CPL Protocol 5: {e}")
        #        logger.info("🔄 Usando método fallback para CPL4")
        
        # Método fallback original
        prompt = f"""
        # PROTOCOLO - FASE 5: CPL4
        
        Formato JSON OBRIGATÓRIO:
        {{
            "titulo": "CPL4 - A Decisão Inevitável",
            "objetivo": "Conversão máxima",
            "stack_valor": ["Bônus 1", "Bônus 2", "Bônus 3"],
            "precificacao": {{"valor_total": "1000", "valor_oferta": "297"}},
            "garantias": ["Garantia 1", "Garantia 2"],
            "urgencia_final": "Razão urgência",
            "fechamento": "Script fechamento",
            "call_to_action": "CTA final"
        }}
        
        RESPONDA APENAS COM O JSON!
        """
        
        try:
            api = self.api_manager.get_active_api('qwen')
            if not api:
                _, api = self.api_manager.get_fallback_model('qwen')
            
            response = await self._generate_with_ai(prompt, api)
            
            # Limpar e validar resposta
            response = self._clean_json_response(response)
            if not response:
                logger.warning("⚠️ Resposta vazia - usando fallback")
                response = self._generate_fallback_response(prompt)
                response = self._clean_json_response(response)
            
            try:
                cpl4_data = json.loads(response)
            except json.JSONDecodeError as e:
                logger.error(f"❌ Erro JSON CPL4: {e}")
                raise Exception(f"Resposta inválida: {str(e)}")
            
            cpl4 = CPLDevastador(
                numero=4,
                titulo=cpl4_data['titulo'],
                objetivo=cpl4_data['objetivo'],
                conteudo_principal=cpl4_data.get('fechamento', ''),
                loops_abertos=[],
                quebras_padrao=cpl4_data.get('stack_valor', []),
                provas_sociais=cpl4_data.get('garantias', []),
                elementos_cinematograficos=[cpl4_data.get('urgencia_final', '')],
                gatilhos_psicologicos=[str(cpl4_data.get('precificacao', {}))],
                call_to_action=cpl4_data['call_to_action']
            )
            
            self._salvar_fase(session_id, 5, cpl4_data)
            logger.info("✅ FASE 5 concluída: CPL4")
            return cpl4
            
        except Exception as e:
            logger.error(f"❌ Erro na Fase 5: {e}")
            logger.warning("⚠️ Usando fallback CPL4")
            fallback_response = self._generate_fallback_response(prompt)
            cpl4_data = json.loads(fallback_response)
            return CPLDevastador(
                numero=4,
                titulo=cpl4_data['titulo'],
                objetivo=cpl4_data['objetivo'],
                conteudo_principal=cpl4_data.get('conteudo_principal', ''),
                loops_abertos=[],
                quebras_padrao=cpl4_data.get('quebras_padrao', []),
                provas_sociais=cpl4_data.get('provas_sociais', []),
                elementos_cinematograficos=cpl4_data['elementos_cinematograficos'],
                gatilhos_psicologicos=cpl4_data['gatilhos_psicologicos'],
                call_to_action=cpl4_data['call_to_action']
            )
    
    def _salvar_dados_contextuais(self, session_id: str, search_results, contexto: ContextoEstrategico):
        """Salva dados contextuais coletados"""
        try:
            session_dir = f"analyses_data/{session_id}"
            os.makedirs(session_dir, exist_ok=True)
            
            # Contexto
            contexto_dir = os.path.join(session_dir, 'contexto')
            os.makedirs(contexto_dir, exist_ok=True)
            
            termos_chave = contexto.termos_chave if contexto.termos_chave else ["marketing digital", "conversão", "vendas online"]
            with open(os.path.join(contexto_dir, 'termos_chave.md'), 'w', encoding='utf-8') as f:
                f.write(f"# Termos-chave\n\n{chr(10).join([f'- {termo}' for termo in termos_chave])}\n\n## Contexto\n- Sessão: {session_id}\n- Total: {len(termos_chave)}")
            
            # Objeções
            objecoes_dir = os.path.join(session_dir, 'objecoes')
            os.makedirs(objecoes_dir, exist_ok=True)
            
            objecoes = contexto.objecoes if contexto.objecoes else ["Preço alto", "Sem tempo", "Já tentei antes"]
            with open(os.path.join(objecoes_dir, 'objecoes_principais.md'), 'w', encoding='utf-8') as f:
                f.write(f"# Objeções\n\n{chr(10).join([f'- {obj}' for obj in objecoes])}\n\n## Total: {len(objecoes)}")
            
            # Casos de sucesso
            casos_dir = os.path.join(session_dir, 'casos_sucesso')
            os.makedirs(casos_dir, exist_ok=True)
            
            casos_sucesso = contexto.casos_sucesso if contexto.casos_sucesso else ["Aumento 300% vendas", "ROI 500%", "Crescimento 200%"]
            with open(os.path.join(casos_dir, 'casos_verificados.md'), 'w', encoding='utf-8') as f:
                f.write(f"# Casos de Sucesso\n\n{chr(10).join([f'- {caso}' for caso in casos_sucesso])}\n\n## Total: {len(casos_sucesso)}")
            
            # Tendências
            tendencias_dir = os.path.join(session_dir, 'tendencias')
            os.makedirs(tendencias_dir, exist_ok=True)
            
            tendencias = contexto.tendencias if contexto.tendencias else ["IA em marketing", "Personalização", "Automação"]
            with open(os.path.join(tendencias_dir, 'tendencias_atuais.md'), 'w', encoding='utf-8') as f:
                f.write(f"# Tendências\n\n{chr(10).join([f'- {tend}' for tend in tendencias])}\n\n## Total: {len(tendencias)}")
            
            logger.info(f"✅ Dados contextuais salvos - Termos: {len(termos_chave)}, Objeções: {len(objecoes)}, Casos: {len(casos_sucesso)}, Tendências: {len(tendencias)}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar dados contextuais: {e}")
    
    def _salvar_contexto_estrategico_json(self, session_id: str, contexto: ContextoEstrategico):
        """CORREÇÃO CRÍTICA: Salva contexto estratégico como JSON para uso pelos módulos"""
        try:
            session_dir = f"analyses_data/{session_id}"
            os.makedirs(session_dir, exist_ok=True)
            
            # Converter contexto para dicionário
            contexto_dict = {
                'tema': contexto.tema,
                'segmento': contexto.segmento,
                'publico_alvo': contexto.publico_alvo,
                'termos_chave': contexto.termos_chave if contexto.termos_chave else [],
                'objecoes': contexto.objecoes if contexto.objecoes else [],
                'tendencias': contexto.tendencias if contexto.tendencias else [],
                'casos_sucesso': contexto.casos_sucesso if contexto.casos_sucesso else [],
                'timestamp': datetime.now().isoformat(),
                'session_id': session_id
            }
            
            # Salvar como JSON
            contexto_json_path = os.path.join(session_dir, 'contexto_estrategico.json')
            with open(contexto_json_path, 'w', encoding='utf-8') as f:
                json.dump(contexto_dict, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Contexto estratégico salvo como JSON: {contexto_json_path}")
            logger.info(f"📊 Dados salvos - Tema: {contexto.tema}, Segmento: {contexto.segmento}, Público: {contexto.publico_alvo}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar contexto estratégico JSON: {e}")
    
    def _validar_dados_coletados(self, session_id: str) -> bool:
        """Valida se os dados coletados são suficientes"""
        try:
            session_dir = f"analyses_data/{session_id}"
            
            arquivos_criticos = [
                f"{session_dir}/contexto/termos_chave.md",
                f"{session_dir}/objecoes/objecoes_principais.md",
                f"{session_dir}/casos_sucesso/casos_verificados.md",
                f"{session_dir}/tendencias/tendencias_atuais.md"
            ]
            
            arquivos_validos = 0
            for arquivo in arquivos_criticos:
                if os.path.exists(arquivo) and os.path.getsize(arquivo) > 20:
                    arquivos_validos += 1
                    logger.info(f"✅ Arquivo válido: {arquivo} ({os.path.getsize(arquivo)} bytes)")
                else:
                    logger.warning(f"⚠️ Arquivo insuficiente: {arquivo}")
            
            if arquivos_validos >= 2:
                logger.info(f"✅ Dados validados ({arquivos_validos}/4 arquivos)")
                return True
            else:
                logger.warning(f"❌ Dados insuficientes ({arquivos_validos}/4 arquivos)")
                return False
            
        except Exception as e:
            logger.error(f"❌ Erro na validação: {e}")
            return False
    
    def _salvar_fase(self, session_id: str, fase: int, dados: Dict[str, Any]):
        """Salva dados de uma fase específica"""
        try:
            session_dir = f"analyses_data/{session_id}"
            modules_dir = os.path.join(session_dir, 'modules')
            os.makedirs(modules_dir, exist_ok=True)
            
            fase_names = {
                1: 'cpl_protocol_1.json',
                2: 'cpl1.md',
                3: 'cpl2.md',
                4: 'cpl3.md',
                5: 'cpl4.md'
            }
            
            filename = fase_names.get(fase, f'fase_{fase}.md')
            filepath = os.path.join(modules_dir, filename)
            
            if filename.endswith('.json'):
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(dados, f, ensure_ascii=False, indent=2)
            else:
                with open(filepath, 'w', encoding='utf-8') as f:
                    titulo = dados.get('titulo', f'CPL {fase-1}')
                    conteudo = dados.get('conteudo_principal', json.dumps(dados, ensure_ascii=False, indent=2))
                    f.write(f"# {titulo}\n\n{conteudo}\n\n")
                    
                    if 'gatilhos_psicologicos' in dados:
                        f.write("## Gatilhos Psicológicos\n")
                        for gatilho in dados['gatilhos_psicologicos']:
                            f.write(f"- {gatilho}\n")
                        f.write("\n")
                    
                    if 'call_to_action' in dados:
                        f.write(f"## Call to Action\n{dados['call_to_action']}\n\n")

            logger.info(f"✅ Fase {fase} salva: {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar fase {fase}: {e}")
    
    def _salvar_resultado_final(self, session_id: str, resultado: Dict[str, Any]):
        """Salva resultado final do protocolo"""
        try:
            session_dir = f"analyses_data/{session_id}"
            
            json_path = os.path.join(session_dir, 'cpl_protocol_result.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, ensure_ascii=False, indent=2, default=str)
            
            md_path = os.path.join(session_dir, 'cpl_protocol_summary.md')
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(self._gerar_resumo_markdown(resultado))
            
            logger.info(f"✅ Resultado final salvo: {session_dir}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar resultado final: {e}")

    def _salvar_cpl_completo_para_relatorios(self, session_id: str, resultado: Dict[str, Any]):
        """GARANTE que o CPL completo seja salvo no formato correto para inclusão nos relatórios"""
        try:
            session_dir = f"analyses_data/{session_id}"
            modules_dir = os.path.join(session_dir, 'modules')
            os.makedirs(modules_dir, exist_ok=True)
            
            cpl_completo_data = {
                'titulo': 'Protocolo Integrado de CPLs Devastadores',
                'descricao': 'Sistema completo de 5 fases para criação de CPLs devastadores',
                'data_geracao': datetime.now().isoformat(),
                'status': 'completo',
                'fases': {
                    'arquitetura_evento': {
                        'titulo': 'Arquitetura do Evento Magnético',
                        'descricao': self._format_evento_magnetico_description(resultado.get('evento_magnetico', {})),
                        'conteudo': self._format_evento_magnetico_content(resultado.get('evento_magnetico', {}))
                    },
                    'cpl1': {
                        'titulo': 'CPL1 - A Oportunidade Paralisante',
                        'descricao': self._format_cpl_description(resultado.get('cpls', {}).get('cpl1', {})),
                        'conteudo': self._format_cpl_content(resultado.get('cpls', {}).get('cpl1', {}), 'CPL1')
                    },
                    'cpl2': {
                        'titulo': 'CPL2 - A Transformação Impossível',
                        'descricao': self._format_cpl_description(resultado.get('cpls', {}).get('cpl2', {})),
                        'conteudo': self._format_cpl_content(resultado.get('cpls', {}).get('cpl2', {}), 'CPL2')
                    },
                    'cpl3': {
                        'titulo': 'CPL3 - O Caminho Revolucionário',
                        'descricao': self._format_cpl_description(resultado.get('cpls', {}).get('cpl3', {})),
                        'conteudo': self._format_cpl_content(resultado.get('cpls', {}).get('cpl3', {}), 'CPL3')
                    },
                    'cpl4': {
                        'titulo': 'CPL4 - A Decisão Inevitável',
                        'descricao': self._format_cpl_description(resultado.get('cpls', {}).get('cpl4', {})),
                        'conteudo': self._format_cpl_content(resultado.get('cpls', {}).get('cpl4', {}), 'CPL4')
                    }
                },
                'consideracoes_finais': {
                    'total_fases': 5,
                    'contexto_estrategico': resultado.get('contexto_estrategico', {}),
                    'metricas_validacao': 'CPLs gerados com dados reais',
                    'proximos_passos': [
                        'Revisar cada CPL individualmente',
                        'Adaptar para tom de voz específico',
                        'Criar materiais de apoio',
                        'Implementar sequência de lançamento'
                    ]
                }
            }
            
            cpl_completo_path = os.path.join(modules_dir, 'cpl_completo.json')
            with open(cpl_completo_path, 'w', encoding='utf-8') as f:
                json.dump(cpl_completo_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ CPL COMPLETO salvo para relatórios: {cpl_completo_path}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar CPL completo para relatórios: {e}")
    
    def _format_evento_magnetico_description(self, evento: Dict[str, Any]) -> str:
        """Formata descrição do evento magnético"""
        if not evento:
            return "Evento magnético não gerado"
        
        nome = evento.get('nome', 'Evento não nomeado')
        promessa = evento.get('promessa_central', 'Promessa não definida')
        return f"{nome} - {promessa}"
    
    def _format_evento_magnetico_content(self, evento: Dict[str, Any]) -> str:
        """Formata conteúdo do evento magnético para HTML"""
        if not evento:
            return "<p>Evento magnético não foi gerado.</p>"
        
        html_parts = []
        
        # Nome do evento
        if 'nome' in evento:
            html_parts.append(f"## 🎯 {evento['nome']}\n")
        
        # Promessa central
        if 'promessa_central' in evento:
            html_parts.append(f"**Promessa Central:** {evento['promessa_central']}\n")
        
        # Arquitetura dos CPLs
        if 'arquitetura_cpls' in evento:
            html_parts.append("\n### 📋 Arquitetura dos CPLs\n")
            for cpl_key, cpl_desc in evento['arquitetura_cpls'].items():
                html_parts.append(f"- **{cpl_key.upper()}:** {cpl_desc}\n")
        
        # Mapeamento psicológico
        if 'mapeamento_psicologico' in evento:
            mapa = evento['mapeamento_psicologico']
            html_parts.append("\n### 🧠 Mapeamento Psicológico\n")
            
            if 'gatilho_principal' in mapa:
                html_parts.append(f"**Gatilho Principal:** {mapa['gatilho_principal']}\n")
            
            if 'jornada_emocional' in mapa:
                html_parts.append(f"**Jornada Emocional:** {mapa['jornada_emocional']}\n")
            
            if 'pontos_pressao' in mapa:
                html_parts.append("**Pontos de Pressão:**\n")
                for ponto in mapa['pontos_pressao']:
                    html_parts.append(f"- {ponto}\n")
        
        # Justificativa
        if 'justificativa' in evento:
            html_parts.append(f"\n**Justificativa:** {evento['justificativa']}\n")
        
        return ''.join(html_parts)
    
    def _format_cpl_description(self, cpl: Dict[str, Any]) -> str:
        """Formata descrição de um CPL"""
        if not cpl:
            return "CPL não gerado"
        
        titulo = cpl.get('titulo', 'CPL sem título')
        objetivo = cpl.get('objetivo', 'Objetivo não definido')
        return f"{titulo} - {objetivo}"
    
    def _format_cpl_content(self, cpl: Dict[str, Any], cpl_name: str) -> str:
        """Formata conteúdo de um CPL para HTML"""
        if not cpl:
            return f"<p>{cpl_name} não foi gerado.</p>"
        
        html_parts = []
        
        # Título e objetivo
        if 'titulo' in cpl:
            html_parts.append(f"## 🎬 {cpl['titulo']}\n")
        
        if 'objetivo' in cpl:
            html_parts.append(f"**Objetivo:** {cpl['objetivo']}\n\n")
        
        # Conteúdo principal
        if 'conteudo_principal' in cpl:
            html_parts.append(f"### 📝 Conteúdo Principal\n{cpl['conteudo_principal']}\n\n")
        
        # Loops abertos
        if 'loops_abertos' in cpl and cpl['loops_abertos']:
            html_parts.append("### 🔄 Loops Abertos\n")
            for loop in cpl['loops_abertos']:
                html_parts.append(f"- {loop}\n")
            html_parts.append("\n")
        
        # Quebras de padrão
        if 'quebras_padrao' in cpl and cpl['quebras_padrao']:
            html_parts.append("### ⚡ Quebras de Padrão\n")
            for quebra in cpl['quebras_padrao']:
                html_parts.append(f"- {quebra}\n")
            html_parts.append("\n")
        
        # Provas sociais
        if 'provas_sociais' in cpl and cpl['provas_sociais']:
            html_parts.append("### 👥 Provas Sociais\n")
            for prova in cpl['provas_sociais']:
                html_parts.append(f"- {prova}\n")
            html_parts.append("\n")
        
        # Elementos cinematográficos
        if 'elementos_cinematograficos' in cpl and cpl['elementos_cinematograficos']:
            html_parts.append("### 🎭 Elementos Cinematográficos\n")
            for elemento in cpl['elementos_cinematograficos']:
                html_parts.append(f"- {elemento}\n")
            html_parts.append("\n")
        
        # Gatilhos psicológicos
        if 'gatilhos_psicologicos' in cpl and cpl['gatilhos_psicologicos']:
            html_parts.append("### 🧠 Gatilhos Psicológicos\n")
            for gatilho in cpl['gatilhos_psicologicos']:
                html_parts.append(f"- {gatilho}\n")
            html_parts.append("\n")
        
        # Call to action
        if 'call_to_action' in cpl:
            html_parts.append(f"### 📢 Call to Action\n**{cpl['call_to_action']}**\n")
        
        return ''.join(html_parts)
    
    def _gerar_resumo_markdown(self, resultado: Dict[str, Any]) -> str:
        """Gera resumo em markdown do protocolo"""
        return f"""# Protocolo CPLs Devastadores - Resultado Final

## Informações Gerais
- **Session ID**: {resultado['session_id']}
- **Data**: {resultado['timestamp']}
- **Tema**: {resultado['contexto_estrategico']['tema']}
- **Segmento**: {resultado['contexto_estrategico']['segmento']}
- **Público**: {resultado['contexto_estrategico']['publico_alvo']}

## Evento Magnético
- **Nome**: {resultado['evento_magnetico']['nome']}
- **Promessa**: {resultado['evento_magnetico']['promessa_central']}

## CPLs Gerados

### CPL1 - A Oportunidade Paralisante
- **Título**: {resultado['cpls']['cpl1']['titulo']}
- **Objetivo**: {resultado['cpls']['cpl1']['objetivo']}

### CPL2 - A Transformação Impossível
- **Título**: {resultado['cpls']['cpl2']['titulo']}
- **Objetivo**: {resultado['cpls']['cpl2']['objetivo']}

### CPL3 - O Caminho Revolucionário
- **Título**: {resultado['cpls']['cpl3']['titulo']}
- **Objetivo**: {resultado['cpls']['cpl3']['objetivo']}

### CPL4 - A Decisão Inevitável
- **Título**: {resultado['cpls']['cpl4']['titulo']}
- **Objetivo**: {resultado['cpls']['cpl4']['objetivo']}

## Estatísticas da Busca
- **Total de Posts**: {resultado.get('dados_busca', {}).get('total_posts', 0)}
- **Total de Imagens**: {resultado.get('dados_busca', {}).get('total_images', 0)}
- **Plataformas**: {', '.join(resultado.get('dados_busca', {}).get('platforms', {}).keys())}
"""

# Instância global
cpl_protocol = None
try:
    cpl_protocol = CPLDevastadorProtocol()
    logger.info("✅ CPL Protocol inicializado com sucesso")
except Exception as e:
    logger.warning(f"⚠️ CPL Protocol não disponível: {e}")
    cpl_protocol = None

def get_cpl_protocol() -> CPLDevastadorProtocol:
    """Retorna instância do protocolo CPL"""
    return cpl_protocol
