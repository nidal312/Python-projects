# Copyright 2020 Paul Lu
import sys
import copy     # for deepcopy()
from heapq import nlargest #for top-n dict

Debug = False   # Sometimes, print for debugging
InputFilename = "file.input.txt"
TargetWords = [
        'outside', 'today', 'weather', 'raining', 'nice', 'rain', 'snow',
        'day', 'winter', 'cold', 'warm', 'snowing', 'out', 'hope', 'boots',
        'sunny', 'windy', 'coming', 'perfect', 'need', 'sun', 'on', 'was',
        '-40', 'jackets', 'wish', 'fog', 'pretty', 'summer'
        ]


def open_file(filename=InputFilename):
    try:
        f = open(filename, "r")
        return(f)
    except FileNotFoundError:
        # FileNotFoundError is subclass of OSError
        if Debug:
            print("File Not Found")
        return(sys.stdin)
    except OSError:
        if Debug:
            print("Other OS Error")
        return(sys.stdin)


def safe_input(f=None, prompt=""):
    try:
        # Case:  Stdin
        if f is sys.stdin or f is None:
            line = input(prompt)
        # Case:  From file
        else:
            assert not (f is None)
            assert (f is not None)
            line = f.readline()
            if Debug:
                print("readline: ", line, end='')
            if line == "":  # Check EOF before strip()
                if Debug:
                    print("EOF")
                return("", False)
        return(line.strip(), True)
    except EOFError:
        return("", False)


class C274:
    def __init__(self):
        self.type = str(self.__class__)
        return

    def __str__(self):
        return(self.type)

    def __repr__(self):
        s = "<%d> %s" % (id(self), self.type)
        return(s)


class ClassifyByTarget(C274):
    def __init__(self, lw=[]):
        # FIXME:  Call superclass, here and for all classes
        self.type = str(self.__class__)
        self.allWords = 0
        self.theCount = 0
        self.nonTarget = []
        self.set_target_words(lw)
        self.initTF()
        return

    def initTF(self):
        self.TP = 0
        self.FP = 0
        self.TN = 0
        self.FN = 0
        return

    def get_TF(self):
        return(self.TP, self.FP, self.TN, self.FN)

    # FIXME:  Use Python properties
    #     https://www.python-course.eu/python3_properties.php
    def set_target_words(self, lw):
        # Could also do self.targetWords = lw.copy().  Thanks, TA Jason Cannon
        self.targetWords = copy.deepcopy(lw)
        return

    def get_target_words(self):
        return(self.targetWords)

    def get_allWords(self):
        return(self.allWords)

    def incr_allWords(self):
        self.allWords += 1
        return

    def get_theCount(self):
        return(self.theCount)

    def incr_theCount(self):
        self.theCount += 1
        return

    def get_nonTarget(self):
        return(self.nonTarget)

    def add_nonTarget(self, w):
        self.nonTarget.append(w)
        return

    def print_config(self):
        print("-------- Print Config --------")
        ln = len(self.get_target_words())
        print("TargetWords Hardcoded (%d): " % ln, end='')
        print(self.get_target_words())
        return

    def print_run_info(self):
        print("-------- Print Run Info --------")
        print("All words:%3s. " % self.get_allWords(), end='')
        print(" Target words:%3s" % self.get_theCount())
        print("Non-Target words (%d): " % len(self.get_nonTarget()), end='')
        print(self.get_nonTarget())
        return

    def print_confusion_matrix(self, targetLabel, doKey=False, tag=""):
        assert (self.TP + self.TP + self.FP + self.TN) > 0
        print(tag+"-------- Confusion Matrix --------")
        print(tag+"%10s | %13s" % ('Predict', 'Label'))
        print(tag+"-----------+----------------------")
        print(tag+"%10s | %10s %10s" % (' ', targetLabel, 'not'))
        if doKey:
            print(tag+"%10s | %10s %10s" % ('', 'TP   ', 'FP   '))
        print(tag+"%10s | %10d %10d" % (targetLabel, self.TP, self.FP))
        if doKey:
            print(tag+"%10s | %10s %10s" % ('', 'FN   ', 'TN   '))
        print(tag+"%10s | %10d %10d" % ('not', self.FN, self.TN))
        return

    def eval_training_set(self, tset, targetLabel):
        print("-------- Evaluate Training Set --------")
        self.initTF()
        z = zip(tset.get_instances(), tset.get_lines())
        for ti, w in z:
            lb = ti.get_label()
            cl = ti.get_class()
            if lb == targetLabel:
                if cl:
                    self.TP += 1
                    outcome = "TP"
                else:
                    self.FN += 1
                    outcome = "FN"
            else:
                if cl:
                    self.FP += 1
                    outcome = "FP"
                else:
                    self.TN += 1
                    outcome = "TN"
            explain = ti.get_explain()
            print("TW %s: ( %10s) %s" % (outcome, explain, w))
            if Debug:
                print("-->", ti.get_words())
        self.print_confusion_matrix(targetLabel)
        return

    def classify_by_words(self, ti, update=False, tlabel="last"):
        inClass = False
        evidence = ''
        lw = ti.get_words()
        for w in lw:
            if update:
                self.incr_allWords()
            if w in self.get_target_words():    # FIXME Write predicate
                inClass = True
                if update:
                    self.incr_theCount()
                if evidence == '':
                    evidence = w            # FIXME Use first word, but change
            elif w != '':
                if update and (w not in self.get_nonTarget()):
                    self.add_nonTarget(w)
        if evidence == '':
            evidence = '#negative'
        if update:
            ti.set_class(inClass, tlabel, evidence)
        return(inClass, evidence)

    # Could use a decorator, but not now
    def classify(self, ti, update=False, tlabel="last"):
        cl, e = self.classify_by_words(ti, update, tlabel)
        return(cl, e)


