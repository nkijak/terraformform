from copy import deepcopy
import logging
from typing import Tuple
import motor.motor_asyncio  # type: ignore
from pymongo import MongoClient
from bson.objectid import ObjectId


log = logging.getLogger(__name__)


class MongoService:
    def __init__(self, connectionstring: str, db: str):
        self.__client = motor.motor_asyncio.AsyncIOMotorClient(connectionstring)[db]

    async def upsert(self, collection: str, doc: dict) -> Tuple[dict, bool]:
        if "id" in doc:
            doc["_id"] = ObjectId(id)
            result = await self.__client[collection].replace_one(
                {"_id": doc["_id"]}, doc, upsert=True
            )
            return doc, result.matched_count == 0
        else:
            log.info("creating a new record...")
            result = await self.__client[collection].insert_one(doc)
            retval = deepcopy(doc)
            retval["id"] = str(result.inserted_id)
            del retval["_id"]
            return retval, True

    async def get(self, collection, id):
        return await self.__client[collection].find_one({"_id": {"$eq": id}})


from opentelemetry.instrumentation.pymongo import PymongoInstrumentor


class BlockingMongoService:
    def __init__(self, connectionstring: str, db: str):
        PymongoInstrumentor().instrument(capture_statement=True)
        self.__client = MongoClient(connectionstring)[db]

    def upsert(self, collection: str, doc: dict) -> Tuple[dict, bool]:
        if "id" in doc:
            _id = doc.pop("id")
            doc["_id"] = _id
            result = self.__client[collection].replace_one(
                {"_id": doc["_id"]}, doc, upsert=True
            )
            return doc, result.matched_count == 0
        else:
            log.info("creating a new record...")
            result = self.__client[collection].insert_one(doc)
            retval = deepcopy(doc)
            retval["id"] = str(result.inserted_id)
            del retval["_id"]
            return retval, True

    def get(self, collection, _id):
        if item := self.__client[collection].find_one({"_id": ObjectId(_id)}):
            _id = item.pop("_id")
            item["id"] = str(_id)
            return item
        return None

    def list(self, collection):
        return self.__client[collection].find()
