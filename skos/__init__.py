from rdflib.namespace import RDF, SKOS, DCTERMS, RDFS, OWL
from rdflib import URIRef
import markdown

from config import Config
from skos.concept_scheme import ConceptScheme
from skos.concept import Concept

from datetime import date
from urllib import parse


# Controlled values
CONCEPT = 0
CONCEPTSCHEME = 1
COLLECTION = 2


def list_concept_schemes():
    concept_schemes = []

    for cc in Config.g.subjects(RDF.type, SKOS.ConceptScheme):
        label = get_label(cc)
        concept_schemes.append({'uri': cc, 'label': label})

    return sorted(concept_schemes, key=lambda i: i['label'])


def get_label(uri):
    for label in Config.g.objects(URIRef(uri), SKOS.prefLabel):
        return label
    for label in Config.g.objects(URIRef(uri), DCTERMS.title):
        return label
    for label in Config.g.objects(URIRef(uri), RDFS.label):
        return label


def get_description(uri):
    for description in Config.g.objects(URIRef(uri), DCTERMS.description):
        return (DCTERMS.description, description)
    for description in Config.g.objects(URIRef(uri), RDFS.comment):
        return (RDFS.comment, markdown.markdown(description))


def get_definition(uri):
    for definition in Config.g.objects(URIRef(uri), SKOS.definition):
        return markdown.markdown(definition)


def get_class_types(uri):
    types = []
    for type in Config.g.objects(URIRef(uri), RDF.type):
        # Only add URIs (and not blank nodes!)
        if str(type)[:4] == 'http':
            types.append(type)
    return types


def get_narrowers(uri):
    narrowers = []
    for narrower in Config.g.objects(URIRef(uri), SKOS.narrower):
        label = get_label(narrower)
        narrowers.append((parse.quote_plus(narrower), label))
    return sorted(narrowers, key=lambda i: i[1])


def get_broaders(uri):
    broaders = []
    for broader in Config.g.objects(URIRef(uri), SKOS.broader):
        label = get_label(broader)
        broaders.append((parse.quote_plus(broader), label))
    return sorted(broaders, key=lambda i: i[1])


def get_top_concept_of(uri):
    top_concept_ofs = []
    for tco in Config.g.objects(URIRef(uri), SKOS.topConceptOf):
        label = get_label(tco)
        top_concept_ofs.append((parse.quote_plus(tco), label))
    return sorted(top_concept_ofs, key=lambda i: i[1])


def get_top_concepts(uri):
    top_concepts = []
    for tc in Config.g.objects(URIRef(uri), SKOS.hasTopConcept):
        label = get_label(tc)
        top_concepts.append((parse.quote_plus(tc), label))
    return top_concepts


def get_change_note(uri):
    for cn in Config.g.objects(URIRef(uri), SKOS.changeNote):
        return cn


def get_alt_labels(uri):
    labels = []
    for alt_label in Config.g.objects(URIRef(uri), SKOS.altLabel):
        labels.append(alt_label)
    return sorted(labels)


def get_created_date(uri):
    for created in Config.g.objects(URIRef(uri), DCTERMS.created):
        created = created.split('-')
        created = date(int(created[0]), int(created[1]), int(created[2][:2]))
        return created


def get_modified_date(uri):
    for modified in Config.g.objects(URIRef(uri), DCTERMS.modified):
        return modified


def get_uri_skos_type(uri):
    for _ in Config.g.triples((URIRef(uri), RDF.type, SKOS.ConceptScheme)):
        return CONCEPTSCHEME
    for _ in Config.g.triples((URIRef(uri), RDF.type, SKOS.Concept)):
        return CONCEPT
    for _ in Config.g.triples((URIRef(uri), RDF.type, SKOS.Collection)):
        return COLLECTION
    return None


def get_properties(uri):
    ignore = [
        # Common
        RDF.type, SKOS.prefLabel, DCTERMS.title, RDFS.label, DCTERMS.description, SKOS.definition, SKOS.changeNote,
        DCTERMS.created, DCTERMS.modified, OWL.sameAs,

          # Concept
          SKOS.narrowers, SKOS.broaders, SKOS.topConceptOf,

        # Concept Scheme
        SKOS.hasTopConcept
    ]

    properties = []
    for _, property, value in Config.g.triples((URIRef(uri), None, None)):
        if property in ignore:
            continue
        properties.append(((property, get_label(property)), value))
    return properties
