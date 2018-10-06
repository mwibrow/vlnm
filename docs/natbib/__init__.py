"""
natbib module.

Adapted from https://bitbucket.org/wnielson/sphinx-natbib
"""
import codecs
import collections
import os
import re

from docutils import nodes, transforms
from docutils.parsers.rst import Directive, directives

import latexcodec

from sphinx import addnodes
from sphinx.domains import Domain, ObjType
from sphinx.locale import l_, _
from sphinx.roles import XRefRole

from pybtex.database.input import bibtex

from .utils import (KEY, PREV, NEXT, OrderedSet)

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
    # Get the keys and any pre- and post-ciation text
    # Spaces nor commas are allowed in cite keys, so we split on commas
    # first.  This will give us a list of keys, however, the last item may have
    # pre- and post-citation text (in brackets "[pre][post]")
    #
    # TODO: This isn't the best implementation and this should also
    #       handle errors
    """
    pre = u''
    post = u''
    keys = []
    for k in rawtext.split(','):
        k = k.strip() # Remove leading and trailing whitespace
        k = k.split(' ', 1) # Split on the first space in the key, if any
        if len(k) > 1:
            # We have some extra text here
            k, text = k
            bo, bc = 0, 0
            for c in text.strip():
                if c == "[" and bo == bc:
                    bo += 1
                elif c == "]" and bo == bc+1:
                    bc += 1
                else:
                    if bc == 0:
                        pre += c
                    else:
                        post += c
            if bc == bo and bc == 1:
                post = pre
                pre = u''
        else:
            k = k[0]
        keys.append(k)
    return (keys, pre, post)


class Citations(object):
    """
    Citations docstring
    """
    def __init__(self, env):
        self.conf = DEFAULT_CONF.copy()
        # self.conf.update(env.config.natbib)
        print(env)
        self.file_name = None
        self.parser = None
        self.data = None
        self.ref_map = {}

        file_name = self.conf.get('file')
        if file_name:
            self.file_name  = file_name
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
        if len(authors) > 2 and not all_authors:
            author = u'%s et al.' % authors[0].last()[0]
        else:
            author = u"%s & %s" % (u', '.join([a.last()[0] for a in authors[:-1]]),
                                                                                    authors[-1].last()[0])
        return author

    def cite(self, cmd, refuri):
        """
        Return a docutils Node consisting of properly formatted citations children
        nodes.
        """
        bo, bc    = self.config['brackets']
        sep       = u'%s ' % self.config['separator']
        style     = self.config['style']
        all_auths = (cmd.endswith('s'))
        alt       = (cmd.startswith('alt') or \
                                (cmd.startswith('alp')) or \
                                (style == 'citeyear'))

        if (cmd.startswith('p') or cmd == 'yearpar') and style != 'super':
            node = nodes.inline(bo, bo, classes=['citation'])
        else:
            node = nodes.inline('', '', classes=['citation'])

        if self.pre:
            pre = u"%s " % latex_decode(self.pre)
            node += nodes.inline(pre, pre, classes=['pre'])

        for i, ref in enumerate(self.refs):
            authors = ref.persons.get('author', [])
            author_text = latex_decode(self.get_author(authors, all_auths))
            lrefuri = refuri + '#citation-' + nodes.make_id(ref.key)

            if i > 0 and i < len(self.refs):
                if style == "authoryear":
                    node += nodes.inline(sep, sep)
                else:
                    if style == "super":
                        node += nodes.superscript(', ', ', ')
                    else:
                        node += nodes.inline(', ', ', ')

            if (style == "authoryear" and (cmd.startswith('p') or cmd.startswith('alp'))) or \
                 (cmd.startswith('t') or cmd.startswith('alt') or cmd.startswith('author')):
                node += nodes.reference(author_text, author_text, internal=True, refuri=lrefuri)

                if cmd.startswith('p') or cmd.startswith('alp'):
                    node += nodes.inline(', ', ', ')
                else:
                    node += nodes.inline(' ', ' ')

            # Add in either the year or the citation number
            if not cmd.startswith('author'):
                if style != 'authoryear':
                    num = self.get_ref_num(ref.key)
                else:
                    num = ref.fields.get('year')

                refnode = nodes.reference(str(num), str(num), internal=True, refuri=lrefuri)

                if cmd.startswith('t') and style != 'super':
                    node += nodes.inline(bo, bo)

                if style == 'super':
                    node += nodes.superscript('', '', refnode)
                else:
                    node += refnode

                if cmd.startswith('t') and style != 'super':
                    node += nodes.inline(bc, bc)

        if self.post:
            post = u", %s" % latex_decode(self.post)
            node += nodes.inline(post, post, classes=['post'])

        if (cmd.startswith('p') or cmd == 'yearpar') and style != 'super':
            node += nodes.inline(bc, bc, classes=['citation'])

        return node


class CitationXRefRole(XRefRole):
    def __call__(self, typ, rawtext, text, lineno, inliner, options={},\
                                content=[]):
        """
        When a ``cite`` role is encountered, we replace it with a
        ``docutils.nodes.pending`` node that uses a ``CitationTrasform`` for
        generating the proper citation reference representation during the
        resolve_xref phase.
        """
        rnodes = super(CitationXRefRole, self).__call__(typ, rawtext, text, lineno,
                                        inliner, options, content)
        rootnode = rnodes[0][0]

        env = inliner.document.settings.env
        print(env)
        citations = env.domains['cite'].citations

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
                if citations.get(key) is None:
                    env.warn(env.docname, "cite-key `%s` not found in bibtex file" % key, lineno)
                    continue
                env.domaindata['cite']['keys'].add(key)

        data = {
            'keys': keys,
            'pre': pre,
            'post': post,
            'typ': typ,
            'global_keys': env.domaindata['cite']['keys'],
            'config': config}

        rootnode += nodes.pending(CitationTransform, data)
        return [rootnode], []

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
            author_node = nodes.inline(text, text)
            author_node['classes'].append('author')
            author_nodes.append(author_node)

            if len(authors) == 2 and i == 0:
                author_nodes.append(nodes.inline(' & ', ' & '))
        return author_nodes

    @staticmethod
    def get_editor(editor, **kwargs):
        node_list = []
        if editor:
            node_list.append(nodes.inline('In ', 'In '))
            node_list.append(ApaStyle.get_authors(editor))
            node_list.append(nodes.inline(' (eds), ', ' (eds), '))
        return node_list

    @staticmethod
    def get_pages(pages, **kwargs):
        node_list = []
        if pages:
            node_list.append(nodes.inline('pp', 'pp'))
            node_list.append(nodes.inline(pages, pages))
            node_list.append(nodes.inline('. ', '. '))
        return node_list

    @staticmethod
    def get_volume(volume, **kwargs):
        """Get publication volume"""
        node_list = []
        fields = kwargs.get('fields', {})
        if volume:
            node_list.append(nodes.inline('Vol. ', 'Vol. '))
            node_list.append(nodes.inline(volume, volume))
            if fields.get('number'):
                node_list.append(nodes.inline(' ', ' '))
            else:
                node_list.append(nodes.inline('. ', '. '))
        return node_list

    @staticmethod
    def get_number(number, **kwargs):
        """Get publication number"""
        node_list = []
        if number:
            node_list.append(nodes.inline('No. ', 'No. '))
            node_list.append(nodes.inline(number, number))
            node_list.append(nodes.inline('. ', '. '))
        return node_list

    @staticmethod
    def get_year(year, **kwargs):
        node_list = []
        if year:
            year = latex_decode(year)
            node_list.append(
                nodes.inline(year, ' ({})'.format(year), classes=['year']))
            node_list.append(nodes.inline('. ', '. '))
        return node_list

    @staticmethod
    def get_title(title, **kwargs):
        node_list = []
        if title:
            node_list.append(nodes.inline(title, title, classes=['title']))
            node_list.append(nodes.inline('.  ', '.  '))
        return node_list

    @staticmethod
    def get_booktitle(booktitle, **kwargs):
        node_list = []
        fields = kwargs.get('fields' or {})
        if booktitle:
            title = latex_decode(booktitle)
            node_list.append(nodes.emphasis(
                title, title, classes=['publication']))
            if fields.get('volume'):
                node_list.append(nodes.inline(', ', ', '))
            else:
                node_list.append(nodes.inline('. ', '. '))
        return node_list

    @staticmethod
    def get_journal(journal, **kwargs):
        return ApaStyle.get_booktitle(journal, **kwargs)

    def get_nodes(self, ref):
        publication = self.publications[ref.type]
        ref_node = nodes.paragraph('', '', classes=[ref.type, 'reference'])
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
    required_arguments = 0
    optional_arguments = 0

    # TODO: Implement support for multiple bib files
    option_spec = {
        'path': directives.unchanged,
    }

    def get_reference_node(self, ref):
        node = nodes.inline('','', classes=[ref.type, 'reference'])

        style = ApaStyle()

        return style.get_nodes(ref)
        # print(ref.type, ref)
        # # Authors

        # node_list = get_authors(ref.persons.get('author', []))
        # for item in node_list:
        #     node += item

        # node_list = get_year(ref.fields.get('year'))
        # for item in node_list:
        #     node += item

        # # Title
        # node_list = get_title(ref.fields.get('title'))
        # for item in node_list:
        #     node += item


        # # Publication
        # # TODO: handle other types of publications
        # pub = ref.fields.get('journal') or ref.fields.get('booktitle')
        # if pub:
        #     pub = latex_decode(pub)
        #     node += nodes.emphasis(pub, pub, classes=['publication'])
        #     node += nodes.inline('.', '.')

        # vol = ref.fields.get('volume')
        # if vol:
        #     vol = latex_decode(vol)
        #     node += nodes.inline(vol, vol, classes=['volume'])
        #     node += nodes.inline(':', ':')

        # pages = ref.fields.get('pages')
        # if pages:
        #     pages = latex_decode(pages)
        #     node += nodes.inline(pages, pages, classes=['pages'])
        #     node += nodes.inline(', ', ', ')



        # return node

    def run(self):
        """
        Generate the definition list that displays the actual references.
        """
        env = self.state.document.settings.env
        keys = env.domaindata['cite']['keys']
        env.domaindata['cite']['refdoc'] = env.docname

        citations = env.domains['cite'].citations

        # TODO: implement
        #env.domaindata['cite']['refdocs'][env.docname] = Citations(env, path)

        # Build the references list
        # TODO: Make this an enumerated_list or field_list maybe?
        node = nodes.definition_list()
        node.document = self.state.document
        node['classes'].append('references')

        items = []
        for i, key in enumerate(keys):
            term = nodes.term('', '')

            # TODO: Allow the format of the reference list be configurable
            # if env.domaindata['cite']['conf']['style'] == 'super':
            #   term.children = [nodes.superscript('', i+1)]
            # else:
            #   term.children = [nodes.inline('', "%s) " % (i+1))]

            nid = "citation-%s" % nodes.make_id(key)
            definition = self.get_reference_node(citations.get(key))

            li = nodes.definition_list_item('', term, definition)
            li[0]['ids'].append(nid)
            li[0]['names'].append(nid)
            items.append(li)
        node.extend(item for item in items)

        return [node]

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
        self.citations = Citations(env)

    def resolve_xref(self, env, fromdocname, builder,
                                             typ, target, node, contnode):

        refdoc = env.domaindata['cite'].get('refdoc')
        if not refdoc:
            env.warn(fromdocname  , 'no `refs` directive found; citations will have dead links', node.line)
            refuri = ''
        else:
            refuri = builder.get_relative_uri(fromdocname, refdoc)

        for nd in node.children:
            if isinstance(nd, nodes.pending):
                nd.details['refs'] = []
                for key in nd.details.pop('keys'):
                    ref = self.citations.get(key)
                    if ref is None:
                        continue
                    nd.details['refs'].append(ref)

                transform = nd.transform(**nd.details)
                node = transform.cite(typ, refuri)

        return node

def setup(app):
    app.add_config_value('natbib', DEFAULT_CONF, 'env')
    app.add_domain(CitationDomain)
    app.add_stylesheet('css/style.css')
