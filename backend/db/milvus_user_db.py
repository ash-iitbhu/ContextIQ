from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from ..config import DB_HOST, DB_PORT, DB_NAME, DB_USER_COLLECTION

class MilvusUserDB:
    def __init__(self, host=DB_HOST, port=DB_PORT, db_name=DB_NAME, user_collection_name=DB_USER_COLLECTION):
        self.db_name = db_name
        self.host = host
        self.port = port
        self.collection_name = user_collection_name
        self.user_collection = None
        self.connect()
        self.setup_collection()

    def connect(self):
        connections.connect(self.db_name, host=self.host, port=self.port)

    def setup_collection(self):
        if not utility.has_collection(self.collection_name):
            user_fields = [
                FieldSchema(name="username", dtype=DataType.VARCHAR, max_length=64, is_primary=True, auto_id=False),
                FieldSchema(name="password_hash", dtype=DataType.VARCHAR, max_length=128),
                FieldSchema(name="user_vector", dtype=DataType.FLOAT_VECTOR, dim=2)
            ]
            user_schema = CollectionSchema(fields=user_fields, description="User collection")
            self.user_collection = Collection(self.collection_name, user_schema, consistency_level="Strong")
            self.user_collection.create_index(
                field_name="username",
                index_params={"index_type": "AUTOINDEX", "metric_type": "NONE"}
            )
            self.user_collection.create_index(
                field_name="user_vector",
                index_params={"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 128}}
            )
        else:
            self.user_collection = Collection(self.collection_name)
        self.user_collection.load()

    def user_exists(self, username):
        expr = f"username == '{username}'"
        result = self.user_collection.query(expr, output_fields=["username"])
        return bool(result)

    def insert_user(self, username, password_hash):
        self.user_collection.insert([[username], [password_hash], [[0.0, 0.0]]])

    def get_password_hash(self, username):
        expr = f"username == '{username}'"
        result = self.user_collection.query(expr, output_fields=["password_hash"])
        if result:
            return result[0]["password_hash"]
        return None
