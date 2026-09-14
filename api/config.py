from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings

_REPO_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    spl_dir: Path = Path.home() / "projects/digital-duck/SPL.py"
    public_domains: Path = _REPO_ROOT / "public" / "domains"
    llm: str = "claude_cli:claude-sonnet-5"
    default_model: str = "gemma4"
    spl_while_max_iter: int = 50
    spl_max_llm_calls: int = 50

    # User-supplied API keys for adapters that need one (set from the
    # Settings page, kept in-memory only like every other setting here —
    # never echoed back to the browser, only injected into the spl3
    # subprocess env at generate time; see executor.py's _ADAPTER_ENV_VAR).
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    openai_api_key: str = ""
    openrouter_api_key: str = ""

    model_config = {"env_prefix": "CB_", "env_file": ".env", "extra": "ignore"}

    @field_validator("spl_dir", mode="before")
    @classmethod
    def _expand_spl_dir(cls, v):
        return Path(v).expanduser() if v else v

    @field_validator("public_domains", mode="before")
    @classmethod
    def _resolve_public_domains(cls, v):
        if not v:
            return v
        p = Path(v).expanduser()
        return p if p.is_absolute() else (_REPO_ROOT / p).resolve()


settings = Settings()
