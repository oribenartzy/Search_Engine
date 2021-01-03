import pandas as pd

import configuration
from WordNet_ranker import WordNet_ranker
from reader import ReadFile
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
        # utils.save_obj(self._indexer.inverted_idx, "inverted_idx")

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        self._indexer.load_index(fn)

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_precomputed_model(self):
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
        wordNet = WordNet_ranker(query)
        new_query = wordNet.extend_query()
        searcher = Searcher(self._parser, self._indexer, model=self._model)
        return searcher.search(new_query)  # TODO: add K results


def main():
    empty_query = False
    """config.set__toStem(stemming)
    config.set__corpusPath(corpus_path)
    config.set__savedFileMainFolder(output_path)
    k = num_docs_to_retrieve
    query = queries
    empty_query = False
    # if query is empty
    if type(query) is list:  # if queries is a list
        if len(query) == 0 or (len(query) == 1 and query[0] == ""):
            empty_query = True
            with open('results.csv', 'a', encoding='utf-8') as fp:
                s = "Tweet id: " + "{}" + " Score: " + "{}" + "\n"
                fp.write(s)
            print("Tweet id: " + "{}" + " Score: " + "{}" + "\n")
    if type(query) is str:  # if queries is a text file
        with open(query, encoding='utf-8') as f:
            for line in f:
                if line == "":
                    empty_query = True
                    with open('results.csv', 'a', encoding='utf-8') as fp:
                        s = "Tweet id: " + "{}" + " Score: " + "{}" + "\n"
                        fp.write(s)
                    print("Tweet id: " + "{}" + " Score: " + "{}" + "\n")"""
    if not empty_query:
        config = ConfigClass()
        corpus_path = configuration.ConfigClass.get__corpusPath(config)
        Search_Engine = SearchEngine(config)
        Search_Engine.build_index_from_parquet(corpus_path)
        # query = input("Please enter a query: ")
        # k = int(input("Please enter number of docs to retrieve: "))
        # inverted_index = self.load_index()
        """final_tweets = search_and_rank_query(query, inverted_index, k, lda)
        for query in final_tweets:
            num = 1
            for res in query:
                print("Tweet id: " + "{" + res + "}" + " Score: " + "{" + str(num) + "}")
                num += 1"""
        final_tweets = Search_Engine.search(["Children are “almost immune from this disease.”"])
        print("num of relevant:", final_tweets[0])
        num = 1
        for tweet_id in final_tweets[1].keys():
            print("Tweet id: " + "{" + tweet_id + "}" + " Score: " + "{" + str(num) + "}")
            num += 1