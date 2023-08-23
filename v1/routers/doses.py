from http import HTTPStatus
from bson import ObjectId
from fastapi import APIRouter, status, HTTPException, Query
from typing import Annotated, Optional, Union
from datetime import datetime

from v1.db.models.dose import Dose
from v1.db.client import db_client
from v1.db.logic.dose import DoseHelper

router = APIRouter(prefix="/doses",
                   tags=["doses"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado."}})

@router.get("/", response_model= Optional[list[Dose]])
async def f_doses(dropper_id: Annotated[Optional[str], Query()] = None,
                  dropper_name: Annotated[Optional[str], Query()] = None,
                  application_datetime: Annotated[Optional[datetime], Query()] = None,
                  place_apply: Annotated[Optional[int], Query()] =None,
                  start: Annotated[Optional[datetime], Query()] = None,
                  end: Annotated[Optional[datetime], Query()] = None
                     ) -> Optional[list[Dose]]:
    return DoseHelper.get_doses({
        "dropper_id": dropper_id,
        "dropper_name": dropper_name,
        "application_datetime": application_datetime,
        "place_apply": place_apply,
        "start": start,
        "end": end})

@router.delete("/", response_model= HTTPStatus, status_code=status.HTTP_200_OK)
async def f_delete_dose(dose: Dose) -> Union[HTTPStatus, HTTPException]:
    if dose.dropper_id:
        if db_client.droppers.update_one({
            "_id": ObjectId(dose.dropper_id),
            "doses": {
                "$elemMatch": {
                    "application_datetime": dose.application_datetime
                    }
            }
        },
        {"$pull": {
            "doses": {
                "application_datetime": dose.application_datetime
            }
        }}).matched_count > 0:
            return HTTPStatus(status.HTTP_200_OK)

    raise HTTPException(
        status_code=status.HTTP_204_NO_CONTENT,
        detail="Dose not found. Not deleted."
    )

# index = IndexModel([("application_datetime", ASCENDING), ("dropper_id", ASCENDING)],
#                    unique=True,
#                    name="application_datetime")
# db_client.doses.create_indexes([index])