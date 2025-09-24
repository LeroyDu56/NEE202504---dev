from fastapi import FastAPI
from api.v1.endpoints import ofs
from services.odoo_service import Odoo

app = FastAPI()

@app.on_event("/")
def startup_event():
  app.state.odoo_service = Odoo(
        settings.odoo_url,
        settings.odoo_db,
        settings.odoo_user,
        settings.odoo_password,
    )