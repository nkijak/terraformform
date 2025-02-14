from fastapi import FastAPI
from api.payments.api import router as payment_router
from api.terraformform.api import router as terraform_router

app = FastAPI()

app.include_router(payment_router)
app.include_router(terraform_router)
