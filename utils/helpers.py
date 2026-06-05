"""
Utilitários e funções auxiliares para o sistema ETL.
"""

from typing import Any, List, Dict
from datetime import datetime


def sanitize_sql_identifier(identifier: str) -> str:
    """
    Sanitiza um identificador SQL.
    
    Args:
        identifier: Nome do identificador (tabela, coluna, etc)
    
    Returns:
        Identificador sanitizado
    """
    if not isinstance(identifier, str):
        raise ValueError("Identificador deve ser uma string")
    
    # Remove caracteres especiais, mantém apenas alphanumericos e underscore
    sanitized = ''.join(c if c.isalnum() or c == '_' else '' for c in identifier)
    
    if not sanitized:
        raise ValueError(f"Identificador '{identifier}' é inválido")
    
    return sanitized


def format_bytes(bytes_value: int) -> str:
    """
    Formata bytes em unidade legível.
    
    Args:
        bytes_value: Tamanho em bytes
    
    Returns:
        String formatada (ex: "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024
    
    return f"{bytes_value:.2f} PB"


def format_duration(seconds: float) -> str:
    """
    Formata duração em tempo legível.
    
    Args:
        seconds: Tempo em segundos
    
    Returns:
        String formatada (ex: "1h 30m 45s")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    Flatten a nested dictionary.
    
    Args:
        d: Dicionário a ser achatado
        parent_key: Chave pai (para recursão)
        sep: Separador entre chaves
    
    Returns:
        Dicionário achatado
    """
    items: List = []
    
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                list_key = f"{new_key}[{i}]"
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, list_key, sep=sep).items())
                else:
                    items.append((list_key, item))
        else:
            items.append((new_key, v))
    
    return dict(items)
