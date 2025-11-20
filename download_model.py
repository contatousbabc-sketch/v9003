#!/usr/bin/env python3
"""
Script para download de modelos GGUF recomendados
"""

import os
import sys
import requests
from pathlib import Path
from tqdm import tqdm

def download_file(url: str, filename: str, model_dir: Path):
    """Download de arquivo com barra de progresso"""
    
    filepath = model_dir / filename
    
    if filepath.exists():
        print(f"✅ Arquivo já existe: {filename}")
        return True
    
    try:
        print(f"🔄 Baixando {filename}...")
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(filepath, 'wb') as f, tqdm(
            desc=filename,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
        
        print(f"✅ Download concluído: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Erro no download: {e}")
        if filepath.exists():
            filepath.unlink()  # Remove arquivo parcial
        return False

def main():
    """Função principal"""
    
    print("🤖 ARQV18 Enhanced - Download de Modelos Locais ULTRA-OTIMIZADOS")
    print("=" * 70)
    print("🎯 MODELOS FREE, LEVES E ALTA PERFORMANCE PARA ANÁLISE DE MERCADO")
    print("=" * 70)
    
    # Criar diretório model se não existir
    model_dir = Path("model")
    model_dir.mkdir(exist_ok=True)
    
    # Modelos categorizados por performance e uso
    models = {
        # ========== CATEGORIA: ULTRA-LEVES (< 2GB) ==========
        "1": {
            "name": "🚀 Llama 3.2 1B GGUF (Q4_K_M) - ULTRA-RÁPIDO",
            "filename": "llama-3.2-1b-instruct-q4_k_m.gguf",
            "size": "0.8GB",
            "url": "https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
            "description": "⚡ MAIS RÁPIDO - Ideal para análises rápidas e respostas instantâneas",
            "category": "Ultra-Leve",
            "use_case": "Análises rápidas, resumos, classificação",
            "speed": "⚡⚡⚡⚡⚡",
            "quality": "⭐⭐⭐",
            "memory": "2GB RAM"
        },
        "2": {
            "name": "🔥 Qwen2.5 0.5B GGUF (Q4_K_M) - MICRO-MODELO",
            "filename": "qwen2.5-0.5b-instruct-q4_k_m.gguf",
            "size": "0.4GB",
            "url": "https://huggingface.co/bartowski/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/Qwen2.5-0.5B-Instruct-Q4_K_M.gguf",
            "description": "🏃 EXTREMAMENTE RÁPIDO - Perfeito para tarefas simples e fallback",
            "category": "Micro",
            "use_case": "Fallback, classificação básica, tags",
            "speed": "⚡⚡⚡⚡⚡",
            "quality": "⭐⭐",
            "memory": "1GB RAM"
        },
        "3": {
            "name": "💎 Phi-3.5 Mini GGUF (Q4_K_M) - MICROSOFT",
            "filename": "phi-3.5-mini-instruct-q4_k_m.gguf",
            "size": "2.4GB",
            "url": "https://huggingface.co/bartowski/Phi-3.5-mini-instruct-GGUF/resolve/main/Phi-3.5-mini-instruct-Q4_K_M.gguf",
            "description": "🧠 INTELIGENTE - Excelente para análise de dados e insights",
            "category": "Leve",
            "use_case": "Análise de dados, insights, relatórios",
            "speed": "⚡⚡⚡⚡",
            "quality": "⭐⭐⭐⭐",
            "memory": "4GB RAM"
        },
        
        # ========== CATEGORIA: BALANCEADOS (2-4GB) ==========
        "4": {
            "name": "🎯 Llama 3.2 3B GGUF (Q4_K_M) - EQUILIBRADO",
            "filename": "llama-3.2-3b-instruct-q4_k_m.gguf",
            "size": "2.0GB",
            "url": "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
            "description": "⚖️ BALANCEADO - Ótima relação velocidade/qualidade para análises",
            "category": "Balanceado",
            "use_case": "Análise completa, relatórios detalhados",
            "speed": "⚡⚡⚡⚡",
            "quality": "⭐⭐⭐⭐",
            "memory": "4GB RAM"
        },
        "5": {
            "name": "🌟 Qwen2.5 3B GGUF (Q4_K_M) - MULTILÍNGUE",
            "filename": "qwen2.5-3b-instruct-q4_k_m.gguf",
            "size": "2.0GB",
            "url": "https://huggingface.co/bartowski/Qwen2.5-3B-Instruct-GGUF/resolve/main/Qwen2.5-3B-Instruct-Q4_K_M.gguf",
            "description": "🌍 MULTILÍNGUE - Excelente para português e análises internacionais",
            "category": "Balanceado",
            "use_case": "Análise multilíngue, mercados globais",
            "speed": "⚡⚡⚡⚡",
            "quality": "⭐⭐⭐⭐",
            "memory": "4GB RAM"
        },
        "6": {
            "name": "💼 Gemma 2B GGUF (Q4_K_M) - GOOGLE",
            "filename": "gemma-2b-it-q4_k_m.gguf",
            "size": "1.6GB",
            "url": "https://huggingface.co/bartowski/gemma-2b-it-GGUF/resolve/main/gemma-2b-it-Q4_K_M.gguf",
            "description": "🏢 CORPORATIVO - Ideal para análises de negócios e mercado",
            "category": "Leve",
            "use_case": "Análise de negócios, estratégia",
            "speed": "⚡⚡⚡⚡",
            "quality": "⭐⭐⭐⭐",
            "memory": "3GB RAM"
        },
        
        # ========== CATEGORIA: ALTA QUALIDADE (4-6GB) ==========
        "7": {
            "name": "🏆 Qwen2.5 7B GGUF (Q4_K_M) - PREMIUM",
            "filename": "qwen2.5-7b-instruct-q4_k_m.gguf",
            "size": "4.4GB",
            "url": "https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf",
            "description": "👑 PREMIUM - Máxima qualidade para análises complexas e detalhadas",
            "category": "Premium",
            "use_case": "Análises complexas, insights profundos",
            "speed": "⚡⚡⚡",
            "quality": "⭐⭐⭐⭐⭐",
            "memory": "6GB RAM"
        },
        "8": {
            "name": "🧪 Mistral 7B GGUF (Q4_K_M) - CIENTÍFICO",
            "filename": "mistral-7b-instruct-q4_k_m.gguf",
            "size": "4.1GB",
            "url": "https://huggingface.co/bartowski/Mistral-7B-Instruct-v0.3-GGUF/resolve/main/Mistral-7B-Instruct-v0.3-Q4_K_M.gguf",
            "description": "🔬 CIENTÍFICO - Excelente para análises técnicas e dados complexos",
            "category": "Premium",
            "use_case": "Análise técnica, dados científicos",
            "speed": "⚡⚡⚡",
            "quality": "⭐⭐⭐⭐⭐",
            "memory": "6GB RAM"
        },
        
        # ========== CATEGORIA: ESPECIALIZADOS ==========
        "9": {
            "name": "💻 CodeLlama 7B GGUF (Q4_K_M) - CÓDIGO",
            "filename": "codellama-7b-instruct-q4_k_m.gguf",
            "size": "4.0GB",
            "url": "https://huggingface.co/bartowski/CodeLlama-7B-Instruct-GGUF/resolve/main/CodeLlama-7B-Instruct-Q4_K_M.gguf",
            "description": "⌨️ CÓDIGO - Especializado em análise de código e automação",
            "category": "Especializado",
            "use_case": "Análise de código, automação, scripts",
            "speed": "⚡⚡⚡",
            "quality": "⭐⭐⭐⭐⭐",
            "memory": "6GB RAM"
        },
        "10": {
            "name": "📊 Llama 3.1 8B GGUF (Q4_K_M) - ANÁLISE",
            "filename": "llama-3.1-8b-instruct-q4_k_m.gguf",
            "size": "4.7GB",
            "url": "https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
            "description": "📈 ANÁLISE - Otimizado para análise de mercado e dados financeiros",
            "category": "Especializado",
            "use_case": "Análise financeira, mercado, tendências",
            "speed": "⚡⚡⚡",
            "quality": "⭐⭐⭐⭐⭐",
            "memory": "6GB RAM"
        },
        
        # ========== CATEGORIA: PORTUGUÊS NATIVO ==========
        "11": {
            "name": "🇧🇷 Sabiá 7B GGUF (Q4_K_M) - PORTUGUÊS",
            "filename": "sabia-7b-portuguese-q4_k_m.gguf",
            "size": "4.2GB",
            "url": "https://huggingface.co/bartowski/sabia-7b-GGUF/resolve/main/sabia-7b-Q4_K_M.gguf",
            "description": "🇧🇷 PORTUGUÊS - Modelo brasileiro especializado em português",
            "category": "Português",
            "use_case": "Análise em português, mercado brasileiro",
            "speed": "⚡⚡⚡",
            "quality": "⭐⭐⭐⭐⭐",
            "memory": "6GB RAM"
        },
        "12": {
            "name": "🇧🇷 BrTuning Llama 7B GGUF (Q4_K_M) - PORTUGUÊS",
            "filename": "brtuning-llama-7b-portuguese-q4_k_m.gguf",
            "size": "4.1GB",
            "url": "https://huggingface.co/recogna-nlp/brtuning-llama-7b-GGUF/resolve/main/brtuning-llama-7b-Q4_K_M.gguf",
            "description": "🇧🇷 PORTUGUÊS AVANÇADO - Fine-tuned para português brasileiro",
            "category": "Português",
            "use_case": "Análise avançada em português, cultura brasileira",
            "speed": "⚡⚡⚡",
            "quality": "⭐⭐⭐⭐⭐",
            "memory": "6GB RAM"
        },
        
        # ========== CATEGORIA: NOVOS MODELOS 2024 ==========
        "13": {
            "name": "🚀 Llama 3.3 70B GGUF (Q4_K_M) - MAIS RECENTE",
            "filename": "llama-3.3-70b-instruct-q4_k_m.gguf",
            "size": "39GB",
            "url": "https://huggingface.co/bartowski/Llama-3.3-70B-Instruct-GGUF/resolve/main/Llama-3.3-70B-Instruct-Q4_K_M.gguf",
            "description": "🔥 MAIS RECENTE - Llama 3.3 com capacidades avançadas",
            "category": "Ultra-Premium",
            "use_case": "Análises extremamente complexas, pesquisa avançada",
            "speed": "⚡",
            "quality": "⭐⭐⭐⭐⭐",
            "memory": "48GB RAM"
        },
        "14": {
            "name": "🧠 Qwen2.5 14B GGUF (Q4_K_M) - INTELIGENTE",
            "filename": "qwen2.5-14b-instruct-q4_k_m.gguf",
            "size": "8.5GB",
            "url": "https://huggingface.co/bartowski/Qwen2.5-14B-Instruct-GGUF/resolve/main/Qwen2.5-14B-Instruct-Q4_K_M.gguf",
            "description": "🧠 SUPER INTELIGENTE - Capacidades avançadas de raciocínio",
            "category": "Premium",
            "use_case": "Análises complexas, raciocínio avançado",
            "speed": "⚡⚡",
            "quality": "⭐⭐⭐⭐⭐",
            "memory": "12GB RAM"
        },
        "15": {
            "name": "⚡ Gemma 2 9B GGUF (Q4_K_M) - GOOGLE V2",
            "filename": "gemma-2-9b-it-q4_k_m.gguf",
            "size": "5.4GB",
            "url": "https://huggingface.co/bartowski/gemma-2-9b-it-GGUF/resolve/main/gemma-2-9b-it-Q4_K_M.gguf",
            "description": "⚡ GOOGLE V2 - Nova geração do Gemma com melhor performance",
            "category": "Premium",
            "use_case": "Análise corporativa, insights de negócios",
            "speed": "⚡⚡⚡",
            "quality": "⭐⭐⭐⭐⭐",
            "memory": "8GB RAM"
        },
        
        # ========== CATEGORIA: SAFETENSORS ==========
        "16": {
            "name": "🔒 Llama 3.2 1B SafeTensors - SEGURO",
            "filename": "llama-3.2-1b-instruct.safetensors",
            "size": "2.5GB",
            "url": "https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct/resolve/main/model.safetensors",
            "description": "🔒 SAFETENSORS - Formato seguro para carregamento rápido",
            "category": "SafeTensors",
            "use_case": "Desenvolvimento seguro, produção",
            "speed": "⚡⚡⚡⚡",
            "quality": "⭐⭐⭐",
            "memory": "4GB RAM",
            "format": "safetensors"
        },
        "17": {
            "name": "🔒 Qwen2.5 3B SafeTensors - MULTILÍNGUE SEGURO",
            "filename": "qwen2.5-3b-instruct.safetensors",
            "size": "6.2GB",
            "url": "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct/resolve/main/model.safetensors",
            "description": "🔒 SAFETENSORS MULTILÍNGUE - Formato seguro com suporte avançado",
            "category": "SafeTensors",
            "use_case": "Produção multilíngue, análise segura",
            "speed": "⚡⚡⚡⚡",
            "quality": "⭐⭐⭐⭐",
            "memory": "8GB RAM",
            "format": "safetensors"
        },
        "18": {
            "name": "🔒 Phi-3.5 Mini SafeTensors - MICROSOFT SEGURO",
            "filename": "phi-3.5-mini-instruct.safetensors",
            "size": "7.6GB",
            "url": "https://huggingface.co/microsoft/Phi-3.5-mini-instruct/resolve/main/model.safetensors",
            "description": "🔒 MICROSOFT SAFETENSORS - Formato seguro da Microsoft",
            "category": "SafeTensors",
            "use_case": "Análise corporativa segura, compliance",
            "speed": "⚡⚡⚡⚡",
            "quality": "⭐⭐⭐⭐",
            "memory": "10GB RAM",
            "format": "safetensors"
        },
        
        # ========== CATEGORIA: BIN (PYTORCH) ==========
        "19": {
            "name": "📦 Llama 3.2 3B PyTorch BIN - CLÁSSICO",
            "filename": "llama-3.2-3b-instruct.bin",
            "size": "6.4GB",
            "url": "https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct/resolve/main/pytorch_model.bin",
            "description": "📦 PYTORCH BIN - Formato clássico PyTorch para compatibilidade",
            "category": "PyTorch",
            "use_case": "Compatibilidade legacy, desenvolvimento",
            "speed": "⚡⚡⚡",
            "quality": "⭐⭐⭐⭐",
            "memory": "8GB RAM",
            "format": "bin"
        },
        "20": {
            "name": "📦 Mistral 7B PyTorch BIN - CIENTÍFICO CLÁSSICO",
            "filename": "mistral-7b-instruct.bin",
            "size": "13.5GB",
            "url": "https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3/resolve/main/pytorch_model.bin",
            "description": "📦 MISTRAL BIN - Formato PyTorch para análises científicas",
            "category": "PyTorch",
            "use_case": "Análise científica, pesquisa, desenvolvimento",
            "speed": "⚡⚡",
            "quality": "⭐⭐⭐⭐⭐",
            "memory": "16GB RAM",
            "format": "bin"
        },
        
        # ========== CATEGORIA: ESPECIALIZADOS AVANÇADOS ==========
        "21": {
            "name": "🎨 Stable Code 3B GGUF (Q4_K_M) - CÓDIGO AVANÇADO",
            "filename": "stable-code-3b-q4_k_m.gguf",
            "size": "2.1GB",
            "url": "https://huggingface.co/bartowski/stable-code-3b-GGUF/resolve/main/stable-code-3b-Q4_K_M.gguf",
            "description": "🎨 CÓDIGO AVANÇADO - Especializado em geração e análise de código",
            "category": "Código",
            "use_case": "Geração de código, análise de software",
            "speed": "⚡⚡⚡⚡",
            "quality": "⭐⭐⭐⭐⭐",
            "memory": "4GB RAM"
        },
        "22": {
            "name": "📊 DeepSeek Math 7B GGUF (Q4_K_M) - MATEMÁTICA",
            "filename": "deepseek-math-7b-q4_k_m.gguf",
            "size": "4.3GB",
            "url": "https://huggingface.co/bartowski/deepseek-math-7b-instruct-GGUF/resolve/main/deepseek-math-7b-instruct-Q4_K_M.gguf",
            "description": "📊 MATEMÁTICA - Especializado em cálculos e análises quantitativas",
            "category": "Matemática",
            "use_case": "Análises quantitativas, estatísticas, finanças",
            "speed": "⚡⚡⚡",
            "quality": "⭐⭐⭐⭐⭐",
            "memory": "6GB RAM"
        },
        "23": {
            "name": "🌐 Aya 8B GGUF (Q4_K_M) - MULTILÍNGUE GLOBAL",
            "filename": "aya-8b-multilingual-q4_k_m.gguf",
            "size": "4.8GB",
            "url": "https://huggingface.co/bartowski/aya-8b-GGUF/resolve/main/aya-8b-Q4_K_M.gguf",
            "description": "🌐 MULTILÍNGUE GLOBAL - Suporte a 101 idiomas incluindo português",
            "category": "Multilíngue",
            "use_case": "Análise global, mercados internacionais",
            "speed": "⚡⚡⚡",
            "quality": "⭐⭐⭐⭐⭐",
            "memory": "7GB RAM"
        },
        
        # ========== CATEGORIA: ULTRA-MODERNOS 2024 ==========
        "24": {
            "name": "🔮 Qwen2.5 32B GGUF (Q4_K_M) - FUTURO",
            "filename": "qwen2.5-32b-instruct-q4_k_m.gguf",
            "size": "18.5GB",
            "url": "https://huggingface.co/bartowski/Qwen2.5-32B-Instruct-GGUF/resolve/main/Qwen2.5-32B-Instruct-Q4_K_M.gguf",
            "description": "🔮 FUTURO - Capacidades de IA de próxima geração",
            "category": "Ultra-Premium",
            "use_case": "Análises futurísticas, pesquisa avançada",
            "speed": "⚡",
            "quality": "⭐⭐⭐⭐⭐",
            "memory": "24GB RAM"
        },
        "25": {
            "name": "🎯 Llama 3.1 70B GGUF (Q4_K_M) - GIGANTE",
            "filename": "llama-3.1-70b-instruct-q4_k_m.gguf",
            "size": "39.5GB",
            "url": "https://huggingface.co/bartowski/Meta-Llama-3.1-70B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-70B-Instruct-Q4_K_M.gguf",
            "description": "🎯 GIGANTE - Máxima capacidade para análises extremamente complexas",
            "category": "Ultra-Premium",
            "use_case": "Análises extremas, pesquisa científica",
            "speed": "⚡",
            "quality": "⭐⭐⭐⭐⭐",
            "memory": "48GB RAM"
        },
        
        # ========== CATEGORIA: EXPERIMENTAIS ==========
        "26": {
            "name": "🧪 Hermes 3 8B GGUF (Q4_K_M) - EXPERIMENTAL",
            "filename": "hermes-3-llama-3.1-8b-q4_k_m.gguf",
            "size": "4.9GB",
            "url": "https://huggingface.co/bartowski/Hermes-3-Llama-3.1-8B-GGUF/resolve/main/Hermes-3-Llama-3.1-8B-Q4_K_M.gguf",
            "description": "🧪 EXPERIMENTAL - Modelo experimental com capacidades únicas",
            "category": "Experimental",
            "use_case": "Testes, pesquisa, inovação",
            "speed": "⚡⚡⚡",
            "quality": "⭐⭐⭐⭐",
            "memory": "7GB RAM"
        },
        "27": {
            "name": "🔬 OpenHermes 2.5 7B GGUF (Q4_K_M) - PESQUISA",
            "filename": "openhermes-2.5-mistral-7b-q4_k_m.gguf",
            "size": "4.1GB",
            "url": "https://huggingface.co/bartowski/OpenHermes-2.5-Mistral-7B-GGUF/resolve/main/OpenHermes-2.5-Mistral-7B-Q4_K_M.gguf",
            "description": "🔬 PESQUISA - Otimizado para pesquisa e análise científica",
            "category": "Pesquisa",
            "use_case": "Pesquisa científica, análise acadêmica",
            "speed": "⚡⚡⚡",
            "quality": "⭐⭐⭐⭐⭐",
            "memory": "6GB RAM"
        },
        
        # ========== CATEGORIA: EFICIÊNCIA EXTREMA ==========
        "28": {
            "name": "⚡ TinyLlama 1.1B GGUF (Q4_K_M) - NANO",
            "filename": "tinyllama-1.1b-chat-q4_k_m.gguf",
            "size": "0.7GB",
            "url": "https://huggingface.co/bartowski/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/TinyLlama-1.1B-Chat-v1.0-Q4_K_M.gguf",
            "description": "⚡ NANO - Extremamente eficiente para tarefas básicas",
            "category": "Nano",
            "use_case": "Tarefas básicas, IoT, edge computing",
            "speed": "⚡⚡⚡⚡⚡",
            "quality": "⭐⭐",
            "memory": "1GB RAM"
        },
        "29": {
            "name": "🏃 Phi-2 2.7B GGUF (Q4_K_M) - VELOCIDADE",
            "filename": "phi-2-q4_k_m.gguf",
            "size": "1.7GB",
            "url": "https://huggingface.co/bartowski/phi-2-GGUF/resolve/main/phi-2-Q4_K_M.gguf",
            "description": "🏃 VELOCIDADE - Balanceamento perfeito entre velocidade e qualidade",
            "category": "Rápido",
            "use_case": "Análises rápidas, prototipagem",
            "speed": "⚡⚡⚡⚡⚡",
            "quality": "⭐⭐⭐",
            "memory": "3GB RAM"
        },
        "30": {
            "name": "🎪 Zephyr 7B GGUF (Q4_K_M) - CONVERSACIONAL",
            "filename": "zephyr-7b-beta-q4_k_m.gguf",
            "size": "4.1GB",
            "url": "https://huggingface.co/bartowski/zephyr-7b-beta-GGUF/resolve/main/zephyr-7b-beta-Q4_K_M.gguf",
            "description": "🎪 CONVERSACIONAL - Otimizado para interações naturais",
            "category": "Conversacional",
            "use_case": "Chatbots, assistentes, análise conversacional",
            "speed": "⚡⚡⚡",
            "quality": "⭐⭐⭐⭐⭐",
            "memory": "6GB RAM"
        },
        "12": {
            "name": "🌎 Qwen2.5 1.5B GGUF (Q4_K_M) - COMPACTO",
            "filename": "qwen2.5-1.5b-instruct-q4_k_m.gguf",
            "size": "1.0GB",
            "url": "https://huggingface.co/bartowski/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf",
            "description": "🎯 COMPACTO - Pequeno mas poderoso, ótimo custo-benefício",
            "category": "Compacto",
            "use_case": "Uso geral, análises médias",
            "speed": "⚡⚡⚡⚡",
            "quality": "⭐⭐⭐",
            "memory": "2GB RAM"
        }
    }
    
    # Agrupar modelos por categoria
    categories = {}
    for key, model in models.items():
        category = model['category']
        if category not in categories:
            categories[category] = []
        categories[category].append((key, model))
    
    print("📋 CATÁLOGO DE MODELOS ULTRA-OTIMIZADOS:")
    print()
    
    # Ordem das categorias
    category_order = ["Micro", "Ultra-Leve", "Compacto", "Leve", "Balanceado", "Premium", "Especializado", "Português"]
    
    for category in category_order:
        if category in categories:
            print(f"🏷️  CATEGORIA: {category.upper()}")
            print("─" * 60)
            
            for key, model in categories[category]:
                print(f"{key:2}. {model['name']}")
                print(f"    📁 Arquivo: {model['filename']}")
                print(f"    📊 Tamanho: {model['size']} | 💾 RAM: {model['memory']}")
                print(f"    🚀 Velocidade: {model['speed']} | ⭐ Qualidade: {model['quality']}")
                print(f"    🎯 Uso: {model['use_case']}")
                print(f"    💡 {model['description']}")
                print()
            print()
    
    print("🔧 OPÇÕES ESPECIAIS:")
    print("─" * 60)
    print("13. 📊 Mostrar comparativo detalhado")
    print("14. 🎯 Recomendação personalizada")
    print("15. 🔄 Baixar múltiplos modelos")
    print("0.  👋 Sair")
    print()
    
    while True:
        choice = input("Escolha uma opção (0-15): ").strip()
        
        if choice == "0":
            print("👋 Saindo...")
            break
        
        elif choice == "13":
            show_detailed_comparison(models)
        
        elif choice == "14":
            show_personalized_recommendation(models)
        
        elif choice == "15":
            download_multiple_models(models, model_dir)
        
        elif choice in models:
            model = models[choice]
            print(f"\n🎯 MODELO SELECIONADO:")
            print("=" * 50)
            print(f"📛 Nome: {model['name']}")
            print(f"📁 Arquivo: {model['filename']}")
            print(f"📊 Tamanho: {model['size']} | 💾 RAM necessária: {model['memory']}")
            print(f"🚀 Velocidade: {model['speed']} | ⭐ Qualidade: {model['quality']}")
            print(f"🏷️ Categoria: {model['category']}")
            print(f"🎯 Melhor uso: {model['use_case']}")
            print(f"💡 {model['description']}")
            print("=" * 50)
            
            confirm = input(f"\n✅ Confirma download de {model['size']}? (s/N): ").strip().lower()
            
            if confirm in ['s', 'sim', 'y', 'yes']:
                print(f"\n🚀 Iniciando download do {model['name']}...")
                success = download_file(model['url'], model['filename'], model_dir)
                
                if success:
                    # Renomear para model.gguf se for o primeiro modelo
                    main_model = model_dir / "model.gguf"
                    if not main_model.exists():
                        downloaded_file = model_dir / model['filename']
                        downloaded_file.rename(main_model)
                        print(f"✅ Modelo configurado como padrão (model.gguf)")
                        print(f"🚀 Modelo pronto para uso no ARQV18!")
                    else:
                        print(f"✅ Modelo salvo como: {model['filename']}")
                        print(f"💡 Para usar este modelo, renomeie para 'model.gguf'")
                    
                    print(f"\n🎉 DOWNLOAD CONCLUÍDO COM SUCESSO!")
                    print(f"📁 Localização: {model_dir / model['filename']}")
                    print(f"💾 RAM recomendada: {model['memory']}")
                    print(f"🔄 Reinicie o ARQV18 para usar o novo modelo")
                    
                    # Mostrar próximos passos
                    print(f"\n📋 PRÓXIMOS PASSOS:")
                    print(f"1. 🔄 Reinicie o sistema ARQV18")
                    print(f"2. ⚙️ Configure max_tokens para 4096+ no config")
                    print(f"3. 🧪 Teste o modelo com uma análise simples")
                    
                else:
                    print(f"\n❌ FALHA NO DOWNLOAD")
                    print(f"💡 Verifique sua conexão e tente novamente")
            else:
                print("❌ Download cancelado")
        else:
            print("❌ Opção inválida! Escolha entre 0-15")
        
        print()

def show_detailed_comparison(models):
    """Mostra comparativo detalhado dos modelos"""
    print("\n📊 COMPARATIVO DETALHADO DE MODELOS")
    print("=" * 80)
    print(f"{'#':<3} {'Nome':<25} {'Tamanho':<8} {'RAM':<8} {'Velocidade':<12} {'Qualidade':<10} {'Categoria':<12}")
    print("─" * 80)
    
    for key, model in models.items():
        speed_score = len(model['speed'].replace('⚡', ''))
        quality_score = len(model['quality'].replace('⭐', ''))
        
        print(f"{key:<3} {model['name'][:25]:<25} {model['size']:<8} {model['memory']:<8} "
              f"{'⚡' * speed_score:<12} {'⭐' * quality_score:<10} {model['category']:<12}")
    
    print("─" * 80)
    print("💡 LEGENDA:")
    print("   ⚡ = Velocidade (mais ⚡ = mais rápido)")
    print("   ⭐ = Qualidade (mais ⭐ = melhor qualidade)")
    print("   RAM = Memória RAM recomendada")
    input("\n📱 Pressione ENTER para continuar...")

def show_personalized_recommendation(models):
    """Mostra recomendação personalizada baseada nas necessidades"""
    print("\n🎯 RECOMENDAÇÃO PERSONALIZADA")
    print("=" * 50)
    
    print("Responda algumas perguntas para encontrar o modelo ideal:")
    print()
    
    # Pergunta 1: RAM disponível
    print("1. 💾 Quanta RAM você tem disponível?")
    print("   a) 2-4GB (Limitado)")
    print("   b) 4-6GB (Médio)")
    print("   c) 6GB+ (Alto)")
    ram_choice = input("Escolha (a/b/c): ").strip().lower()
    
    # Pergunta 2: Prioridade
    print("\n2. 🎯 Qual sua prioridade?")
    print("   a) Velocidade máxima")
    print("   b) Qualidade máxima")
    print("   c) Equilibrio velocidade/qualidade")
    priority = input("Escolha (a/b/c): ").strip().lower()
    
    # Pergunta 3: Uso principal
    print("\n3. 📊 Uso principal?")
    print("   a) Análises rápidas e resumos")
    print("   b) Análises complexas e detalhadas")
    print("   c) Análise de código/técnica")
    print("   d) Conteúdo em português")
    use_case = input("Escolha (a/b/c/d): ").strip().lower()
    
    # Lógica de recomendação
    recommendations = []
    
    if ram_choice == 'a':  # RAM limitada
        if priority == 'a':  # Velocidade
            recommendations = ['1', '2', '12']
        elif priority == 'b':  # Qualidade
            recommendations = ['3', '4', '6']
        else:  # Equilibrio
            recommendations = ['1', '4', '12']
    
    elif ram_choice == 'b':  # RAM média
        if priority == 'a':  # Velocidade
            recommendations = ['4', '5', '6']
        elif priority == 'b':  # Qualidade
            recommendations = ['7', '8', '10']
        else:  # Equilibrio
            recommendations = ['4', '5', '7']
    
    else:  # RAM alta
        if use_case == 'c':  # Código
            recommendations = ['9', '10', '8']
        elif use_case == 'd':  # Português
            recommendations = ['11', '7', '5']
        elif priority == 'b':  # Qualidade
            recommendations = ['7', '8', '10', '11']
        else:
            recommendations = ['7', '10', '8']
    
    print(f"\n🎯 RECOMENDAÇÕES PARA VOCÊ:")
    print("=" * 40)
    
    for i, rec in enumerate(recommendations[:3], 1):
        model = models[rec]
        print(f"{i}. {model['name']}")
        print(f"   📊 {model['size']} | 💾 {model['memory']}")
        print(f"   🎯 {model['use_case']}")
        print(f"   💡 {model['description']}")
        print()
    
    input("📱 Pressione ENTER para continuar...")

def download_multiple_models(models, model_dir):
    """Permite download de múltiplos modelos"""
    print("\n🔄 DOWNLOAD MÚLTIPLO DE MODELOS")
    print("=" * 50)
    
    print("Digite os números dos modelos separados por vírgula (ex: 1,4,7):")
    choices = input("Modelos: ").strip().split(',')
    
    selected_models = []
    total_size = 0
    
    for choice in choices:
        choice = choice.strip()
        if choice in models:
            selected_models.append(models[choice])
            # Converter tamanho para GB para cálculo
            size_str = models[choice]['size'].replace('GB', '').replace(',', '.')
            try:
                total_size += float(size_str)
            except:
                pass
    
    if not selected_models:
        print("❌ Nenhum modelo válido selecionado")
        return
    
    print(f"\n📋 MODELOS SELECIONADOS:")
    print("─" * 40)
    for model in selected_models:
        print(f"• {model['name']} ({model['size']})")
    print(f"📊 Tamanho total aproximado: {total_size:.1f}GB")
    
    confirm = input(f"\n✅ Confirma download de {len(selected_models)} modelos? (s/N): ").strip().lower()
    
    if confirm in ['s', 'sim', 'y', 'yes']:
        print(f"\n🚀 Iniciando downloads...")
        
        successful = 0
        for i, model in enumerate(selected_models, 1):
            print(f"\n📥 [{i}/{len(selected_models)}] Baixando {model['name']}...")
            
            if download_file(model['url'], model['filename'], model_dir):
                successful += 1
                print(f"✅ Concluído: {model['filename']}")
            else:
                print(f"❌ Falhou: {model['filename']}")
        
        print(f"\n🎉 DOWNLOADS CONCLUÍDOS!")
        print(f"✅ Sucessos: {successful}/{len(selected_models)}")
        
        if successful > 0:
            print(f"\n💡 Para usar um modelo específico:")
            print(f"1. Renomeie o arquivo desejado para 'model.gguf'")
            print(f"2. Reinicie o ARQV18")
    else:
        print("❌ Downloads cancelados")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Download interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
