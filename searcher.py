import re

from nltk.corpus import stopwords

from ranker import Ranker
import utils


# DO NOT MODIFY CLASS NAME
class Searcher:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit. The model 
    # parameter allows you to pass in a precomputed model that is already in 
    # memory for the searcher to use such as LSI, LDA, Word2vec models. 
    # MAKE SURE YOU DON'T LOAD A MODEL INTO MEMORY HERE AS THIS IS RUN AT QUERY TIME.
    def __init__(self, parser, indexer, model=None):
        self._parser = parser
        self._indexer = indexer
        self._ranker = Ranker()
        self._model = model

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def search(self, query, k=None):
        """ 
        Executes a query over an existing index and returns the number of 
        relevant docs and an ordered list of search results (tweet ids).
        Input:
            query - string.
            k - number of top results to return, default to everything.
        Output:
            A tuple containing the number of relevant search results, and 
            a list of tweet_ids where the first element is the most relavant 
            and the last is the least relevant result.
        """
        queries_list = []
        if type(query) is list:  # if queries is a list
            for one_query in query:
                queries_list.append(one_query)
        if type(query) is str:  # if queries is a text file
            with open(query, encoding='utf-8') as f:
                for line in f:
                    if line != "\n":
                        queries_list.append(line)
        query_num = 1
        tweet_id_num = 1
        for query in queries_list:
            query_as_list = self._parser.parse_sentence(query, 0)
            original_query_list = query.split(" ")
            stop_words = stopwords.words('english')
            original_query_list = [w for w in original_query_list if w not in stop_words]
            # find long terms and upper case words
            counter = 0
            while counter < len(original_query_list):
                len_term = 1
                word = original_query_list[counter]
                if word.isupper():  # NBA
                    if word.find("\n") != -1:
                        word = word[:-1]
                        if word.find(".") != -1:
                            word = word[:-1]
                    query_as_list.append(word)
                elif len(word) > 1 and re.search('[a-zA-Z]', word) and word[0].isupper():  # upper first char
                    term = word
                    if original_query_list.index(word) + 1 < len(original_query_list):
                        index = original_query_list.index(word) + 1
                        while index < len(original_query_list):  # find all term
                            if len(original_query_list[index]) > 1 and re.search('[a-zA-Z]',
                                                                                 original_query_list[index]) and \
                                    original_query_list[index][0].isupper():
                                new_word2 = original_query_list[index][0] + original_query_list[index][
                                                                            1:].lower()  # Donald Trump
                                term += " " + new_word2
                                index += 1
                                len_term += 1
                            else:
                                break
                        if len_term > 1:
                            query_as_list.append(term)
                counter += len_term

            relevant_docs = self._relevant_docs_from_posting(query_as_list)
            n_relevant = len(relevant_docs)
            with open('results.csv', 'a', encoding='utf-8') as fp:
                for p in relevant_docs:  # TODO: [:k]
                    s = ("Tweet id: " + "{" + p + "}" + " Score: " + "{" + str(tweet_id_num) + "}" + "\n")
                    tweet_id_num += 1
                    fp.write(s)
            query_num += 1

            # ranked_doc_ids = Ranker.rank_relevant_docs(relevant_docs)
        return n_relevant, relevant_docs

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _relevant_docs_from_posting(self, query_as_list):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query_as_list: parsed query tokens
        :return: dictionary of relevant documents mapping doc_id to document frequency.
        """
        relevant_docs = {}
        for term in query_as_list:
            if term in self._indexer.inverted_idx:
                with open("posting.txt", buffering=2000000, encoding='utf-8') as f:
                    for line in f:
                        term_list = line.split(":")
                        key = term_list[0]
                        value = term_list[1]
                        if " " not in key:
                            key = key.lower()
                        if term == key:
                            try:
                                split = value.split("-")
                                tweet_id = split[0]
                                occur = split[1]  # tf
                                if tweet_id not in relevant_docs.keys():
                                    relevant_docs[tweet_id] = float(occur)*self._indexer.inverted_idx[term][0][1]  # TF-IDF
                                else:
                                    relevant_docs[tweet_id] += float(occur)*self._indexer.inverted_idx[term][0][1]
                            except:
                                print('term {} not found in posting'.format(term))
        sorted_relevant_docs = {k: v for k, v in sorted(relevant_docs.items(), key=lambda item: item[1], reverse=True)}

        return sorted_relevant_docs
