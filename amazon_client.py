"""Amazon Product Advertising API v5 client.

This client intentionally uses Amazon's official API instead of HTML scraping
so it remains compliant and less likely to get blocked.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class AmazonCredentials:
    access_key: str
    secret_key: str
    partner_tag: str
    host: str = "webservices.amazon.com"
    region: str = "us-east-1"


class AmazonPaApiError(RuntimeError):
    """Raised when PA-API request fails."""


class AmazonPaApiClient:
    def __init__(self, credentials: AmazonCredentials, timeout_seconds: int = 15) -> None:
        self.credentials = credentials
        self.timeout_seconds = timeout_seconds
        self.endpoint = f"https://{credentials.host}/paapi5/searchitems"
        self.service = "ProductAdvertisingAPI"

    def search_items(self, keywords: str, marketplace: str = "www.amazon.com", limit: int = 5) -> list[dict[str, Any]]:
        payload: dict[str, Any] = {
            "Keywords": keywords,
            "Resources": [
                "ItemInfo.Title",
                "Offers.Listings.Price",
                "Images.Primary.Medium",
                "DetailPageURL",
            ],
            "PartnerTag": self.credentials.partner_tag,
            "PartnerType": "Associates",
            "Marketplace": marketplace,
            "ItemCount": max(1, min(limit, 10)),
        }

        headers = self._signed_headers(payload)
        response = requests.post(
            self.endpoint,
            headers=headers,
            data=json.dumps(payload),
            timeout=self.timeout_seconds,
        )

        if response.status_code != 200:
            raise AmazonPaApiError(f"PA-API HTTP {response.status_code}: {response.text[:300]}")

        data = response.json()
        if data.get("Errors"):
            raise AmazonPaApiError(str(data["Errors"]))

        items = data.get("SearchResult", {}).get("Items", [])
        result: list[dict[str, Any]] = []
        for item in items:
            title = item.get("ItemInfo", {}).get("Title", {}).get("DisplayValue", "Bilinmeyen ürün")
            detail_url = item.get("DetailPageURL", "")
            image_url = item.get("Images", {}).get("Primary", {}).get("Medium", {}).get("URL", "")

            price_info = (
                item.get("Offers", {})
                .get("Listings", [{}])[0]
                .get("Price", {})
            )
            price_text = price_info.get("DisplayAmount", "Fiyat bulunamadı")

            result.append(
                {
                    "title": title,
                    "price": price_text,
                    "url": detail_url,
                    "image": image_url,
                }
            )
        return result

    def _signed_headers(self, payload: dict[str, Any]) -> dict[str, str]:
        t = dt.datetime.now(dt.timezone.utc)
        amz_date = t.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = t.strftime("%Y%m%d")

        canonical_uri = "/paapi5/searchitems"
        canonical_querystring = ""
        content_encoding = "amz-1.0"
        content_type = "application/json; charset=utf-8"
        host = self.credentials.host

        payload_json = json.dumps(payload)
        payload_hash = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()

        canonical_headers = (
            f"content-encoding:{content_encoding}\n"
            f"content-type:{content_type}\n"
            f"host:{host}\n"
            f"x-amz-date:{amz_date}\n"
            f"x-amz-target:com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems\n"
        )
        signed_headers = "content-encoding;content-type;host;x-amz-date;x-amz-target"

        canonical_request = (
            f"POST\n{canonical_uri}\n{canonical_querystring}\n"
            f"{canonical_headers}\n{signed_headers}\n{payload_hash}"
        )

        algorithm = "AWS4-HMAC-SHA256"
        credential_scope = f"{date_stamp}/{self.credentials.region}/{self.service}/aws4_request"
        string_to_sign = (
            f"{algorithm}\n{amz_date}\n{credential_scope}\n"
            f"{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
        )

        signing_key = self._get_signature_key(
            self.credentials.secret_key,
            date_stamp,
            self.credentials.region,
            self.service,
        )
        signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

        authorization_header = (
            f"{algorithm} Credential={self.credentials.access_key}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, Signature={signature}"
        )

        return {
            "Content-Encoding": content_encoding,
            "Content-Type": content_type,
            "Host": host,
            "X-Amz-Date": amz_date,
            "X-Amz-Target": "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems",
            "Authorization": authorization_header,
        }

    @staticmethod
    def _sign(key: bytes, msg: str) -> bytes:
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def _get_signature_key(self, key: str, date_stamp: str, region_name: str, service_name: str) -> bytes:
        k_date = self._sign(("AWS4" + key).encode("utf-8"), date_stamp)
        k_region = self._sign(k_date, region_name)
        k_service = self._sign(k_region, service_name)
        return self._sign(k_service, "aws4_request")
