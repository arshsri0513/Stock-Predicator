"""
Centralized application configuration.

Why this file exists:
Instead of scattering os.environ.get("SOME_VAR") calls throughout the codebase,
we define every configuration value ONCE here, with types and defaults.
pydantic-settings automatically reads from a `.env` file and validates types
(e.g. it will error loudly if PORT isn't actually a number, instead of failing
silently later at runtime).

Every other file in the backend imports `settings` from here rather than
reading environment variables directly.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App metadata
    APP_NAME: str = "Stock Predictor API"
    ENVIRONMENT: str = "development"  # "development" | "production"
    DEBUG: bool = True

    # Database (filled in properly in Phase 9)
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/stockdb"

    # Stock data fallback (Phase 8) -- used by app/services/stock_data.py
    # when yfinance is blocked from cloud IPs. Get a free key (no credit
    # card, 800 requests/day) at https://twelvedata.com. Left blank by
    # default; the fallback simply raises a clear error if unset rather
    # than failing silently.
    TWELVE_DATA_API_KEY: str = ""
    # Finnhub (Markets)
    FINNHUB_API_KEY: str = ""

    # Redis (filled in properly in Phase 13)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Auth (filled in properly in Phase 12)
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_ENV_FILE"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Email alerts (Phase 13) -- Gmail SMTP. SMTP_PASSWORD must be a Gmail
    # "App Password" (16 characters), NOT your regular Gmail password --
    # Google blocks regular-password SMTP login for security reasons.
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""  # your full Gmail address
    SMTP_PASSWORD: str = ""  # Gmail App Password, NOT your real password

    # Telegram alerts (Phase 13)
    TELEGRAM_BOT_TOKEN: str = ""

    # CORS (Phase 15) -- comma-separated list of origins allowed to call
    # this API. Defaults to local development; in production this gets
    # set via an environment variable on Render to the real deployed
    # Vercel URL, e.g. "https://stock-predictor.vercel.app" -- never left
    # as a hardcoded localhost value or a wildcard "*" in production.
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # Reads from a .env file sitting next to where the app is run from
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def allowed_origins_list(self) -> list[str]:
        """Splits the comma-separated ALLOWED_ORIGINS string into a list,
        trimming whitespace -- so .env can read naturally as
        ALLOWED_ORIGINS=https://a.com,https://b.com without needing JSON
        array syntax."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


# A single shared instance, imported everywhere else in the app
settings = Settings()
