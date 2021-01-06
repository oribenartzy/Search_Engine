from spellchecker import SpellChecker
from nltk import word_tokenize
spell_checker = SpellChecker()


def correct(query: str):
    """
    This function corrects the words those who have a spelling correction,
    and returns a corrected query.
    """
    tokens = word_tokenize(query)
    for ind, token in enumerate(tokens):
        tokens[ind] = spell_checker.correction(token)
    corrected_query = " ".join([x for x in tokens])
    return corrected_query