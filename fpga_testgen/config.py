"""Application configuration."""

import shutil
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.1-pro-preview"
    default_simulator: str = "iverilog"
    max_retries: int = 3
    sim_timeout: int = 30
    server_port: int = 8000

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def has_iverilog(self) -> bool:
        return shutil.which("iverilog") is not None

    @property
    def has_verilator(self) -> bool:
        return shutil.which("verilator") is not None


settings = Settings()
