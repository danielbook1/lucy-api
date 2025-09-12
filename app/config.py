from starlette.config import Config

config = Config(".env")

JWT_EXP: int = 30  # 30 minutes
JWT_ALG: str = config("ALGORITHM")
JWT_SECRET: str = config("SECRET_KEY")

SQLALCHEMY_DATABASE_URI = config("DATABASE_URL")
