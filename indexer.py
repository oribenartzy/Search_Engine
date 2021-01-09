# DO NOT MODIFY CLASS NAME
import math
import pickle

class Indexer:

    finished_inverted = False
    cur_num_of_tweets = 0
    num_of_all_tweets = 0
    N_tweets = 0
    save_inverted = False


    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def __init__(self, config):
        self.config = config
        self.inverted_idx = {}
        self.tweet_info_dict = {}
        self.df_dict = {}
        self.sorted_term_dict = {}
        self.path = self.config.get__savedFileMainFolder()+"\\"

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        num_of_all_tweets = document.num_of_tweets
        self.cur_num_of_tweets += 1

        document_dictionary = document.term_doc_dictionary

        # Update tweet_info_dict
        """tweet_id = document.tweet_id
        self.tweet_info_dict[tweet_id] = []       # max_tf         # distinct_words        # tweet_length
        self.tweet_info_dict[tweet_id].append((document.max_tf, document.distinct_words, document.doc_length))"""

        # Go over each term in the doc
        if document.doc_length != -1:  # if NOT RT
            self.N_tweets += 1
            for term in document_dictionary.keys():
                try:
                    if term not in self.df_dict.keys():
                        self.df_dict[term] = 1  # DF
                    else:
                        self.df_dict[term] += 1  # DF

                    # building inverted idx
                    key = (term, document.tweet_id)
                    if key not in self.inverted_idx.keys():
                        self.inverted_idx[key] = []   # TF/max_tf, TF*IDF, TF
                        self.inverted_idx[key].append([document_dictionary[term][0]/document.max_tf, 0, document_dictionary[term][0]])
                except:
                    print('problem with the following key {}'.format(term[0]))

        if self.cur_num_of_tweets == num_of_all_tweets and document.doc_length != -1:
            for term in self.inverted_idx.keys():
                try:
                    # Update inverted_idx with TF*IDF
                    IDF = math.log(self.N_tweets/self.df_dict[term[0]], 2)  # LOG(N/DF)
                    self.inverted_idx[term][0][1] = self.inverted_idx[term][0][0]*IDF  # TF*IDF
                except:
                    print('problem with the following key {}'.format(term[0]))

        # remove all term with term frequency < 8
        if self.cur_num_of_tweets == num_of_all_tweets and document.doc_length != -1:  # last tweet
            inverted_keys = []
            for key in self.inverted_idx.keys():
                inverted_keys.append(key)
            for tuple_key in inverted_keys:
                if self.df_dict[tuple_key[0]] < 8:
                    del self.inverted_idx[tuple_key]

            # count num of term in dict
            """num = 0
            for term in self.df_dict.keys():
                if self.df_dict[term] < 5:
                    num += 1
            print("num of word without 8", len(self.df_dict)-num)
            print("num of all word", len(self.df_dict))"""

        # adding terms to inverted idx
        if self.cur_num_of_tweets == num_of_all_tweets:  # last tweet
            for p in document.term_dict.items():
                if len(p[1]) > 1:  # more then 2 tweet_id
                    for str1 in p[1]:
                        key = (p[0], str1[0])
                        if key not in self.inverted_idx.keys():
                            self.inverted_idx[key] = []  # TF/|D|, TF*IDF
                            self.inverted_idx[key].append([str1[1], 1, 1])

            # empty sorted_term_dict
            self.sorted_term_dict.clear()
            self.finished_inverted = True

        # Change all capital letter terms in dict
        if self.finished_inverted:
            inverted_keys = []
            for key in self.inverted_idx.keys():
                inverted_keys.append(key)
            for term in document.capital_letter_dict.keys():
                for tuple_key in inverted_keys:
                    if tuple_key[0] == term.lower():
                        new_tuple = (term, tuple_key[1])
                        self.inverted_idx[new_tuple] = self.inverted_idx[tuple_key]
                        del self.inverted_idx[tuple_key]
            self.save_inverted = True


        """if self.cur_num_of_tweets == num_of_all_tweets and self.save_inverted == True:  # finished inverted
            #self.save_index('idx_bench.pkl')
            #self.load_index('idx_bench.pkl')"""

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        file_name = fn
        open_file = open(file_name, "rb")
        loaded_list = pickle.load(open_file)
        open_file.close()
        #print(loaded_list)
        self.inverted_idx = loaded_list[0]

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def save_index(self, fn):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """
        file_name = fn
        open_file = open(file_name, "wb")
        sample_list = [self.inverted_idx]
        pickle.dump(sample_list, open_file)
        open_file.close()

    # feel free to change the signature and/or implementation of this function
    # or drop altogether.
    def _is_term_exist(self, term):
        """
        Checks if a term exist in the dictionary.
        """

        return term in self.df_dict

