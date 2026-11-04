from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_host: str = "localhost"
    database_port: int = 5432
    database_admin_user: str = "busca_bula"
    database_admin_password: str = "busca_bula"
    database_maintenance_name: str = "postgres"
    platform_database_name: str = "busca_bula"
    tenant_database_prefix: str = "tenant_"
    tenant_database_secret: str = "dev-tenant-database-secret"
    catalog_database_name: str = "busca_bula_catalog"

    catalog_cache_dir: str = ".cache/catalog"
    catalog_user_agent: str = "BuscaBula/1.0 (projeto academico de dados abertos)"
    anvisa_medicines_url: str = "https://dados.anvisa.gov.br/dados/DADOS_ABERTOS_MEDICAMENTOS.csv"
    anvisa_leaflets_url: str = "https://dados.anvisa.gov.br/dados/CONSULTAS/DOCUMENTOS/TA_CONSULTA_BULA_PRODUTO.CSV"
    cmed_prices_url: str = "https://dados.anvisa.gov.br/dados/TA_PRECO_MEDICAMENTO.csv"
    chatbulario_dataset_url: str = "https://huggingface.co/datasets/walmeidadf/ChatBulario/resolve/main/data"

    jwt_secret: str = "dev-jwt-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
