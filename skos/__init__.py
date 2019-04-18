from rdflib.namespace import RDF, SKOS, DCTERMS, RDFS, OWL
from rdflib import URIRef
import markdown

from config import Config
from skos.concept_scheme import ConceptScheme
from skos.concept import Concept
from skos.register import Register
import helper

from datetime import date
from urllib import parse


# Controlled values
CONCEPT = 0
CONCEPTSCHEME = 1
COLLECTION = 2


def list_concepts():
    concepts = []
    for c in Config.g.subjects(RDF.type, SKOS.Concept):
        label = get_label(c)
        concepts.append((c, label))
    return sorted(concepts, key=lambda i: i[1])


def list_concept_schemes():
    concept_schemes = []

    for cc in Config.g.subjects(RDF.type, SKOS.ConceptScheme):
        label = get_label(cc)
        concept_schemes.append((cc, label))

    return sorted(concept_schemes, key=lambda i: i[1])


def _split_camel_case_label(label):
    new_label = ''
    last = 0
    for i, letter in enumerate(label):
        if letter.isupper():
            new_label += ' {}'.format(label[last:i])
            last = i

    new_label += ' {}'.format(label[last:])
    new_label = new_label.strip()
    return new_label


def get_label(uri):
    for label in Config.g.objects(URIRef(uri), SKOS.prefLabel):
        return label.capitalize()
    for label in Config.g.objects(URIRef(uri), DCTERMS.title):
        return label.capitalize()
    for label in Config.g.objects(URIRef(uri), RDFS.label):
        return label.capitalize()

    # Create a label from the URI.
    label = helper.uri_label(uri)
    label = _split_camel_case_label(label)
    label = label.capitalize()
    return label


def get_description(uri):
    for description in Config.g.objects(URIRef(uri), DCTERMS.description):
        return (DCTERMS.description, description)
    for description in Config.g.objects(URIRef(uri), RDFS.comment):
        return (RDFS.comment, description)


def get_definition(uri):
    for definition in Config.g.objects(URIRef(uri), SKOS.definition):
        return definition


def get_class_types(uri):
    types = []
    for type in Config.g.objects(URIRef(uri), RDF.type):
        # Only add URIs (and not blank nodes!)
        if str(type)[:4] == 'http' \
                and str(type) != 'http://www.w3.org/2004/02/skos/core#ConceptScheme' \
                and str(type) != 'http://www.w3.org/2004/02/skos/core#Concept' \
                and str(type) != 'http://www.w3.org/2004/02/skos/core#Collection':
            types.append(type)
    return types


def get_narrowers(uri):
    narrowers = []
    for narrower in Config.g.objects(URIRef(uri), SKOS.narrower):
        label = get_label(narrower)
        narrowers.append((narrower, label))
    return sorted(narrowers, key=lambda i: i[1])


def get_broaders(uri):
    broaders = []
    for broader in Config.g.objects(URIRef(uri), SKOS.broader):
        label = get_label(broader)
        broaders.append((broader, label))
    return sorted(broaders, key=lambda i: i[1])


def get_top_concept_of(uri):
    top_concept_ofs = []
    for tco in Config.g.objects(URIRef(uri), SKOS.topConceptOf):
        label = get_label(tco)
        top_concept_ofs.append((tco, label))
    return sorted(top_concept_ofs, key=lambda i: i[1])


def get_top_concepts(uri):
    top_concepts = []
    for tc in Config.g.objects(URIRef(uri), SKOS.hasTopConcept):
        label = get_label(tc)
        top_concepts.append((tc, label))
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
        modified = modified.split('-')
        modified = date(int(modified[0]), int(modified[1]), int(modified[2][:2]))
        return modified


def get_uri_skos_type(uri):
    uri = parse.unquote_plus(uri)
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
        DCTERMS.created, DCTERMS.modified, OWL.sameAs, RDFS.comment, SKOS.altLabel, DCTERMS.bibliographicCitation,
        RDFS.isDefinedBy,

          # Concept
          SKOS.narrower, SKOS.broader, SKOS.topConceptOf, SKOS.inScheme, SKOS.closeMatch, SKOS.exactMatch,

        # Concept Scheme
        SKOS.hasTopConcept
    ]

    properties = []
    for _, property, value in Config.g.triples((URIRef(uri), None, None)):
        if property in ignore:
            continue
        properties.append(((property, get_label(property)), value))
    return properties


def get_in_scheme(uri):
    """A concept scheme in which the concept is included. A concept may be a member of more than one concept scheme"""
    schemes = []
    for scheme in Config.g.objects(URIRef(uri), SKOS.inScheme):
        label = get_label(scheme)
        schemes.append((scheme, label))
    return schemes


def _add_narrower(uri, hierarchy, indent):
    for concept in Config.g.objects(URIRef(uri), SKOS.narrower):
        label = get_label(concept)
        tab = indent * '\t'
        hierarchy += tab + '- [{} ({})]({}id/{})\n'.format(label, indent + 1, Config.url_root, parse.quote_plus(concept))
        hierarchy = _add_narrower(concept, hierarchy, indent + 1)

    return hierarchy


def get_concept_hierarchy(uri):
    hierarchy = ''
    for top_concept in Config.g.objects(URIRef(uri), SKOS.hasTopConcept):
        label = get_label(top_concept)
        hierarchy += '- [{} ({})]({}id/{})\n'.format(label, 1, Config.url_root, top_concept)
        hierarchy = _add_narrower(top_concept, hierarchy, 1)
    return markdown.markdown(hierarchy)


def get_is_defined_by(uri):
    for is_def in Config.g.objects(URIRef(uri), RDFS.isDefinedBy):
        return is_def


def get_close_match(uri):
    close_match = []
    for cm in Config.g.objects(URIRef(uri), SKOS.closeMatch):
        close_match.append(cm)
    return close_match


def get_exact_match(uri):
    exact_match = []
    for em in Config.g.objects(URIRef(uri), SKOS.exactMatch):
        exact_match.append(em)
    return exact_match


def get_bibliographic_citation(uri):
    for bg in Config.g.objects(URIRef(uri), DCTERMS.bibliographicCitation):
        return bg
