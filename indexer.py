# DO NOT MODIFY CLASS NAME
import copy
import collections
import os

from search_engine_best import SearchEngine


class Indexer:

    posting_file_num = 1
    file_counter = 1
    file_name_list = []
    finished_inverted = False
    tweet_line_dict = {}
    line_number = 0
    cur_num_of_tweets = 0
    writen_terms = 0
    zipf = {}
    num_of_all_tweets = 0


    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def __init__(self, config):
        self.postingDict = {}
        self.config = config
        self.inverted_idx = {}
        self.temp_posting_dict = {}
        self.copy_posting_dict = {}
        self.sorted_posting_dict = {}
        self.tf_idf_dict = {}
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
        num_of_all_tweets = SearchEngine.get_num_of_tweets()
        self.cur_num_of_tweets += 1
        document_dictionary = document.term_doc_dictionary

        # Update tf-idf dict
        tweet_id = document.tweet_id
        self.tf_idf_dict[tweet_id] = []       # max_tf         # distinct_words        # tweet_length
        self.tf_idf_dict[tweet_id].append((document.max_tf, document.distinct_words, document.doc_length))

        # Go over each term in the doc
        if document.doc_length != -1:  # if NOT RT
            for term in document_dictionary.keys():
                try:
                    # Update posting
                    if term not in self.temp_posting_dict.keys():
                        self.temp_posting_dict[term] = []
                        self.temp_posting_dict[term].append([document.tweet_id, document_dictionary[term][0], document_dictionary[term][1]])

                    else:
                        self.temp_posting_dict[term].append([document.tweet_id, document_dictionary[term][0], document_dictionary[term][1]])
                except:
                    print('problem with the following key {}'.format(term[0]))
            self.tweet_line_dict[document.tweet_id] = self.line_number  # tweet_id, line_num
            self.line_number += 1

        if self.cur_num_of_tweets == num_of_all_tweets and document.doc_length != -1:  # last tweet
            # sort the dict
            self.sorted_posting_dict = collections.OrderedDict(sorted(self.temp_posting_dict.items()))
            #print("*********************************************")
            # make a txt file out of the sorted_posting_dict
            with open(self.path+'posting.txt', 'w', encoding='utf-8') as fp:
                for p in self.sorted_posting_dict.items():
                    for str1 in p[1]:
                        self.writen_terms += 1
                        s = p[0] + ":" + str(str1[0]) + "-" + str(str1[1]) + "-" + str(str1[2])[1:-1]
                        fp.write(s+"\n")
            #print("*********************************************")
            # empty dicts
            self.temp_posting_dict.clear()
            self.sorted_posting_dict.clear()
            self.file_counter += 1

        # create new file of term_dict
        if self.cur_num_of_tweets == num_of_all_tweets:  # last tweet
            # sort the dict
            self.sorted_term_dict = collections.OrderedDict(sorted(document.term_dict.items()))
            # make a txt file out of the term_dict
            with open(self.path+'posting.txt', 'a', encoding='utf-8') as fp:
                for p in self.sorted_term_dict.items():
                    if len(p[1]) > 1:  # more then 2 tweet_id
                        for str1 in p[1]:
                            self.writen_terms += 1
                            s = p[0] + ":" + str(str1[0]) + "-" + str(str1[1]) + "-100"
                            fp.write(s + "\n")
            # empty sorted_term_dict
            self.sorted_term_dict.clear()
            self.file_counter += 1
            self.create_inverted_index(self.path+'posting.txt')

        # Change all capital letter terms in dict
        if self.finished_inverted:
            for term in document.capital_letter_dict:
                if document.capital_letter_dict[term]:  # if the term is upper is all corpus
                    if term.lower() in self.inverted_idx:
                        self.inverted_idx[term] = self.inverted_idx[term.lower()]
                        del self.inverted_idx[term.lower()]


    def create_inverted_index(self, file_name):
        with open(self.path+file_name, buffering=2000000, encoding='utf-8') as f:
            num_of_lines = 1
            count = 1
            posting_string = []
            post_line = self.writen_terms / 3
            for line in f:
                posting_string.append(line)
                split_line = line.split(":")
                term = split_line[0]
                #tf = line.split("-")[-2]
                if term not in self.inverted_idx.keys():
                    self.inverted_idx[term] = []
                    self.inverted_idx[term].append([1, self.path+'posting' + str(self.posting_file_num) + '.txt'])  # num of tweets, pointer
                else:
                    self.inverted_idx[term][0][0] += 1
                # break the big posting file into smaller files
                if num_of_lines == int(post_line):
                    if count <= 2:
                        #print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                        with open(self.path+'posting' + str(self.posting_file_num) + '.txt', 'w', encoding='utf-8') as fp:
                            for p in posting_string:
                                fp.write(p)
                        #print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                        self.posting_file_num += 1
                        num_of_lines = 0
                        posting_string = []
                        count += 1
                num_of_lines += 1

            # adding the last terms to new posting file
            if len(posting_string) > 0:
                #print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                with open(self.path+'posting' + str(self.posting_file_num) + '.txt', 'w', encoding='utf-8') as fp:
                    for p in posting_string:
                        fp.write(p)
                #print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                self.posting_file_num += 1
        if self.file_counter > self.posting_file_num:
            os.remove(self.path+self.file_name_list[0])
        self.finished_inverted = True




    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        raise NotImplementedError

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def save_index(self, fn):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """
        raise NotImplementedError

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _is_term_exist(self, term):
        """
        Checks if a term exist in the dictionary.
        """
        return term in self.postingDict

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def get_term_posting_list(self, term):
        """
        Return the posting list from the index for a term.
        """
        return self.postingDict[term] if self._is_term_exist(term) else []
