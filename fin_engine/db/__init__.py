from fin_engine.db.router import (
    Router,
)
from fin_engine.db.db import *

router = Router()


def get_db_router():
    return router
