"""
natbib module.

Adapted from https://bitbucket.org/wnielson/sphinx-natbib
"""
import codecs
import collections
import os
import re

import docutils.nodes
from docutils import transforms
from docutils.parsers.rst import Directive, directives

import latexcodec

from sphinx import addnodes
from sphinx.domains import Domain, ObjType
from sphinx.locale import l_, _
from sphinx.roles import XRefRole

from pybtex.database.input import bibtex

from .utils import (KEY, PREV, NEXT, OrderedSet)

# pylint: disable=C0111,W0221

DEFAULT_CONF = {
    'file': '/home/mwibrow/github/vlnm/docs/source/bibliography.bib',
    'brackets': '()',
    'separator': ';',
    'style': 'authoryear', # 'numbers', 'super'
    'sort': False,
    'sort_compress': False,
    'entries': {}
}

ROLES = [
    'xxx',
    'p', 'ps', 'alp', 'alps',
    't', 'ts', 'alt', 'alts',
    'author', 'authors', 'year', 'yearpar', 'text'
]

def latex_decode(text):
    """
    Decode ascii text latex formant to UTF-8
    """
    return text.encode('ascii').decode('latex')

def parse_keys(rawtext):
    """
    Parse :rawtext: into reference and pre/post text
    """
    tokens = re.split(r'\s*\{%\s*(.*?)\s*%\}\s*', rawtext.strip())
    if len(tokens) == 3:
        pre, refs, post = tokens
    else:
        pre, refs, post = '', tokens[0], ''
    keys = [ref.strip() for ref in refs.split(',')]
    return keys, pre, post

class Citations(object):
    """
    Citations docstring
    """
    def __init__(self, env, bibfile):
        self.conf = DEFAULT_CONF.copy()
        self.file_name = None
        self.parser = None
        self.data = None
        self.ref_map = {}

        bibfile = os.path.normpath(env.relfn2path(bibfile.strip())[1])

        file_name = bibfile
        if file_name:
            self.file_name = file_name
            self.parser = bibtex.Parser()
            self.data = self.parser.parse_file(self.file_name)
        else:
            raise ValueError('No bibliography file given')

    def get(self, key):
        if self.data:
            return self.data.entries.get(key)
        return key

class CitationTransform(object):
    """
    This class is meant to be applied to a ``docutils.nodes.pending`` node when a
    ``cite`` role is encountered.  Later (during the resolve_xref stage) this
    class can be used to generate the proper citation reference nodes for
    insertion into the actual document.
    """
    def __init__(self, refs, pre, post, typ, global_keys, config):
        self.refs = refs
        self.pre = pre
        self.post = post
        self.config = config
        self.typ = typ
        self.global_keys = global_keys

    def __repr__(self):
        return '<%s>' % self.__str__()

    def __str__(self):
        return ','.join([r.key for r in self.refs])

    def get_ref_num(self, key):
        for i, k in enumerate(self.global_keys):
            if k == key:
                return i+1

    def get_author(self, authors, all_authors=False):
        if len(authors) == 1:
            author = '{}'.format(authors[0].last()[0])
        elif len(authors) > 2 and not all_authors:
            author = u'%s et al.' % authors[0].last()[0]
        else:
            author = '{} & {}'.format(
                ', '.join([a.last()[0] for a in authors[:-1]]),
                authors[-1].last()[0])
        return author

    def cite(self, cmd, refuri):
        """
        Return a docutils Node consisting of properly formatted citations children
        docutils.nodes.
        """
        bo, bc    = self.config['brackets']
        sep       = u'%s ' % self.config['separator']
        style     = self.config['style']
        all_auths = (cmd.endswith('s'))
        alt       = (cmd.startswith('alt') or \
                                (cmd.startswith('alp')) or \
                                (style == 'citeyear'))

        if (cmd.startswith('p') or cmd == 'yearpar') and style != 'super':
            node = docutils.nodes.inline(bo, bo, classes=['citation'])
        else:
            node = docutils.nodes.inline('', '', classes=['citation'])

        if self.pre:
            pre = u"%s " % latex_decode(self.pre)
            node += docutils.nodes.inline(pre, pre, classes=['pre'])

        for i, ref in enumerate(self.refs):
            authors = ref.persons.get('author', [])
            author_text = latex_decode(self.get_author(authors, all_auths))
            lrefuri = refuri + '#citation-' + docutils.nodes.make_id(ref.key)

            if i > 0 and i < len(self.refs):
                if style == "authoryear":
                    node += docutils.nodes.inline(sep, sep)
                else:
                    if style == "super":
                        node += docutils.nodes.superscript(', ', ', ')
                    else:
                        node += docutils.nodes.inline(', ', ', ')

            if (style == "authoryear" and (cmd.startswith('p') or cmd.startswith('alp'))) or \
                 (cmd.startswith('t') or cmd.startswith('alt') or cmd.startswith('author')):
                node += docutils.nodes.reference(author_text, author_text, internal=True, refuri=lrefuri)

                if cmd.startswith('p') or cmd.startswith('alp'):
                    node += docutils.nodes.inline(', ', ', ')
                else:
                    node += docutils.nodes.inline(' ', ' ')

            # Add in either the year or the citation number
            if not cmd.startswith('author'):
                if style != 'authoryear':
                    num = self.get_ref_num(ref.key)
                else:
                    num = ref.fields.get('year')

                refnode = docutils.nodes.reference(str(num), str(num), internal=True, refuri=lrefuri)

                if cmd.startswith('t') and style != 'super':
                    node += docutils.nodes.inline(bo, bo)

                if style == 'super':
                    node += docutils.nodes.superscript('', '', refnode)
                else:
                    node += refnode

                if cmd.startswith('t') and style != 'super':
                    if self.post:
                        post = u", %s" % latex_decode(self.post)
                        node += docutils.nodes.inline(post, post, classes=['post'])
                        self.post = ''
                    node += docutils.nodes.inline(bc, bc)

        if self.post:
            post = u", %s" % latex_decode(self.post)
            node += docutils.nodes.inline(post, post, classes=['post'])

        if (cmd.startswith('p') or cmd == 'yearpar') and style != 'super':
            node += docutils.nodes.inline(bc, bc, classes=['citation'])

        return node


