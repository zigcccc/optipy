from typing import Optional, Dict, Any
from pydantic import BaseSettings, PostgresDsn, validator, AnyHttpUrl


class Settings(BaseSettings):
    # App
    APP_HOST: Optional[str] = "localhost"
    APP_PORT: Optional[int] = 8000

    # Database
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    # Auth
    AUTH0_DOMAIN: str
    AUTH0_API_AUDIENCE: AnyHttpUrl
    AUTH0_ALGORITHMS: str
    AUTH0_ISSUER: AnyHttpUrl

    # AWS
    AWS_URL: AnyHttpUrl
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION_NAME: str

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("DB_USER"),
            password=values.get("DB_PASS"),
            host=values.get("DB_HOST", "localhost"),
            port=values.get("DB_PORT", "5432"),
            path=f"/{values.get('DB_NAME')}",
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