class TrainingInstance(C274):
    def __init__(self):
        self.type = str(self.__class__)
        self.inst = dict()
        # FIXME:  Get rid of dict, and use attributes
        self.inst["label"] = "N/A"      # Class, given by oracle
        self.inst["words"] = []         # Bag of words
        self.inst["class"] = ""         # Class, by classifier
        self.inst["explain"] = ""       # Explanation for classification
        self.inst["experiments"] = dict()   # Previous classifier runs
        self.prep = []
        return

    def get_label(self):
        return(self.inst["label"])

    def get_words(self):
        return(self.inst["words"])

    def set_class(self, theClass, tlabel="last", explain=""):
        # tlabel = tag label
        self.inst["class"] = theClass
        self.inst["experiments"][tlabel] = theClass
        self.inst["explain"] = explain
        return

    def get_class_by_tag(self, tlabel):             # tlabel = tag label
        cl = self.inst["experiments"].get(tlabel)
        if cl is None:
            return("N/A")
        else:
            return(cl)

    def get_explain(self):
        cl = self.inst.get("explain")
        if cl is None:
            return("N/A")
        else:
            return(cl)

    def get_class(self):
        return self.inst["class"]
        
    def lowercase_input(self, text):
        text = ' '.join(text)
        text = text.lower()
        self.prep = text.split()    
        return self.prep

    def rm_punc_symbols(self, text):
        text = ' '.join(text)
        newtext = []
        '''Going through each character in string to
           check if it is alphanumeric or space and
           appending alphanumeric character to a new list'''
        for i in range(len(text)):
            if text[i].isalnum() or text[i] == " ":
                newtext.append(text[i])
        text = "".join(newtext)
        self.prep = text.split()
        return self.prep
    

    def rm_digits(self, text):
        text = ' '.join(text)
        text = list(text.split())
        correct_text = []
        ''' Checking if element in list is number or word,
            then proceeding to remove digits from the words and
            keeping seperate numbers as it is'''
        for char in text:
            if not char.isdigit():
                letters = list(char)
                for i in letters:
                    if not i.isdigit():
                        correct_text.append(i)
                correct_text.append(" ")
            else:
                correct_text.append(char + " ")
        text = "".join(correct_text)
        self.prep = text.split()
        return self.prep
    

    def rm_stopwords(self, text):
        txt_without_stop = []
        stopwords = [
            "i", "me", "my", "myself", "we", "our", "ours", "ourselves",
            "you", "your", "yours", "yourself", "yourselves",
            "he", "him", "his", "himself", "she", "her",
            "hers", "herself", "it", "its", "itself", "they",
            "them", "their", "theirs", "themselves", "what",
            "which", "who", "whom", "this", "that", "these",
            "those", "am", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "having", "do", "does",
            "did", "doing", "a", "an", "the", "and", "but", "if",
            "or", "because", "as", "until", "while", "of", "at",
            "by", "for", "with", "about", "against", "between",
            "into", "through", "during", "before", "after", "above",
            "below", "to", "from", "up", "down", "in", "out", "on",
            "off", "over", "under", "again", "further", "then", "once",
            "here", "there", "when", "where", "why", "how", "all",
            "any", "both", "each", "few", "more", "most", "other",
            "some", "such", "no", "nor", "not", "only", "own", "same",
            "so", "than", "too", "very", "s", "t", "can", "will",
            "just", "don", "should", "now"
            ]
        ''' Removing stopwords by appending non-stopwords
            to a new list'''
        for char in text:
            if char not in stopwords:
                txt_without_stop.append(char)
        text = " ".join(txt_without_stop)
        self.prep = text.split()
        return self.prep
    
    
    def preprocess_words(self, mode = ' '):
        self.prep = self.lowercase_input(self.prep)
        if mode == "keep-digits":
            processed_words = self.rm_stopwords(self.rm_punc_symbols(self.prep))
        elif mode == "keep-stops":
            processed_words = self.rm_digits(self.rm_punc_symbols(self.prep))
        elif mode == "keep-symbols":
            processed_words = self.rm_stopwords(self.rm_digits(self.prep))
        else:
            processed_words = self.rm_stopwords(self.rm_digits(self.rm_punc_symbols(self.prep)))
        self.prep = processed_words
        return self.prep
    
    
    def process_input_line(
                self, line, run=None,
                tlabel="read", inclLabel=True
            ):
        for w in line.split():
            if w[0] == "#":
                self.inst["label"] = w
                # FIXME: For testing only.  Compare to previous version.
                if inclLabel:
                    self.inst["words"].append(w)
            else:
                self.inst["words"].append(w)

        if not (run is None):
            cl, e = run.classify(self, update=True, tlabel=tlabel)
        return(self)


