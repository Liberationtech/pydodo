#!/usr/bin/python

"""

pydodo

A python library to build markov models from text and generate text
from the contructed models.

Inspired by dadadodo

"""

import re, string, operator, random

class AbstractState:

    def __init__(self):
        self.transitions_absolute = {}
        self.transitions_relative = []

    def append_successor(self,nextstate):
        """
        """
        try:
            self.transitions_absolute[nextstate] += 1
        except KeyError:
            self.transitions_absolute[nextstate] = 1

    def set_relative_transitions(self):

        items = self.transitions_absolute.items()
        n = 1.0 *  reduce(operator.add, map(lambda item:item[1], items))
        self.transitions_relative = map(lambda item: (item[0], item[1]/n), items)

    def isend(self):
        return 0

    def isstart(self):
        return 0

class StateForPickle:
    """
    A representation of Pickle suitable for dumping/loading cPickle
    """

    def __init__(self, state):
        self.data = state.data
        self.transitions_absolute  = map(lambda pair:(pair[0].data, value), state.transitions_absolute)
        self.transitions_relative  = map(lambda pair:(pair[0].data, value), state.transitions_relative)



class State(AbstractState):

    def __init__(self,data):
        self.data = data
        self.transitions_absolute = {}
        self.transitions_relative = {}

    def to_file(self):
        result = self.data

    def is_pine(self, state=None, result = 1):

        if not state:
            state = self

        #print state.transitions_relative

        if len(state.transitions_relative) > 1:
            result = 0
        else:
            next = state.transitions_relative[0][0]
            if not next.isend():
                self.is_pine(next, result)
        return result


class StartState(AbstractState):

    def isstart(self):
        return 1

class EndState(AbstractState):

    def isend(self):
        return 1


