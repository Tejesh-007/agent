from fastapi import APIRouter, Depends, HTTPException

from models.schemas import DatabaseSchemaResponse, TablePreviewResponse
from api.dependencies import get_db

router = APIRouter(prefix="/database", tags=["database"])


@router.get("/schema", response_model=DatabaseSchemaResponse)
async def get_schema(db=Depends(get_db)):
    """Return all table names and their schema information."""
    tables = []
    for table_name in db.get_usable_table_names():
        table_info = db.get_table_info([table_name])
        tables.append({"name": table_name, "info": table_info})
    return DatabaseSchemaResponse(tables=tables)


@router.get("/tables/{table_name}", response_model=TablePreviewResponse)
async def get_table_preview(
    table_name: str,
    db=Depends(get_db),
    limit: int = 10,
):
    """Return sample rows from a specific table."""
    if table_name not in db.get_usable_table_names():
        raise HTTPException(
            status_code=404, detail=f"Table '{table_name}' not found"
        )
    result = db.run(f'SELECT * FROM "{table_name}" LIMIT {limit}')
    return TablePreviewResponse(table_name=table_name, result=result)
