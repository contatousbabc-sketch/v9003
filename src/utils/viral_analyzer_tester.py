#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Viral Analyzer Tester
Testa o analisador de conteúdo viral para verificar se está funcionando corretamente
"""

import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ViralAnalyzerTester:
    """Testa o analisador de conteúdo viral"""
    
    def __init__(self):
        self.test_content = [
            {
                'url': 'https://www.instagram.com/p/DDXnzJdSBlK/',
                'title': 'Amazing viral dance video with 1.2M likes',
                'description': 'This dance video went viral with over 1.2 million likes and 50K comments',
                'snippet': 'Viral dance challenge - 1.2M likes, 50K comments, 10M views',
                'timestamp': '2024-11-01T10:00:00Z'
            },
            {
                'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                'title': 'Never Gonna Give You Up - Rick Astley',
                'description': 'Official music video with 1.4B views',
                'snippet': '1.4B views • 15M likes • 2M comments • Rick Astley',
                'timestamp': '2009-10-25T06:57:33Z'
            },
            {
                'url': 'https://www.tiktok.com/@user/video/123456789',
                'title': 'Funny cat video goes viral',
                'description': 'Cat doing funny tricks - 5M views, 800K likes',
                'snippet': 'Viral cat video • 5M views • 800K likes • 100K shares',
                'timestamp': '2024-10-30T15:30:00Z'
            },
            {
                'url': 'https://twitter.com/user/status/123456789',
                'title': 'Breaking news tweet',
                'description': 'Important announcement that got 500K retweets',
                'snippet': '500K retweets • 1M likes • 50K replies',
                'timestamp': '2024-11-01T12:00:00Z'
            }
        ]
    
    async def test_basic_content_analysis(self) -> Dict[str, Any]:
        """Testa o método _analyze_basic_content"""
        
        try:
            # Importa o analisador
            from ..services.viral_content_analyzer import ViralContentAnalyzer
            analyzer = ViralContentAnalyzer()
            
            results = []
            
            for content in self.test_content:
                logger.info(f"🧪 Testando análise básica para: {content['url']}")
                
                try:
                    # Testa o método _analyze_basic_content
                    analysis = await analyzer._analyze_basic_content(content['url'], content)
                    
                    if analysis:
                        result = {
                            'url': content['url'],
                            'success': True,
                            'platform': analysis.get('platform', 'unknown'),
                            'likes': analysis.get('likes', 0),
                            'comments': analysis.get('comments', 0),
                            'views': analysis.get('views', 0),
                            'viral_score': analysis.get('viral_score', 0),
                            'engagement_rate': analysis.get('engagement_rate', 0),
                            'extraction_method': analysis.get('extraction_method', 'unknown'),
                            'has_hashtags': len(analysis.get('hashtags', [])) > 0,
                            'has_mentions': len(analysis.get('mentions', [])) > 0,
                            'is_video': analysis.get('is_video', False),
                            'has_media': analysis.get('has_media', False)
                        }
                        logger.info(f"✅ Sucesso: {result['platform']} - {result['likes']} likes")
                    else:
                        result = {
                            'url': content['url'],
                            'success': False,
                            'error': 'Análise retornou None'
                        }
                        logger.warning(f"❌ Falha: análise retornou None")
                    
                    results.append(result)
                    
                except Exception as e:
                    result = {
                        'url': content['url'],
                        'success': False,
                        'error': str(e)
                    }
                    results.append(result)
                    logger.error(f"❌ Erro: {e}")
            
            # Análise dos resultados
            successful = [r for r in results if r.get('success', False)]
            failed = [r for r in results if not r.get('success', False)]
            
            summary = {
                'timestamp': datetime.now().isoformat(),
                'total_tests': len(results),
                'successful_tests': len(successful),
                'failed_tests': len(failed),
                'success_rate': len(successful) / len(results) if results else 0,
                'results': results,
                'platform_detection': {
                    result['url']: result.get('platform', 'unknown')
                    for result in successful
                },
                'metrics_extraction': {
                    'likes_detected': len([r for r in successful if r.get('likes', 0) > 0]),
                    'comments_detected': len([r for r in successful if r.get('comments', 0) > 0]),
                    'views_detected': len([r for r in successful if r.get('views', 0) > 0]),
                    'hashtags_detected': len([r for r in successful if r.get('has_hashtags', False)]),
                    'video_detected': len([r for r in successful if r.get('is_video', False)])
                }
            }
            
            return summary
            
        except ImportError as e:
            return {
                'error': f'Erro ao importar ViralContentAnalyzer: {e}',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'error': f'Erro geral no teste: {e}',
                'timestamp': datetime.now().isoformat()
            }
    
    async def test_platform_detection(self) -> Dict[str, Any]:
        """Testa detecção de plataformas"""
        
        test_urls = [
            ('https://www.instagram.com/p/ABC123/', 'instagram'),
            ('https://www.youtube.com/watch?v=ABC123', 'youtube'),
            ('https://youtu.be/ABC123', 'youtube'),
            ('https://www.tiktok.com/@user/video/123', 'tiktok'),
            ('https://twitter.com/user/status/123', 'twitter'),
            ('https://x.com/user/status/123', 'twitter'),
            ('https://www.facebook.com/user/posts/123', 'facebook'),
            ('https://www.linkedin.com/posts/user_123', 'linkedin'),
            ('https://example.com/some-page', 'unknown')
        ]
        
        try:
            from ..services.viral_content_analyzer import ViralContentAnalyzer
            analyzer = ViralContentAnalyzer()
            
            results = []
            
            for url, expected_platform in test_urls:
                detected_platform = analyzer._detect_platform_from_url(url)
                success = detected_platform == expected_platform
                
                results.append({
                    'url': url,
                    'expected': expected_platform,
                    'detected': detected_platform,
                    'success': success
                })
                
                status = "✅" if success else "❌"
                logger.info(f"{status} {url} -> {detected_platform} (esperado: {expected_platform})")
            
            successful = [r for r in results if r['success']]
            
            return {
                'timestamp': datetime.now().isoformat(),
                'total_tests': len(results),
                'successful_tests': len(successful),
                'success_rate': len(successful) / len(results),
                'results': results
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def test_number_extraction(self) -> Dict[str, Any]:
        """Testa extração de números do texto"""
        
        test_cases = [
            ('1.2M likes and 50K comments', 'likes', 1200000),
            ('Video with 500 likes', 'likes', 500),
            ('10.5K views on this post', 'views', 10500),
            ('2B views worldwide', 'views', 2000000000),
            ('No numbers here', 'likes', 0),
            ('1,234 curtidas', 'curtidas', 1234),
            ('5.7M visualizações', 'visualizações', 5700000)
        ]
        
        try:
            from ..services.viral_content_analyzer import ViralContentAnalyzer
            analyzer = ViralContentAnalyzer()
            
            results = []
            
            for text, keyword, expected in test_cases:
                extracted = analyzer._extract_number_from_text(text, [keyword])
                success = extracted == expected
                
                results.append({
                    'text': text,
                    'keyword': keyword,
                    'expected': expected,
                    'extracted': extracted,
                    'success': success
                })
                
                status = "✅" if success else "❌"
                logger.info(f"{status} '{text}' -> {extracted} (esperado: {expected})")
            
            successful = [r for r in results if r['success']]
            
            return {
                'timestamp': datetime.now().isoformat(),
                'total_tests': len(results),
                'successful_tests': len(successful),
                'success_rate': len(successful) / len(results),
                'results': results
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_test_report(self) -> str:
        """Gera relatório completo dos testes"""
        
        async def run_all_tests():
            basic_test = await self.test_basic_content_analysis()
            platform_test = await self.test_platform_detection()
            number_test = await self.test_number_extraction()
            return basic_test, platform_test, number_test
        
        try:
            basic_test, platform_test, number_test = asyncio.run(run_all_tests())
            
            report = f"""
