import os


class Config:
    """
    Hold configuration variable for evaluation. These variables
    should not be changed during evaluation.
    """

    def __init__(self):
        pass

    # TBF file formats.
    comment_marker = "#"
    bod_marker = "#BeginOfDocument"  # mark begin of a document
    eod_marker = "#EndOfDocument"  # mark end of a document
    relation_marker = "@"  # mark start of a relation
    coreference_relation_name = "Coreference"  # mark coreference
    after_relation_name = "After"  # mark after

    directed_relations = {"After", "Subevent"}

    token_joiner = ","
    span_seperator = ";"
    span_joiner = ","

    missing_attribute_place_holder = "NOT_ANNOTATED"

    default_token_file_ext = ".tab"
    default_token_offset_fields = [2, 3]

    # We should probably remove this as a whole.
    invisible_words = {}

    # Attribute names, these are the same order as they appear in submissions.
    attribute_names = ["mention_type", "realis_status"]

    # Conll related settings.
    conll_bod_marker = "#begin document"
    conll_eod_marker = "#end document"

    conll_gold_file = None
    conll_sys_file = None

    conll_out = None

    # By default, this reference scorer is shipped with the script. We do it this way so that we can call the script
    # successfully from outside scripts.
    relative_perl_script_path = "/reference-coreference-scorers-8.01/scorer.pl"
    conll_scorer_executable = os.path.dirname(os.path.realpath(__file__)) + relative_perl_script_path

    skipped_metrics = {"ceafm"}

    zero_for_empty_metrics = {"muc"}

    token_miss_msg = "Token ID [%s] not found in token list, the score file provided is incorrect."

    coref_criteria = ((0, "mention_type"),)

    possible_coref_mapping = [((-1, "span_only"),),
                              ((0, "mention_type"),), ((1, "realis_status"),),
                              ((0, "mention_type"), (1, "realis_status"))]

    canonicalize_types = True

    # Temporal link settings.

    temporal_result_dir = None

    temporal_gold_dir = "gold"

    temporal_sys_dir = "sys"

    temporal_out = "seq.out"

    temporal_out_cluster = "seq_cluster.out"

    temp_eval_executable = os.path.dirname(os.path.realpath(__file__)) + "/evaluation-relations/temporal_evaluation.py"

    no_temporal_validation = False


class EvalMethod:
    """
    Two different evaluation methods
    Char based evaluation is not supported and is only here for legacy reasons.
    """

    def __init__(self):
        pass

    Token, Char = range(2)


class MutableConfig:
    """
    Some configuration that might be changed at setup. Default
    values are set here. Do not modify these variables outside
    the Main() function (i.e. outside the setup stage)
    """

    def __init__(self):
        pass

    remove_conll_tmp = False
    eval_mode = EvalMethod.Char
    coref_mention_threshold = 1.0