class CitationXRefRole(XRefRole):
    """
    Citation Role docstring,
    """
    def __call__(self, typ, rawtext, text, lineno, inliner,
                 options=None, content=None):
        """
        When a ``cite`` role is encountered, we replace it with a
        ``docutils.nodes.pending`` node that uses a ``CitationTrasform`` for
        generating the proper citation reference representation during the
        resolve_xref phase.
        """
        options = options or {}
        content = content or []
        root_nodes = super(CitationXRefRole, self).__call__(
            typ, rawtext, text, lineno, inliner, options, content)
        root_node = root_nodes[0][0]

        env = inliner.document.settings.env
        # citations = env.domains['cite'].citations

        # Get the config at this point in the document
        config = {}
        for opt in ['style', 'brackets', 'separator', 'sort', 'sort_compress']:
            config[opt] = env.temp_data.get("cite_%s" % opt, env.domaindata['cite']['conf'].get(opt, DEFAULT_CONF[opt]))

        if typ == "cite:text":
            # A ``text`` citation is unique because it doesn't reference a cite-key
            keys = []
            pre, post = text, ''
        else:
            keys, pre, post = parse_keys(text)
            for key in keys:
                # if citations.get(key) is None:
                #     env.warn(env.docname, "cite-key `%s` not found in bibtex file" % key, lineno)
                #     continue
                env.bibtex_keys.add(key)

        data = {
            'keys': keys,
            'pre': pre,
            'post': post,
            'typ': typ,
            'global_keys': env.bibtex_keys,
            'config': config}

        root_node += docutils.nodes.pending(CitationTransform, data)
        return [root_node], []

    def result_nodes(self, document, env, node, is_ref):

        return [node], []



class CiteP(CitationXRefRole):
    def __call__(self, typ, *args, **kwargs):
        return super(CiteP, self).__call__('cite:p', *args, **kwargs)

class CiteAlp(CitationXRefRole):
    def __call__(self, typ, *args, **kwargs):
        return super(CiteAlp, self).__call__('cite:alp', *args, **kwargs)

class CiteT(CitationXRefRole):
    def __call__(self, typ, *args, **kwargs):
        return super(CiteT, self).__call__('cite:t', *args, **kwargs)

class CiteAlt(CitationXRefRole):
    def __call__(self, typ, *args, **kwargs):
        return super(CiteAlt, self).__call__('cite:alt', *args, **kwargs)

class CiteText(CitationXRefRole):
    def __call__(self, typ, *args, **kwargs):
        return super(CiteText, self).__call__('cite:text', *args, **kwargs)

