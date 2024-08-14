# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.orm import sessionmaker
# from vinda.api.config import cfg

# engine = create_async_engine(cfg.SQLALCHEMY_DATABASE_URL, echo=True)
# SessionLocal = sessionmaker(
#     expire_on_commit=False,
#     class_=AsyncSession,
#     bind=engine,
# )