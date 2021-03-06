import re
from datetime import datetime

import pandas as pd
from nltk.corpus import stopwords

import configuration
from WordNet_ranker import WordNet_ranker
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
import utils


# DO NOT CHANGE THE CLASS NAME
class SearchEngine:

    num_of_tweets = 0

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation, but you must have a parser and an indexer.
    def __init__(self, config=None):
        self._config = config
        self._parser = Parse()
        self._indexer = Indexer(config)
        self._model = None

    def get_num_of_tweets(self):
        return self.num_of_tweets
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def build_index_from_parquet(self, fn):
        """
        Reads parquet file and passes it to the parser, then indexer.
        Input:
            fn - path to parquet file
        Output:
            No output, just modifies the internal _indexer object.
        """
        df = pd.read_parquet(fn, engine="pyarrow")
        documents_list = df.values.tolist()
        self.num_of_tweets = len(documents_list)

        # Iterate over every document in the file
        number_of_documents = 0
        for idx, document in enumerate(documents_list):
            # parse the document
            parsed_document = self._parser.parse_doc(document)
            parsed_document.num_of_tweets = self.num_of_tweets
            number_of_documents += 1
            # index the document data
            self._indexer.add_new_doc(parsed_document)
        print('Finished parsing and indexing.')
        # TODO: check indexer saving
        utils.save_obj(self._indexer.inverted_idx, "inverted_idx")

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        inverted_idx = self._indexer.load_index(fn)
        return inverted_idx

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_precomputed_model(self, model_dir=None):
        """
        Loads a pre-computed model (or models) so we can answer queries.
        This is where you would load models like word2vec, LSI, LDA, etc. and
        assign to self._model, which is passed on to the searcher at query time.
        """
        pass

        # DO NOT MODIFY THIS SIGNATURE
        # You can change the internal implementation as you see fit.

    def search(self, query):
        """
        Executes a query over an existing index and returns the number of
        relevant docs and an ordered list of search results.
        Input:
            query - string.
        Output:
            A tuple containing the number of relevant search results, and
            a list of tweet_ids where the first element is the most relavant
            and the last is the least relevant result.
        """
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
        wordNet = WordNet_ranker(query_as_list)
        new_query = wordNet.extend_query()
        searcher = Searcher(self._parser, self._indexer, model=self._model)
        return searcher.search(new_query)  # TODO: add K results


def main():
    config = ConfigClass()
    corpus_path = configuration.ConfigClass.get__corpusPath(config)
    Search_Engine = SearchEngine(config)
    Search_Engine.build_index_from_parquet(corpus_path)
    print(datetime.now())
    final_tweets = Search_Engine.search("Children are ???almost immune from this disease.???")
    print(datetime.now())
    print("num of relevant:", final_tweets[0])
    num = 1
    for tweet_id in final_tweets[1].keys():
        if num >= 5:
            print("Tweet id: " + "{" + tweet_id + "}" + " Score: " + "{" + str(num) + "}")
            num += 1