from faststream.rabbit import RabbitRouter

from .auth import router as AuthController

router = RabbitRouter(prefix="auth")

router.include_router(AuthController)