class TrainingSet(C274):
    def __init__(self):
        self.type = str(self.__class__)
        self.inObjList = []     # Unparsed lines, from training set
        self.inObjHash = []     # Parsed lines, in dictionary/hash
        return

    def get_instances(self):
        return(self.inObjHash)    # FIXME Should protect this more

    def get_lines(self):
        return(self.inObjList)      # FIXME Should protect this more
    
    def print_training_set(self):
        print("-------- Print Training Set --------")
        z = zip(self.inObjHash, self.inObjList)
        for ti, w in z:
            lb = ti.get_label()
            cl = ti.get_class_by_tag("last")     # Not used
            explain = ti.get_explain()
            print("( %s) (%s) %s" % (lb, explain, w))
            if Debug:
                print("-->", ti.get_words())
        return

    def process_input_stream(self, inFile, run=None):
        assert not (inFile is None), "Assume valid file object"
        cFlag = True
        while cFlag:
            line, cFlag = safe_input(inFile)
            if not cFlag:
                break
            assert cFlag, "Assume valid input hereafter"
            # Check for comments
            if line[0] == '%':  # Comments must start with %
                continue

            # Save the training data input, by line
            self.inObjList.append(line)
            # Save the training data input, after parsing
            ti = TrainingInstance()
            ti.process_input_line(line, run=run)
            self.inObjHash.append(ti)
        return
    
    
    def preprocess(self, mode = ' '):
        tr = self.get_instances()
        ti = TrainingInstance()
        '''Checking for matching labels in order to perform
           preprocessing for the corresponding terms'''         
        for i in range (len(self.get_instances())):
            ti.prep = tr[i].inst["words"]
            ti.preprocess_words()
            tr[i].inst["words"] = ti.prep
        return
    
    
    def return_nfolds(self, num = 3):
        self.folds = num
        self.object_lst = [] # -----> list of objects 
        # initialising n objects
        for i in range(num):
             ti = TrainingSet()
             self.object_lst.append(ti)
        self.copy()
        self.split_folds()
        return self.object_lst
    
        
    def copy(self):
        tset_copy = copy.deepcopy(self)
        return tset_copy
    
    
    def add_fold(self, tset):
        self.inObjHash.extend(copy.deepcopy(tset.inObjHash))
        self.inObjList.extend(copy.deepcopy(tset.inObjList))
        return
    
    
    def split_folds(self):
        for i in range(len(self.inObjList)):
            #Appending by checking the remainder 
            r = i % self.folds
            self.object_lst[r].inObjList.append(copy.deepcopy(self.inObjList[i]))
            self.object_lst[r].inObjHash.append(copy.deepcopy(self.inObjHash[i]))
        return
    
    
