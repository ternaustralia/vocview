# VocView 
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![GitHub license](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/edmondchuc/vocview/graphs/commit-activity)
[![Website](https://img.shields.io/website/https/www.edmondchuc.com.svg?down_color=red&down_message=Edmond%20Chuc&label=Author&style=social&up_color=blue&up_message=Edmond%20Chuc)](https://www.edmondchuc.com)

*A Python web application to serve SKOS-encoded vocabularies as Linked Data.*

### VocView instances
Click on a badge to see a live instance of VocView.

[![corveg](https://img.shields.io/website/http/linkeddata.tern.org.au/viewer/corveg.svg?down_color=red&down_message=offline&label=CORVEG&up_color=green&up_message=online)](http://linkeddata.tern.org.au/viewer/corveg)

[![tern](https://img.shields.io/website/http/linkeddata.tern.org.au/viewer/tern.svg?down_color=red&down_message=offline&label=TERN&up_color=green&up_message=online)](http://linkeddata.tern.org.au/viewer/tern)

[![ausplots](https://img.shields.io/website/http/linkeddata.tern.org.au/viewer/ausplots.svg?down_color=red&down_message=offline&label=AUSPLOTS&up_color=green&up_message=online)](http://linkeddata.tern.org.au/viewer/ausplots)


## SKOS
SKOS stands for [Simple Knowledge Organization System](https://www.w3.org/2004/02/skos/), a W3C recommendation, as of April, 2019.

SKOS is used to create controlled vocabularies and taxonomies using the [RDF](https://en.wikipedia.org/wiki/Resource_Description_Framework) model. Combined with models created in the [Web Ontology Language](https://en.wikipedia.org/wiki/Web_Ontology_Language) (OWL), SKOS allows [Semantic Web](https://en.wikipedia.org/wiki/Semantic_Web) users to provide information in an unambiguous, interoperable, and reusable manner. 


## Linked Data
VocView uses the [pyLDAPI](https://pyldapi.readthedocs.io/en/latest/) library to provide registry information as Linked Data. The library also provides VocView with different *views* of things. For example, a register view to describe a register and its items, an alternates view, to describe the alternative views of the same resource, and a SKOS view, to describe SKOS concept schemes and concepts.

VocView also provides different *formats* for things, such as text/html, text/turtle, application/rdf+xml, etc.

Specifying views and formats can be done by using the query string arguments `_view` and `_format` or content negotiation with an *Accept* header.

##### Example usage
```bash
http://localhost:5000/vocabulary/?_view=alternates&format=html
```
The above request will show the HTML page of the alternates view, and display all the available views and formats in a table.
 
 All vocabulary data are accessible via the Linked Data API.


## Getting started

### Installation
Clone this repository's master branch
```bash
git clone https://github.com/edmondchuc/vocview.git
```

Change directory into vocview and install the Python dependencies
```bash
pip install -r requirements.txt
```

Note: Python *virtualenv* is highly recommended. See [this](https://docs.python-guide.org/dev/virtualenvs/) article on Python virtual environments.

### Configuration
Add some vocabulary sources in the `vocabs.yaml` file
```yaml
download:
  material_types:
    source: https://vocabs.ands.org.au/registry/api/resource/downloads/524/ga_material-type_v1-0.ttl
    format: turtle
local:
  skos:
    source: skos.ttl
    format: turtle
rva:
  resource_endpoint: 'https://demo.ands.org.au/vocabs-registry/api/resource/vocabularies/{}?includeVersions=true&includeAccessPoints=true&includeRelatedEntitiesAndVocabularies=false'
  download_endpoint: 'https://demo.ands.org.au/vocabs-registry/api/resource/downloads/{}'
  extension: ttl # Use Turtle as it has excellent compression compared to other RDF serialisations
  format: turtle
  ids: [
    245, # CORVEG
  ]
```
The example snippet above shows how to enable three types of vocabulary files, an online file, a local file, and a file accessed via [Research Vocabularies Australia](https://vocabs.ands.org.au/)'s (RVA) API. 

The `material_types` is an online file (hence the `download` node), where the `source` node lists the absolute URL of the file. The `format` node tells the RDFLib parser what format the file is in. See the list of available parsers for RDFLib [here](https://rdflib.readthedocs.io/en/stable/plugin_parsers.html).

The `local` node lists RDF files on the local filesystem. By default, the path of the `source` node is relative to the `local_vocabs` directory in this repository. 

The RVA resource finds the latest API endpoint for a given project referenced by the ID `245`. The extension informs the API what format we want to download and the format informs the VocView system what file type to expect. The `resource_endpoint` is used to determine the RVA project's latest version's *download ID*. The *download ID* is then used with the `download_endpoint` to download the latest RDF resource. 

> Note: there is significance with loading in the `skos.ttl` file, which is a modified version of the SKOS definition. The modifications consist of removing a few `rdfs:subPropertyOf`statements used by the rule-based inference engine (discussed later). Loading this file in to the graph allows the inferencer to create new triples.


## Rule-based inferencing
### OWLRL
VocView utilises the Python rule-based inferencer for RDF known as [owlrl](https://owl-rl.readthedocs.io/en/latest/). The inferencer is used in VocView to expand the graph on SKOS-specific properties. To expand the graph on SKOS properties, ensure that the `skos.ttl` is declared in `vocabs.yaml`. Additional ontologies can also be loaded in to expand the graph further. 

A good example of why an inferencing engine is used in VocView is to expand properties that have inverse properties of itself. For example, declaring top concepts with `skos:topConceptOf` need only be declared within concepts of a concept scheme. The inferencing engine is capable of performing a deductive closure and add the inverse statements of `skos:topConceptOf` to the concept scheme as `skos:hasTopConcept`. The HTML view of the concept scheme will now display a listing of the top concepts. Without the additional triples added by the inferencing engine, the listing will not be displayed (as the information is missing).

The downside of using a rule-based inferencer like owlrl is the expensive calculations. This causes a slow start-up time for VocView.

It is recommended to have inferencing performed on the source repository before loading the data into VocView.

Therefore, inferencing is an optional feature.


### Skosify
An alternative to rule-based inferencing is the Python [skosify](https://skosify.readthedocs.io/en/latest/index.html) library. This library contains a collection of inferencing functions specifically for SKOS properties. Since this library only focuses on SKOS things, it may be much faster than the owlrl library, thus reducing start-up time.   

*This is a potential feature for a future VocView version*. 
 

## Search within registers
VocView contains registers for vocabularies and concepts.

### Naive search
The current search implementation is a naive, string-based text-match on the register items' labels. For simple searches on the label, this works well (and fast) enough. Time complexity is Θ(n) where *n* is the number of items in the register. 

This naive search matches not only full-text in labels, but also partial text. It is also case-insensitive. 

E.g. a search query "*form*" will match: 
 - *Landform type concepts* .
 - *Structural formation classification system concepts*

### Whoosh (full text search)
*To be implemented in VocView...*
 
Whoosh is a pure Python library text indexer for full text search. It is suitable for light-weight Python applications like VocView, to provide full text search, without requiring external dependencies (outside of Python).

A description of Whoosh from the official [documentation](https://whoosh.readthedocs.io/en/latest/index.html):

- *Like one of its ancestors, Lucene, Whoosh is not really a search engine, it’s a programmer library for creating a search engine.*

Creating a full text search engine using Whoosh would greatly improve the capabilities of searching items within registers. Whoosh would allow users to search for not only key words to match register items' labels, but also their *definition*, *date*, or any other interesting properties.

Whoosh has been used in related projects already, and it will only take *probably* a full weekend to implement.


## Persistent store
On start-up, the first request performs the loading of all the RDF files into an in-memory graph. It then performs a deductive closure to expand the graph with additional triples outlined in the `skos.ttl`. This process makes the initial start-up time very slow.

One way to solve this is to have persistence of the graph between server restarts. 

There are three options to choose from in `config.py`'s `Config` class. 

- memory
- pickle
- sleepycat
- sqlite (not implemented)

> Note: to re-index, simply delete the `triplestore.p` file if using the **pickle** method or delete the `triplestore` directory if using the **sleepycat** method. 

### Memory
There is no *persistence* when using `memory` as this mode requires loading all the RDF files into the graph on start-up each time. 

#### Pros
Start-up time is very slow but performance is fast as the queries are performed on the graph, which is in memory (RAM). 

#### Cons
Memory use is high as it requires the whole graph to be stored in the application's memory.

### Pickle
VocView supports saving the graph object to disk as a binary file. In Python, this is known as [pickling](https://docs.python.org/3/library/pickle.html). On start-up, VocView loads in the graph and saves it to disk. Each subsequent restart, VocView will automatically load in the pickled graph object from disk if it exists. 

#### Pros
Performance is very fast compared to other persistent store methods. Queries made by each web request are performed on the in-memory graph, which is very fast.

#### Cons
Memory use is high as it requires the whole graph to be stored in the application's memory. 

### Sleepycat
(The defunct) Sleepycat was the company that maintained the freely-licensed Berkeley DB, a data store written in C for embedded systems. 

RDFLib currently ships Sleepycat by default. See RDFLib's documentation on persistence [here](https://rdflib.readthedocs.io/en/stable/persistence.html).

#### Pros
Extremely low memory usage compared to a method using in-memory graph. Good for instances of VocView with a large collection of vocabularies.  

#### Cons
Roughly 10-20% slower than in-memory graph (due to filesystem read/write speeds). Requires installing Berkeley DB to the host system as well as downloading the Python **bsddb3** package source and installing it manually.

#### Installing Sleepycat (Berkeley DB)
##### Ubuntu 18.04 and above
Install the Berkeley DB
```bash
sudo apt install python3-bsddb3
```
Install the Python package
```bash
pip install bsddb3
```
You now can use the Sleepycat as a persistent store.

##### macOS Mojave and above
First, ensure that [brew](https://brew.sh/) is installed on macOS, then run
```bash
brew install berkeley-db
```
Download the **bsddb3** source from PyPI like https://pypi.python.org/packages/source/b/bsddb3/bsddb3-5.3.0.tar.gz#md5=d5aa4f293c4ea755e84383537f74be82

Once unzipped and inside the package, run
```bash
python setup.py install --berkeley-db=$(brew --prefix)/berkeley-db/5.3.21/ 
```
You now can use the Sleepycat as a persistent store.

### SQLite (not implemented)
According to the textbook *Programming the Semantic Web* [1], it is possible to use [SQLite](https://www.sqlite.org/index.html) as the persistent data store for an RDFLib graph. 

It will be a good experiment to investigate on the ease of using this, since most systems come with SQLite pre-installed (unlike Sleepycat's Berkeley DB).

It will also be interesting to see the speed differences between SQLite and Sleepycat's store.  


## References
[1] Segaran, Evans, & Taylor. (2009). Programming the Semantic Web (1st ed.). Beijing ; Sebastopol, CA: O'Reilly.


## License
See [LICENSE](LICENSE).

## Developer's guide
See [DEVELOPER.md](DEVELOPER.md).


## Contact
**Edmond Chuc**  
[e.chuc@uq.edu.au](mailto:e.chuc@uq.edu.au)  
