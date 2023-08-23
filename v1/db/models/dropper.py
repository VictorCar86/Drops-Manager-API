from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field, validator
from pymongo import IndexModel, ASCENDING, ReturnDocument
from datetime import date, datetime, timedelta, time
from v1.db.client import db_client
from v1.db.models.dose import Dose
from v1.db.models.pyObjectId import PyObjectId
from v1.db.logic.helpers import Helper

class Dropper(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    place_apply: Optional[int] = None
    frequency: Optional[int] = None
    start_datetime: Optional[datetime] = None
    end_day: Optional[datetime] = None
    date_expiration: Optional[datetime] = None
    doses: Optional[list[Dose]] = None

    def __init__(self, **data):
        if "_id" in data and data["_id"] == "":
            del data["_id"]
        super().__init__(**data)
        self._check_db()
    # def __setattr__(self, name, value):
    #     if name == "frequency":
    #         # self.generateDoses()
    #         print(f"Seetting {name} with value {value}")
    #     super().__setattr__(name, value)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}

    def _check_db(self):
        index = IndexModel([("_id", ASCENDING), ("doses.application_datetime", ASCENDING)], 
                   unique=True,
                   name="dose_application_datetime")
        db_client.droppers.create_indexes([index])
        # db_client.droppers.drop_index(index_or_name="name_date_expiration_unique")
        # db_client.droppers.create_index("code", unique=True)

    def getDoses(self, start: datetime, end: datetime) -> Optional[list[Dose]]:
        # If doses in range date exist return it, else create it.
        if self.doses == None or len(self.doses) == 0 or max(d.application_datetime for d in self.doses) < end:
            self.generateDoses(end=end)
        return self.doses

    def generateDoses(self, end: Optional[datetime] = None, start: Optional[datetime] = None):
        if not start:
            start = self.start_datetime if self.start_datetime else datetime.combine(date.today(), time(hour=8))
        if not end:
            end = self.end_day if self.end_day else self.date_expiration if self.date_expiration else datetime.today()

        if self.frequency:
            print("### Generating doses ###")
            # Separate doses to keep
            keep_doses = list(filter(lambda dose: dose.application_datetime < start, self.doses)) if self.doses else []
            # Create doses from start to end.
            td_to_hours = lambda time_delta: time_delta.total_seconds() / (60 * 60)
            doses_in_delta = round(td_to_hours(end-start) / self.frequency)
            # print(f"start: {start}, end: {end}, frequency: {self.frequency}, td_to_hours: {round(td_to_hours(end-start))}, doses_in_delta: {doses_in_delta}")
            for i in range(doses_in_delta + 1):
                set_dose_time = lambda start, freq: start + timedelta(hours= freq * i)
                keep_doses.append(Dose(dropper_id=self.id, application_datetime= set_dose_time(start, self.frequency)))
                # print(f"set_dose_time: {set_dose_time(start, self.frequency)}, i: {i}")

            self.doses=keep_doses

            db_client.droppers.find_one_and_update(
                {"_id": ObjectId(self.id)},
                {"$set": Helper.clean_query(self.dict())},
                return_document= ReturnDocument.AFTER
                )