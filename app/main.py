from fastapi import FastAPI
from app.api.endpoints.valuation import router as ppss_router
from app.api.endpoints.confidence import router as confidence_router
from app.api.endpoints.ppcp import router as ppcp_router

app = FastAPI(title="Property Score API")

app.include_router(ppss_router)
app.include_router(confidence_router)
app.include_router(ppcp_router)


@app.get("/")
def home():
    return {
        "message": "API is running"
    }