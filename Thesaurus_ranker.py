from nltk.corpus import lin_thesaurus as thesaurus

class Thesaurus_ranker:

    def __init__(self, query):
        self.query = query

    def extend_query(self):
        word_to_add = []
        if len(self.query) == 0:
            return []
        for word in self.query:
            list_of_thes = thesaurus.synonyms(word)
            #print(list_of_thes)
            for i in range(len(list_of_thes)):
                if len(list_of_thes[i][1]) > 1:
                    word_to_add.append(list(list_of_thes[i][1])[0])

        self.query.extend(word_to_add)
        return self.query