#!/usr/bin/env python3
"""Maintain shared applicability metadata and synthetic complete examples."""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]/'schema'
def read(p):
    return json.loads(p.read_text())
def write(p, d):
    p.write_text(json.dumps(d, indent=2)+'\n')

terms = {'applicability':'Alternative condition sets; fields within one set apply together.',
         'subjectIds':'Governed subjects for one condition.', 'seasons':'Regional season references.',
         'growthStages':'Observed developmental stage references.', 'relativeTiming':'Inclusive days since a named event.',
         'event':'Event used as day zero.', 'fromDays':'Inclusive lower day bound.', 'toDays':'Inclusive upper day bound.',
         'establishmentMethods':'Direct seeding or transplanting.', 'waterRegimes':'Rainfed or irrigated.',
         'extensions':'Provider-owned restrictions; unknown qualifiers cannot be ignored.',
         'codeSystem':'Versioned vocabulary URI.', 'agronomicCode':'Code within a vocabulary.', 'agronomicLabel':'Display label.'}
base=ROOT/'AgricultureResource/v0.1'
context=read(base/'context.jsonld'); mapping=context['@context'][-1]
mapping.update({term:'openagrinet:'+term for term in terms})
for term in ('applicability','establishmentMethods','waterRegimes'):
    mapping[term]={'@id':'openagrinet:'+term,'@container':'@set'}
mapping['subjectIds']={'@id':'openagrinet:subjectIds','@container':'@set','@type':'@id'}
for term in ('seasons','growthStages'):
    mapping[term]={'@id':'openagrinet:'+term,'@container':'@set','@context':{
        'codeSystem':{'@id':'openagrinet:codeSystem','@type':'@id'},'code':'openagrinet:agronomicCode','label':'openagrinet:agronomicLabel'}}
mapping['extensions']={'@id':'openagrinet:extensions','@type':'@json'}
write(base/'context.jsonld',context)
vocab=read(base/'vocab.jsonld'); existing={x['@id'] for x in vocab['@graph']}
for term,description in terms.items():
    if 'openagrinet:'+term not in existing:
        vocab['@graph'].append({'@id':'openagrinet:'+term,'@type':'rdfs:Property','rdfs:label':term,'rdfs:comment':description})
write(base/'vocab.jsonld',vocab)
suffixes=['subjectIds[]','seasons[].codeSystem','seasons[].code','growthStages[].codeSystem','growthStages[].code',
          'relativeTiming.event','relativeTiming.fromDays','relativeTiming.toDays','establishmentMethods[]','waterRegimes[]']
for p in ROOT.glob('*/v0.1/profile.json'):
    pack=p.parent.parent.name
    if pack in ('Grievance','SchemeApplication'): continue
    d=read(p); prefixes=['beckn:resourceAttributes.applicability[]']
    if pack in ('KnowledgeAdvisory','WeatherAdvisory'): prefixes+=['beckn:resourceAttributes.recommendations[].applicability[]']
    for key in ('filterable_paths','indexable_paths'):
        d[key]=list(dict.fromkeys(d.get(key,[])+[prefix+'.'+suffix for prefix in prefixes for suffix in suffixes]))
    d['applicability_filtering']={'status':'consumer-review','correlation':'Predicates must match within one applicability entry.',
        'relative_timing':'Matching event AND fromDays <= age AND toDays >= age; absent bound is unbounded.',
        'unknown':'Missing facts or unsupported extension conditions are unknown, not true.',
        'extensions':'Not automatically indexed; agree provider schemas and evaluators.'}
    write(p,d)
season=lambda code:{'codeSystem':'https://example.org/seasons/india/v1','code':code,'label':code}
subject=lambda crop:'https://example.org/crops/'+crop
cases={
 'cotton-sowing-window':[{'subjectIds':[subject('cotton')],'seasons':[season('Kharif')],'relativeTiming':{'event':'Sowing','fromDays':20,'toDays':30}}],
 'rice-transplanting-window':[{'subjectIds':[subject('rice')],'establishmentMethods':['Transplanted'],'relativeTiming':{'event':'Transplanting','fromDays':7,'toDays':10}}],
 'mango-pruning-window':[{'subjectIds':[subject('mango')],'relativeTiming':{'event':'Pruning','fromDays':14,'toDays':21}}],
 'correlated-crop-seasons':[{'subjectIds':[subject('cotton')],'seasons':[season('Kharif')]},{'subjectIds':[subject('wheat')],'seasons':[season('Rabi')]}],
 'stage-and-irrigation':[{'subjectIds':[subject('rice')],'waterRegimes':['Irrigated'],'growthStages':[{'codeSystem':'https://example.org/rice-stages/v1','code':'flowering','label':'Flowering'}]}],
 'provider-specific-restriction':[{'extensions':{'https://example.org/agronomy/v1/soilClass':{'allowed':['Vertisol']}}}]
}
template=read(ROOT/'KnowledgeAdvisory/v0.1/examples/direct-crop-advisory.json')
for name,conditions in cases.items():
    d=copy.deepcopy(template)
    for key in ('agricultureSubjects','validity','supportingResourceIds','coverageAreas'): d.pop(key,None)
    d.update(languages=['en'],topics=['Applicability modelling review'],
        rationale='Synthetic schema-review fixture, not agricultural advice.',
        source={'sourceId':'example:applicability-review','sourceName':'Synthetic review fixture'},
        applicability=conditions,recommendations=[{'message':'Illustrative scope only. Consult a reviewed source before acting.','language':'en'}])
    write(ROOT/'KnowledgeAdvisory/v0.1/examples'/('applicability-'+name+'.json'),d)
d['applicability']=[{'subjectIds':[subject('cotton')]}]
d['recommendations'][0]['applicability']=[{'relativeTiming':{'event':'Sowing','fromDays':20,'toDays':30}}]
write(ROOT/'KnowledgeAdvisory/v0.1/examples/applicability-recommendation-scope.json',d)
print('Updated shared vocabulary, eight profiles and seven synthetic advisory examples.')
