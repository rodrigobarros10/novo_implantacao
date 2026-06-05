"""
Schema Pydantic para entidade Produto do Sistema BR.

Define a estrutura, validações e transformações para produtos
no padrão de dados do Sistema BR.
"""

from typing import Optional
from decimal import Decimal
from datetime import datetime
from pydantic import Field, field_validator
from models.schemas.base import AuditableSchema, AtivosSchema


class ProdutoSchema(AuditableSchema, AtivosSchema):
    """
    Schema para entidade Produto.
    
    Representa um produto no Sistema BR com todas as suas informações
    fiscais, de estoque e precificação.
    
    Attributes:
        id: Identificador único do produto
        codigobarras: Código de barras (EAN)
        descricaocompleta: Descrição completa do produto
        descricaoreduzida: Descrição reduzida (para PDV)
        descricaogondola: Descrição para etiqueta de gôndola
        unidade: Unidade de medida (UN, KG, L, etc)
        balanca: Indica se é fracionável em balança
        pesobruto: Peso bruto em kg
        pesoliquido: Peso líquido em kg
        ncm: Nomenclatura Comum do Mercosul
        cest: Código Especificador da Substituição Tributária
        estoquemaximo: Estoque máximo recomendado
        estoqueminimo: Estoque mínimo recomendado
        estoque: Estoque atual da loja
        custosemimposto: Custo sem imposto
        custocomimposto: Custo com imposto
        customediosemimposto: Custo médio sem imposto
        customediocomimposto: Custo médio com imposto
        precovenda: Preço de venda
        margem: Margem de lucro (%)
        validade: Dias de validade do produto
        qtdembalagemcotacao: Quantidade por embalagem de cotação
        qtqtdembalagem: Quantidade por embalagem padrão
    """
    
    # Identificadores
    id: int = Field(..., gt=0, description="ID único do produto")
    codigobarras: Optional[str] = Field(None, min_length=8, max_length=14)
    
    # Descrições
    descricaocompleta: str = Field(..., min_length=3, max_length=255)
    descricaoreduzida: Optional[str] = Field(None, max_length=30)
    descricaogondola: Optional[str] = Field(None, max_length=50)
    
    # Dimensões e peso
    unidade: str = Field(..., min_length=1, max_length=3)
    balanca: bool = False
    pesobruto: Optional[Decimal] = Field(None, ge=0, decimal_places=3)
    pesoliquido: Optional[Decimal] = Field(None, ge=0, decimal_places=3)
    
    # Informações fiscais
    ncm: Optional[str] = Field(None, regex=r'^\d{8}$')
    cest: Optional[str] = Field(None, regex=r'^\d{7}$')
    piscofins_cst_debito: Optional[str] = Field(None, max_length=2)
    piscofins_cst_credito: Optional[str] = Field(None, max_length=2)
    piscofins_natureza_receita: Optional[str] = Field(None, max_length=6)
    
    # ICMS - Saída
    icms_cst_saida: str = Field(default='000', max_length=3)
    icms_aliquota_saida: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    icms_reduzido_saida: Optional[Decimal] = Field(default=0, ge=0, le=100, decimal_places=2)
    
    # ICMS - Saída Fora Estado
    icms_cst_saida_foraestado: str = Field(default='000', max_length=3)
    icms_aliquota_saida_foraestado: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    icms_reduzido_saida_foraestado: Optional[Decimal] = Field(default=0, ge=0, le=100, decimal_places=2)
    
    # ICMS - Saída Fora Estado NF
    icms_cst_saida_foraestadonf: str = Field(default='000', max_length=3)
    icms_aliquota_saida_foraestadonf: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    icms_reduzido_saida_foraestadonf: Optional[Decimal] = Field(default=0, ge=0, le=100, decimal_places=2)
    
    # ICMS - Consumidor
    icms_cst_consumidor: str = Field(default='000', max_length=3)
    icms_aliq_consumidor: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    icms_reduzido_consumidor: Optional[Decimal] = Field(default=0, ge=0, le=100, decimal_places=2)
    
    # ICMS - Entrada
    icms_cst_entrada: str = Field(default='000', max_length=3)
    icms_aliquota_entrada: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    icms_reduzido_entrada: Optional[Decimal] = Field(default=0, ge=0, le=100, decimal_places=2)
    
    # ICMS - Entrada Fora Estado
    icms_cst_entrada_foraestado: str = Field(default='000', max_length=3)
    icms_aliquota_entrada_foraestado: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    icms_reduzido_entrada_foraestado: Optional[Decimal] = Field(default=0, ge=0, le=100, decimal_places=2)
    
    # Estoque
    estoquemaximo: Optional[Decimal] = Field(None, ge=0)
    estoqueminimo: Optional[Decimal] = Field(None, ge=0)
    estoque: Optional[Decimal] = Field(None, ge=0)
    
    # Custos
    custosemimposto: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    custocomimposto: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    customediosemimposto: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    customediocomimposto: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    
    # Preço e margem
    precovenda: Decimal = Field(..., gt=0, decimal_places=2)
    margem: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    validade: Optional[int] = Field(None, ge=0, description="Dias de validade")
    
    # Embalagem
    qtdembalagemcotacao: Optional[Decimal] = Field(None, gt=0)
    qtqtdembalagem: Optional[Decimal] = Field(None, gt=0)
    
    # Auditoria
    datacadastro: Optional[datetime] = None
    
    @field_validator('codigobarras')
    @classmethod
    def validar_codigobarras(cls, v):
        """Valida código de barras (EAN)."""
        if v:
            v = v.strip()
            if not v.isdigit():
                raise ValueError("Código de barras deve conter apenas dígitos")
        return v
    
    @field_validator('unidade')
    @classmethod
    def validar_unidade(cls, v):
        """Valida unidade de medida."""
        unidades_validas = ['UN', 'KG', 'L', 'M', 'M2', 'M3', 'CX', 'PC', 'DZ', 'FD']
        if v.upper() not in unidades_validas:
            raise ValueError(
                f"Unidade '{v}' não suportada. Válidas: {', '.join(unidades_validas)}"
            )
        return v.upper()
    
    @field_validator('ncm')
    @classmethod
    def validar_ncm(cls, v):
        """Valida NCM."""
        if v:
            return cls.validate_ncm(v)
        return v
    
    @field_validator('estoque')
    @classmethod
    def validar_estoque(cls, v, info):
        """Valida coerência de estoque."""
        if v is None:
            return v
        
        max_est = info.data.get('estoquemaximo')
        if max_est and v > max_est:
            raise ValueError(
                f"Estoque atual ({v}) não pode ser maior que máximo ({max_est})"
            )
        
        return v
    
    class Config:
        """Configuração Pydantic para Produto."""
        json_schema_extra = {
            "example": {
                "id": 1,
                "codigobarras": "12345678901234",
                "descricaocompleta": "Arroz Integral 5kg",
                "descricaoreduzida": "Arroz Integral 5kg",
                "unidade": "KG",
                "precovenda": 25.50,
                "estoque": 100.0,
                "ncm": "10061000",
                "ativo": True
            }
        }
