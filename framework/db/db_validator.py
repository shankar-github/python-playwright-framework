"""
Database validation utilities
"""
from typing import Dict, Any, Optional, List
from framework.db.db_client import DatabaseClient, MongoDBClient
from framework.core.logger import log
from framework.utils.assertions import hard_assert, AssertionError, SoftAssertions


class DatabaseValidator:
    """Validates database state and data integrity"""
    
    def __init__(self, db_client: DatabaseClient):
        self.db = db_client
    
    def assert_record_exists(
        self,
        table_name: str,
        where_clause: str,
        params: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None
    ):
        """Assert that a record exists in the table"""
        query = f"SELECT COUNT(*) FROM {table_name} WHERE {where_clause}"
        count = self.db.execute_scalar(query, params)
        
        msg = message or f"Record not found in {table_name} with condition: {where_clause}"
        hard_assert.assert_greater_than(count, 0, msg)
        log.info(f"Record exists in {table_name}")
    
    def assert_record_not_exists(
        self,
        table_name: str,
        where_clause: str,
        params: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None
    ):
        """Assert that a record does not exist in the table"""
        query = f"SELECT COUNT(*) FROM {table_name} WHERE {where_clause}"
        count = self.db.execute_scalar(query, params)
        
        msg = message or f"Record found in {table_name} with condition: {where_clause}"
        hard_assert.assert_equal(count, 0, msg)
        log.info(f"Record does not exist in {table_name}")
    
    def assert_field_value(
        self,
        table_name: str,
        field_name: str,
        expected_value: Any,
        where_clause: str,
        params: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None
    ):
        """Assert that a field has expected value"""
        query = f"SELECT {field_name} FROM {table_name} WHERE {where_clause}"
        actual_value = self.db.execute_scalar(query, params)
        
        msg = message or f"Field {field_name} value mismatch in {table_name}: expected {expected_value}, got {actual_value}"
        hard_assert.assert_equal(actual_value, expected_value, msg)
        log.info(f"Field {field_name} value assertion passed")
    
    def assert_row_count(
        self,
        table_name: str,
        expected_count: int,
        where_clause: Optional[str] = None,
        message: Optional[str] = None
    ):
        """Assert that table has expected row count"""
        actual_count = self.db.get_row_count(table_name, where_clause)
        
        msg = message or f"Row count mismatch in {table_name}: expected {expected_count}, got {actual_count}"
        hard_assert.assert_equal(actual_count, expected_count, msg)
        log.info(f"Row count assertion passed: {actual_count}")
    
    def assert_referential_integrity(
        self,
        child_table: str,
        child_fk: str,
        parent_table: str,
        parent_pk: str,
        message: Optional[str] = None
    ):
        """Assert referential integrity between tables"""
        query = f"""
            SELECT COUNT(*) 
            FROM {child_table} c
            LEFT JOIN {parent_table} p ON c.{child_fk} = p.{parent_pk}
            WHERE c.{child_fk} IS NOT NULL AND p.{parent_pk} IS NULL
        """
        orphan_count = self.db.execute_scalar(query)
        
        msg = message or f"Referential integrity violation: {orphan_count} orphan records in {child_table}"
        hard_assert.assert_equal(orphan_count, 0, msg)
        log.info(f"Referential integrity check passed for {child_table} -> {parent_table}")
    
    def get_record(self, table_name: str, where_clause: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Get a single record"""
        query = f"SELECT * FROM {table_name} WHERE {where_clause} LIMIT 1"
        results = self.db.execute_query(query, params)
        return results[0] if results else None
    
    def compare_api_response_with_db(
        self,
        api_data: Dict[str, Any],
        table_name: str,
        where_clause: str,
        field_mapping: Dict[str, str],
        params: Optional[Dict[str, Any]] = None
    ):
        """Compare API response data with database record"""
        db_record = self.get_record(table_name, where_clause, params)
        
        if not db_record:
            raise AssertionError(
                message=f"Record not found in {table_name} for comparison",
                context={"table": table_name, "where_clause": where_clause, "params": params}
            )
        
        soft_assert = SoftAssertions()
        for api_key, db_field in field_mapping.items():
            api_value = api_data.get(api_key)
            db_value = db_record.get(db_field)
            
            soft_assert.assert_equal(
                api_value,
                db_value,
                f"Field mismatch: {api_key} (API)={api_value}, {db_field} (DB)={db_value}"
            )
        
        # Raise if any soft assertions failed
        try:
            soft_assert.assert_all()
        except AssertionError as e:
            log.error(f"API-DB comparison failed: {str(e)}")
            raise
        
        log.info("API-DB comparison passed")
    
    def assert_transactional_integrity(
        self,
        operations: List[Dict[str, Any]],
        rollback_on_failure: bool = True
    ):
        """Assert transactional integrity across multiple operations
        
        Args:
            operations: List of operations to execute in transaction
            rollback_on_failure: Whether to rollback on failure
        
        Example:
            operations = [
                {"type": "insert", "table": "orders", "data": {...}},
                {"type": "update", "table": "inventory", "where": "...", "data": {...}}
            ]
        """
        from framework.db.transaction_manager import TransactionManager
        
        transaction_manager = TransactionManager(self.db)
        
        with transaction_manager.transaction(rollback_on_error=rollback_on_failure):
            for op in operations:
                op_type = op.get("type")
                table = op.get("table")
                
                if op_type == "insert":
                    # Insert operation
                    columns = ", ".join(op["data"].keys())
                    values = ", ".join([f":{k}" for k in op["data"].keys()])
                    query = f"INSERT INTO {table} ({columns}) VALUES ({values})"
                    self.db.execute_update(query, op["data"])
                    log.debug(f"Transactional insert into {table}")
                
                elif op_type == "update":
                    # Update operation
                    set_clause = ", ".join([f"{k} = :{k}" for k in op["data"].keys()])
                    query = f"UPDATE {table} SET {set_clause} WHERE {op['where']}"
                    params = {**op["data"], **op.get("params", {})}
                    self.db.execute_update(query, params)
                    log.debug(f"Transactional update in {table}")
                
                elif op_type == "delete":
                    # Delete operation
                    query = f"DELETE FROM {table} WHERE {op['where']}"
                    self.db.execute_update(query, op.get("params", {}))
                    log.debug(f"Transactional delete from {table}")
            
            log.info(f"Transactional integrity validated for {len(operations)} operations")
    
    def assert_no_concurrent_modification(
        self,
        table_name: str,
        record_id: Any,
        version_field: str = "version",
        timeout_seconds: int = 5
    ):
        """Assert that record has not been modified concurrently (optimistic locking)
        
        Args:
            table_name: Table name
            record_id: Record identifier
            version_field: Version/timestamp field name
            timeout_seconds: Timeout for check
        """
        import time

        query = f"SELECT {version_field} FROM {table_name} WHERE id = :id"
        initial_version = self.db.execute_scalar(query, {"id": record_id})

        if initial_version is None:
            raise AssertionError(
                message=f"Record {record_id} not found in {table_name}",
                context={"table": table_name, "record_id": record_id}
            )

        deadline = time.time() + timeout_seconds
        poll_interval = 0.2
        while time.time() < deadline:
            time.sleep(poll_interval)
            current_version = self.db.execute_scalar(query, {"id": record_id})
            if current_version != initial_version:
                raise AssertionError(
                    message=f"Concurrent modification detected for record {record_id} in {table_name}",
                    actual=current_version,
                    expected=initial_version,
                    context={
                        "table": table_name,
                        "record_id": record_id,
                        "version_field": version_field
                    }
                )

        log.info(f"No concurrent modification detected for record {record_id}")


class MongoDBValidator:
    """Validates MongoDB collections and documents"""
    
    def __init__(self, mongo_client: MongoDBClient):
        self.mongo = mongo_client
    
    def assert_document_exists(
        self,
        collection_name: str,
        filter: Dict[str, Any],
        message: Optional[str] = None
    ):
        """Assert that a document exists"""
        doc = self.mongo.find_one(collection_name, filter)
        
        msg = message or f"Document not found in {collection_name} with filter: {filter}"
        hard_assert.assert_is_not_none(doc, msg)
        log.info(f"Document exists in {collection_name}")
    
    def assert_document_not_exists(
        self,
        collection_name: str,
        filter: Dict[str, Any],
        message: Optional[str] = None
    ):
        """Assert that a document does not exist"""
        doc = self.mongo.find_one(collection_name, filter)
        
        msg = message or f"Document found in {collection_name} with filter: {filter}"
        hard_assert.assert_is_none(doc, msg)
        log.info(f"Document does not exist in {collection_name}")
    
    def assert_field_value(
        self,
        collection_name: str,
        field_name: str,
        expected_value: Any,
        filter: Dict[str, Any],
        message: Optional[str] = None
    ):
        """Assert that a field has expected value"""
        doc = self.mongo.find_one(collection_name, filter)
        
        if not doc:
            raise AssertionError(
                message=f"Document not found in {collection_name} with filter: {filter}",
                context={"collection": collection_name, "filter": filter}
            )
        
        actual_value = doc.get(field_name)
        msg = message or f"Field {field_name} value mismatch: expected {expected_value}, got {actual_value}"
        hard_assert.assert_equal(actual_value, expected_value, msg)
        log.info(f"Field {field_name} value assertion passed")
    
    def assert_document_count(
        self,
        collection_name: str,
        expected_count: int,
        filter: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None
    ):
        """Assert that collection has expected document count"""
        actual_count = self.mongo.count_documents(collection_name, filter)
        
        msg = message or f"Document count mismatch in {collection_name}: expected {expected_count}, got {actual_count}"
        hard_assert.assert_equal(actual_count, expected_count, msg)
        log.info(f"Document count assertion passed: {actual_count}")
