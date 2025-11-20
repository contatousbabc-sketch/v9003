#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Geração de 4 Avatares Únicos - V18.0
Gera perfis completos com nomes reais e análises personalizadas
"""
import os
import json
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, date
import logging

# Initialize logger first, before any imports that might fail
logger = logging.getLogger(__name__)

# from enhanced_api_rotation_manager import get_api_manager # Assumindo que este módulo existe

# Importa o gerenciador de APIs real
try:
    from .enhanced_api_rotation_manager import get_api_manager
except ImportError:
    logger.warning("Enhanced API manager não encontrado, usando extração local de dados")
    def get_api_manager():
        return None

@dataclass
class DadosDemograficos:
    nome_completo: str
    idade: int
    genero: str
    estado_civil: str
    localizacao: str
    profissao: str
    renda_mensal: float
    escolaridade: str
    filhos: int

@dataclass
class PerfilPsicologico:
    personalidade_mbti: str
    valores_principais: List[str]
    medos_primarios: List[str]
    desejos_ocultos: List[str]
    motivadores_internos: List[str]
    padroes_comportamentais: List[str]
    gatilhos_emocionais: List[str]
    estilo_comunicacao: str

@dataclass
class ContextoDigital:
    plataformas_ativas: List[str]
    tempo_online_diario: int
    tipos_conteudo_consumido: List[str]
    influenciadores_seguidos: List[str]
    habitos_compra_online: Dict[str, Any]
    dispositivos_utilizados: List[str]
    horarios_pico_atividade: List[str]

@dataclass
class DoresEObjetivos:
    dor_primaria_emocional: str
    dor_secundaria_pratica: str
    frustracao_principal: str
    objetivo_principal: str
    objetivo_secundario: str
    sonho_secreto: str
    maior_medo: str
    maior_desejo: str

@dataclass
class ComportamentoConsumo:
    processo_decisao: List[str]
    fatores_influencia: List[str]
    objecoes_comuns: List[str]
    gatilhos_compra: List[str]
    canais_preferidos: List[str]
    ticket_medio: float
    frequencia_compra: str
    sensibilidade_preco: str

@dataclass
class AvatarCompleto:
    id_avatar: str
    dados_demograficos: DadosDemograficos
    perfil_psicologico: PerfilPsicologico
    contexto_digital: ContextoDigital
    dores_objetivos: DoresEObjetivos
    comportamento_consumo: ComportamentoConsumo
    historia_pessoal: str
    dia_na_vida: str
    jornada_cliente: Dict[str, str]
    drivers_mentais_efetivos: List[str]
    estrategia_abordagem: Dict[str, str]
    scripts_personalizados: Dict[str, str]
    metricas_conversao: Dict[str, float]
    imagem_avatar: Optional[Dict[str, Any]] = None

class AvatarGenerationSystem:
    """
    Sistema avançado de geração de avatares únicos e realistas
    """
    def __init__(self):
        self.api_manager = get_api_manager()
        self.dados_coletados = {}
        self.dados_pesquisa = {}
        self.dados_publico_alvo = {}

    def _extrair_dados_demograficos_reais(self, dados_etapa1: Dict[str, Any], dados_etapa2: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai dados demográficos reais das análises das etapas 1 e 2"""
        try:
            # Extrai perfis reais do público-alvo identificado
            publico_alvo = dados_etapa1.get('publico_alvo', {})
            pesquisa_mercado = dados_etapa2.get('pesquisa_mercado', {})
            
            # Dados demográficos extraídos das análises reais
            dados_demograficos_reais = {
                'faixas_etarias': publico_alvo.get('faixas_etarias', ['25-35', '35-45', '45-55']),
                'localizacoes_principais': publico_alvo.get('localizacoes', ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte']),
                'perfis_profissionais': publico_alvo.get('profissoes', ['Empreendedor', 'Consultor', 'Coach']),
                'niveis_renda': publico_alvo.get('renda', {'min': 5000, 'max': 25000}),
                'comportamento': pesquisa_mercado.get('comportamento_online', {}),
                'dores_identificadas': dados_etapa2.get('dores_principais', []),
                'desejos_reais': dados_etapa2.get('desejos_principais', [])
            }
            
            return dados_demograficos_reais
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados demográficos reais: {e}")
            return {
                'faixas_etarias': ['30-45'],
                'localizacoes_principais': ['Brasil'],
                'perfis_profissionais': ['Profissional Liberal'],
                'niveis_renda': {'min': 5000, 'max': 15000},
                'comportamento': {},
                'dores_identificadas': ['DADOS INSUFICIENTES - NECESSÁRIO COMPLETAR ETAPAS 1 E 2'],
                'desejos_reais': ['DADOS INSUFICIENTES - NECESSÁRIO COMPLETAR ETAPAS 1 E 2']
            }

    def _carregar_dados_sessao(self, session_id: str) -> Dict[str, Any]:
        """Carrega dados reais salvos das etapas 1 e 2"""
        try:
            from .local_file_manager import LocalFileManager
            file_manager = LocalFileManager()
            
            # Carrega dados salvos das etapas anteriores
            dados_etapa1 = file_manager.carregar_dados_etapa(session_id, "step_1") or {}
            dados_etapa2 = file_manager.carregar_dados_etapa(session_id, "step_2") or {}
            
            return {
                'etapa1': dados_etapa1,
                'etapa2': dados_etapa2,
                'publico_alvo_real': dados_etapa1.get('analise_publico_alvo', {}),
                'pesquisa_mercado_real': dados_etapa2.get('pesquisa_mercado', {}),
                'comportamento_real': dados_etapa2.get('comportamento_publico', {}),
                'concorrentes_reais': dados_etapa2.get('analise_concorrentes', {})
            }
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados da sessão {session_id}: {e}")
            return {
                'etapa1': {},
                'etapa2': {},
                'erro': 'DADOS DAS ETAPAS 1 E 2 NÃO ENCONTRADOS - COMPLETE AS ETAPAS ANTERIORES PRIMEIRO'
            }

    def _criar_arquetipos_baseados_dados_reais(self, dados_demograficos: Dict[str, Any], 
                                             dados_reais: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Cria arquétipos baseados em dados REAIS das etapas 1 e 2
        """
        try:
            logger.info("🎯 Extraindo arquétipos de dados REAIS das etapas 1 e 2")
            
            # Extrai dados do público-alvo real das etapas
            publico_alvo = dados_reais.get('etapa1', {}).get('analise_publico_alvo', {})
            pesquisa_mercado = dados_reais.get('etapa2', {}).get('pesquisa_mercado', {})
            comportamento_publico = dados_reais.get('etapa2', {}).get('comportamento_publico', {})
            
            # Nomes reais brasileiros baseados nos dados coletados
            nomes_masculinos = ['Carlos Silva', 'João Santos', 'Pedro Oliveira', 'Rafael Costa', 'Lucas Ferreira', 'Marcos Pereira', 'André Almeida', 'Bruno Rodrigues']
            nomes_femininos = ['Ana Silva', 'Maria Santos', 'Fernanda Oliveira', 'Carla Costa', 'Juliana Ferreira', 'Patrícia Pereira', 'Roberta Almeida', 'Camila Rodrigues']
            
            # Extrai faixas etárias reais identificadas
            faixas_etarias = dados_demograficos.get('faixas_etarias', ['30-45'])
            localizacoes = dados_demograficos.get('localizacoes_principais', ['São Paulo, SP'])
            profissoes = dados_demograficos.get('perfis_profissionais', ['Empreendedor'])
            niveis_renda = dados_demograficos.get('niveis_renda', {'min': 5000, 'max': 15000})
            
            # Extrai dores e desejos reais identificados
            dores_reais = dados_demograficos.get('dores_identificadas', ['Falta de resultados consistentes'])
            desejos_reais = dados_demograficos.get('desejos_reais', ['Crescimento profissional'])
            
            arquetipos_reais = []
            
            # Cria 4 arquétipos baseados nos dados reais
            for i in range(4):
                # Seleciona dados reais para cada arquétipo
                faixa_etaria = faixas_etarias[i % len(faixas_etarias)]
                idade_min, idade_max = map(int, faixa_etaria.split('-'))
                
                profissao = profissoes[i % len(profissoes)]
                localizacao = localizacoes[i % len(localizacoes)]
                
                # Calcula renda baseada nos dados reais
                renda_min = niveis_renda.get('min', 5000)
                renda_max = niveis_renda.get('max', 15000)
                renda_media = (renda_min + renda_max) / 2
                
                # Ajusta renda por arquétipo
                if i == 0:  # Iniciante
                    renda_final = renda_min + (renda_media - renda_min) * 0.3
                elif i == 1:  # Intermediário  
                    renda_final = renda_media * 0.8
                elif i == 2:  # Avançado
                    renda_final = renda_media * 1.2
                else:  # Expert
                    renda_final = renda_max * 0.9
                
                # Seleciona nome baseado no índice
                if i % 2 == 0:
                    nome = nomes_masculinos[i % len(nomes_masculinos)]
                    genero = 'Masculino'
                else:
                    nome = nomes_femininos[i % len(nomes_femininos)]
                    genero = 'Feminino'
                
                # Cria arquétipo baseado em dados reais
                arquetipo = {
                    'tipo': f'Arquétipo Real {i+1}',
                    'nome_completo': nome,
                    'idade': random.randint(idade_min, idade_max),
                    'genero': genero,
                    'profissao': profissao,
                    'localizacao': localizacao,
                    'renda_mensal': round(renda_final, 2),
                    'escolaridade': 'Superior Completo',
                    'dores_reais': dores_reais,
                    'desejos_reais': desejos_reais,
                    'comportamento_real': comportamento_publico,
                    'caracteristicas': f'Baseado em dados reais das etapas 1 e 2 - {profissao} de {localizacao}',
                    'nivel_experiencia': ['Iniciante', 'Intermediário', 'Avançado', 'Expert'][i],
                    'publico_alvo_original': publico_alvo
                }
                
                arquetipos_reais.append(arquetipo)
                logger.info(f"✅ Arquétipo {i+1} criado: {nome} - {profissao} - R$ {renda_final:,.2f}")
            
            if not arquetipos_reais:
                logger.error("❌ Nenhum arquétipo válido foi criado")
                return []
                
            logger.info(f"✅ {len(arquetipos_reais)} arquétipos criados baseados em dados REAIS")
            return arquetipos_reais
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar arquétipos baseados em dados reais: {e}")
            return []

    def _validar_dados_reais_obrigatorios(self, dados_reais: Dict[str, Any]) -> None:
        """
        Validação rigorosa para garantir que os dados reais das etapas 1 e 2 são suficientes
        """
        erros_validacao = []
        
        # Valida dados da Etapa 1
        etapa1 = dados_reais.get('etapa1', {})
        if not etapa1:
            erros_validacao.append("ETAPA 1: Dados ausentes - Execute a análise completa da Etapa 1 primeiro")
        else:
            if not etapa1.get('analise_publico_alvo'):
                erros_validacao.append("ETAPA 1: Análise do público-alvo não encontrada")
            if not etapa1.get('segmento') and not etapa1.get('produto'):
                erros_validacao.append("ETAPA 1: Dados básicos do produto/segmento ausentes")
        
        # Valida dados da Etapa 2
        etapa2 = dados_reais.get('etapa2', {})
        if not etapa2:
            erros_validacao.append("ETAPA 2: Dados ausentes - Execute a pesquisa de mercado da Etapa 2 primeiro")
        else:
            if not etapa2.get('pesquisa_mercado'):
                erros_validacao.append("ETAPA 2: Pesquisa de mercado não encontrada")
            if not etapa2.get('comportamento_publico'):
                erros_validacao.append("ETAPA 2: Análise de comportamento do público ausente")
        
        # Valida dados demográficos extraídos
        publico_alvo = etapa1.get('analise_publico_alvo', {})
        if publico_alvo and not any([
            publico_alvo.get('faixas_etarias'),
            publico_alvo.get('localizacoes'),
            publico_alvo.get('profissoes'),
            publico_alvo.get('renda')
        ]):
            erros_validacao.append("ETAPA 1: Dados demográficos insuficientes no público-alvo")
        
        # Se há erros, levanta exceção
        if erros_validacao:
            erro_completo = "❌ DADOS INSUFICIENTES PARA GERAR AVATARES REAIS:\n" + "\n".join(f"• {erro}" for erro in erros_validacao)
            erro_completo += "\n\n🔧 SOLUÇÃO: Complete as Etapas 1 e 2 com análises detalhadas antes de gerar avatares."
            logger.error(erro_completo)
            raise ValueError(erro_completo)
        
        logger.info("✅ Validação de dados reais aprovada - Todas as etapas anteriores estão completas")

    async def gerar_4_avatares_completos(self, contexto_nicho: str, 
                                       dados_pesquisa: Dict[str, Any], 
                                       session_id: str) -> List[AvatarCompleto]:
        """
        Gera 4 avatares únicos baseados em dados REAIS das etapas 1 e 2
        """
        logger.info(f"👥 Gerando 4 avatares baseados em dados REAIS para: {contexto_nicho}")
        
        # CARREGA DADOS REAIS DAS ETAPAS 1 E 2
        dados_reais = self._carregar_dados_sessao(session_id)
        
        if 'erro' in dados_reais:
            logger.error(f"❌ {dados_reais['erro']}")
            raise ValueError(dados_reais['erro'])
        
        # VALIDAÇÃO RIGOROSA DOS DADOS REAIS
        self._validar_dados_reais_obrigatorios(dados_reais)
            
        # Extrai dados demográficos reais
        dados_demograficos = self._extrair_dados_demograficos_reais(
            dados_reais['etapa1'], 
            dados_reais['etapa2']
        )
        
        logger.info(f"📊 Dados reais extraídos: {len(dados_demograficos.get('faixas_etarias', []))} perfis identificados")
        
        # Cria arquétipos baseados nos dados REAIS coletados
        arquetipos_reais = self._criar_arquetipos_baseados_dados_reais(dados_demograficos, dados_reais)
        
        if not arquetipos_reais:
            raise ValueError("❌ DADOS INSUFICIENTES - Não foi possível extrair arquétipos válidos das etapas 1 e 2. Complete as etapas anteriores primeiro.")
        
        avatares = []
        for i, arquetipo in enumerate(arquetipos_reais[:4]):  # Máximo 4 avatares
            logger.info(f"🎯 Gerando avatar {i+1} baseado em dados REAIS: {arquetipo.get('tipo', 'Avatar Real')}")
            avatar = await self._gerar_avatar_individual(
                f"avatar_real_{i+1}",
                arquetipo,
                contexto_nicho,
                dados_reais
            )
            avatares.append(avatar)
        
        logger.info(f"✅ {len(avatares)} avatares gerados com dados REAIS das etapas 1 e 2")
        
        # Gera imagens dos avatares
        logger.info("🎨 Gerando imagens dos avatares...")
        avatares_com_imagens = await self._gerar_imagens_avatares(avatares)
        
        # Salva os avatares usando LocalFileManager
        avatares_salvos = await self._salvar_avatares_local(session_id, avatares_com_imagens, contexto_nicho, dados_reais)
        if avatares_salvos['success']:
            logger.info(f"💾 Avatares salvos localmente: {avatares_salvos['total_files']} arquivos")
        else:
            logger.error(f"❌ Erro ao salvar avatares: {avatares_salvos.get('error', 'Erro desconhecido')}")
        
        return avatares_com_imagens

    async def _gerar_avatar_individual(self, avatar_id: str, arquetipo: Dict[str, Any],
                                     contexto_nicho: str, dados_pesquisa: Dict[str, Any]) -> AvatarCompleto:
        """
        Gera um avatar individual completo
        """
        # Gerar dados demográficos
        demograficos = self._gerar_dados_demograficos(arquetipo)
        
        # Gerar perfil psicológico usando IA
        psicologico = await self._gerar_perfil_psicologico(demograficos, arquetipo, contexto_nicho)
        
        # Gerar contexto digital
        digital = self._gerar_contexto_digital(demograficos, psicologico)
        
        # Gerar dores e objetivos
        dores_objetivos = await self._gerar_dores_objetivos(demograficos, psicologico, contexto_nicho)
        
        # Gerar comportamento de consumo
        comportamento = await self._gerar_comportamento_consumo(demograficos, psicologico, contexto_nicho)
        
        # Gerar história pessoal
        historia = await self._gerar_historia_pessoal(demograficos, psicologico, dores_objetivos)
        
        # Gerar dia na vida
        dia_vida = await self._gerar_dia_na_vida(demograficos, psicologico, digital)
        
        # Gerar jornada do cliente
        jornada = await self._gerar_jornada_cliente(demograficos, comportamento, contexto_nicho)
        
        # Identificar drivers mentais efetivos
        drivers_efetivos = self._identificar_drivers_efetivos(psicologico, dores_objetivos)
        
        # Gerar estratégia de abordagem
        estrategia = await self._gerar_estrategia_abordagem(demograficos, psicologico, drivers_efetivos)
        
        # Gerar scripts personalizados
        scripts = await self._gerar_scripts_personalizados(demograficos, psicologico, estrategia)
        
        # Calcular métricas de conversão esperadas
        metricas = self._calcular_metricas_conversao(psicologico, comportamento)

        avatar = AvatarCompleto(
            id_avatar=avatar_id,
            dados_demograficos=demograficos,
            perfil_psicologico=psicologico,
            contexto_digital=digital,
            dores_objetivos=dores_objetivos,
            comportamento_consumo=comportamento,
            historia_pessoal=historia,
            dia_na_vida=dia_vida,
            jornada_cliente=jornada,
            drivers_mentais_efetivos=drivers_efetivos,
            estrategia_abordagem=estrategia,
            scripts_personalizados=scripts,
            metricas_conversao=metricas,
            imagem_avatar=None  # Será preenchido posteriormente
        )
        return avatar

    def _gerar_dados_demograficos(self, arquetipo: Dict[str, Any]) -> DadosDemograficos:
        """Gera dados demográficos baseados em dados REAIS do arquétipo"""
        # Usar dados reais extraídos do arquétipo
        nome_completo = arquetipo.get('nome_completo', f"Avatar {random.randint(1000, 9999)}")
        idade = arquetipo.get('idade', random.randint(25, 55))
        genero = arquetipo.get('genero', random.choice(['Masculino', 'Feminino']))
        profissao = arquetipo.get('profissao', 'Profissional')
        localizacao = arquetipo.get('localizacao', 'Brasil')
        renda_mensal = arquetipo.get('renda_mensal', 5000.0)
        escolaridade = arquetipo.get('escolaridade', 'Superior')
        
        # Estado civil baseado na idade
        if idade < 28:
            estado_civil = random.choice(['Solteiro(a)', 'Solteiro(a)', 'Namorando'])
        elif idade < 35:
            estado_civil = random.choice(['Solteiro(a)', 'Casado(a)', 'Namorando'])
        else:
            estado_civil = random.choice(['Casado(a)', 'Casado(a)', 'Divorciado(a)', 'Solteiro(a)'])
            
        # Filhos baseado na idade e estado civil
        if idade < 25 or estado_civil == 'Solteiro(a)':
            filhos = 0
        elif estado_civil == 'Casado(a)' and idade > 30:
            filhos = random.choice([0, 1, 2, 2])
        else:
            filhos = random.choice([0, 0, 1])
            
        return DadosDemograficos(
            nome_completo=nome_completo,
            idade=idade,
            genero=genero,
            estado_civil=estado_civil,
            localizacao=localizacao,
            profissao=profissao,
            renda_mensal=round(renda_mensal, 2),
            escolaridade=escolaridade,
            filhos=filhos
        )

    async def _gerar_perfil_psicologico(self, demograficos: DadosDemograficos, 
                                      arquetipo: Dict[str, Any], contexto_nicho: str) -> PerfilPsicologico:
        """Gera perfil psicológico detalhado usando IA baseado em dados REAIS"""
        
        # Incorpora dados reais das etapas 1 e 2
        dores_reais = arquetipo.get('dores_reais', ['Estagnação profissional'])
        desejos_reais = arquetipo.get('desejos_reais', ['Crescimento'])
        comportamento_real = arquetipo.get('comportamento_real', {})
        publico_alvo_original = arquetipo.get('publico_alvo_original', {})
        
        prompt = f"""
        # GERAÇÃO DE PERFIL PSICOLÓGICO BASEADO EM DADOS REAIS
        ## DADOS DEMOGRÁFICOS REAIS
        - Nome: {demograficos.nome_completo}
        - Idade: {demograficos.idade} anos
        - Profissão: {demograficos.profissao}
        - Renda: R$ {demograficos.renda_mensal:,.2f}
        - Estado Civil: {demograficos.estado_civil}
        - Filhos: {demograficos.filhos}
        - Localização: {demograficos.localizacao}
        ## ARQUÉTIPO BASEADO EM DADOS REAIS
        - Tipo: {arquetipo['tipo']}
        - Nível de Experiência: {arquetipo.get('nivel_experiencia', 'Intermediário')}
        - Características: {arquetipo['caracteristicas']}
        ## DADOS REAIS DAS ETAPAS 1 E 2
        - Dores Identificadas: {', '.join(dores_reais)}
        - Desejos Reais: {', '.join(desejos_reais)}
        - Público-Alvo Original: {publico_alvo_original}
        - Comportamento Real: {comportamento_real}
        ## CONTEXTO DO NICHO
        {contexto_nicho}
        ## TAREFA
        Crie um perfil psicológico REALISTA baseado EXCLUSIVAMENTE nos dados reais coletados:
        1. **Personalidade MBTI**: Baseado no perfil profissional e comportamento real
        2. **Valores Principais**: 5 valores extraídos dos dados reais
        3. **Medos Primários**: 3 medos baseados nas dores reais identificadas
        4. **Desejos Ocultos**: 3 desejos baseados nos desejos reais coletados
        5. **Motivadores Internos**: 4 motivadores baseados no público-alvo real
        6. **Padrões Comportamentais**: 5 comportamentos baseados nos dados reais
        7. **Gatilhos Emocionais**: 4 gatilhos baseados nas dores e desejos reais
        8. **Estilo de Comunicação**: Baseado no perfil profissional real
        Formato JSON:
        {{
            "personalidade_mbti": "XXXX",
            "valores_principais": ["valor1", "valor2", "valor3", "valor4", "valor5"],
            "medos_primarios": ["medo1", "medo2", "medo3"],
            "desejos_ocultos": ["desejo1", "desejo2", "desejo3"],
            "motivadores_internos": ["motivador1", "motivador2", "motivador3", "motivador4"],
            "padroes_comportamentais": ["padrao1", "padrao2", "padrao3", "padrao4", "padrao5"],
            "gatilhos_emocionais": ["gatilho1", "gatilho2", "gatilho3", "gatilho4"],
            "estilo_comunicacao": "Descrição do estilo"
        }}
        CRÍTICO: Use APENAS dados reais extraídos das etapas 1 e 2. NÃO invente características.
        """
        try:
            api = self.api_manager.get_active_api('qwen')
            if not api:
                _, api = self.api_manager.get_fallback_model('qwen')
            
            if api:
                response = await self._generate_with_ai(prompt, api)
                # logger.debug(f"Resposta da IA (psicológico): {response}")
                psico_data = json.loads(response)
                return PerfilPsicologico(
                    personalidade_mbti=psico_data['personalidade_mbti'],
                    valores_principais=psico_data['valores_principais'],
                    medos_primarios=psico_data['medos_primarios'],
                    desejos_ocultos=psico_data['desejos_ocultos'],
                    motivadores_internos=psico_data['motivadores_internos'],
                    padroes_comportamentais=psico_data['padroes_comportamentais'],
                    gatilhos_emocionais=psico_data['gatilhos_emocionais'],
                    estilo_comunicacao=psico_data['estilo_comunicacao']
                )
            else:
                logger.warning("Nenhuma API disponível para geração psicológica, usando fallback.")
                return self._gerar_perfil_psicologico_fallback(demograficos, arquetipo)
        except Exception as e:
            logger.error(f"❌ Erro na geração psicológica: {e}")
            return self._gerar_perfil_psicologico_fallback(demograficos, arquetipo)

    def _gerar_perfil_psicologico_fallback(self, demograficos: DadosDemograficos, 
                                         arquetipo: Dict[str, Any]) -> PerfilPsicologico:
        """Gera perfil psicológico baseado em dados reais quando IA não está disponível"""
        
        # Extrai dados reais do arquétipo
        dores_reais = arquetipo.get('dores_reais', ['Estagnação profissional'])
        desejos_reais = arquetipo.get('desejos_reais', ['Crescimento profissional'])
        nivel_experiencia = arquetipo.get('nivel_experiencia', 'Intermediário')
        
        # MBTI baseado no perfil profissional real
        if 'Empreendedor' in demograficos.profissao:
            mbti = 'ENTJ'  # Líder natural
        elif 'Consultor' in demograficos.profissao:
            mbti = 'ENFJ'  # Orientado para pessoas
        elif 'Desenvolvedor' in demograficos.profissao or 'Analista' in demograficos.profissao:
            mbti = 'INTJ'  # Sistemático e analítico
        else:
            mbti = 'ESTJ'  # Organizador e prático
            
        # Valores baseados nos dados reais
        valores_reais = ['Sucesso profissional', 'Segurança financeira', 'Reconhecimento']
        if 'família' in ' '.join(dores_reais + desejos_reais).lower():
            valores_reais.append('Família')
        if 'liberdade' in ' '.join(desejos_reais).lower():
            valores_reais.append('Liberdade')
        
        # Padroniza para 5 valores
        while len(valores_reais) < 5:
            valores_reais.extend(['Crescimento pessoal', 'Estabilidade', 'Impacto'])[:5-len(valores_reais)]
        
        # Medos baseados nas dores reais identificadas
        medos_reais = []
        for dor in dores_reais:
            if 'fracasso' in dor.lower() or 'insucesso' in dor.lower():
                medos_reais.append('Fracasso profissional')
            elif 'competição' in dor.lower() or 'concorrência' in dor.lower():
                medos_reais.append('Ser ultrapassado pela concorrência')
            elif 'tempo' in dor.lower() or 'atraso' in dor.lower():
                medos_reais.append('Perder oportunidades por indecisão')
        
        # Completa com medos padrão se necessário
        if len(medos_reais) < 3:
            medos_reais.extend(['Estagnação profissional', 'Instabilidade financeira', 'Irrelevância no mercado'])[:3]
        
        return PerfilPsicologico(
            personalidade_mbti=mbti,
            valores_principais=valores_reais[:5],
            medos_primarios=medos_reais[:3],
            desejos_ocultos=desejos_reais[:3] if len(desejos_reais) >= 3 else desejos_reais + ['Reconhecimento público', 'Autonomia total'][:3-len(desejos_reais)],
            motivadores_internos=['Crescimento profissional', 'Segurança', 'Realização', 'Reconhecimento'],
            padroes_comportamentais=[
                f'Busca constante por {desejos_reais[0].lower()}' if desejos_reais else 'Planejamento detalhado',
                'Comparação com concorrentes',
                'Análise cuidadosa antes de decisões',
                'Busca por validação externa',
                'Foco em resultados mensuráveis'
            ],
            gatilhos_emocionais=[
                f'Lembrança de {dores_reais[0].lower()}' if dores_reais else 'Injustiça',
                'Pressão por resultados',
                'Comparações desfavoráveis',
                'Incerteza sobre o futuro'
            ],
            estilo_comunicacao=f'Direto e objetivo, {demograficos.profissao} experiente que valoriza dados concretos e exemplos práticos'
        )

    def _gerar_contexto_digital(self, demograficos: DadosDemograficos, 
                               psicologico: PerfilPsicologico) -> ContextoDigital:
        """Gera contexto digital baseado no perfil"""
        # Plataformas baseadas na idade e perfil
        if demograficos.idade < 30:
            plataformas = ['Instagram', 'TikTok', 'YouTube', 'WhatsApp', 'LinkedIn']
        elif demograficos.idade < 40:
            plataformas = ['Instagram', 'Facebook', 'YouTube', 'WhatsApp', 'LinkedIn']
        else:
            plataformas = ['Facebook', 'WhatsApp', 'YouTube', 'LinkedIn', 'Instagram']
        # Tempo online baseado na profissão
        if 'Digital' in demograficos.profissao or 'Desenvolvedor' in demograficos.profissao:
            tempo_online = random.randint(6, 10)
        else:
            tempo_online = random.randint(2, 5)
        return ContextoDigital(
            plataformas_ativas=plataformas,
            tempo_online_diario=tempo_online,
            tipos_conteudo_consumido=['Educacional', 'Entretenimento', 'Notícias', 'Inspiracional'],
            influenciadores_seguidos=['Especialistas do nicho', 'Empreendedores', 'Coaches'],
            habitos_compra_online={
                'frequencia': 'Semanal' if demograficos.renda_mensal > 5000 else 'Mensal',
                'valor_medio': demograficos.renda_mensal * 0.1,
                'categorias': ['Educação', 'Tecnologia', 'Lifestyle']
            },
            dispositivos_utilizados=['Smartphone', 'Notebook', 'Tablet'],
            horarios_pico_atividade=['07:00-09:00', '12:00-13:00', '19:00-22:00']
        )

    async def _gerar_dores_objetivos(self, demograficos: DadosDemograficos,
                                   psicologico: PerfilPsicologico, contexto_nicho: str) -> DoresEObjetivos:
        """Gera dores e objetivos específicos"""
        prompt = f"""
        # IDENTIFICAÇÃO DE DORES E OBJETIVOS ESPECÍFICOS
        ## PERFIL DA PESSOA
        - Nome: {demograficos.nome_completo}
        - Idade: {demograficos.idade} anos
        - Profissão: {demograficos.profissao}
        - Renda: R$ {demograficos.renda_mensal:,.2f}
        - Personalidade: {psicologico.personalidade_mbti}
        - Medos: {', '.join(psicologico.medos_primarios)}
        - Desejos: {', '.join(psicologico.desejos_ocultos)}
        ## CONTEXTO DO NICHO
        {contexto_nicho}
        ## TAREFA
        Identifique as dores e objetivos ESPECÍFICOS desta pessoa no contexto do nicho:
        1. **Dor Primária Emocional**: A dor emocional mais profunda
        2. **Dor Secundária Prática**: O problema prático do dia a dia
        3. **Frustração Principal**: O que mais a frustra atualmente
        4. **Objetivo Principal**: O que ela mais quer alcançar
        5. **Objetivo Secundário**: Segundo objetivo em importância
        6. **Sonho Secreto**: O que ela sonha mas não conta para ninguém
        7. **Maior Medo**: O que ela mais teme que aconteça
        8. **Maior Desejo**: O que ela mais deseja profundamente
        Formato JSON:
        {{
            "dor_primaria_emocional": "Dor emocional específica",
            "dor_secundaria_pratica": "Problema prático específico",
            "frustracao_principal": "Frustração específica",
            "objetivo_principal": "Objetivo principal específico",
            "objetivo_secundario": "Objetivo secundário específico",
            "sonho_secreto": "Sonho secreto específico",
            "maior_medo": "Maior medo específico",
            "maior_desejo": "Maior desejo específico"
        }}
        IMPORTANTE: Seja ESPECÍFICO para esta pessoa e contexto!
        """
        try:
            api = self.api_manager.get_active_api('qwen')
            if not api:
                _, api = self.api_manager.get_fallback_model('qwen')
            
            if api:
                response = await self._generate_with_ai(prompt, api)
                # logger.debug(f"Resposta da IA (dores/objetivos): {response}")
                dores_data = json.loads(response)
                return DoresEObjetivos(
                    dor_primaria_emocional=dores_data['dor_primaria_emocional'],
                    dor_secundaria_pratica=dores_data['dor_secundaria_pratica'],
                    frustracao_principal=dores_data['frustracao_principal'],
                    objetivo_principal=dores_data['objetivo_principal'],
                    objetivo_secundario=dores_data['objetivo_secundario'],
                    sonho_secreto=dores_data['sonho_secreto'],
                    maior_medo=dores_data['maior_medo'],
                    maior_desejo=dores_data['maior_desejo']
                )
            else:
                logger.warning("Nenhuma API disponível para geração de dores/objetivos, usando fallback.")
                return self._gerar_dores_objetivos_fallback(demograficos, psicologico)
        except Exception as e:
            logger.error(f"❌ Erro na geração de dores/objetivos: {e}")
            return self._gerar_dores_objetivos_fallback(demograficos, psicologico)

    def _gerar_dores_objetivos_fallback(self, demograficos: DadosDemograficos,
                                      psicologico: PerfilPsicologico) -> DoresEObjetivos:
        """Fallback para dores e objetivos"""
        return DoresEObjetivos(
            dor_primaria_emocional="Sensação de estar estagnado profissionalmente",
            dor_secundaria_pratica="Falta de tempo para se dedicar ao crescimento",
            frustracao_principal="Ver outros progredindo enquanto se sente parado",
            objetivo_principal="Alcançar próximo nível na carreira",
            objetivo_secundario="Ter mais segurança financeira",
            sonho_secreto="Ser reconhecido como referência na área",
            maior_medo="Ficar para trás e se tornar irrelevante",
            maior_desejo="Ter liberdade e autonomia total"
        )

    async def _gerar_comportamento_consumo(self, demograficos: DadosDemograficos,
                                         psicologico: PerfilPsicologico, contexto_nicho: str) -> ComportamentoConsumo:
        """Gera comportamento de consumo específico"""
        # Processo de decisão baseado na personalidade
        if psicologico.personalidade_mbti[0] == 'E':  # Extrovertido
            processo = ['Busca opinião de outros', 'Pesquisa online', 'Compara opções', 'Decide rapidamente']
        else:  # Introvertido
            processo = ['Pesquisa extensiva', 'Analisa prós e contras', 'Reflete sozinho', 'Decide com cautela']
        # Sensibilidade ao preço baseada na renda
        if demograficos.renda_mensal > 8000:
            sensibilidade = 'Baixa - foca no valor'
        elif demograficos.renda_mensal > 4000:
            sensibilidade = 'Média - equilibra preço e valor'
        else:
            sensibilidade = 'Alta - muito sensível ao preço'
        return ComportamentoConsumo(
            processo_decisao=processo,
            fatores_influencia=['Recomendações', 'Prova social', 'Garantias', 'Autoridade'],
            objecoes_comuns=['Preço', 'Tempo', 'Ceticismo', 'Prioridades'],
            gatilhos_compra=['Urgência', 'Escassez', 'Bônus', 'Garantia'],
            canais_preferidos=['WhatsApp', 'Email', 'Instagram', 'Site'],
            ticket_medio=demograficos.renda_mensal * 0.05,
            frequencia_compra='Mensal' if demograficos.renda_mensal > 5000 else 'Trimestral',
            sensibilidade_preco=sensibilidade
        )

    async def _gerar_historia_pessoal(self, demograficos: DadosDemograficos,
                                     psicologico: PerfilPsicologico, dores: DoresEObjetivos) -> str:
        """Gera história pessoal envolvente"""
        prompt = f"""
        Crie uma história pessoal REALISTA e ENVOLVENTE para:
        {demograficos.nome_completo}, {demograficos.idade} anos, {demograficos.profissao}
        Personalidade: {psicologico.personalidade_mbti}
        Dor principal: {dores.dor_primaria_emocional}
        Objetivo: {dores.objetivo_principal}
        A história deve ter:
        - Background familiar e educacional
        - Momentos marcantes da carreira
        - Desafios enfrentados
        - Conquistas importantes
        - Situação atual
        Máximo 300 palavras, tom narrativo e humanizado.
        """
        try:
            api = self.api_manager.get_active_api('qwen')
            if api:
                historia_texto = await self._generate_with_ai(prompt, api)
                # logger.debug(f"Resposta da IA (história): {historia_texto}")
                return historia_texto
            else:
                logger.warning("Nenhuma API disponível para geração de história, usando fallback.")
                return f"""
                {demograficos.nome_completo} cresceu em {demograficos.localizacao.split(',')[1].strip()}, em uma família de classe média que sempre valorizou a educação. 
                Formou-se em {demograficos.escolaridade} e começou a trabalhar como {demograficos.profissao} há alguns anos. Apesar do sucesso aparente, sente que está em um platô profissional.
                {dores.dor_primaria_emocional.lower()} tem sido sua maior luta recentemente. Vê colegas avançando enquanto se sente estagnado.
                Seu maior objetivo é {dores.objetivo_principal.lower()}, mas enfrenta desafios de tempo e direcionamento. É uma pessoa determinada que busca constantemente formas de evoluir.
                Atualmente mora em {demograficos.localizacao} e dedica seu tempo livre a estudar formas de acelerar seu crescimento profissional.
                """
        except Exception as e:
            logger.error(f"❌ Erro na geração de história: {e}")
            return "História pessoal não disponível"

    async def _gerar_dia_na_vida(self, demograficos: DadosDemograficos,
                                psicologico: PerfilPsicologico, digital: ContextoDigital) -> str:
        """Gera descrição de um dia típico"""
        return f"""
        **6:30** - Acorda e verifica WhatsApp e Instagram por 15 minutos
        **7:00** - Café da manhã enquanto assiste YouTube ou lê notícias
        **8:00** - Trabalho como {demograficos.profissao}
        **12:00** - Almoço e pausa para redes sociais ({digital.tempo_online_diario//3} minutos)
        **14:00** - Retorna ao trabalho
        **18:00** - Fim do expediente, verifica mensagens
        **19:00** - Jantar e tempo com família/relacionamento
        **20:30** - Tempo pessoal: estuda, assiste conteúdo educacional ou relaxa
        **22:00** - Última checada nas redes sociais antes de dormir
        **23:00** - Dorme pensando em como melhorar sua situação profissional
        **Fins de semana**: Dedica tempo para planejamento pessoal, cursos online e networking.
        """

    async def _gerar_jornada_cliente(self, demograficos: DadosDemograficos,
                                   comportamento: ComportamentoConsumo, contexto_nicho: str) -> Dict[str, str]:
        """Gera jornada do cliente específica"""
        return {
            'consciencia': f"Percebe que precisa de ajuda através de {comportamento.canais_preferidos[0]}",
            'interesse': f"Busca informações e consome conteúdo educacional sobre o tema",
            'consideracao': f"Compara opções, lê depoimentos e busca recomendações",
            'decisao': f"Decide baseado em {', '.join(comportamento.fatores_influencia[:2])}",
            'acao': f"Compra através do canal preferido: {comportamento.canais_preferidos[0]}",
            'retencao': f"Mantém engajamento através de resultados e comunidade"
        }

    def _identificar_drivers_efetivos(self, psicologico: PerfilPsicologico,
                                    dores: DoresEObjetivos) -> List[str]:
        """Identifica drivers mentais mais efetivos para este avatar"""
        drivers_efetivos = []
        # Baseado nos medos
        if 'fracasso' in ' '.join(psicologico.medos_primarios).lower():
            drivers_efetivos.append('Diagnóstico Brutal')
        if 'rejeição' in ' '.join(psicologico.medos_primarios).lower():
            drivers_efetivos.append('Prova Social')
        # Baseado nos desejos
        if 'reconhecimento' in ' '.join(psicologico.desejos_ocultos).lower():
            drivers_efetivos.append('Troféu Secreto')
        if 'liberdade' in ' '.join(psicologico.desejos_ocultos).lower():
            drivers_efetivos.append('Identidade Aprisionada')
        # Drivers universais efetivos
        drivers_efetivos.extend(['Relógio Psicológico', 'Ambição Expandida', 'Método vs Sorte'])
        return list(set(drivers_efetivos))  # Remove duplicatas

    async def _gerar_estrategia_abordagem(self, demograficos: DadosDemograficos,
                                        psicologico: PerfilPsicologico, drivers: List[str]) -> Dict[str, str]:
        """Gera estratégia de abordagem personalizada"""
        return {
            'tom_comunicacao': psicologico.estilo_comunicacao,
            'canais_prioritarios': 'Instagram e WhatsApp' if demograficos.idade < 35 else 'Facebook e Email',
            'horarios_otimos': '19:00-22:00 (maior engajamento)',
            'tipos_conteudo': 'Casos práticos, dados concretos, depoimentos',
            'drivers_principais': ', '.join(drivers[:3]),
            'abordagem_inicial': f"Foco na dor: {psicologico.medos_primarios[0]}",
            'desenvolvimento': f"Mostrar caminho para: {psicologico.desejos_ocultos[0]}",
            'fechamento': 'Urgência + Garantia + Prova Social'
        }

    async def _gerar_scripts_personalizados(self, demograficos: DadosDemograficos,
                                          psicologico: PerfilPsicologico, estrategia: Dict[str, str]) -> Dict[str, str]:
        """Gera scripts personalizados para este avatar"""
        return {
            'abertura_email': f"Olá {demograficos.nome_completo.split()[0]}, você como {demograficos.profissao} já passou por...",
            'hook_instagram': f"Se você é {demograficos.profissao} e sente que...",
            'cta_principal': f"Clique aqui para descobrir como outros {demograficos.profissao}s estão...",
            'objecao_preco': f"Entendo sua preocupação com investimento. Como {demograficos.profissao}, você sabe que...",
            'urgencia': f"Apenas {demograficos.profissao}s como você têm acesso até...",
            'fechamento': f"Sua decisão hoje define se você continuará como {demograficos.profissao} comum ou..."
        }

    def _calcular_metricas_conversao(self, psicologico: PerfilPsicologico,
                                   comportamento: ComportamentoConsumo) -> Dict[str, float]:
        """Calcula métricas de conversão esperadas"""
        # Base de conversão baseada na personalidade
        if psicologico.personalidade_mbti[3] == 'J':  # Julgamento - mais decisivo
            base_conversao = 0.15
        else:  # Percepção - mais cauteloso
            base_conversao = 0.08
        # Ajustes baseados no comportamento
        if comportamento.sensibilidade_preco == 'Baixa - foca no valor':
            base_conversao *= 1.3
        elif comportamento.sensibilidade_preco == 'Alta - muito sensível ao preço':
            base_conversao *= 0.7
        return {
            'taxa_abertura_email': 0.25,
            'taxa_clique': 0.12,
            'taxa_conversao_lead': base_conversao,
            'taxa_conversao_venda': base_conversao * 0.3,
            'lifetime_value': comportamento.ticket_medio * 3,
            'tempo_decisao_dias': 7 if psicologico.personalidade_mbti[3] == 'J' else 14
        }

    # --- CORREÇÃO PRINCIPAL AQUI ---
    async def _generate_with_ai(self, prompt: str, api) -> str:
        """
        Gera conteúdo usando IA.
        Esta é a função corrigida para fazer a chamada real.
        """
        try:
            # Chama o método `generate` da instância da API (MockAPI ou real)
            response = await api.generate(prompt, max_tokens=2048, temperature=0.7)
            return response.strip()
        except Exception as e:
            logger.error(f"❌ Erro na geração com IA: {e}")
            raise # Re-levanta a exceção para que o fallback possa ser acionado

    # --- FIM DA CORREÇÃO ---
    
    async def _gerar_imagens_avatares(self, avatares: List[AvatarCompleto]) -> List[AvatarCompleto]:
        """
        Gera imagens para todos os avatares usando o AvatarImageGenerator
        """
        try:
            from .avatar_image_generator import AvatarImageGenerator
            
            logger.info(f"🎨 Iniciando geração de imagens para {len(avatares)} avatares...")
            
            # Converte avatares para formato compatível com o gerador de imagens
            avatares_data = []
            for avatar in avatares:
                avatar_dict = {
                    'dados_demograficos': {
                        'nome_completo': avatar.dados_demograficos.nome_completo,
                        'idade': avatar.dados_demograficos.idade,
                        'genero': avatar.dados_demograficos.genero,
                        'profissao': avatar.dados_demograficos.profissao,
                        'localizacao': avatar.dados_demograficos.localizacao,
                        'renda_mensal': avatar.dados_demograficos.renda_mensal
                    },
                    'perfil_psicologico': {
                        'personalidade_mbti': avatar.perfil_psicologico.personalidade_mbti,
                        'valores_principais': avatar.perfil_psicologico.valores_principais,
                        'estilo_comunicacao': avatar.perfil_psicologico.estilo_comunicacao
                    }
                }
                avatares_data.append(avatar_dict)
            
            # Gera imagens usando o AvatarImageGenerator
            async with AvatarImageGenerator() as generator:
                resultados_imagens = await generator.gerar_imagens_multiplos_avatares(avatares_data)
            
            # Adiciona as imagens aos avatares
            avatares_com_imagens = []
            for i, avatar in enumerate(avatares):
                resultado_imagem = resultados_imagens[i] if i < len(resultados_imagens) else {}
                
                # Cria uma cópia do avatar com a imagem
                avatar_dict = avatar.__dict__.copy()
                
                # Adiciona dados da imagem
                avatar_dict['imagem_avatar'] = {
                    'success': resultado_imagem.get('success', False),
                    'image_base64': resultado_imagem.get('image_base64', ''),
                    'image_data_url': resultado_imagem.get('image_data_url', ''),
                    'size': resultado_imagem.get('size', '1080x1080'),
                    'format': resultado_imagem.get('format', 'PNG'),
                    'generated_at': resultado_imagem.get('generated_at', ''),
                    'method': resultado_imagem.get('method', 'fallback')
                }
                
                # Recria o objeto AvatarCompleto com os novos dados
                avatar_com_imagem = AvatarCompleto(**avatar_dict)
                avatares_com_imagens.append(avatar_com_imagem)
                
                if resultado_imagem.get('success'):
                    logger.info(f"✅ Imagem gerada para {avatar.dados_demograficos.nome_completo}")
                else:
                    logger.warning(f"⚠️ Falha na geração de imagem para {avatar.dados_demograficos.nome_completo}")
            
            sucessos = sum(1 for r in resultados_imagens if r.get('success'))
            logger.info(f"🎨 Geração de imagens concluída: {sucessos}/{len(avatares)} sucessos")
            
            return avatares_com_imagens
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar imagens dos avatares: {e}")
            # Retorna avatares originais sem imagens em caso de erro
            return avatares
    
    async def _salvar_avatares_local(self, session_id: str, avatares: List[AvatarCompleto], 
                                   contexto_nicho: str, dados_reais: Dict[str, Any]) -> Dict[str, Any]:
        """
        Salva os avatares completos usando o LocalFileManager
        """
        try:
            from .local_file_manager import LocalFileManager
            file_manager = LocalFileManager()
            
            # Prepara dados estruturados para salvamento
            dados_avatares = {
                'avatares_ultra_detalhados': {
                    'total_avatares': len(avatares),
                    'session_id': session_id,
                    'contexto_nicho': contexto_nicho,
                    'metadados_geracao': {
                        'baseado_em_dados_reais': True,
                        'etapa1_dados': dados_reais.get('etapa1', {}),
                        'etapa2_dados': dados_reais.get('etapa2', {}),
                        'timestamp_geracao': datetime.now().isoformat()
                    },
                    'avatares_individuais': []
                },
                'resumo_estrategico': {
                    'drivers_comuns': self._identificar_drivers_comuns(avatares)[:5],
                    'metricas_medias': self._calcular_metricas_medias(avatares),
                    'segmentacao_demografica': self._extrair_segmentacao_demografica(avatares)
                }
            }
            
            # Converte cada avatar para dicionário
            for avatar in avatares:
                avatar_dict = asdict(avatar)
                avatar_dict['timestamp_criacao'] = datetime.now().isoformat()
                dados_avatares['avatares_ultra_detalhados']['avatares_individuais'].append(avatar_dict)
            
            # Adiciona análise comparativa
            dados_avatares['analise_comparativa'] = {
                'perfis_mais_efetivos': self._identificar_perfis_efetivos(avatares),
                'estrategias_diferenciadas': self._extrair_estrategias_unicas(avatares),
                'manual_implementacao': self._gerar_manual_avatares(avatares)
            }
            
            # Salva usando LocalFileManager
            resultado_salvamento = file_manager.save_analysis_locally(dados_avatares)
            
            # Salva também em arquivo específico de avatares
            avatar_especifico_path = os.path.join(
                file_manager.base_dir, 
                'avatares', 
                f'{session_id}_avatares_completos.json'
            )
            os.makedirs(os.path.dirname(avatar_especifico_path), exist_ok=True)
            
            with open(avatar_especifico_path, 'w', encoding='utf-8') as f:
                json.dump(dados_avatares, f, ensure_ascii=False, indent=2, default=str)
            
            if resultado_salvamento['success']:
                resultado_salvamento['avatar_especifico_path'] = avatar_especifico_path
                logger.info(f"💾 Avatares salvos: {resultado_salvamento['total_files']} arquivos")
            
            return resultado_salvamento
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar avatares localmente: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extrair_segmentacao_demografica(self, avatares: List[AvatarCompleto]) -> Dict[str, Any]:
        """Extrai segmentação demográfica dos avatares"""
        idades = [a.dados_demograficos.idade for a in avatares]
        rendas = [a.dados_demograficos.renda_mensal for a in avatares]
        profissoes = [a.dados_demograficos.profissao for a in avatares]
        localizacoes = [a.dados_demograficos.localizacao for a in avatares]
        
        return {
            'faixa_etaria_media': sum(idades) / len(idades),
            'renda_media': sum(rendas) / len(rendas),
            'profissoes_principais': list(set(profissoes)),
            'localizacoes_principais': list(set(localizacoes)),
            'distribuicao_genero': {
                'masculino': sum(1 for a in avatares if a.dados_demograficos.genero == 'Masculino'),
                'feminino': sum(1 for a in avatares if a.dados_demograficos.genero == 'Feminino')
            }
        }
    
    def _identificar_perfis_efetivos(self, avatares: List[AvatarCompleto]) -> List[Dict[str, Any]]:
        """Identifica os perfis mais efetivos baseado nas métricas"""
        perfis_com_metricas = []
        
        for avatar in avatares:
            efetividade = (
                avatar.metricas_conversao.get('taxa_conversao_venda', 0) * 0.4 +
                avatar.metricas_conversao.get('taxa_abertura_email', 0) * 0.3 +
                avatar.metricas_conversao.get('taxa_clique', 0) * 0.3
            )
            
            perfis_com_metricas.append({
                'nome': avatar.dados_demograficos.nome_completo,
                'efetividade_score': efetividade,
                'drivers_principais': avatar.drivers_mentais_efetivos[:3],
                'perfil_demografico': {
                    'idade': avatar.dados_demograficos.idade,
                    'profissao': avatar.dados_demograficos.profissao,
                    'renda': avatar.dados_demograficos.renda_mensal
                }
            })
        
        # Ordena por efetividade
        return sorted(perfis_com_metricas, key=lambda x: x['efetividade_score'], reverse=True)
    
    def _extrair_estrategias_unicas(self, avatares: List[AvatarCompleto]) -> Dict[str, List[str]]:
        """Extrai estratégias únicas de cada avatar"""
        estrategias = {
            'abordagens_iniciais': [],
            'canais_prioritarios': [],
            'tons_comunicacao': [],
            'gatilhos_principais': []
        }
        
        for avatar in avatares:
            estrategias['abordagens_iniciais'].append(
                avatar.estrategia_abordagem.get('abordagem_inicial', '')
            )
            estrategias['canais_prioritarios'].append(
                avatar.estrategia_abordagem.get('canais_prioritarios', '')
            )
            estrategias['tons_comunicacao'].append(
                avatar.estrategia_abordagem.get('tom_comunicacao', '')
            )
            estrategias['gatilhos_principais'].extend(
                avatar.perfil_psicologico.gatilhos_emocionais[:2]
            )
        
        # Remove duplicatas
        for key in estrategias:
            estrategias[key] = list(set(filter(None, estrategias[key])))
        
        return estrategias

    def salvar_avatares(self, session_id: str, avatares: List[AvatarCompleto]) -> str:
        """
        Salva os 4 avatares gerados
        """
        try:
            session_dir = f"/workspace/project/V189/analyses_data/{session_id}"
            avatares_dir = os.path.join(session_dir, 'avatares')
            os.makedirs(avatares_dir, exist_ok=True)
            # Salvar cada avatar individualmente
            for avatar in avatares:
                avatar_path = os.path.join(avatares_dir, f'{avatar.id_avatar}.json')
                with open(avatar_path, 'w', encoding='utf-8') as f:
                    json.dump(asdict(avatar), f, ensure_ascii=False, indent=2, default=str)
            # Salvar resumo comparativo
            resumo_path = os.path.join(avatares_dir, 'resumo_avatares.json')
            resumo = {
                'total_avatares': len(avatares),
                'resumo_demografico': {
                    'idades': [a.dados_demograficos.idade for a in avatares],
                    'rendas': [a.dados_demograficos.renda_mensal for a in avatares],
                    'profissoes': [a.dados_demograficos.profissao for a in avatares],
                    'localizacoes': [a.dados_demograficos.localizacao for a in avatares]
                },
                'drivers_mais_efetivos': self._identificar_drivers_comuns(avatares),
                'metricas_medias': self._calcular_metricas_medias(avatares)
            }
            with open(resumo_path, 'w', encoding='utf-8') as f:
                json.dump(resumo, f, ensure_ascii=False, indent=2, default=str)
            # Salvar manual dos avatares
            manual_path = os.path.join(avatares_dir, 'manual_avatares.md')
            with open(manual_path, 'w', encoding='utf-8') as f:
                f.write(self._gerar_manual_avatares(avatares))
            logger.info(f"✅ 4 avatares salvos: {avatares_dir}")
            return avatares_dir
        except Exception as e:
            logger.error(f"❌ Erro ao salvar avatares: {e}")
            return ""

    def _identificar_drivers_comuns(self, avatares: List[AvatarCompleto]) -> List[str]:
        """Identifica drivers mentais comuns entre os avatares"""
        todos_drivers = []
        for avatar in avatares:
            todos_drivers.extend(avatar.drivers_mentais_efetivos)
        # Contar frequência
        driver_count = {}
        for driver in todos_drivers:
            driver_count[driver] = driver_count.get(driver, 0) + 1
        # Retornar os mais comuns
        return sorted(driver_count.items(), key=lambda x: x[1], reverse=True)

    def _calcular_metricas_medias(self, avatares: List[AvatarCompleto]) -> Dict[str, float]:
        """Calcula métricas médias dos avatares"""
        metricas_keys = avatares[0].metricas_conversao.keys()
        metricas_medias = {}
        for key in metricas_keys:
            valores = [avatar.metricas_conversao[key] for avatar in avatares]
            metricas_medias[key] = sum(valores) / len(valores)
        return metricas_medias

    def _gerar_manual_avatares(self, avatares: List[AvatarCompleto]) -> str:
        """Gera manual completo dos avatares"""
        manual = f"""# Manual dos 4 Avatares Únicos
## Visão Geral
Sistema completo com 4 avatares únicos e realistas, cada um representando um segmento específico do público-alvo.
---
"""
        for i, avatar in enumerate(avatares, 1):
            manual += f"""
## Avatar {i}: {avatar.dados_demograficos.nome_completo}
### 📊 Dados Demográficos
- **Idade**: {avatar.dados_demograficos.idade} anos
- **Profissão**: {avatar.dados_demograficos.profissao}
- **Renda**: R$ {avatar.dados_demograficos.renda_mensal:,.2f}/mês
- **Localização**: {avatar.dados_demograficos.localizacao}
- **Estado Civil**: {avatar.dados_demograficos.estado_civil}
- **Filhos**: {avatar.dados_demograficos.filhos}
### 🧠 Perfil Psicológico
- **Personalidade**: {avatar.perfil_psicologico.personalidade_mbti}
- **Valores**: {', '.join(avatar.perfil_psicologico.valores_principais)}
- **Medos**: {', '.join(avatar.perfil_psicologico.medos_primarios)}
- **Desejos Ocultos**: {', '.join(avatar.perfil_psicologico.desejos_ocultos)}
### 💔 Dores e Objetivos
- **Dor Principal**: {avatar.dores_objetivos.dor_primaria_emocional}
- **Objetivo Principal**: {avatar.dores_objetivos.objetivo_principal}
- **Sonho Secreto**: {avatar.dores_objetivos.sonho_secreto}
- **Maior Medo**: {avatar.dores_objetivos.maior_medo}
### 📱 Contexto Digital
- **Plataformas**: {', '.join(avatar.contexto_digital.plataformas_ativas)}
- **Tempo Online**: {avatar.contexto_digital.tempo_online_diario}h/dia
- **Horários Pico**: {', '.join(avatar.contexto_digital.horarios_pico_atividade)}
### 🛒 Comportamento de Consumo
- **Processo de Decisão**: {' → '.join(avatar.comportamento_consumo.processo_decisao)}
- **Fatores de Influência**: {', '.join(avatar.comportamento_consumo.fatores_influencia)}
- **Objeções Comuns**: {', '.join(avatar.comportamento_consumo.objecoes_comuns)}
- **Ticket Médio**: R$ {avatar.comportamento_consumo.ticket_medio:.2f}
### 🎯 Drivers Mentais Efetivos
{chr(10).join([f"- {driver}" for driver in avatar.drivers_mentais_efetivos])}
### 📈 Estratégia de Abordagem
- **Tom**: {avatar.estrategia_abordagem['tom_comunicacao']}
- **Canais**: {avatar.estrategia_abordagem['canais_prioritarios']}
- **Horários**: {avatar.estrategia_abordagem['horarios_otimos']}
- **Abordagem**: {avatar.estrategia_abordagem['abordagem_inicial']}
### 💬 Scripts Personalizados
- **Abertura Email**: {avatar.scripts_personalizados['abertura_email']}
- **Hook Instagram**: {avatar.scripts_personalizados['hook_instagram']}
- **CTA Principal**: {avatar.scripts_personalizados['cta_principal']}
### 📊 Métricas Esperadas
- **Taxa de Conversão**: {avatar.metricas_conversao['taxa_conversao_venda']*100:.1f}%
- **Lifetime Value**: R$ {avatar.metricas_conversao['lifetime_value']:.2f}
- **Tempo de Decisão**: {avatar.metricas_conversao['tempo_decisao_dias']} dias
### 📖 História Pessoal
{avatar.historia_pessoal}
### 🕐 Um Dia na Vida
{avatar.dia_na_vida}
---
"""
        manual += f"""
## Resumo Estratégico
### Drivers Mentais Mais Efetivos (Todos os Avatares)
{chr(10).join([f"- **{driver}**: {count} avatares" for driver, count in self._identificar_drivers_comuns(avatares)[:5]])}
### Canais Prioritários
- **Jovens (25-35)**: Instagram, TikTok, WhatsApp
- **Adultos (35-45)**: Facebook, LinkedIn, Email
- **Experientes (45+)**: Facebook, Email, WhatsApp
### Horários Ótimos
- **Manhã**: 07:00-09:00 (check matinal)
- **Almoço**: 12:00-13:00 (pausa trabalho)
- **Noite**: 19:00-22:00 (tempo pessoal)
### Abordagens por Perfil
1. **Iniciante Ambicioso**: Foco em crescimento rápido e oportunidades
2. **Profissional Estabelecido**: Otimização e próximo nível
3. **Empreendedor Frustrado**: Método comprovado e garantias
4. **Expert em Evolução**: Estratégias avançadas e exclusividade
*Sistema de 4 Avatares Únicos - Análises Personalizadas Completas*
"""
        return manual

# Instância global
avatar_system = AvatarGenerationSystem()

def get_avatar_system() -> AvatarGenerationSystem:
    """Retorna instância do sistema de avatares"""
    return avatar_system

# --- EXEMPLO DE USO ---
if __name__ == "__main__":
    import asyncio
    import logging

    # Configuração básica de logging
    logging.basicConfig(level=logging.INFO)

    async def main():
        sistema = get_avatar_system()
        
        contexto_nicho_exemplo = """
        Nicho: Marketing Digital para Profissionais Liberais (Advogados, Médicos, Psicólogos)
        Objetivo: Ajudar esses profissionais a atrair clientes qualificados online, aumentando sua visibilidade e faturamento.
        Produto: Um curso completo de marketing digital prático e específico para o nicho.
        """
        
        dados_pesquisa_exemplo = {
            "segmento": "Saúde e Jurídico",
            "publico_principal": "Profissionais liberais com 5-15 anos de experiência",
            "dor_principal": "Dificuldade em conseguir novos clientes consistentemente"
        }

        print("Gerando 4 avatares únicos...")
        avatares_gerados = await sistema.gerar_4_avatares_completos(contexto_nicho_exemplo, dados_pesquisa_exemplo)
        
        print("\n--- AVATARES GERADOS ---")
        for avatar in avatares_gerados:
            print(f"\n--- {avatar.id_avatar.upper()}: {avatar.dados_demograficos.nome_completo} ---")
            print(f"  Profissão: {avatar.dados_demograficos.profissao}")
            print(f"  Idade: {avatar.dados_demograficos.idade}")
            print(f"  Localização: {avatar.dados_demograficos.localizacao}")
            print(f"  Renda Mensal: R$ {avatar.dados_demograficos.renda_mensal:,.2f}")
            print(f"  Personalidade MBTI: {avatar.perfil_psicologico.personalidade_mbti}")
            print(f"  Dor Primária: {avatar.dores_objetivos.dor_primaria_emocional}")
            print(f"  Objetivo Principal: {avatar.dores_objetivos.objetivo_principal}")
            print(f"  Desejo Oculto: {avatar.perfil_psicologico.desejos_ocultos[0]}")
            print(f"  Medo Primário: {avatar.perfil_psicologico.medos_primarios[0]}")
            print(f"  Estilo de Comunicação: {avatar.perfil_psicologico.estilo_comunicacao}")
            print(f"  Drivers Mentais: {', '.join(avatar.drivers_mentais_efetivos)}")
            print("\n  HISTÓRIA PESSOAL RESUMIDA:")
            # Imprime as primeiras 2 linhas da história
            linhas_historia = avatar.historia_pessoal.strip().split('\n')
            for linha in linhas_historia[:2]:
                print(f"    {linha}")
            if len(linhas_historia) > 2:
                print("    ...")

        # Salvar avatares (opcional, requer permissão de escrita no diretório)
        # session_id_teste = "teste_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        # caminho_salvo = sistema.salvar_avatares(session_id_teste, avatares_gerados)
        # if caminho_salvo:
        #     print(f"\n✅ Avatares salvos em: {caminho_salvo}")

    asyncio.run(main())

