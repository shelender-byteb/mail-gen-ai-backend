from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.common.database_config import get_db
from app.models.config_item import ConfigItem
from app.schemas.request.config_items import ServiceType, ConfigItemRequest, ConfigItemResponse

router = APIRouter(
    prefix="/v1/config_items",
    tags=["ConfigItems"],
)

ALLOWED_SERVICES = {t.value for t in ServiceType}

@router.get("/", status_code=status.HTTP_200_OK)
def get_all_configs(session: Session = Depends(get_db)):
    items = session.query(ConfigItem).all()
    return {
        # item.service_type: ConfigItemResponse(
        #     placeholder=item.placeholder,
        #     heading=item.heading,
        #     subheading=item.subheading
        # ).dict()
        item.service_type: ConfigItemResponse(
            placeholder=item.placeholder,
            heading=item.heading,
            subheading=item.subheading,
            styleheading=item.styleheading,
            boldstyle=item.boldstyle,
            cozystyle=item.cozystyle,
            urlheading=item.urlheading,
        ).dict()
        for item in items
    }

@router.get("/{service_type}", status_code=status.HTTP_200_OK)
def get_config(
    service_type: ServiceType,
    session: Session = Depends(get_db)
):
    if service_type.value not in ALLOWED_SERVICES:
        raise HTTPException(status_code=400, detail="Invalid service type")
    cfg = session.query(ConfigItem).filter_by(service_type=service_type.value).first()
    if not cfg:
        raise HTTPException(status_code=404, detail="Config not found")
    return {
        service_type.value: ConfigItemResponse(
            placeholder=cfg.placeholder,
            heading=cfg.heading,
            subheading=cfg.subheading,
            styleheading=cfg.styleheading,
            boldstyle=cfg.boldstyle,
            cozystyle=cfg.cozystyle,
            urlheading=cfg.urlheading,
        ).dict()
    }

@router.put("/{service_type}", status_code=status.HTTP_200_OK)
def upsert_config(
    service_type: ServiceType,
    data: ConfigItemRequest,
    session: Session = Depends(get_db)
):
    if service_type.value not in ALLOWED_SERVICES:
        raise HTTPException(status_code=400, detail="Invalid service type")
    cfg = session.query(ConfigItem).filter_by(service_type=service_type.value).first()
    if not cfg:
        cfg = ConfigItem(
            service_type=service_type.value,
            placeholder=data.placeholder,
            heading=data.heading,
            subheading=data.subheading,
            styleheading=data.styleheading,
            boldstyle=data.boldstyle,
            cozystyle=data.cozystyle,
            urlheading=data.urlheading,
        )
        session.add(cfg)
    else:
        cfg.placeholder  = data.placeholder
        cfg.heading      = data.heading
        cfg.subheading   = data.subheading
        cfg.styleheading = data.styleheading
        cfg.boldstyle    = data.boldstyle
        cfg.cozystyle    = data.cozystyle
        cfg.urlheading   = data.urlheading
    session.commit()
    session.refresh(cfg)

    return {
        service_type.value: ConfigItemResponse.from_orm(cfg).dict()
    }
