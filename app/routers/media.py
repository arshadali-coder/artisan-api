import os
import uuid
from fastapi import APIRouter, UploadFile, File, Request, HTTPException, status
from app.config import settings
from app.schemas import MediaUploadResponse

router = APIRouter(tags=["Media Endpoints"])

@router.post("/media/upload", response_model=MediaUploadResponse, status_code=status.HTTP_201_CREATED)
@router.post("/media/upload/", response_model=MediaUploadResponse, status_code=status.HTTP_201_CREATED)
@router.post("/upload", response_model=MediaUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_media(
    request: Request,
    file: UploadFile = File(None),
    image: UploadFile = File(None),
    media: UploadFile = File(None)
):
    """
    Accepts multi-part form data (images/audio) and returns hosted file URL.
    Returns expected JSON:
    {
      "status": "success",
      "filename": "uploaded_image_123.jpg",
      "url": "https://example.com/media/uploaded_image_123.jpg",
      "message": "Media uploaded successfully"
    }
    """
    upload_file = file or image or media
    if not upload_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided in form data. Pass file, image, or media field."
        )

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    filename_raw = upload_file.filename or "uploaded_media.jpg"
    ext = filename_raw.split(".")[-1] if "." in filename_raw else "jpg"
    filename = f"uploaded_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    contents = await upload_file.read()
    with open(filepath, "wb") as f:
        f.write(contents)

    # Build public URL
    base_url = str(request.base_url).rstrip("/")
    media_url = f"{base_url}/static/uploads/{filename}"

    return MediaUploadResponse(
        status="success",
        filename=filename,
        url=media_url,
        message="Media uploaded successfully"
    )
