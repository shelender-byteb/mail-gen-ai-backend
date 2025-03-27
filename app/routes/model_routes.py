from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.request.model_update import ModelUpdateRequest, ModelType
from app.models.model_config import ModelConfig
from app.common.database_config import get_db

router = APIRouter(
    prefix="/v1/models",
    tags=["Models"],
)

# Only allow updates for these model types
ALLOWED_MODEL_TYPES = {"email", "splash_page", "banner"}

@router.get("/", status_code=status.HTTP_200_OK)
def get_all_models(session: Session = Depends(get_db)):
    """
    Retrieve all available model configurations.
    """
    models = session.query(ModelConfig).all()
    return {
        model.model_type: {"model_name": model.model_name, "temperature": model.temperature}
        for model in models
    }

@router.get("/{model_type}", status_code=status.HTTP_200_OK)
def get_model(model_type: str, session: Session = Depends(get_db)):
    """
    Retrieve a specific model configuration by its type.
    """
    if model_type not in ALLOWED_MODEL_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid model type"
        )
    model_config = session.query(ModelConfig).filter(ModelConfig.model_type == model_type).first()
    if not model_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model configuration not found"
        )
    return {model_type: {"model_name": model_config.model_name, "temperature": model_config.temperature}}

@router.put("/{model_type}", status_code=status.HTTP_200_OK)
def upsert_model(
    model_type: ModelType,
    data: ModelUpdateRequest,
    session: Session = Depends(get_db)
):
    """
    Update an existing model configuration or create a new one if it doesn't exist.
    Only allowed model types can be updated/added.
    """
    if model_type not in ALLOWED_MODEL_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid model type"
        )
    model_config = session.query(ModelConfig).filter(ModelConfig.model_type == model_type).first()
    if not model_config:
        # Create new record if not present
        model_config = ModelConfig(
            model_type=model_type,
            model_name=data.model_name,
            temperature=data.temperature
        )
        session.add(model_config)
    else:
        # Update existing record
        model_config.model_name = data.model_name
        model_config.temperature = data.temperature
    session.commit()
    session.refresh(model_config)
    return {model_type: {"model_name": model_config.model_name, "temperature": model_config.temperature}}
