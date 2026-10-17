from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.limiter import limiter
from app.routes import (
    auth_routes,
    profile_routes,
    course_routes,
    assignment_routes,
    grade_routes,
    message_routes,
    admin_routes,
    utility_routes,
)

app = FastAPI(title="DAT250 SecureApp", debug=False)

# Rate limiting setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/uploads", StaticFiles(directory="app/uploads"), name="uploads")

app.include_router(auth_routes.router)
app.include_router(profile_routes.router)
app.include_router(course_routes.router)
app.include_router(assignment_routes.router)
app.include_router(grade_routes.router)
app.include_router(message_routes.router)
app.include_router(admin_routes.router)
app.include_router(utility_routes.router)