class MarkovModel:

    def __init__(self):
        self.start = StartState()
        self.end = EndState()
        self.states = {}

    def get_states(self):
        return self.states.values()

    def set_relative_transitions(self):
        for state in self.get_states():
            state.set_relative_transitions()
        self.start.set_relative_transitions()

    def new_state(self, data):
        try:
            result = self.states[data]
        except KeyError:
            result = State(data)
            self.states[data] = result

        return result

    def construct(self, data,order=3):
        """
        takes open file, parses it to build model.
        """
        for sentence in self.sentence_iterator(data):
            tokens = self.sentence2tokens(sentence)
            states = self.tokens2states(tokens, order)
            if len(states) > 0:
                self.appendstates(states)
        self.set_relative_transitions()


    def remove_pines(self):
        """
        Remove pines

        Pines are chains of states that do not branch.

        These chains will never generate sentences that are not
        present in the raw data.

        Think of pine trees.

        Returns new MarkovModel without pines
        """

        result = self.__class__()

        for state in self.start.transitions_absolute:

            if state.is_pine():
                pass
            else:
                result.start.append_successor(state)


        result.start.set_relative_transitions()
        result.end = self.end

        return result


    def string2charset(self,str):
        """
        convert a string ie 'ABC' to a regexp charset
        string '[A|B|C]'
        """
        result = []
        for i in range(len(str)):
            #print "i",str[i]
            result.append(str[i])
        result = "[%s]" %(string.join(result,"|"),)
        return result

    def appendstates(self,states):
        """
        append a series of consecutive states to the markov model.
        """
        currentstate = states[0]
        self.start.append_successor(currentstate)
        nextstate = currentstate
        for i in range(len(states) - 1):
            currentstate = states[i]
            try:
                nextstate = states[i+1]
                currentstate.append_successor(nextstate)
            except:
                pass

        nextstate.append_successor(self.end)

    def tokens2states(self, tokens, order):
        """
        convert a sequnce of tokens and turn it in to states (ngrams).

        """
        i = 0
        result = []
        while 1:
            data = tuple(tokens[:order])
            del tokens[:1]
            if order > len(data):
                break

            new = self.new_state(data)
            result.append(new)
        return result

    def sentence2tokens(self,sentence):
        """
        """
        wordchars = self.string2charset(self.__class__.wordchars)
        punctuation_marks = self.string2charset(self.__class__.punctuation_marks)

        wordchars = re.compile("%s+|%s" % (wordchars, punctuation_marks))
        return wordchars.findall(sentence)




    def sentence_iterator(self,data):
        """
        extract sentences from open file
        """

        start = self.string2charset(self.__class__.uppercaseletters)
        stop = "[\.\?\!]"
        notstop = "[^\.\?\!]"
        pattern = re.compile("%s%s+%s" % (start,notstop,stop))

        for m in pattern.findall(data.read()):
            m = m.replace("'","")
            m = m.replace('"',"")
            m = m.replace('(',"")
            m = m.replace(')',"")
            m = m.replace('[',"")
            m = m.replace(']',"")
            m = m.replace("\n"," ")
            m = m.strip()
            yield m



    def tokens2sentence(self,tokens):
        result = ""
        result += tokens[0]
        for token in tokens[1:]:
            if token not in self.__class__.punctuation_marks:
                result += " "
            result += token
        return result


    def generate_sentence(self, n=7):
        """
        Generate sentence of length n from MarkovModel.

        n is not absolute.
        The generator will try to terminate after accumulating more than n tokens,
        but only if it can move to the end state.

        """
        import bisect

        def cum(lst):
            result = []
            c = 0
            for i in lst:
                c += i
                result.append(c)
            result[-1] = 1
            return result

        selected_states = []
        current = self.start

        #select the tokens
        c = 0
        while 1:

            #get out of here if our sentence is long enough and start.end is in sight.
            if c > n and self.end in map(lambda pair:pair[0], current.transitions_relative):

                break

            cums = cum(map(lambda pair:pair[1],current.transitions_relative))

            pos = bisect.bisect_left(cums, random.random())
            current = current.transitions_relative[pos][0]
            if current == self.end:
                break
            else:
                selected_states.append(current)
                c += 1

        tokens = []
        tokens.extend(selected_states[0].data)
        for state in  selected_states[1:]:
            tokens.extend((state.data[-1],))
        return self.tokens2sentence(tokens)

class Language:
    """
    Dealing with particularities in natural languages in a rational manner
    """
    digits = "0123456789-"
    punctuation_marks = ".!?,;:"

class Swedish(Language):

    letters = "abcdefghijklmnopqrstuvwxyzÂ‰ˆÈËÔ/"
    uppercaseletters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ≈ƒ÷…»À"
    digits = Language.digits
    wordchars = letters + uppercaseletters + digits


class SwedishCharbased(Language):

    digits = "0123456789 -"
    punctuation_marks = ".!?,;:"
    letters = "abcdefghijklmnopqrstuvwxyzÂ‰ˆÈËÔ/"
    uppercaseletters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ≈ƒ÷…»À"
    wordchars = letters + uppercaseletters + digits


## class English(Language):

##     letters = "abcdefghijklmnopqrstuvwxyz"
##     uppercaseletters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
##     digits = Language.digits
##     wordchars = letters + uppercaseletters + digits




class SwedishMarkov(MarkovModel, Swedish):
    pass

class CharBasesSwedishMarkov(MarkovModel, SwedishCharbased):


    def sentence2tokens(self,sentence):
        """
        """
        wordchars = self.string2charset(self.__class__.wordchars)
        punctuation_marks = self.string2charset(self.__class__.punctuation_marks)
        #print "[%s]" %( wordchars,)
        wordchars = re.compile("%s|%s" % (wordchars, punctuation_marks))
        result = wordchars.findall(sentence)
        #print result
        return result


    def tokens2sentence(self,tokens):
        result = ""
        result += tokens[0]
        for token in tokens[1:]:
            #if token not in self.__class__.punctuation_marks:
            #    result += ""
            result += token
        return result
