import requests
import yaml
from typing import List, Dict, Optional
from ..data.mock_data import MOCK_ORGANIZATION_DATA, MOCK_SEARCH_RESULTS


class ProPublicaClient:
    def __init__(self, config_path: str):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        self.base_url = config["propublica"]["base_url"]
        self.timeout = config["propublica"]["timeout"]
        
        global_mock = config.get("mock_mode", False)
        service_mock = config["propublica"].get("mock_mode", False)
        self.mock_mode = global_mock or service_mock
    
    def search_organizations(self, query: str) -> List[Dict]:
        if self.mock_mode:
            return self._mock_search(query)
        
        url = f"{self.base_url}/search.json"
        response = requests.get(url, params={"q": query}, timeout=self.timeout)
        response.raise_for_status()
        return response.json().get("organizations", [])
    
    def get_organization(self, ein: str) -> Dict:
        if self.mock_mode:
            return self._mock_organization(ein)
        
        url = f"{self.base_url}/organizations/{ein}.json"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def get_all_filings(self, ein: str) -> List[Dict]:
        if self.mock_mode:
            return self._mock_filings(ein)
        
        org_data = self.get_organization(ein)
        return org_data.get("filings", [])
    
    def _mock_search(self, query: str) -> List[Dict]:
        query_lower = query.lower()
        for search_term, results in MOCK_SEARCH_RESULTS.items():
            if search_term in query_lower:
                return results
        return []
    
    def _mock_organization(self, ein: str) -> Dict:
        if ein in MOCK_ORGANIZATION_DATA:
            return MOCK_ORGANIZATION_DATA[ein]
        return {"name": f"Mock Organization {ein}", "ein": ein, "filings": []}
    
    def _mock_filings(self, ein: str) -> List[Dict]:
        if ein in MOCK_ORGANIZATION_DATA:
            return MOCK_ORGANIZATION_DATA[ein]["filings"]
        return []