class CitationConfDirective(Directive):
    """
    Allows the user to change the citation style on a per-page or
    per-block basis.
    """
    has_content = False
    required_arguments = 0
    optional_arguments = 1
    option_spec = {
        'brackets':       directives.unchanged,
        'separator':      directives.unchanged,
        'style':          directives.unchanged,
        'sort':           directives.flag,
        'sort_compress':  directives.flag,
    }

    def run(self):
        env = self.state.document.settings.env

        # TODO: verify options
        if self.arguments:
            env.temp_data['cite_style'] = self.arguments[0]
        else:
            env.temp_data['cite_style'] = self.options.get(
                'style', DEFAULT_CONF['style'])

        try:
            self.options.pop('style')
        except KeyError:
            pass

        for key, value in self.options.items():
            env.temp_data['cite_{}'.format(key)] = value

        return []



class ApaStyle:


    def __init__(self):
        self.publications = {
            'article': [
                'authors',
                'year',
                'title',
                'journal',
                'volume',
                'number',
                'pages',
                'doi',
            ],
            'inproceedings': [
                'authors',
                'year',
                'title',
                'editor',
                'booktitle',
                'publisher',
                'volume',
                'number',
                'pages'
            ],
            'incollection': [
                'authors',
                'year',
                'title',
                'editor',
                'booktitle',
                'publisher',
                'volume',
                'number',
                'pages'
            ]
        }

    @staticmethod
    def get_authors(authors, **kwargs):
        """
        Authors
        """
        author_nodes = []
        for i, author in enumerate(authors):
            text = ' '.join(latex_decode(name) for name in author.last())

            if author.first() or author.middle():
                names = [author.first(), author.middle()]
                text += ', '
                for name in names:
                    parts = [part for part in name if part]
                    text += ' '.join(
                        '{}. '.format(latex_decode(part)[0].upper())
                        for part in parts)

            text = text.strip()
            author_node = docutils.nodes.inline(text, text)
            author_node['classes'].append('author')
            author_nodes.append(author_node)

            if len(authors) == 2 and i == 0:
                author_nodes.append(docutils.nodes.inline(' & ', ' & '))
        return author_nodes

    @staticmethod
    def get_editor(editor, **kwargs):
        node_list = []
        if editor:
            node_list.append(docutils.nodes.inline('In ', 'In '))
            node_list.append(ApaStyle.get_authors(editor))
            node_list.append(docutils.nodes.inline(' (eds), ', ' (eds), '))
        return node_list

    @staticmethod
    def get_pages(pages, **kwargs):
        node_list = []
        if pages:
            node_list.append(docutils.nodes.inline('pp', 'pp'))
            node_list.append(docutils.nodes.inline(pages, pages))
            node_list.append(docutils.nodes.inline('. ', '. '))
        return node_list

    @staticmethod
    def get_volume(volume, **kwargs):
        """Get publication volume"""
        node_list = []
        fields = kwargs.get('fields', {})
        if volume:
            node_list.append(docutils.nodes.inline('Vol. ', 'Vol. '))
            node_list.append(docutils.nodes.inline(volume, volume))
            if fields.get('number'):
                node_list.append(docutils.nodes.inline(' ', ' '))
            else:
                node_list.append(docutils.nodes.inline('. ', '. '))
        return node_list

    @staticmethod
    def get_number(number, **kwargs):
        """Get publication number"""
        node_list = []
        if number:
            node_list.append(docutils.nodes.inline('No. ', 'No. '))
            node_list.append(docutils.nodes.inline(number, number))
            node_list.append(docutils.nodes.inline('. ', '. '))
        return node_list

    @staticmethod
    def get_year(year, **kwargs):
        node_list = []
        if year:
            year = latex_decode(year)
            node_list.append(
                docutils.nodes.inline(year, ' ({})'.format(year), classes=['year']))
            node_list.append(docutils.nodes.inline('. ', '. '))
        return node_list

    @staticmethod
    def get_title(title, **kwargs):
        node_list = []
        if title:
            node_list.append(docutils.nodes.inline(title, title, classes=['title']))
            node_list.append(docutils.nodes.inline('.  ', '.  '))
        return node_list

    @staticmethod
    def get_booktitle(booktitle, **kwargs):
        node_list = []
        fields = kwargs.get('fields' or {})
        if booktitle:
            title = latex_decode(booktitle)
            node_list.append(docutils.nodes.emphasis(
                title, title, classes=['publication']))
            if fields.get('volume'):
                node_list.append(docutils.nodes.inline(', ', ', '))
            else:
                node_list.append(docutils.nodes.inline('. ', '. '))
        return node_list

    @staticmethod
    def get_journal(journal, **kwargs):
        return ApaStyle.get_booktitle(journal, **kwargs)

    def get_nodes(self, ref):
        publication = self.publications[ref.type]
        ref_node = docutils.nodes.paragraph('', '', classes=[ref.type, 'reference'])
        ref_fields = ref.fields
        for field in publication:
            if field == 'authors':
                source = ref.persons.get('author', [])
            elif field == 'editor':
                source = ref.persons.get('editor', [])
            else:
                source = ref.fields.get(field)
            getter = 'get_{}'.format(field)
            if hasattr(self, getter):
                node_list = getattr(self, getter)(source, fields=ref_fields)
                for node in node_list:
                    ref_node += node
        return ref_node

