from fastapi import APIRouter, Depends, Request
from typing import List
from schemas.of_schema import OFSchema
from services.odoo_service import Odoo

router - APIRouter()

def