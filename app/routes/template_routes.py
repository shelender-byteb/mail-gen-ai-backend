from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.request.template_update import TemplateUpdateRequest, TemplateType
from app.models.template import Template
from app.common.database_config import get_db

router = APIRouter(
    prefix="/v1/templates",
    tags=["Templates"],
)

@router.get("/", status_code=status.HTTP_200_OK)
def get_all_templates(session: Session = Depends(get_db)):
    """
    Retrieve all available templates.
    """
    templates = session.query(Template).all()
    return {template.template_type: template.content for template in templates}

@router.get("/{template_type}", status_code=status.HTTP_200_OK)
def get_template(template_type: str, session: Session = Depends(get_db)):
    """
    Retrieve a specific template by its type.
    """
    template = session.query(Template).filter(Template.template_type == template_type).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    return {template_type: template.content}

@router.put("/{template_type}", status_code=status.HTTP_200_OK)
def upsert_template(
    template_type: TemplateType,
    data: TemplateUpdateRequest, 
    session: Session = Depends(get_db)
):
    """
    Update an existing template or create a new one if it doesn't exist.
    """
    template = session.query(Template).filter(Template.template_type == template_type).first()
    if not template:
        # Create new template record
        template = Template(template_type=template_type, content=data.content)
        session.add(template)
    else:
        # Update existing template record
        template.content = data.content
    session.commit()
    session.refresh(template)
    return {template_type: template.content}
