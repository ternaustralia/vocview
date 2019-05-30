import skos


class SchemaOrgMixin:
    def __init__(self, uri):
        self.uri = uri
        self.parent_organization = skos.get_schema_org_parent_org(uri)
        self.contact_point = skos.get_schema_org_contact_point(uri)
        self.members = skos.get_schema_org_members(uri)
        self.sub_organizations = skos.get_schema_org_sub_orgs(uri)


class SchemaPersonMixin:
    def __init__(self, uri):
        self.uri = uri
        self.family_name = skos.get_schema_org_family_name(uri)
        self.given_name = skos.get_schema_org_given_name(uri)
        self.honorific_prefix = skos.get_schema_org_honorific_prefix(uri)
        self.job_title = skos.get_schema_org_job_title(uri)
        self.member_of = skos.get_schema_org_member_of(uri)