import math
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

        # save the result into csv file
        """tweet_id_num = 1
        with open('results.csv', 'a', encoding='utf-8') as fp:
            for p in relevant_docs:
                if tweet_id_num <= 10:
                    s = ("Tweet id: " + "{" + p + "}" + " Score: " + "{" + str(tweet_id_num) + "}" + "\n")
                    tweet_id_num += 1
                    fp.write(s)"""

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
        last_dict = {}
        relevant_docs = {}
        inverted_keys = []
        for key in self._indexer.inverted_idx.keys():
            inverted_keys.append(key)
        for term in query_as_list:  # remove all term with term frequency 1
            for tuple_key in inverted_keys:
                if tuple_key[0] == term or tuple_key[0] == term.lower() or tuple_key[0] == term.upper():
                    try:
                        TF_IDF = self._indexer.inverted_idx[tuple_key][0][1]
                        """if tuple_key[1] not in relevant_docs.keys():
                            relevant_docs[tuple_key[1]] = 1  # TF-IDF
                        else:
                            relevant_docs[tuple_key[1]] += 1"""
                        TF = self._indexer.inverted_idx[tuple_key][0][2]
                        if tuple_key[1] not in relevant_docs.keys():
                            relevant_docs[tuple_key[1]] = [pow(TF_IDF, 2), TF_IDF, TF]  # TF-IDF
                        else:
                            relevant_docs[tuple_key[1]][0] += pow(TF_IDF, 2)
                            relevant_docs[tuple_key[1]][1] += TF_IDF
                            relevant_docs[tuple_key[1]][2] += TF

                    except:
                        print('term {} not found in posting'.format(term))

        # cosine similarity
        len_query = len(query_as_list)
        for term in relevant_docs.keys():
            pow_TFIDF = relevant_docs[term][0]
            TFIDF = relevant_docs[term][1]
            square_root = math.sqrt(pow_TFIDF*len_query)
            cosine = (TFIDF/square_root)
            #relevant_docs[term] = cosine
            #print(relevant_docs)
            if len(query_as_list) > 2:
                if relevant_docs[term][2] > 1:
                    last_dict[term] = cosine
            else:
                last_dict[term] = cosine

        #sorted_relevant_docs = {k: v for k, v in sorted(relevant_docs.items(), key=lambda item: item[1], reverse=True)}
        sorted_relevant_docs = {k: v for k, v in sorted(last_dict.items(), key=lambda item: item[1], reverse=True)}

        return sorted_relevant_docs
