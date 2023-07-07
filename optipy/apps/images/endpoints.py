import hashlib
from datetime import datetime

from botocore.exceptions import ClientError
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from optipy.api.deps import get_db
from optipy.api.exceptions import BadRequestFromRaisedException
from optipy.config import settings
from optipy.services import s3

from .models import Image
from .schemas import ImageOut


router = APIRouter(prefix="/images", tags=["images"])


@router.post("/", response_model=ImageOut, status_code=status.HTTP_201_CREATED)
def upload_image(image: UploadFile = File(), db: Session = Depends(get_db)):
    try:
        file_extension = image.filename.split('.')[-1]
        hash_content = f"{image.filename}_{datetime.now()}".encode()
        hash_str = hashlib.md5(hash_content).hexdigest()
        key = f"{hash_str}.{file_extension}"

        s3.upload_fileobj(image.file, "optipy-dev", key)

        url = f"{settings.AWS_URL}/optipy-dev/{key}"

        db_image = Image(url=url, filename=key)
        db.add(db_image)
        db.commit()
        db.refresh(db_image)

    except ClientError:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="Unable to upload image to the S3 server",
        )

    except IntegrityError as e:
        db.rollback()
        raise BadRequestFromRaisedException(exception=e)

    return db_image