class CitationReferencesDirective(Directive):
    """
    Generates the actual reference list.
    """
    has_content = False
    required_arguments = 1
    optional_arguments = 0

    # TODO: Implement support for multiple bib files
    option_spec = {
        'path': directives.unchanged,
    }

    def get_reference_node(self, ref):
        node = docutils.nodes.inline('','', classes=[ref.type, 'reference'])

        style = ApaStyle()

        return style.get_nodes(ref)

    def run(self):
        """
        Generate the definition list that displays the actual references.
        """
        env = self.state.document.settings.env
        keys = env.bibtex_keys
        env.domaindata['cite']['refdoc'] = env.docname


        bibfile = self.arguments[0]

        env.domains['cite'].citations = Citations(env, bibfile)

        citations = env.domains['cite'].citations

        # TODO: implement
        #env.domaindata['cite']['refdocs'][env.docname] = Citations(env, path)

        # Build the references list
        # TODO: Make this an enumerated_list or field_list maybe?
        node = docutils.nodes.definition_list()
        node.document = self.state.document
        node['classes'].append('references')

        items = []
        for i, key in enumerate(keys):
            term = docutils.nodes.term('', '')

            # TODO: Allow the format of the reference list be configurable
            # if env.domaindata['cite']['conf']['style'] == 'super':
            #   term.children = [docutils.nodes.superscript('', i+1)]
            # else:
            #   term.children = [docutils.nodes.inline('', "%s) " % (i+1))]

            nid = "citation-%s" % docutils.nodes.make_id(key)
            definition = self.get_reference_node(citations.get(key))

            li = docutils.nodes.definition_list_item('', term, definition)
            li[0]['ids'].append(nid)
            li[0]['names'].append(nid)
            items.append(li)
        node.extend(item for item in items)

        return [node]

class bibliography(docutils.nodes.General, docutils.nodes.Element):
    pass

class CitationDomain(Domain):
    name = "cite"
    label = "citation"

    object_types = {
        'citation': ObjType(l_('citation'), *ROLES, searchprio=-1),
    }

    directives = {
        'conf': CitationConfDirective,
        'refs': CitationReferencesDirective
    }

    roles = dict([(r, CitationXRefRole()) for r in ROLES])
    initial_data = {
        'keys':     OrderedSet(),  # Holds cite-keys in order of reference
        'conf':     DEFAULT_CONF,
        'refdocs':  {}
    }

    def __init__(self, env):
        super(CitationDomain, self).__init__(env)

        # Update conf
        # env.domaindata['cite']['conf'].update(env.config.natbib)
        #import sys
        #print(dir(env), file=sys.stderr, flush=True)
        # TODO: warn if citations can't parse bibtex file
        #self.citations = Citations(env)
        self.citations = {}
    def resolve_xref(self, env, fromdocname, builder,
                                             typ, target, node, contnode):


        refdoc = env.domaindata['cite'].get('refdoc')
        if not refdoc:
            env.warn(fromdocname  , 'no `refs` directive found; citations will have dead links', node.line)
            refuri = ''
        else:
            refuri = builder.get_relative_uri(fromdocname, refdoc)

        for nd in node.children:
            if isinstance(nd, docutils.nodes.pending):
                nd.details['refs'] = []
                for key in nd.details.pop('keys'):
                    ref = self.citations.get(key)
                    if ref is None:
                        continue
                    nd.details['refs'].append(ref)

                transform = nd.transform(**nd.details)
                node = transform.cite(typ, refuri)

        return node


def init_app(app):
    app.env.bibtex_keys =  OrderedSet()

def setup(app):
    app.connect('builder-inited', init_app)
    #app.connect('missing-reference', missing)
    app.add_config_value('natbib', DEFAULT_CONF, 'env')
    app.add_domain(CitationDomain)
    app.add_role('citealp', CiteP())
    app.add_role('citealt', CiteT())
    app.add_role('citep', CiteP())
    app.add_role('citet', CiteT())

    app.add_stylesheet('css/style.css')
