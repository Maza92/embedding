import uvicorn
from app.config.settings import Config

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=Config.PORT,
        reload=Config.DEBUG_MODE
    )