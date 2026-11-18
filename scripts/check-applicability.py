#!/usr/bin/env python3
"""Validate complete preview fixtures and demonstrate three-valued filtering.

This is a reference matcher for review, not a deployed discovery implementation.
"""
import json
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT=Path(__file__).resolve().parents[1]
BASE='https://openagrinet.github.io/network-specs/'


def conjunction(values):
    return False if False in values else None if None in values else True


def matches(conditions, facts):
    """None means unknown. Caller supplies facts for the same crop cycle."""
    if conditions is None:
        return None
    outcomes=[]
    for condition in conditions:
        values=[]
        for key, expected in condition.items():
            actual=facts.get(key)
            if key=='extensions':
                values.append(None)
            elif key=='relativeTiming':
                lo,hi=expected.get('fromDays'),expected.get('toDays')
                if lo is not None and hi is not None and lo>hi:
                    raise ValueError('Reversed day bounds')
                if actual is None or actual.get('event')!=expected['event'] or actual.get('days') is None:
                    values.append(None)
                else:
                    age=actual['days']
                    values.append((lo is None or age>=lo) and (hi is None or age<=hi))
            elif actual is None:
                values.append(None)
            elif key in ('seasons','growthStages'):
                identity=lambda value:(value['codeSystem'],value['code'])
                values.append(identity(actual) in [identity(value) for value in expected])
            else:
                values.append(actual in expected)
        outcomes.append(conjunction(values))
    return True if True in outcomes else None if None in outcomes else False


def main():
    registry=Registry()
    for path in ROOT.glob('schema/*/v0.1/attributes.yaml'):
        registry=registry.with_resource(BASE+str(path.relative_to(ROOT)),
            Resource.from_contents(yaml.safe_load(path.read_text()),default_specification=DRAFT202012))
    advisory=Draft202012Validator({'$ref':BASE+'schema/KnowledgeAdvisory/v0.1/attributes.yaml#/components/schemas/KnowledgeAdvisory'},
        registry=registry,format_checker=FormatChecker())
    count=0
    for path in ROOT.glob('schema/KnowledgeAdvisory/v0.1/examples/applicability-*.json'):
        data=json.loads(path.read_text()); advisory.validate(data); count+=1
        for condition in data.get('applicability',[]):
            window=condition.get('relativeTiming',{})
            assert window.get('fromDays',0)<=window.get('toDays',float('inf'))
    applicability=Draft202012Validator({'$ref':BASE+'schema/AgricultureResource/v0.1/attributes.yaml#/components/schemas/AgriculturalApplicability'},
        registry=registry,format_checker=FormatChecker())
    for invalid in [[],[{}],[{'relativeTiming':{'event':'Sowing'}}],
                    [{'relativeTiming':{'event':'Sowing','fromDays':-1}}],
                    [{'relativeTiming':{'event':'Sowing','fromDays':True}}],
                    [{'relativeTiming':{'event':'Unknown','toDays':5}}],
                    [{'extensions':{'plainKey':'value'}}],[{'seasons':[{'code':'Kharif'}]}]]:
        assert not applicability.is_valid(invalid), invalid; count+=1
    condition=[{'relativeTiming':{'event':'Sowing','fromDays':20,'toDays':30}}]
    for age,expected in [(19,False),(20,True),(25,True),(30,True),(31,False)]:
        assert matches(condition,{'relativeTiming':{'event':'Sowing','days':age}}) is expected; count+=1
    assert matches(condition,{}) is None; count+=1
    assert matches(condition,{'relativeTiming':{'event':'Transplanting','days':25}}) is None; count+=1
    assert matches([{'extensions':{'https://example.org/soil':'x'}}],{}) is None; count+=1
    season=lambda code:{'codeSystem':'https://example.org/seasons','code':code}
    alternatives=[{'subjectIds':['cotton'],'seasons':[season('Kharif')]},
                  {'subjectIds':['wheat'],'seasons':[season('Rabi')]}]
    assert matches(alternatives,{'subjectIds':'cotton','seasons':season('Kharif')}) is True; count+=1
    assert matches(alternatives,{'subjectIds':'cotton','seasons':season('Rabi')}) is False; count+=1
    assert conjunction([True,None]) is None; count+=1
    assert conjunction([False,True]) is False; count+=1
    try:
        matches([{'relativeTiming':{'event':'Sowing','fromDays':30,'toDays':20}}],{})
    except ValueError:
        count+=1
    else:
        raise AssertionError('Reversed interval accepted')
    print(f'{count} applicability checks passed, including seven complete Resource-attributes examples. No consumer integration tested.')


if __name__=='__main__':
    main()
