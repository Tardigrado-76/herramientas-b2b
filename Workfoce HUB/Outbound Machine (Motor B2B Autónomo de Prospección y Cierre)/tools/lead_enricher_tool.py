"""Lead Enrichment and Corporate Profile Builder Tool.
Normalizes company entities, infers corporate domains, and synthesizes OSINT intelligence.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from pydantic import Field

from .base import BaseTool


class LeadEnricherTool(BaseTool):
    """Enriches company information, cleans legal suffixes, and builds qualified contact profiles."""

    company_raw_name: str = Field(..., description="Raw company name (e.g., 'Acme Logistics S.L.')")
    website_url: Optional[str] = Field(None, description="Website URL or domain if available")
    known_contact_name: Optional[str] = Field(None, description="Name of contact person if known")
    notes_or_scraped_snippet: Optional[str] = Field(None, description="Scraped description or notes about company operations")

    def run(self) -> Dict[str, Any]:
        # 1. Clean company name (remove legal forms like S.L., S.A., etc.)
        legal_suffix_pattern = re.compile(
            r"\b(s\.?l\.?u\.?|s\.?l\.?|s\.?a\.?|s\.?c\.?p\.?|inc\.?|corp\.?|llc|gmbh|ltd\.?)\b",
            re.IGNORECASE,
        )
        clean_name = legal_suffix_pattern.sub("", self.company_raw_name).strip()
        clean_name = re.sub(r"[\-–,\.]+$", "", clean_name).strip()

        # 2. Extract or infer domain
        domain = ""
        if self.website_url:
            clean_url = self.website_url.lower().replace("https://", "").replace("http://", "").replace("www.", "")
            domain = clean_url.split("/")[0].strip()
        else:
            # Infer plausible slug domain
            slug = re.sub(r"[^a-zA-Z0-9]+", "", clean_name.lower())
            domain = f"{slug}.es"

        # 3. Detect tech stack hints from notes/snippet
        detected_tech = []
        if self.notes_or_scraped_snippet:
            snippet = self.notes_or_scraped_snippet.lower()
            keywords = {
                "Shopify": "ecommerce",
                "WooCommerce": "wordpress ecommerce",
                "WordPress": "cms",
                "Salesforce": "crm",
                "SAP": "enterprise erp",
                "AWS": "cloud infrastructure",
                "Azure": "cloud infrastructure",
                "Python": "data/backend",
                "React": "modern frontend",
                "Next.js": "modern web",
            }
            for kw, desc in keywords.items():
                if kw.lower() in snippet:
                    detected_tech.append(f"{kw} ({desc})")

        # 4. Generate likely corporate email formats
        inferred_emails = [
            f"contacto@{domain}",
            f"info@{domain}",
            f"direccion@{domain}",
        ]
        if self.known_contact_name:
            parts = self.known_contact_name.lower().split()
            first = re.sub(r"[^a-z]", "", parts[0])
            last = re.sub(r"[^a-z]", "", parts[-1]) if len(parts) > 1 else ""
            if last:
                inferred_emails.insert(0, f"{first}.{last}@{domain}")
                inferred_emails.insert(1, f"{first[0]}{last}@{domain}")

        return {
            "clean_company_name": clean_name or self.company_raw_name,
            "corporate_domain": domain,
            "detected_tech_stack": detected_tech,
            "inferred_email_patterns": inferred_emails,
            "has_dedicated_domain": bool(self.website_url and "." in domain),
        }
