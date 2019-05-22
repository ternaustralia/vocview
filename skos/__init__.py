from rdflib.namespace import RDF, SKOS, DCTERMS, RDFS, OWL, DC
from rdflib import URIRef, Namespace
import markdown
from flask import url_for

from config import Config
from skos.concept_scheme import ConceptScheme, ConceptSchemeRenderer
from skos.concept import Concept, ConceptRenderer
from skos.register import Register
import helper

from datetime import date
from urllib import parse


# Controlled values
CONCEPT = 0
CONCEPTSCHEME = 1
COLLECTION = 2

SCHEMAORG = Namespace('http://schema.org/')


def list_concepts():
    concepts = []
    for c in Config.g.subjects(RDF.type, SKOS.Concept):
        label = get_label(c)
        date_created = get_created_date(c)
        date_modified = get_modified_date(c)
        definition = get_definition(c)
        scheme = get_in_scheme(c)
        concepts.append((c, label, [
            ('http://purl.org/dc/terms/created', date_created),
            ('http://purl.org/dc/terms/modified', date_modified),
            ('http://www.w3.org/2004/02/skos/core#definition', definition),
            ('http://www.w3.org/2004/02/skos/core#inScheme', scheme)
        ]))
    return sorted(concepts, key=lambda i: i[1])


def list_concept_schemes():
    concept_schemes = []

    for cc in Config.g.subjects(RDF.type, SKOS.ConceptScheme):
        label = get_label(cc)
        date_created = get_created_date(cc)
        date_modified = get_modified_date(cc)
        description = get_description(cc)
        concept_schemes.append((cc, label, [
            ('http://purl.org/dc/terms/created', date_created),
            ('http://purl.org/dc/terms/modified', date_modified),
            description
        ]))

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
    # TODO: title() capitalises all words, we need a post-process function to lower case words that are of types
    #       such as preposition and conjunction.
    for label in Config.g.objects(URIRef(uri), SKOS.prefLabel):
        return label.title()
    for label in Config.g.objects(URIRef(uri), DCTERMS.title):
        return label.title()
    for label in Config.g.objects(URIRef(uri), RDFS.label):
        return label.title()

    # Create a label from the URI.
    label = helper.uri_label(uri)
    label = _split_camel_case_label(label)
    label = label.title()
    return label


def get_description(uri):
    for description in Config.g.objects(URIRef(uri), DCTERMS.description):
        return (DCTERMS.description, description)
    for description in Config.g.objects(URIRef(uri), DC.description):
        return (DC.description, description)
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
    return sorted(top_concepts, key=lambda i: i[1])


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
        RDFS.isDefinedBy, DC.description, DCTERMS.creator, DCTERMS.contributor, SCHEMAORG.parentOrganization,
        SCHEMAORG.contactPoint, SCHEMAORG.member, SCHEMAORG.subOrganization, SCHEMAORG.familyName,
        URIRef('http://schema.semantic-web.at/ppt/propagateType'), SCHEMAORG.givenName, SCHEMAORG.honorificPrefix,
        SCHEMAORG.jobTitle, SCHEMAORG.memberOf, URIRef('http://schema.semantic-web.at/ppt/appliedType'),

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
    """A concept scheme in which the concept is a part of. A concept may be a member of more than one concept scheme"""
    schemes = []
    for scheme in Config.g.objects(URIRef(uri), SKOS.inScheme):
        label = get_label(scheme)
        schemes.append((scheme, label))
    return schemes


def _add_narrower(uri, hierarchy, indent):
    concepts = []

    for concept in Config.g.objects(URIRef(uri), SKOS.narrower):
        label = get_label(concept)
        concepts.append((concept, label))

    concepts.sort(key=lambda i: i[1])

    for concept in concepts:
        tab = indent * '\t'
        hierarchy += tab + '- [{}]({})\n'.format(concept[1], url_for('routes.ob', uri=concept[0]))
        hierarchy = _add_narrower(concept[0], hierarchy, indent + 1)

    return hierarchy


def get_concept_hierarchy(uri):
    hierarchy = ''
    top_concepts = []

    for top_concept in Config.g.objects(URIRef(uri), SKOS.hasTopConcept):
        label = get_label(top_concept)
        top_concepts.append((top_concept, label))

    top_concepts.sort(key=lambda i: i[1])

    for top_concept in top_concepts:
        hierarchy += '- [{}]({})\n'.format(top_concept[1], url_for('routes.ob', uri=top_concept[0]))
        hierarchy = _add_narrower(top_concept[0], hierarchy, 1)
    return '<div id="concept-hierarchy">' + markdown.markdown(hierarchy) + '</div>'


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


def get_schema_org_parent_org(uri):
    for parent_org in Config.g.objects(URIRef(uri), SCHEMAORG.parentOrganization):
        label = get_label(parent_org)
        return (parent_org, label)


def get_schema_org_contact_point(uri):
    for cp in Config.g.objects(URIRef(uri), SCHEMAORG.contactPoint):
        label = get_label(cp)
        return (cp, label)


def get_schema_org_members(uri):
    members = []
    for m in Config.g.objects(URIRef(uri), SCHEMAORG.member):
        label = get_label(m)
        members.append((m, label))
    return members


def get_schema_org_sub_orgs(uri):
    orgs = []
    for org in Config.g.objects(URIRef(uri), SCHEMAORG.subOrganization):
        label = get_label(org)
        orgs.append((org, label))
    return orgs


def get_schema_org_family_name(uri):
    for fn in Config.g.objects(URIRef(uri), SCHEMAORG.familyName):
        return fn


def get_schema_org_given_name(uri):
    for gn in Config.g.objects(URIRef(uri), SCHEMAORG.givenName):
        return gn


def get_schema_org_honorific_prefix(uri):
    for hp in Config.g.objects(URIRef(uri), SCHEMAORG.honorificPrefix):
        return hp


def get_schema_org_job_title(uri):
    for jt in Config.g.objects(URIRef(uri), SCHEMAORG.jobTitle):
        return jt


def get_schema_org_member_of(uri):
    for org in Config.g.objects(URIRef(uri), SCHEMAORG.memberOf):
        label = get_label(org)
        return (org, label)