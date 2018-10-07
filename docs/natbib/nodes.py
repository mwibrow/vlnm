"""
    New Nodes
    ~~~~~~~~~
"""
import docutils.nodes

class CitationNode(docutils.nodes.Inline, docutils.nodes.Element):
    """
    CitationNode replaced by Bibliography transform.
    """
    def __init__(self, *args, data=None, **kwargs):
        super(CitationNode, self).__init__(*args, **kwargs)
        self.data = data

class BibliographyNode(docutils.nodes.General, docutils.nodes.Element):
    """
    BibliographyNode replaced by Bibliography transform.
    """
    def __init__(self, *args, data=None, **kwargs):
        super(BibliographyNode, self).__init__(*args, **kwargs)
        self.data = data
