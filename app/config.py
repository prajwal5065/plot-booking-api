from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./plot_booking.db"
    secret_key: str = "change-this-in-production-use-a-long-random-string"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    booking_expiry_hours: int = 48
    commission_rate: float = 0.02  # 2% default

    class Config:
        env_file = ".env"


settings = Settings()
