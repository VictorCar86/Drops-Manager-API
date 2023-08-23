from typing import Optional
from v1.db.client import db_client
from v1.db.models.dose import Dose
from v1.db.logic.helpers import Helper

class DoseHelper(Helper):
    @classmethod
    def get_doses(cls, dict_url: dict) -> Optional[list[Dose]]:
        """
        Search doses in database.
        Params considered: dropper_id, dropper_name, application_datetime, start, end
        """
        dict_url = cls.clean_query(dict_url)
        query = {
            "$unwind": "$doses",
            "$match": {},
            "$project": {"_id": 0, "doses": 1}
        }
        if "dropper_id" in dict_url:
            query["$match"].update({"doses.dropper_id": dict_url["dropper_id"]})
        if "dropper_name" in dict_url and dict_url["dropper_name"]:
            query["$match"].update({"name": dict_url["dropper_name"]})
        if "application_datetime" in dict_url:
            query["$match"].update({"doses.application_datetime": dict_url["application_datetime"]})
        if "place_apply" in dict_url:
            query["$match"].update({"$or": [
                {"place_apply": dict_url["place_apply"]},
                {"place_apply": 3},
                ]})
        if "end" in dict_url or "start" in dict_url:
            query["$match"].update({"doses.application_datetime": {}})
            if "start" in dict_url:
                query["$match"]["doses.application_datetime"].update({"$gte": dict_url["start"]})
            if "end" in dict_url:
                query["$match"]["doses.application_datetime"].update({"$lte": dict_url["end"]})
        doses_db = db_client.droppers.aggregate([{k: v} for k,v in query.items()])
        return [Dose.parse_obj(dose_db["doses"]) for dose_db in doses_db] if doses_db else None