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
        relevant_docs = self._relevant_docs_from_posting(query)
        n_relevant = len(relevant_docs)
        tweet_id_num = 1
        with open('results.csv', 'a', encoding='utf-8') as fp:
            for p in relevant_docs:
                if tweet_id_num <= 5:
                    s = ("Tweet id: " + "{" + p + "}" + " Score: " + "{" + str(tweet_id_num) + "}" + "\n")
                    tweet_id_num += 1
                    fp.write(s)

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
        inverted_keys = []
        for key in self._indexer.inverted_idx.keys():
            inverted_keys.append(key)
        for term in query_as_list:  # remove all term with term frequency 1
            for tuple_key in inverted_keys:
                if tuple_key[0] == term or tuple_key[0] == term.lower() or tuple_key[0] == term.upper():
                    try:
                        TF_IDF = self._indexer.inverted_idx[tuple_key][0][1]
                        if tuple_key[1] not in relevant_docs.keys():
                            relevant_docs[tuple_key[1]] = 1  # TF-IDF
                        else:
                            relevant_docs[tuple_key[1]] += 1
                    except:
                        print('term {} not found in posting'.format(term))


        """relevant_docs = {}
        for term in query_as_list:
            if term in self._indexer.inverted_idx or term.upper() in self._indexer.inverted_idx or term.lower() in self._indexer.inverted_idx:
                with open("posting_pkl.txt", buffering=2000000, encoding='utf-8') as f:
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
                                IDF = 0
                                if term in self._indexer.inverted_idx:
                                    IDF = self._indexer.inverted_idx[term][0][1]
                                if term.upper() in self._indexer.inverted_idx:
                                    IDF = self._indexer.inverted_idx[term.upper()][0][1]
                                if term.lower() in self._indexer.inverted_idx:
                                    IDF = self._indexer.inverted_idx[term.lower()][0][1]
                                TF_IDF = float(occur)*IDF
                                if tweet_id not in relevant_docs.keys():
                                    relevant_docs[tweet_id] = 1  # TF-IDF
                                else:
                                    relevant_docs[tweet_id] += 1
                            except:
                                print('term {} not found in posting'.format(term))"""
        sorted_relevant_docs = {k: v for k, v in sorted(relevant_docs.items(), key=lambda item: item[1], reverse=True)}

        return sorted_relevant_docs
