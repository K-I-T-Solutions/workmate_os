# app/modules/backoffice/invoices/routes.py
from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.modules.backoffice.invoices import crud, schemas
from fastapi.responses import FileResponse
import os

router = APIRouter(prefix="/backoffice/invoices", tags=["Backoffice Invoices"])

@router.get("/", response_model=List[schemas.InvoiceResponse])
def list_invoices(db: Session = Depends(get_db)):
    return crud.get_invoices(db)

@router.get("/{invoice_id}", response_model=schemas.InvoiceResponse)
def get_invoice(invoice_id: str, db: Session = Depends(get_db)):
    invoice = crud.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.post("/", response_model=schemas.InvoiceResponse, status_code=status.HTTP_201_CREATED )
def create_invoice(data: schemas.InvoiceCreate, db: Session = Depends(get_db)):
    return crud.create_invoice(db, data)

@router.put("/{invoice_id}", response_model=schemas.InvoiceResponse)
def update_invoice(invoice_id: str, data: schemas.InvoiceUpdate, db: Session = Depends(get_db)):
    updated = crud.update_invoice(db, invoice_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return updated

@router.delete("/{invoice_id}")
def delete_invoice(invoice_id: str, db: Session = Depends(get_db)):
    ok = crud.delete_invoice(db, invoice_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"status": "deleted"}



@router.get("/{invoice_id}/pdf", response_class=FileResponse)
def download_invoice_pdf(invoice_id: str, db: Session = Depends(get_db)):
    invoice = crud.get_invoice(db, invoice_id)
    if not invoice or not invoice.pdf_path or not os.path.exists(invoice.pdf_path):
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(
        path=invoice.pdf_path,
        filename=os.path.basename(invoice.pdf_path),
        media_type="application/pdf"
    )

