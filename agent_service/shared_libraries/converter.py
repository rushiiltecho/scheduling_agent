# Copyright 2025 Your Company
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import json
import logging
import os
import sys
from typing import Any, Dict, List

import requests

# Configure logging
logger = logging.getLogger("atlassian_adk." + __name__)
logging.basicConfig(level=logging.INFO)

class AtlassianApiFetcher:
    """
    Fetches and saves the OpenAPI (Swagger) JSON for Atlassian Cloud products.
    
    Supports:
      - jira-platform (Core REST API v3)
      - jira-software  (Software-specific REST API v3)
      - confluence     (Confluence Cloud REST API v3)
    
    Each of these endpoints publishes a full OpenAPI v3 JSON spec at a stable URL.
    """

    _ENDPOINTS: Dict[str, str] = {
        "jira-platform": "https://developer.atlassian.com/cloud/jira/platform/swagger.v3.json",
        "jira-software":  "https://developer.atlassian.com/cloud/jira/software/swagger.v3.json",
        "confluence":     "https://developer.atlassian.com/cloud/confluence/swagger.v3.json",
    }

    def __init__(self, product: str, cloud_id: str=os.getenv("JIRA_CLOUD_ID")):
        """
        Args:
            product: One of 'jira-platform', 'jira-software', or 'confluence'.
        """
        if product not in self._ENDPOINTS:
            raise ValueError(f"Unsupported product '{product}'. Choose from: {list(self._ENDPOINTS.keys())}")
        self.product = product
        self.url = self._ENDPOINTS[product]
        self._swagger_json: Dict = {}
        self.cloud_id: str = cloud_id

    def fetch_swagger(self) -> None:
        """Downloads the Swagger/OpenAPI JSON from Atlassian’s public endpoint."""
        logger.info("Fetching OpenAPI JSON for %s from %s", self.product, self.url)
        try:
            resp = requests.get(self.url, timeout=30)
            resp.raise_for_status()
            spec_json = resp.text
            self._swagger_json = json.loads(spec_json)
            logger.info("Successfully fetched spec for %s (loaded %d top‐level keys)",
                        self.product, len(self._swagger_json))
        except requests.RequestException as e:
            logger.error("Failed to fetch Swagger JSON: %s", e)
            raise

    def convert(self) -> Dict[str, Any]:
        """Convert the Google API spec to OpenAPI v3 format.

        Returns:
            Dict containing the converted OpenAPI v3 specification
        """
        if not self._swagger_json:
            self.fetch_swagger()

        return self._swagger_json

    def save_to_file(self, output_path: str) -> None:
        """Writes the downloaded OpenAPI JSON to disk."""
        if not self._swagger_json:
            raise RuntimeError("No Swagger JSON loaded; call fetch_swagger() first.")
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(self._swagger_json, f, indent=2)
            logger.info("OpenAPI spec for %s written to %s", self.product, output_path)
        except OSError as e:
            logger.error("Error saving file %s: %s", output_path, e)
            raise


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Download and save Atlassian Cloud OpenAPI (Swagger) specs for Jira or Confluence."
        )
    )
    parser.add_argument(
        "product",
        choices=["jira-platform", "jira-software", "confluence"],
        help="Which Atlassian product’s OpenAPI you want to fetch."
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output file path (e.g. './jira-platform.json'). "
             "If not provided, defaults to '<product>-openapi.json'."
    )

    args = parser.parse_args()

    out_path = args.output or f"{args.product}-openapi.json"
    fetcher = AtlassianApiFetcher(args.product)

    try:
        fetcher.fetch_swagger()
        fetcher.save_to_file(out_path)
        print(f"Successfully downloaded {args.product} OpenAPI spec → {out_path}")
    except Exception as exc:
        logger.error("Operation failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