# 🧪 RELATÓRIO DE TESTE - VIRAL CONTENT ANALYZER
**Data:** {datetime.now().isoformat()}

## 📊 RESUMO EXECUTIVO
- **Análise Básica:** {basic_test.get('success_rate', 0):.1%} sucesso
- **Detecção de Plataforma:** {platform_test.get('success_rate', 0):.1%} sucesso  
- **Extração de Números:** {number_test.get('success_rate', 0):.1%} sucesso

## 🎯 TESTE DE ANÁLISE BÁSICA
"""
            
            if 'error' in basic_test:
                report += f"❌ **Erro:** {basic_test['error']}\n"
            else:
                report += f"- **Total:** {basic_test['total_tests']} testes\n"
                report += f"- **Sucessos:** {basic_test['successful_tests']}\n"
                report += f"- **Falhas:** {basic_test['failed_tests']}\n"
                
                metrics = basic_test.get('metrics_extraction', {})
                report += f"\n### 📈 Extração de Métricas\n"
                report += f"- **Likes detectados:** {metrics.get('likes_detected', 0)}\n"
                report += f"- **Comentários detectados:** {metrics.get('comments_detected', 0)}\n"
                report += f"- **Views detectados:** {metrics.get('views_detected', 0)}\n"
                report += f"- **Hashtags detectadas:** {metrics.get('hashtags_detected', 0)}\n"
                report += f"- **Vídeos detectados:** {metrics.get('video_detected', 0)}\n"
            
            report += f"\n## 🌐 TESTE DE DETECÇÃO DE PLATAFORMA\n"
            if 'error' in platform_test:
                report += f"❌ **Erro:** {platform_test['error']}\n"
            else:
                report += f"- **Taxa de sucesso:** {platform_test['success_rate']:.1%}\n"
                report += f"- **Testes:** {platform_test['successful_tests']}/{platform_test['total_tests']}\n"
            
            report += f"\n## 🔢 TESTE DE EXTRAÇÃO DE NÚMEROS\n"
            if 'error' in number_test:
                report += f"❌ **Erro:** {number_test['error']}\n"
            else:
                report += f"- **Taxa de sucesso:** {number_test['success_rate']:.1%}\n"
                report += f"- **Testes:** {number_test['successful_tests']}/{number_test['total_tests']}\n"
            
            # Status geral
            overall_success = (
                basic_test.get('success_rate', 0) + 
                platform_test.get('success_rate', 0) + 
                number_test.get('success_rate', 0)
            ) / 3
            
            if overall_success >= 0.8:
                report += f"\n## ✅ CONCLUSÃO\nSistema funcionando adequadamente ({overall_success:.1%} sucesso geral)"
            elif overall_success >= 0.6:
                report += f"\n## ⚠️ CONCLUSÃO\nSistema precisa de melhorias ({overall_success:.1%} sucesso geral)"
            else:
                report += f"\n## ❌ CONCLUSÃO\nSistema com problemas críticos ({overall_success:.1%} sucesso geral)"
            
            return report
            
        except Exception as e:
            return f"❌ Erro ao gerar relatório: {e}"

# Instância global
viral_tester = ViralAnalyzerTester()

if __name__ == "__main__":
    # Teste rápido
    print("🧪 Testando Viral Content Analyzer...")
    print(viral_tester.generate_test_report())