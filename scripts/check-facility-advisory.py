"""Offline regression checks for facility type codes and fertilizer advisory examples."""
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

SCHEMA = Path(__file__).resolve().parents[1] / "schema"


def validator(pack, version, pointer):
    registry = Registry()
    for name in {"AgricultureResource", pack}:
        file = SCHEMA / name / version / "attributes.yaml"
        resource = Resource.from_contents(yaml.safe_load(file.read_text()), default_specification=DRAFT202012)
        registry = registry.with_resource(file.as_uri(), resource)
    uri = (SCHEMA / pack / version / "attributes.yaml").as_uri()
    return Draft202012Validator({"$ref": uri + "#/components/schemas/" + pointer},
                                registry=registry, format_checker=FormatChecker())


if __name__ == "__main__":
    facility_dir = SCHEMA / "AgricultureFacility" / "v0.2" / "examples"
    direct = json.loads((facility_dir / "seed-processing-centre.json").read_text())
    offered = json.loads((facility_dir / "on-demand-facility-discovery.json").read_text())
    code = direct["facilityType"]
    assert code in offered["supportedFacilityTypes"]
    # Keep this regression offline: geography brings in external Beckn schemas
    # unrelated to the code field. Test the offer without its optional coverage.
    validator("AgricultureFacility", "v0.2", "AgricultureFacility").validate(
        {key: value for key, value in offered.items() if key != "coverageAreas"})
    for field in ("facilityType", "supportedFacilityTypes/items"):
        v = validator("AgricultureFacility", "v0.2", "AgricultureFacility/allOf/1/properties/" + field)
        for valid in [code, "Warehouse", "https://another.example/facility-types#composting-site"]:
            v.validate(valid)
        for invalid in ["", "UnqualifiedKind", "https://", "https://a b", 123, {"type": code}]:
            assert not v.is_valid(invalid), invalid
    legacy = validator("AgricultureFacility", "v0.1", "FacilityType")
    legacy.validate("Warehouse")
    assert not legacy.is_valid(code)
    pack = "AgricultureAdvisory"
    advisory = validator(pack, "v0.2", pack)
    examples = SCHEMA / pack / "v0.2/examples"
    for mode in ("direct", "on-demand"):
        file = examples / f"{mode}-fertilizer-advice.json"
        advisory.validate(json.loads(file.read_text()))
    weather = json.loads((examples / "on-demand-weather-advisory.json").read_text())
    # Check local mode rules offline; external geometry and descriptor schemas
    # are validated separately for complete example validation.
    weather.pop("coverageAreas", None)
    advisory.validate(weather)
    for missing in ["weatherInformed", "supportedWeatherParameters", "geographicGranularities"]:
        assert not advisory.is_valid({k: v for k, v in weather.items() if k != missing})
    assert not advisory.is_valid({**weather, "subjectCategories": ["Crop"]})
    general = json.loads((examples / "direct-fertilizer-advice.json").read_text())
    assert advisory.is_valid({**general, "subjectCategories": ["Weather"]})
    assert not advisory.is_valid({**general, "weatherInformed": True, "subjectCategories": ["Weather"]})
    # These weather-only constraints can be tested without fetching a Location.
    rules = yaml.safe_load((examples.parent / "attributes.yaml").read_text())["components"]["schemas"][pack]["allOf"]
    weather_direct = next(i for i, rule in enumerate(rules)
                          if rule.get("if", {}).get("properties") ==
                          {"weatherInformed": {"const": True}, "informationMode": {"const": "Direct"}})
    check = validator(pack, "v0.2", f"{pack}/allOf/{weather_direct}")
    direct = json.loads((examples / "district-village-advisory.json").read_text())
    check.validate(direct)
    for missing in ["location", "validity", "weatherBasis"]:
        assert not check.is_valid({k: v for k, v in direct.items() if k != missing})
    assert not check.is_valid({**direct, "validity": {"startsAt": direct["validity"]["startsAt"]}})
    print("Facility type compatibility and general/weather AgricultureAdvisory mode checks passed.")
