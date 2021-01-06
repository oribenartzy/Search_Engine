from spellchecker import SpellChecker

spell_checker = SpellChecker()


def correct_query(query_as_list):
    new_query = []
    for idx, word in enumerate(query_as_list):
        query_as_list[idx] = spell_checker.correction(word)  # changing the spelling errors
    new_query.extend([x for x in query_as_list])
    return new_query
