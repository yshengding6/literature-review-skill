"""
Feishu/Lark API Data Fetcher
Supports fetching data from Feishu bases, tables, and spreadsheets
"""

import re
import time
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse, parse_qs
from dataclasses import dataclass

try:
    import httpx
except ImportError:
    httpx = None


@dataclass
class FeishuTableData:
    """Feishu table data structure"""
    table_id: str
    name: str
    records: List[Dict[str, Any]]
    fields: List[Dict[str, Any]]
    total: int
    has_more: bool
    page_token: Optional[str] = None


@dataclass
class FeishuAPIError(Exception):
    """Base Feishu API error"""
    code: int
    msg: str


class FeishuDataFetcher:
    """Feishu/Lark data fetcher with authentication and pagination support"""

    def __init__(self, app_id: str, app_secret: str):
        """Initialize Feishu data fetcher

        Args:
            app_id: Feishu app ID
            app_secret: Feishu app secret
        """
        if not httpx:
            raise RuntimeError("httpx is required for Feishu integration")

        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = "https://open.feishu.cn/open-apis"
        self.client = httpx.Client(timeout=30.0)
        self._tenant_access_token = None
        self._token_expiry = None

    def close(self):
        """Close HTTP client"""
        if self.client:
            self.client.close()

    def _get_tenant_access_token(self) -> str:
        """Get tenant access token"""
        if self._tenant_access_token and self._token_expiry and time.time() < self._token_expiry:
            return self._tenant_access_token

        response = self.client.post(
            f"{self.base_url}/auth/v3/tenant_access_token/internal",
            json={
                "app_id": self.app_id,
                "app_secret": self.app_secret
            }
        )
        result = response.json()

        if result.get("code") != 0:
            raise FeishuAPIError(code=result.get("code"), msg=result.get("msg"))

        self._tenant_access_token = result.get("tenant_access_token")
        self._token_expiry = time.time() + result.get("expire", 3600) - 60  # Refresh 60s before expiry
        return self._tenant_access_token

    def _api_call(self, endpoint: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
        """Make authenticated API call"""
        token = self._get_tenant_access_token()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"

        if method == "GET":
            response = self.client.get(f"{self.base_url}{endpoint}", headers=headers, params=kwargs)
        elif method == "POST":
            response = self.client.post(f"{self.base_url}{endpoint}", headers=headers, json=kwargs)
        else:
            raise ValueError(f"Unsupported method: {method}")

        return response.json()

    def parse_url(self, url: str) -> Dict[str, str]:
        """Parse Feishu URL and extract resource identifiers

        Supports:
        - Base URL: https://open.feishu.cn/app/{app_id}/base/{base_id}
        - Table URL: https://open.feishu.cn/app/{app_id}/base/{base_id}/table/{table_id}
        - Spreadsheet URL: https://open.feishu.cn/sheets/{spreadsheet_token}
        """
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        query_params = parse_qs(parsed.query)

        result = {
            'app_id': None,
            'base_id': None,
            'table_id': None,
            'spreadsheet_token': None,
            'view_id': None
        }

        if 'sheets' in path_parts:
            idx = path_parts.index('sheets')
            if idx + 1 < len(path_parts):
                result['spreadsheet_token'] = path_parts[idx + 1]
        elif 'app' in path_parts and 'base' in path_parts:
            idx = path_parts.index('app')
            if idx + 1 < len(path_parts):
                result['app_id'] = path_parts[idx + 1]
            idx = path_parts.index('base')
            if idx + 1 < len(path_parts):
                result['base_id'] = path_parts[idx + 1]
            if 'table' in path_parts:
                idx = path_parts.index('table')
                if idx + 1 < len(path_parts):
                    result['table_id'] = path_parts[idx + 1]

        if 'view' in query_params:
            result['view_id'] = query_params['view'][0]

        return result

    def fetch_table_data(
        self,
        base_id: str,
        table_id: str,
        view_id: Optional[str] = None,
        page_size: int = 100,
        page_token: Optional[str] = None
    ) -> FeishuTableData:
        """Fetch table data from Feishu base"""
        params = {
            "page_size": page_size
        }
        if view_id:
            params["view_id"] = view_id
        if page_token:
            params["page_token"] = page_token

        result = self._api_call(f"/bitable/v1/apps/{base_id}/tables/{table_id}/records", **params)

        if result.get("code") != 0:
            raise FeishuAPIError(code=result.get("code"), msg=result.get("msg"))

        data = result.get("data", {})
        items = data.get("items", [])

        return FeishuTableData(
            table_id=table_id,
            name=data.get("table", {}).get("name", ""),
            records=[item.get("fields", {}) for item in items],
            fields=data.get("table", {}).get("fields", []),
            total=data.get("total", 0),
            has_more=data.get("has_more", False),
            page_token=data.get("page_token")
        )

    def fetch_records_paginated(
        self,
        base_id: str,
        table_id: str,
        view_id: Optional[str] = None,
        max_records: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Fetch all records with pagination support"""
        all_records = []
        page_token = None
        page_size = 100

        while True:
            data = self.fetch_table_data(base_id, table_id, view_id, page_size, page_token)
            all_records.extend(data.records)

            if not data.has_more or (max_records and len(all_records) >= max_records):
                break

            page_token = data.page_token

        return all_records[:max_records] if max_records else all_records

    def fetch_base_tables(self, base_id: str) -> List[Dict[str, Any]]:
        """List all tables in a Feishu base"""
        result = self._api_call(f"/bitable/v1/apps/{base_id}/tables")

        if result.get("code") != 0:
            raise FeishuAPIError(code=result.get("code"), msg=result.get("msg"))

        return result.get("data", {}).get("items", [])

    def records_to_text(self, records: List[Dict[str, Any]]) -> str:
        """Convert records to text for literature review analysis"""
        if not records:
            return ""

        text_lines = []
        for i, record in enumerate(records, 1):
            record_parts = [f"记录 {i}:"]
            for key, value in record.items():
                if value is not None:
                    record_parts.append(f"  {key}: {value}")
            text_lines.append("\n".join(record_parts))

        return "\n\n".join(text_lines)
