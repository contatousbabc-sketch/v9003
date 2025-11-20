#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Image Metadata Processor
Sistema robusto de extração e processamento de metadados de imagens
"""

import os
import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import mimetypes

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

class ImageMetadataProcessor:
    """Processador robusto de metadados de imagens"""
    
    def __init__(self):
        """Inicializa o processador de metadados"""
        self.supported_formats = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', 
            '.webp', '.svg', '.ico', '.heic', '.heif'
        }
        
        self.metadata_cache = {}
        
        # Tentar importar bibliotecas opcionais
        self.pillow_available = False
        self.exifread_available = False
        
        try:
            from PIL import Image, ExifTags
            from PIL.ExifTags import TAGS
            self.pillow_available = True
            self.PIL_Image = Image
            self.PIL_ExifTags = ExifTags
            self.PIL_TAGS = TAGS
            logger.info("✅ PIL/Pillow disponível para processamento de imagens")
        except ImportError:
            logger.warning("⚠️ PIL/Pillow não disponível - funcionalidade limitada")
        
        try:
            import exifread
            self.exifread_available = True
            self.exifread = exifread
            logger.info("✅ ExifRead disponível para metadados EXIF")
        except ImportError:
            logger.warning("⚠️ ExifRead não disponível - usando métodos alternativos")
        
        logger.info("🖼️ Image Metadata Processor inicializado")
    
    def process_image_file(self, image_path: str) -> Dict[str, Any]:
        """Processa um arquivo de imagem e extrai todos os metadados"""
        try:
            image_path = Path(image_path)
            
            if not image_path.exists():
                return {
                    'status': 'error',
                    'erro': 'Arquivo não encontrado',
                    'path': str(image_path)
                }
            
            if image_path.suffix.lower() not in self.supported_formats:
                return {
                    'status': 'unsupported',
                    'erro': f'Formato não suportado: {image_path.suffix}',
                    'path': str(image_path)
                }
            
            logger.info(f"🔍 Processando imagem: {image_path.name}")
            
            # Metadados básicos do arquivo
            basic_metadata = self._extract_basic_metadata(image_path)
            
            # Metadados da imagem
            image_metadata = self._extract_image_metadata(image_path)
            
            # Metadados EXIF (se disponível)
            exif_metadata = self._extract_exif_metadata(image_path)
            
            # Hash da imagem para detecção de duplicatas
            image_hash = self._calculate_image_hash(image_path)
            
            # Análise de conteúdo (se PIL disponível)
            content_analysis = self._analyze_image_content(image_path)
            
            # Compilar resultado final
            resultado = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'file_info': basic_metadata,
                'image_info': image_metadata,
                'exif_data': exif_metadata,
                'hash_info': image_hash,
                'content_analysis': content_analysis,
                'processing_info': {
                    'pillow_used': self.pillow_available,
                    'exifread_used': self.exifread_available,
                    'supported_format': True
                }
            }
            
            # Cache do resultado
            self.metadata_cache[str(image_path)] = resultado
            
            logger.info(f"✅ Metadados extraídos: {image_path.name}")
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar imagem {image_path}: {e}")
            return {
                'status': 'error',
                'erro': str(e),
                'path': str(image_path),
                'timestamp': datetime.now().isoformat()
            }
    
    def _extract_basic_metadata(self, image_path: Path) -> Dict[str, Any]:
        """Extrai metadados básicos do arquivo"""
        try:
            stat = image_path.stat()
            
            return {
                'filename': image_path.name,
                'filepath': str(image_path),
                'file_size': stat.st_size,
                'file_size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed_time': datetime.fromtimestamp(stat.st_atime).isoformat(),
                'file_extension': image_path.suffix.lower(),
                'mime_type': mimetypes.guess_type(str(image_path))[0],
                'permissions': oct(stat.st_mode)[-3:]
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair metadados básicos: {e}")
            return {'erro': str(e)}
    
    def _extract_image_metadata(self, image_path: Path) -> Dict[str, Any]:
        """Extrai metadados específicos da imagem"""
        if not self.pillow_available:
            return {'erro': 'PIL não disponível'}
        
        try:
            with self.PIL_Image.open(image_path) as img:
                return {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.size[0],
                    'height': img.size[1],
                    'aspect_ratio': round(img.size[0] / img.size[1], 2) if img.size[1] > 0 else 0,
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info,
                    'color_mode': img.mode,
                    'bits_per_pixel': len(img.getbands()) * 8 if hasattr(img, 'getbands') else 'unknown',
                    'dpi': img.info.get('dpi', (72, 72)),
                    'info_keys': list(img.info.keys()) if img.info else []
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao extrair metadados da imagem: {e}")
            return {'erro': str(e)}
    
    def _extract_exif_metadata(self, image_path: Path) -> Dict[str, Any]:
        """Extrai metadados EXIF da imagem"""
        exif_data = {}
        
        # Tentar com PIL primeiro
        if self.pillow_available:
            try:
                with self.PIL_Image.open(image_path) as img:
                    if hasattr(img, '_getexif') and img._getexif() is not None:
                        exif = img._getexif()
                        for tag_id, value in exif.items():
                            tag = self.PIL_TAGS.get(tag_id, tag_id)
                            exif_data[tag] = str(value)
                            
            except Exception as e:
                logger.warning(f"⚠️ Erro ao extrair EXIF com PIL: {e}")
        
        # Tentar com exifread se PIL falhou ou não está disponível
        if not exif_data and self.exifread_available:
            try:
                with open(image_path, 'rb') as f:
                    tags = self.exifread.process_file(f)
                    for tag, value in tags.items():
                        if tag not in ['JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote']:
                            exif_data[tag] = str(value)
                            
            except Exception as e:
                logger.warning(f"⚠️ Erro ao extrair EXIF com exifread: {e}")
        
        # Processar dados EXIF importantes
        processed_exif = self._process_exif_data(exif_data)
        
        return {
            'raw_exif': exif_data,
            'processed_exif': processed_exif,
            'has_exif': len(exif_data) > 0
        }
    
    def _process_exif_data(self, exif_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa dados EXIF para extrair informações importantes"""
        processed = {}
        
        try:
            # Informações da câmera
            camera_info = {}
            for key in ['Make', 'Model', 'Software']:
                if key in exif_data:
                    camera_info[key.lower()] = exif_data[key]
            
            if camera_info:
                processed['camera'] = camera_info
            
            # Configurações da foto
            photo_settings = {}
            setting_keys = {
                'ExposureTime': 'exposure_time',
                'FNumber': 'f_number',
                'ISO': 'iso',
                'ISOSpeedRatings': 'iso_speed',
                'FocalLength': 'focal_length',
                'Flash': 'flash',
                'WhiteBalance': 'white_balance'
            }
            
            for exif_key, processed_key in setting_keys.items():
                if exif_key in exif_data:
                    photo_settings[processed_key] = exif_data[exif_key]
            
            if photo_settings:
                processed['photo_settings'] = photo_settings
            
            # Informações de data/hora
            datetime_keys = ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']
            for key in datetime_keys:
                if key in exif_data:
                    processed['datetime'] = {
                        'original': exif_data[key],
                        'key_used': key
                    }
                    break
            
            # Informações de GPS (se disponível)
            gps_keys = ['GPSLatitude', 'GPSLongitude', 'GPSAltitude']
            gps_data = {}
            for key in gps_keys:
                if key in exif_data:
                    gps_data[key.lower()] = exif_data[key]
            
            if gps_data:
                processed['gps'] = gps_data
            
            # Orientação
            if 'Orientation' in exif_data:
                processed['orientation'] = exif_data['Orientation']
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao processar dados EXIF: {e}")
            processed['processing_error'] = str(e)
        
        return processed
    
    def _calculate_image_hash(self, image_path: Path) -> Dict[str, Any]:
        """Calcula hashes da imagem para detecção de duplicatas"""
        try:
            # Hash do arquivo
            with open(image_path, 'rb') as f:
                file_content = f.read()
                file_hash = hashlib.md5(file_content).hexdigest()
                file_sha256 = hashlib.sha256(file_content).hexdigest()
            
            hash_info = {
                'file_md5': file_hash,
                'file_sha256': file_sha256,
                'file_size': len(file_content)
            }
            
            # Hash perceptual (se PIL disponível)
            if self.pillow_available:
                try:
                    perceptual_hash = self._calculate_perceptual_hash(image_path)
                    hash_info['perceptual_hash'] = perceptual_hash
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao calcular hash perceptual: {e}")
            
            return hash_info
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular hash: {e}")
            return {'erro': str(e)}
    
    def _calculate_perceptual_hash(self, image_path: Path) -> str:
        """Calcula hash perceptual simples da imagem"""
        try:
            with self.PIL_Image.open(image_path) as img:
                # Converter para escala de cinza e redimensionar
                img = img.convert('L').resize((8, 8), self.PIL_Image.Resampling.LANCZOS)
                
                # Calcular média dos pixels
                pixels = list(img.getdata())
                avg = sum(pixels) / len(pixels)
                
                # Criar hash binário
                hash_bits = []
                for pixel in pixels:
                    hash_bits.append('1' if pixel > avg else '0')
                
                # Converter para hexadecimal
                hash_binary = ''.join(hash_bits)
                hash_hex = hex(int(hash_binary, 2))[2:]
                
                return hash_hex
                
        except Exception as e:
            logger.error(f"❌ Erro ao calcular hash perceptual: {e}")
            return 'error'
    
    def _analyze_image_content(self, image_path: Path) -> Dict[str, Any]:
        """Analisa o conteúdo da imagem"""
        if not self.pillow_available:
            return {'erro': 'PIL não disponível'}
        
        try:
            with self.PIL_Image.open(image_path) as img:
                # Análise de cores
                color_analysis = self._analyze_colors(img)
                
                # Análise de brilho
                brightness_analysis = self._analyze_brightness(img)
                
                # Detecção de transparência
                transparency_info = self._analyze_transparency(img)
                
                return {
                    'colors': color_analysis,
                    'brightness': brightness_analysis,
                    'transparency': transparency_info,
                    'analysis_timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Erro na análise de conteúdo: {e}")
            return {'erro': str(e)}
    
    def _analyze_colors(self, img) -> Dict[str, Any]:
        """Analisa as cores da imagem"""
        try:
            # Converter para RGB se necessário
            if img.mode != 'RGB':
                img_rgb = img.convert('RGB')
            else:
                img_rgb = img
            
            # Redimensionar para análise mais rápida
            img_small = img_rgb.resize((50, 50))
            
            # Obter cores dominantes (simplificado)
            colors = img_small.getcolors(maxcolors=256*256*256)
            
            if colors:
                # Ordenar por frequência
                colors.sort(reverse=True)
                
                # Cores mais comuns
                dominant_colors = []
                for count, color in colors[:5]:
                    dominant_colors.append({
                        'rgb': color,
                        'hex': '#{:02x}{:02x}{:02x}'.format(*color),
                        'frequency': count
                    })
                
                return {
                    'dominant_colors': dominant_colors,
                    'total_unique_colors': len(colors),
                    'is_grayscale': self._is_grayscale(img_rgb)
                }
            else:
                return {'erro': 'Não foi possível analisar cores'}
                
        except Exception as e:
            logger.error(f"❌ Erro na análise de cores: {e}")
            return {'erro': str(e)}
    
    def _analyze_brightness(self, img) -> Dict[str, Any]:
        """Analisa o brilho da imagem"""
        try:
            # Converter para escala de cinza
            gray_img = img.convert('L')
            
            # Calcular estatísticas de brilho
            pixels = list(gray_img.getdata())
            
            avg_brightness = sum(pixels) / len(pixels)
            min_brightness = min(pixels)
            max_brightness = max(pixels)
            
            # Classificar brilho
            if avg_brightness < 85:
                brightness_category = 'dark'
            elif avg_brightness > 170:
                brightness_category = 'bright'
            else:
                brightness_category = 'medium'
            
            return {
                'average': round(avg_brightness, 2),
                'minimum': min_brightness,
                'maximum': max_brightness,
                'range': max_brightness - min_brightness,
                'category': brightness_category,
                'contrast_ratio': round((max_brightness - min_brightness) / 255, 2)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de brilho: {e}")
            return {'erro': str(e)}
    
    def _analyze_transparency(self, img) -> Dict[str, Any]:
        """Analisa informações de transparência"""
        try:
            has_alpha = img.mode in ('RGBA', 'LA')
            has_transparency = 'transparency' in img.info
            
            transparency_info = {
                'has_alpha_channel': has_alpha,
                'has_transparency_info': has_transparency,
                'mode': img.mode
            }
            
            if has_alpha:
                # Analisar canal alpha
                if img.mode == 'RGBA':
                    alpha_channel = img.split()[-1]
                    alpha_pixels = list(alpha_channel.getdata())
                    
                    transparency_info.update({
                        'alpha_min': min(alpha_pixels),
                        'alpha_max': max(alpha_pixels),
                        'alpha_avg': round(sum(alpha_pixels) / len(alpha_pixels), 2),
                        'fully_transparent_pixels': alpha_pixels.count(0),
                        'fully_opaque_pixels': alpha_pixels.count(255)
                    })
            
            return transparency_info
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de transparência: {e}")
            return {'erro': str(e)}
    
    def _is_grayscale(self, img) -> bool:
        """Verifica se a imagem é em escala de cinza"""
        try:
            # Redimensionar para análise mais rápida
            img_small = img.resize((10, 10))
            
            for pixel in img_small.getdata():
                r, g, b = pixel
                if r != g or g != b:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def process_directory(self, directory_path: str, recursive: bool = True) -> Dict[str, Any]:
        """Processa todas as imagens em um diretório"""
        try:
            directory_path = Path(directory_path)
            
            if not directory_path.exists():
                return {
                    'status': 'error',
                    'erro': 'Diretório não encontrado',
                    'path': str(directory_path)
                }
            
            logger.info(f"📁 Processando diretório: {directory_path}")
            
            # Encontrar todas as imagens
            image_files = []
            
            if recursive:
                for ext in self.supported_formats:
                    image_files.extend(directory_path.rglob(f"*{ext}"))
                    image_files.extend(directory_path.rglob(f"*{ext.upper()}"))
            else:
                for ext in self.supported_formats:
                    image_files.extend(directory_path.glob(f"*{ext}"))
                    image_files.extend(directory_path.glob(f"*{ext.upper()}"))
            
            # Remover duplicatas
            image_files = list(set(image_files))
            
            logger.info(f"🔍 Encontradas {len(image_files)} imagens")
            
            # Processar cada imagem
            results = {
                'directory': str(directory_path),
                'timestamp': datetime.now().isoformat(),
                'total_images': len(image_files),
                'processed_successfully': 0,
                'processing_errors': 0,
                'images': {},
                'summary': {}
            }
            
            for image_file in image_files:
                try:
                    result = self.process_image_file(str(image_file))
                    results['images'][str(image_file)] = result
                    
                    if result['status'] == 'success':
                        results['processed_successfully'] += 1
                    else:
                        results['processing_errors'] += 1
                        
                except Exception as e:
                    logger.error(f"❌ Erro ao processar {image_file}: {e}")
                    results['processing_errors'] += 1
                    results['images'][str(image_file)] = {
                        'status': 'error',
                        'erro': str(e)
                    }
            
            # Gerar resumo
            results['summary'] = self._generate_directory_summary(results)
            
            logger.info(f"✅ Processamento concluído: {results['processed_successfully']}/{results['total_images']} sucessos")
            return results
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar diretório: {e}")
            return {
                'status': 'error',
                'erro': str(e),
                'directory': str(directory_path)
            }
    
    def _generate_directory_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Gera resumo do processamento do diretório"""
        try:
            summary = {
                'total_files': results['total_images'],
                'successful_processing': results['processed_successfully'],
                'processing_errors': results['processing_errors'],
                'success_rate': round((results['processed_successfully'] / results['total_images']) * 100, 2) if results['total_images'] > 0 else 0,
                'formats_found': {},
                'total_size_mb': 0,
                'average_size_mb': 0,
                'largest_image': None,
                'smallest_image': None
            }
            
            # Analisar imagens processadas com sucesso
            successful_images = [img for img in results['images'].values() if img['status'] == 'success']
            
            if successful_images:
                sizes = []
                
                for img_data in successful_images:
                    # Contar formatos
                    format_name = img_data.get('image_info', {}).get('format', 'unknown')
                    summary['formats_found'][format_name] = summary['formats_found'].get(format_name, 0) + 1
                    
                    # Calcular tamanhos
                    size_mb = img_data.get('file_info', {}).get('file_size_mb', 0)
                    sizes.append(size_mb)
                    summary['total_size_mb'] += size_mb
                
                if sizes:
                    summary['average_size_mb'] = round(summary['total_size_mb'] / len(sizes), 2)
                    
                    # Encontrar maior e menor imagem
                    max_size = max(sizes)
                    min_size = min(sizes)
                    
                    for img_path, img_data in results['images'].items():
                        if img_data['status'] == 'success':
                            size_mb = img_data.get('file_info', {}).get('file_size_mb', 0)
                            if size_mb == max_size and not summary['largest_image']:
                                summary['largest_image'] = {
                                    'path': img_path,
                                    'size_mb': size_mb
                                }
                            if size_mb == min_size and not summary['smallest_image']:
                                summary['smallest_image'] = {
                                    'path': img_path,
                                    'size_mb': size_mb
                                }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resumo: {e}")
            return {'erro': str(e)}
    
    def save_metadata_report(self, results: Dict[str, Any], output_path: str) -> bool:
        """Salva relatório de metadados em arquivo"""
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Salvar como JSON
            if output_path.suffix.lower() == '.json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
            
            # Salvar como MD
            elif output_path.suffix.lower() == '.md':
                md_content = self._generate_markdown_report(results)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)
            
            else:
                # Salvar ambos os formatos
                json_path = output_path.with_suffix('.json')
                md_path = output_path.with_suffix('.md')
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                
                md_content = self._generate_markdown_report(results)
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)
            
            logger.info(f"📊 Relatório de metadados salvo: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório: {e}")
            return False
    
    def _generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """Gera relatório em formato Markdown"""
        try:
            if 'directory' in results:
                # Relatório de diretório
                return self._generate_directory_markdown_report(results)
            else:
                # Relatório de imagem única
                return self._generate_single_image_markdown_report(results)
                
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório MD: {e}")
            return f"# Erro no Relatório\n\nErro: {str(e)}"
    
    def _generate_directory_markdown_report(self, results: Dict[str, Any]) -> str:
        """Gera relatório MD para diretório"""
        summary = results.get('summary', {})
        
        md_content = f"""# Relatório de Metadados de Imagens

## Informações Gerais
- **Diretório**: {results.get('directory', 'N/A')}
- **Data do Processamento**: {results.get('timestamp', 'N/A')}
- **Total de Imagens**: {results.get('total_images', 0)}
- **Processadas com Sucesso**: {results.get('processed_successfully', 0)}
- **Erros de Processamento**: {results.get('processing_errors', 0)}
- **Taxa de Sucesso**: {summary.get('success_rate', 0)}%

## Resumo Estatístico
- **Tamanho Total**: {summary.get('total_size_mb', 0)} MB
- **Tamanho Médio**: {summary.get('average_size_mb', 0)} MB
- **Maior Imagem**: {summary.get('largest_image', {}).get('path', 'N/A')} ({summary.get('largest_image', {}).get('size_mb', 0)} MB)
- **Menor Imagem**: {summary.get('smallest_image', {}).get('path', 'N/A')} ({summary.get('smallest_image', {}).get('size_mb', 0)} MB)

## Formatos Encontrados
"""
        
        for format_name, count in summary.get('formats_found', {}).items():
            md_content += f"- **{format_name}**: {count} arquivos\n"
        
        md_content += "\n## Detalhes por Imagem\n"
        
        for img_path, img_data in results.get('images', {}).items():
            if img_data['status'] == 'success':
                file_info = img_data.get('file_info', {})
                image_info = img_data.get('image_info', {})
                
                md_content += f"""
### {Path(img_path).name}
- **Caminho**: {img_path}
- **Tamanho**: {file_info.get('file_size_mb', 0)} MB
- **Formato**: {image_info.get('format', 'N/A')}
- **Dimensões**: {image_info.get('width', 0)} x {image_info.get('height', 0)}
- **Modo de Cor**: {image_info.get('mode', 'N/A')}
- **Possui EXIF**: {'Sim' if img_data.get('exif_data', {}).get('has_exif', False) else 'Não'}
"""
            else:
                md_content += f"""
### {Path(img_path).name} ❌
- **Erro**: {img_data.get('erro', 'Erro desconhecido')}
"""
        
        md_content += f"""
---
*Relatório gerado pelo Image Metadata Processor em {datetime.now().isoformat()}*
"""
        
        return md_content
    
    def _generate_single_image_markdown_report(self, results: Dict[str, Any]) -> str:
        """Gera relatório MD para imagem única"""
        file_info = results.get('file_info', {})
        image_info = results.get('image_info', {})
        exif_data = results.get('exif_data', {})
        hash_info = results.get('hash_info', {})
        content_analysis = results.get('content_analysis', {})
        
        md_content = f"""# Relatório de Metadados - {file_info.get('filename', 'Imagem')}

## Informações do Arquivo
- **Nome**: {file_info.get('filename', 'N/A')}
- **Caminho**: {file_info.get('filepath', 'N/A')}
- **Tamanho**: {file_info.get('file_size_mb', 0)} MB ({file_info.get('file_size', 0)} bytes)
- **Tipo MIME**: {file_info.get('mime_type', 'N/A')}
- **Criado em**: {file_info.get('created_time', 'N/A')}
- **Modificado em**: {file_info.get('modified_time', 'N/A')}

## Informações da Imagem
- **Formato**: {image_info.get('format', 'N/A')}
- **Dimensões**: {image_info.get('width', 0)} x {image_info.get('height', 0)} pixels
- **Modo de Cor**: {image_info.get('mode', 'N/A')}
- **Proporção**: {image_info.get('aspect_ratio', 0)}:1
- **DPI**: {image_info.get('dpi', 'N/A')}
- **Possui Transparência**: {'Sim' if image_info.get('has_transparency', False) else 'Não'}

## Dados EXIF
"""
        
        if exif_data.get('has_exif', False):
            processed_exif = exif_data.get('processed_exif', {})
            
            if 'camera' in processed_exif:
                md_content += "\n### Informações da Câmera\n"
                for key, value in processed_exif['camera'].items():
                    md_content += f"- **{key.title()}**: {value}\n"
            
            if 'photo_settings' in processed_exif:
                md_content += "\n### Configurações da Foto\n"
                for key, value in processed_exif['photo_settings'].items():
                    md_content += f"- **{key.replace('_', ' ').title()}**: {value}\n"
            
            if 'datetime' in processed_exif:
                md_content += f"\n### Data/Hora Original\n- **{processed_exif['datetime']['original']}**\n"
            
            if 'gps' in processed_exif:
                md_content += "\n### Localização GPS\n"
                for key, value in processed_exif['gps'].items():
                    md_content += f"- **{key.upper()}**: {value}\n"
        else:
            md_content += "\n*Nenhum dado EXIF encontrado*\n"
        
        md_content += f"""
## Hashes
- **MD5**: {hash_info.get('file_md5', 'N/A')}
- **SHA256**: {hash_info.get('file_sha256', 'N/A')}
- **Hash Perceptual**: {hash_info.get('perceptual_hash', 'N/A')}

## Análise de Conteúdo
"""
        
        if 'colors' in content_analysis:
            colors = content_analysis['colors']
            md_content += f"\n### Cores\n- **Cores Únicas**: {colors.get('total_unique_colors', 0)}\n"
            md_content += f"- **Escala de Cinza**: {'Sim' if colors.get('is_grayscale', False) else 'Não'}\n"
            
            if 'dominant_colors' in colors:
                md_content += "\n#### Cores Dominantes\n"
                for i, color in enumerate(colors['dominant_colors'][:3], 1):
                    md_content += f"{i}. **{color['hex']}** (RGB: {color['rgb']}) - {color['frequency']} pixels\n"
        
        if 'brightness' in content_analysis:
            brightness = content_analysis['brightness']
            md_content += f"""
### Brilho
- **Categoria**: {brightness.get('category', 'N/A').title()}
- **Brilho Médio**: {brightness.get('average', 0)}/255
- **Contraste**: {brightness.get('contrast_ratio', 0)}
- **Faixa**: {brightness.get('minimum', 0)} - {brightness.get('maximum', 0)}
"""
        
        md_content += f"""
---
*Relatório gerado em {results.get('timestamp', datetime.now().isoformat())}*
"""
        
        return md_content

# Instância global
image_metadata_processor = ImageMetadataProcessor()

def process_image_metadata(image_path: str) -> Dict[str, Any]:
    """Função principal para processar metadados de uma imagem"""
    return image_metadata_processor.process_image_file(image_path)

def process_directory_metadata(directory_path: str, recursive: bool = True) -> Dict[str, Any]:
    """Função principal para processar metadados de um diretório"""
    return image_metadata_processor.process_directory(directory_path, recursive)

def save_metadata_report(results: Dict[str, Any], output_path: str) -> bool:
    """Função principal para salvar relatório de metadados"""
    return image_metadata_processor.save_metadata_report(results, output_path)