from nltk.corpus import wordnet as wn


class WordNet_ranker:

    def __init__(self, query):
        self.query = query

    def extend_query(self):
        word_to_add = []
        for term in self.query:
            synonyms = []
            if len(wn.synsets(term)) > 0:
                syn = wn.synsets(term)[0]
                #print("syn", syn)  # Synset('child.n.01')
                #print("name", syn.name())  # child.n.01
                #print(syn.lemmas()[0].name())  # child
                for rule in syn.lemmas():
                    synonyms.append(rule.name())
                res = []
                for word in synonyms:
                    wordFromList1 = wn.synsets(term)[0]
                    wordFromList2 = wn.synsets(word)[0]
                    s = wordFromList1.wup_similarity(wordFromList2)
                    res.append(s)
                new_term = ""
                max = 0
                index = 0
                for num in res:
                    if num is not None:
                        if num > max:
                            if synonyms[index] != term:
                                if "_" in synonyms[index]:
                                    word = synonyms[index].replace("_", " ")
                                    new_term = word
                                    max = num

                                else:
                                    new_term = synonyms[index]
                                    max = num
                    index += 1
                if new_term != "":
                    word_to_add.append(new_term)
        self.query.extend(word_to_add)
        return self.query