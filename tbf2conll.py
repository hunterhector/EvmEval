__author__ = 'zhengzhongliu'

"""
    A simple piece of python code that could take a token table, and
    some event annotations, and produce the conll format data for
    coreference evaluation.

    This is used together with the scorer, but this can be used on its
    own.

    Author: Zhengzhong Liu ( liu@cs.cmu.edu )
"""


class ConllConverter:
    def __init__(self, id2token_map, id2span_map):
        """
        :param id2token_map: a dict, map from token id to its string
        :param id2span_map: a dict, map from token id to its character span
        :return:
        """
        self.id2token = id2token_map
        self.id2span = id2span_map
        pass

    def prepare_conll_lines(self):
        lines = []
        for token_id, token in self.id2token.iteritems():
            span = self.id2span[token_id]
            lines.append("%s\t%s\t%d\t%d" % (token_id, token, span[0], span[1]))
        return lines