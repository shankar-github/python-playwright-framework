"""
Database client supporting PostgreSQL, MySQL, and MongoDB
"""
from typing import Optional, Dict, Any, List
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from pymongo import MongoClient
from framework.core.config_manager import config
from framework.core.logger import log
from contextlib import contextmanager


class DatabaseClient:
    """Database client for SQL databases"""
    
    def __init__(
        self,
        db_type: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        self.db_type = db_type or config.db.db_type
        self.host = host or config.db.db_host
        self.port = port or config.db.db_port
        self.database = database or config.db.db_name
        self.username = username or config.db.db_user
        self.password = password or config.db.db_password
        
        self.engine = None
        self.SessionLocal = None
        self._connect()
    
    def _build_connection_string(self) -> str:
        """Build database connection string
        
        SECURITY: Never log the full connection string as it contains passwords
        """
        if not self.password:
            raise ValueError("Database password is required. Set DB_PASSWORD environment variable.")
        
        if self.db_type == "postgresql":
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.db_type == "mysql":
            return f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def _connect(self):
        """Create database connection with retry logic for transient failures"""
        from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
        from sqlalchemy.exc import OperationalError, DisconnectionError
        
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type((OperationalError, DisconnectionError)),
            reraise=True
        )
        def _create_connection():
            connection_string = self._build_connection_string()
            # Don't log full connection string (security)
            log.info(f"Connecting to {self.db_type} database: {self.database} at {self.host}:{self.port}")
            
            self.engine = create_engine(
                connection_string,
                poolclass=NullPool,  # No connection pooling for tests
                echo=False
            )
            self.SessionLocal = sessionmaker(bind=self.engine)
            log.info(f"Connected to {self.db_type} database: {self.database}")
        
        try:
            _create_connection()
        except Exception as e:
            log.error(f"Failed to connect to database after retries: {str(e)}")
            raise
    
    @contextmanager
    def get_session(self):
        """Get database session context manager"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results"""
        log.debug(f"Executing query: {query}")
        if params:
            log.debug(f"Query params: {params}")
        
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            rows = result.fetchall()
            
            # Convert to list of dicts
            columns = result.keys()
            return [dict(zip(columns, row)) for row in rows]
    
    def execute_update(self, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        """Execute UPDATE/INSERT/DELETE query and return affected rows"""
        log.debug(f"Executing update: {query}")
        if params:
            log.debug(f"Query params: {params}")
        
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            session.commit()
            return result.rowcount
    
    def execute_scalar(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute query and return single scalar value"""
        log.debug(f"Executing scalar query: {query}")
        
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            return result.scalar()
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists"""
        inspector = inspect(self.engine)
        return table_name in inspector.get_table_names()
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """Get column names for a table"""
        inspector = inspect(self.engine)
        columns = inspector.get_columns(table_name)
        return [col['name'] for col in columns]
    
    def get_row_count(self, table_name: str, where_clause: Optional[str] = None) -> int:
        """Get row count for a table"""
        query = f"SELECT COUNT(*) FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        return self.execute_scalar(query)
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            log.info("Database connection closed")


class MongoDBClient:
    """MongoDB client"""
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        self.host = host or config.db.mongo_host
        self.port = port or config.db.mongo_port
        self.database = database or config.db.mongo_db
        self.username = username or config.db.mongo_user
        self.password = password or config.db.mongo_password
        
        self._connect()
    
    def _connect(self):
        """Create MongoDB connection with retry logic"""
        from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
        from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
        
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type((ServerSelectionTimeoutError, ConnectionFailure)),
            reraise=True
        )
        def _create_mongo_connection():
            # Don't log full connection string (security)
            log.info(f"Connecting to MongoDB: {self.database} at {self.host}:{self.port}")
            
            if self.username and self.password:
                connection_string = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}"
            else:
                connection_string = f"mongodb://{self.host}:{self.port}"
            
            self.client = MongoClient(connection_string)
            self.db = self.client[self.database]
            log.info(f"Connected to MongoDB: {self.database}")
        
        try:
            _create_mongo_connection()
        except Exception as e:
            log.error(f"Failed to connect to MongoDB after retries: {str(e)}")
            raise
    
    def get_collection(self, collection_name: str):
        """Get collection object"""
        return self.db[collection_name]
    
    def find_one(self, collection_name: str, filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find one document"""
        log.debug(f"Finding document in {collection_name} with filter: {filter}")
        return self.get_collection(collection_name).find_one(filter)
    
    def find_many(self, collection_name: str, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Find multiple documents"""
        log.debug(f"Finding documents in {collection_name} with filter: {filter}")
        cursor = self.get_collection(collection_name).find(filter or {})
        return list(cursor)
    
    def insert_one(self, collection_name: str, document: Dict[str, Any]) -> str:
        """Insert one document"""
        log.debug(f"Inserting document into {collection_name}")
        result = self.get_collection(collection_name).insert_one(document)
        return str(result.inserted_id)
    
    def insert_many(self, collection_name: str, documents: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple documents"""
        log.debug(f"Inserting {len(documents)} documents into {collection_name}")
        result = self.get_collection(collection_name).insert_many(documents)
        return [str(id) for id in result.inserted_ids]
    
    def update_one(self, collection_name: str, filter: Dict[str, Any], update: Dict[str, Any]) -> int:
        """Update one document"""
        log.debug(f"Updating document in {collection_name}")
        result = self.get_collection(collection_name).update_one(filter, {"$set": update})
        return result.modified_count
    
    def delete_one(self, collection_name: str, filter: Dict[str, Any]) -> int:
        """Delete one document"""
        log.debug(f"Deleting document from {collection_name}")
        result = self.get_collection(collection_name).delete_one(filter)
        return result.deleted_count
    
    def count_documents(self, collection_name: str, filter: Optional[Dict[str, Any]] = None) -> int:
        """Count documents"""
        return self.get_collection(collection_name).count_documents(filter or {})
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            log.info("MongoDB connection closed")
