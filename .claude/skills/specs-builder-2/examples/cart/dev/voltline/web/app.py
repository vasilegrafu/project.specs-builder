"""The one HTTP app: every part's routes, mounted under /api/v1. Platform's."""
from fastapi import FastAPI

from voltline.cart.routes import router as cart_routes

app = FastAPI(title="Voltline shop API", version="1")
app.include_router(cart_routes, prefix="/api/v1")
# the catalogue's, the accounts' and the orders' routers are mounted here too in the product; left out of the demo


@app.get("/api/v1/health")
def health() -> dict:
    return {"ok": True}
