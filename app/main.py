from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.routes import splash_page, email_routes

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    # "http://192.168.18.10:5173",
    # "http://localhost:5173",
    # "http://pdc-frontend-chatbot.s3-website-us-east-1.amazonaws.com",
    # "http://localhost:4173",
    # "http://pdc-frontend-admin.s3-website-us-east-1.amazonaws.com"
    
        # Adjust the port if your React app runs on a different port
    # settings.FRONTEND_HOST,  # The default port for FastAPI, if you want to allow it
    # Add any other origins you want to allow
]


def create_application():
    application = FastAPI()
    
    @application.get("/debug")
    async def debug():
        return {"routes": [{"path": route.path, "name": route.name} for route in application.routes]}
    
    application.include_router(splash_page.router)
    application.include_router(email_routes.router)

    return application


app = create_application()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specified origins to make requests
    allow_credentials=True,  # Allows cookies to be included in cross-origin HTTP requests
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)




@app.get("/")
async def root():
    return {"message": "Customizable chats V2 is live"}

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy"}



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (Change to frontend origin in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)