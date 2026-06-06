"""
GraphQL client with query execution and validation
"""
from typing import Dict, Any, Optional
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from framework.core.config_manager import config
from framework.core.logger import log
from framework.utils.redact import redact_payload, redact_headers
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from requests.exceptions import RequestException, HTTPError


class GraphQLClient:
    """GraphQL API client"""
    
    def __init__(self, endpoint: Optional[str] = None, headers: Optional[Dict[str, str]] = None):
        self.endpoint = endpoint or config.api.graphql_endpoint
        self.headers = headers or {}
        self._fetch_schema = config.api.graphql_fetch_schema
        self._build_client()
        log.info(f"GraphQL client initialized for {self.endpoint}")
        if self.headers:
            log.debug(f"GraphQL headers: {redact_headers(self.headers)}")
    
    def _build_client(self):
        transport = RequestsHTTPTransport(
            url=self.endpoint,
            headers=self.headers,
            use_json=True,
        )
        self.client = Client(
            transport=transport,
            fetch_schema_from_transport=self._fetch_schema,
        )
    
    def set_header(self, key: str, value: str):
        """Set header"""
        self.headers[key] = value
        self._build_client()
    
    def set_auth(self, token: str):
        """Set Bearer token authentication"""
        self.set_header("Authorization", f"Bearer {token}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((RequestException, HTTPError)),
        reraise=True
    )
    def execute_query(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute GraphQL query - safe to retry (read-only)"""
        log.info(f"Executing GraphQL query: {operation_name or 'unnamed'}")
        log.debug(f"Query: {query}")
        if variables:
            log.debug(f"Variables: {redact_payload(variables)}")
        
        try:
            gql_query = gql(query)
            result = self.client.execute(
                gql_query,
                variable_values=variables,
                operation_name=operation_name
            )
            log.info("GraphQL query executed successfully")
            log.debug(f"Result: {redact_payload(result)}")
            return result
        except Exception as e:
            log.error(f"GraphQL query failed: {str(e)}")
            raise
    
    def execute_mutation(
        self,
        mutation: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute GraphQL mutation - NOT retried to prevent duplicate operations"""
        log.info(f"Executing GraphQL mutation: {operation_name or 'unnamed'}")
        log.debug(f"Mutation: {mutation}")
        if variables:
            log.debug(f"Variables: {redact_payload(variables)}")
        
        try:
            gql_mutation = gql(mutation)
            result = self.client.execute(
                gql_mutation,
                variable_values=variables,
                operation_name=operation_name
            )
            log.info("GraphQL mutation executed successfully")
            log.debug(f"Result: {redact_payload(result)}")
            return result
        except Exception as e:
            log.error(f"GraphQL mutation failed: {str(e)}")
            raise
    
    def validate_schema(self, query: str) -> bool:
        """Validate GraphQL query syntax (schema validation requires a live schema)."""
        try:
            gql(query)
            return True
        except Exception as e:
            log.error(f"Query syntax validation failed: {str(e)}")
            return False
