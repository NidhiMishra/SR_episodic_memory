__author__ = 'Zhang Juzheng'
import sys

from conceptnet5_client.utils.debug import print_debug
from conceptnet5_client.web.api import LookUp, Search, Association
from conceptnet5_client.utils.result import Result
from conceptnet5_client.utils.pprint import pprint_paths
from conceptnet5_client.inference.path import Path
import re
from randomFunc import randomFunc

class conceptNetWrapper:
    def __init__(self):
        self.randomFunc=randomFunc()

    def lookup(self,concept,off=0,lim=10):
        # example: http://conceptnet5.media.mit.edu/data/5.4/c/en/toast?offset=5&limit=5
        lookup = LookUp(offset=off,limit=lim)
        data = lookup.search_concept(concept)
        r = Result(data)
        edges = r.parse_all_edges()
        return edges

    def search(self,**kwargs):
        # settings: rel,start,end,limit,offset
        # example: http://conceptnet5.media.mit.edu/data/5.4/search?rel=/r/PartOf&end=/c/en/car&limit=10
        s = Search()
        s.initializeByDict(kwargs)
        data = s.search()
        r=Result(data)
        edges = r.parse_all_edges()
        return edges

 ##########################################################
    def clearSent(self,sent):
        sentence=re.sub(r'''[\*\[\]]+''',"",sent.lower())
        if ":" in sentence:
            res=sentence.split(":")
            sentence=res[1]+ " is "+res[0]
        stop_word=["some","synonym","something"]
        common=set(stop_word) & set(sentence.split())
        if len(common)>0:
            sentence=None
        return sentence

    def get_reply(self,concept,off=0,lim=20):
        sents=[]
        weights=[]
        edges= self.lookup(concept,off,lim)
        for edge in edges:
            if edge.weight>1 and edge.surfaceText!=None and type(edge.surfaceText)==type("str"):
                _str=self.clearSent(edge.surfaceText)
                if _str!=None:
                    sents.append(_str)
                    weights.append(edge.weight)
        if len(sents)==0:
            return None
        elif len(sents)>3:
            res,_=self.randomFunc.randomChoose_w_prob(sents[:3],weights[:3])
        else:
            res,_=self.randomFunc.randomChoose_w_prob(sents,weights)
        return res

    def get_abstract_concept(self,start=None,lim=10):
        if start==None:
            return None
        kwargs={"rel":"/r/IsA"}
        kwargs["start"]=start
        kwargs["limit"]=lim
        s = Search()
        s.initializeByDict(kwargs)
        data = s.search()
        r = Result(data)
        edges = r.parse_all_edges()
        res=[]
        for edge in edges:
            if edge.weight>1 and edge.surfaceEnd!=None:
                res.append(edge.surfaceEnd)
        return res
#############################################################

    def association(self,term,fil,lim=10):
        #example: http://conceptnet5.media.mit.edu/data/5.4/assoc/c/en/cat?filter=/c/en/dog&limit=1
        #example: http://conceptnet5.media.mit.edu/data/5.4/assoc/list/en/toast,cereal,juice,egg
        a = Association(filter=fil, limit=lim)
        data = a.get_similar_concepts(term)
        r = Result(data)
        edges = r.parse_all_edges()
        return edges

    def associateList(self,term_list):
        a = Association()
        data = a.get_similar_concepts_by_term_list(term_list)
        r = Result(data)
        edges = r.parse_all_edges()
        return edges

    def get_concepts_tuples_by_relations(self,concepts,relations):
        p = Path(concepts, relations)
        concepts_tuples = p.get_all_tuples_of_concepts()
        pprint_paths(sys.stdout, concepts_tuples)
        return concepts_tuples

    def get_relations_tuples_by_concepts(self,concepts):
        relations = []
        p = Path(concepts, relations)
        relations_tuples = p.get_all_tuples_of_relations()
        pprint_paths(sys.stdout, relations_tuples)
        return relations_tuples

    def check_path_existence(self,concepts,relations):
        p = Path(concepts, relations)
        exist = p.does_exist(print_where_breaks=True)
        if exist:
            print 'Path exist'
        return exist

if __name__=="__main__":
    cnw=conceptNetWrapper()
    print cnw.get_reply("food")
    print cnw.get_reply("sushi")
    print cnw.get_reply("japanese")
    print cnw.get_reply("singapore")
    print cnw.get_reply("china")

    # r=cnw.search(start="/c/en/singapore")
    # # r=cnw.lookup("university")
    # #r=cnw.search(rel="/r/PartOf",end="/c/en/car",limit=10)
    # # r=cnw.association("cat",'/c/en/dog')
    # # r=cnw.associateList(['toast', 'cereal', 'juice', 'egg'])
    #
    # r=cnw.get_abstract_concept(start="/c/en/singapore",lim=10)
    # print r
    # r=cnw.get_abstract_concept(start="/c/en/dog")
    # print r
    # r=cnw.get_abstract_concept(start="/c/en/singapor")
    # print r
    # print 1

