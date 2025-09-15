from starlette.config import Config

config = Config(".env")

JWT_EXP: int = int(config("EXPIRE_TIME")) * 60  # Convert seconds to minutes
JWT_ALG: str = config("ALGORITHM")
JWT_SECRET: str = config("SECRET_KEY")

SQLALCHEMY_DATABASE_URI = config("DATABASE_URL")