class ClassifyByTopN(ClassifyByTarget):
    def __init__(self):
        super().__init__()
        self.sort_words = {}        
    
    def sort_count_freq_words(self, new_line, num = 5):
        words = {}
        ''' Adding the elements of new_line to a dictionary "words"
            and using it to count the number of occurence of each word'''
        for char in new_line:
            if char not in words:
                words[char] = 1
            else:
                words[char] += 1                
        # Source for heapq https://www.geeksforgeeks.org/
        #python-n-largest-values-in-dictionary        
        res = nlargest(num, words, key = words.get)
        w = []
        res1 = []
        # Accounting for ties
        for char in res:
            for key, value in words.items():
                if words[char] == value:
                    if char != key and char not in w:
                        w.append(key)
        # removing repetitions that could arise
        res.extend(w)
        for i in res:
            if i not in res1:
                res1.append(i)
        return res1
    
       
    def target_top_n(self, tset, num=5, label = ' '):
        new = []
        tr = tset.get_instances()
        for i in range(len(tset.get_instances())):
            if label == tr[i].inst["label"]:
                new.append(tr[i].inst["words"])
        #Since new is a list containing sublists unpacking into a single list
        flat_list = []
        for sublist in new:
            for item in sublist:
                flat_list.append(item)
                           
        lw = self.sort_count_freq_words(flat_list, num)
        self.set_target_words(lw)
        return
    
        
def basemain():
    tset = TrainingSet()
    run1 = ClassifyByTarget(TargetWords)
    print(run1)     # Just to show __str__
    lr = [run1]
    print(lr)       # Just to show __repr__

    argc = len(sys.argv)
    if argc == 1:   # Use stdin, or default filename
        inFile = open_file()
        assert not (inFile is None), "Assume valid file object"
        tset.process_input_stream(inFile, run1)
        inFile.close()
    else:
        for f in sys.argv[1:]:
            inFile = open_file(f)
            assert not (inFile is None), "Assume valid file object"
            tset.process_input_stream(inFile, run1)
            inFile.close()

    if Debug:
        tset.print_training_set()
    run1.print_config()
    run1.print_run_info()
    run1.eval_training_set(tset, '#weather')
    tset.preprocess()
    run1.print_config()
    run1.print_run_info()
    run1.eval_training_set(tset, '#weather')
    return


if __name__ == "__main__":
    basemain()
