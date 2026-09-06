"""
sanctions_db.py
---------------
Mock sanctions and restricted-entity database for the BOM Compliance Screener.

Data is illustrative only. In a production system, replace with live feeds from:
  - OFAC SDN List (US Treasury)
  - BIS Entity List / Denied Persons List (US Commerce)
  - UN Security Council Consolidated List
  - EU Consolidated Financial Sanctions List
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# Sanctioned / embargoed countries (ISO country names, as commonly appear in BOM)
# ─────────────────────────────────────────────────────────────────────────────
SANCTIONED_COUNTRIES: set[str] = {
    "Iran",
    "North Korea",
    "Syria",
    "Cuba",
    "Russia",
    "Belarus",
    "Myanmar",
    "Venezuela",
    "Sudan",
    "Zimbabwe",
    "Libya",
    "Somalia",
    "Yemen",
    "Central African Republic",
    "Democratic Republic of Congo",
    "Mali",
    "Nicaragua",
    "Haiti",
}

# Alternate spellings / abbreviations that might appear in BOM files
_COUNTRY_ALIASES: dict[str, str] = {
    "dprk": "North Korea",
    "north korea": "North Korea",
    "democratic people's republic of korea": "North Korea",
    "islamic republic of iran": "Iran",
    "russian federation": "Russia",
    "republic of belarus": "Belarus",
    "burma": "Myanmar",
    "republic of cuba": "Cuba",
    "syrian arab republic": "Syria",
    "bolivarian republic of venezuela": "Venezuela",
    "republic of sudan": "Sudan",
    "republic of zimbabwe": "Zimbabwe",
    "state of libya": "Libya",
    "federal republic of somalia": "Somalia",
    "republic of yemen": "Yemen",
    "republic of mali": "Mali",
    "republic of nicaragua": "Nicaragua",
    "republic of haiti": "Haiti",
}


def _normalize_country(name: str) -> str:
    """Return canonical country name for alias lookup."""
    return _COUNTRY_ALIASES.get(name.strip().lower(), name.strip())


# ─────────────────────────────────────────────────────────────────────────────
# Restricted / Denied entities (supplier / manufacturer names)
# These are representative mock entries modelled after real list formats.
# ─────────────────────────────────────────────────────────────────────────────
RESTRICTED_ENTITIES: set[str] = {
    # Mock entries — format: "<Company> (<Country>)"
    "SinoTech Ltd",
    "TehranParts Co",
    "Pyongyang Micro",
    "Minsk Sensors",
    "DefenseParts LLC",
    "SanctionedSupply Corp",
    "Tehran Electronics",
    "Havana Components",
    "Damascus Circuits",
    "Caracas Microelectronics",
    "Kremlin Tech Solutions",
    "Khartoum Industrial",
    "Rangoon Manufacturing",
    "Nova Moskva Electronics",
    "Belarusian Defense Supplies",
    "DPRK Precision Parts",
    "Syrian Electronic Systems",
    "MyanTech Industries",
    "Cuba Electronics Corp",
    "VeneSupply SA",
    "ZimParts Ltd",
    "SomaliTech Corp",
    "SanaaTech",
    "BanguiMicro",
    "KinshasaComponents",
    "BamakoTech",
    "ManaguaTech",
    "Port-au-PrinceParts",
}

# Normalized lower-case set for fast matching
_RESTRICTED_ENTITIES_LOWER: set[str] = {e.lower() for e in RESTRICTED_ENTITIES}


def _entity_is_restricted(name: str) -> bool:
    """Case-insensitive exact or substring match against restricted entity list."""
    name_lower = name.lower().strip()
    # Exact match
    if name_lower in _RESTRICTED_ENTITIES_LOWER:
        return True
    # Substring match (catches "SinoTech Ltd (Beijing)" etc.)
    for entity in _RESTRICTED_ENTITIES_LOWER:
        if entity in name_lower or name_lower in entity:
            return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# Restricted part / component keywords (EAR / ITAR dual-use concern indicators)
# ─────────────────────────────────────────────────────────────────────────────
RESTRICTED_PART_KEYWORDS: set[str] = {
    # Munitions / military
    "military",
    "mil-spec",
    "military-grade",
    "defense",
    "defence",
    "munition",
    "ballistic",
    "warhead",
    "explosive",
    "detonator",
    # Dual-use electronics & sensing
    "radar",
    "sonar",
    "lidar",
    "infrared imaging",
    "night vision",
    "thermal imaging",
    "encryption module",
    "cryptographic",
    "secure communication",
    "jamming",
    "signal intelligence",
    "sigint",
    "electronic warfare",
    # Nuclear / chem / bio
    "nuclear",
    "radiological",
    "biological agent",
    "chemical weapon",
    "nerve agent",
    "centrifuge",
    # Aerospace / propulsion
    "rocket propellant",
    "missile guidance",
    "inertial navigation",
    "hypersonic",
    "unmanned aerial",
    "uav",
    "drone guidance",
    # Cyber / surveillance
    "intrusion software",
    "spyware",
    "surveillance system",
    "facial recognition",
}


def _part_has_restricted_keyword(part_number: str, component_name: str) -> list[str]:
    """Return list of matched restricted keywords found in part/component strings."""
    combined = (part_number + " " + component_name).lower()
    return [kw for kw in RESTRICTED_PART_KEYWORDS if kw in combined]


# ─────────────────────────────────────────────────────────────────────────────
# High-risk part number prefixes (mock EAR ECCN / ITAR controlled prefixes)
# ─────────────────────────────────────────────────────────────────────────────
_RESTRICTED_PN_PREFIXES: tuple[str, ...] = (
    "MIL-",
    "DEF-",
    "ITAR-",
    "EAR-",
    "CTRL-",
    "WPN-",
    "NUC-",
)


def _pn_has_restricted_prefix(part_number: str) -> bool:
    upper_pn = part_number.upper().strip()
    return any(upper_pn.startswith(prefix) for prefix in _RESTRICTED_PN_PREFIXES)


# ─────────────────────────────────────────────────────────────────────────────
# Main screening function
# ─────────────────────────────────────────────────────────────────────────────
def get_flags(
    part_number: str,
    component_name: str,
    supplier_name: str,
    country_of_origin: str,
) -> tuple[bool, list[str]]:
    """
    Screen a single BOM row against all sanctions lists.

    Returns
    -------
    flagged : bool
        True if one or more flags were raised.
    reasons : list[str]
        Human-readable descriptions of each flag raised.
    """
    reasons: list[str] = []

    # 1. Sanctioned country
    canonical_country = _normalize_country(country_of_origin)
    if canonical_country in SANCTIONED_COUNTRIES:
        reasons.append(f"Sanctioned country of origin: {canonical_country}")

    # 2. Restricted entity (supplier)
    if supplier_name and _entity_is_restricted(supplier_name):
        reasons.append(f"Supplier on restricted/denied entity list: {supplier_name}")

    # 3. Restricted part keywords
    matched_keywords = _part_has_restricted_keyword(part_number, component_name)
    for kw in matched_keywords:
        reasons.append(f"Component description contains controlled keyword: '{kw}'")

    # 4. Restricted part-number prefix
    if part_number and _pn_has_restricted_prefix(part_number):
        reasons.append(f"Part number prefix indicates controlled item: {part_number}")

    return bool(reasons), reasons
