
# coding: utf-8

# In[ ]:


import networkx as nx

class expert_search:
    """
    Predicts experts for inputed list of tags. 
    Creates obgect of class expert_search, that contains data about articles, authors, conferences and works with them.
        The main function is Expert Search based on the data
    Algo:
        given the list of tags, it creates a graph of citations, that includes only authors, who has publications with
        keywords including the tags. Then it calculates PageRang for all nodes of this citations natwork and returns the 
        authors with the highest PR as the experts in the field.
    Functions: 
        expert_search(tags,n): returns a list of names of authors, who are experts in the field, determined by tags (list of strings)
                           reterns 3 objects: [0] list of n names of experts
                                              [1] graph of citations in the field
                                              [2] sorted list of tuples (authors_id, pagerank) for all authors from the graph
    """
    def __init__(self,articles, authors, conferences,ids,modify_field = 1):
        """Loads the data. Basically, it just rememberes the necessary part of it. 
          All three are necessary for the expert_search
          Modifications the authors data: adds to field list of key words that were published by the author and adds the 
             dictionary that counts how often the key word appeared as a key in his articles.
           
          Args:
            articles (json): data with articles, .json format
            authors (json): path to data with authors (researches), .json format
            conferences(json): path to data with conferences, .json format
            ids (dict):  dictionary that returns article id from database by it's DOI.
            modify_field = 1: put 0 here if authors fields are formed in a proper way in data and there is no need to refill it.
            
          Returns:
            self.articles (json): info about articles
            self.authors (json): info about authors
            self.conferences (json): info about conferences
            self.ids (dict): dict of articles ids to DOIs
            self.dois (dict): dict of erticles DOIs to ids
        """
        #assert y.shape[0] == X.shape[0] # Validate!
        #assert X.shape == (10, 1) # Validate more!
#        with open(articles_path) as f:
#            self.articles = json.load(f)
#        with open(authors_path) as f:
 #           self.authors = json.load(f)
  #      with open(conferences_path) as f:
   #         self.conferences = json.load(f)
        self.articles = articles
        self.authors = authors
        self.conferences = conferences
        self.ids=ids
        
        # here we form one more dictionary for articles, the opposite one id->doi
        self.dois = {}
        for key in ids.keys():
            self.dois[ids[key]]=key

            # here we re-assign the fields of the researchers 
        if modify_field:
            for aut in self.authors:
                field_count={}
                field=[]
                for art in aut['articles']:
                    if self.get_art_info(i=art['title']):   
                        t=self.get_art_info(i=art['title'])['keywords']
                        if t!=None and t!='NaN':
                            for w in t:
                                field_count[w.lower()]=field_count.get(w.lower(),0)+1
                                field.append(w.lower())
                f = list(set(field))
                if len(f)>0:
                    aut['field']=f 
                    aut['firld_count']=field_count
                else:
                    aut['firld_count']=None
        
    def get_aut_info(self,a):
        ''' Returns all the information about the author by id
        Args: id (int)= id from the authors database
        Returns: json object from the authors dataset
        '''
        for i in self.authors:
            if i['id']==a:
                return i 
    def get_aut_info_name(self,a):
        ''' Returns all the information about the author by name. the problem here is that the names may be not unique, 
            so it returns the list of authors with this name.
        Args: name (str): name from the authors database. 
        Returns: list of json object from the authors dataset.
        '''        
        l=[]
        for i in self.authors:
            if i['name']==a:
                l.append(i)
        return l 
    def get_art_info(self,doi=None,i=None):
        ''' 
        Returns all the information about the article by doi or id. One of them must be specified.
        Args: i (int): id from the articles database (the number in the order, coinsides with the ids from self.ids dictionary)
              doi (str): DOI for article in the database. Doi is unique, so identifies the article. Not all articles are in the articles database, 
              that may be found in the authors or articles databases;
        Returns: json object from the authors dataset
        '''
        if doi:
            num = ids[doi]
            if num<len(self.articles):
                return self.articles[num]
            else:
                print('Article %s is not in the base'%doi)
                return None
        if i!=None:
            if i<len(self.articles):
                return(self.articles[i])
            else:
                print('Article %i is not in the base'%i)
                return None
        print('DOI or id must be specified')
        return None
    
    def subgraph(self,tags,narrow = 1):
        '''
        Returnes articles containing listed tags in the keywords and all their authors.
        Args:
            tags (list of str): tags that will be searched through articles keywords. the case doesn't matter.
        Returns 2 objects:
            cv_authors_list (list of int): list of authorsID of authors, who has publications with given keywords
            cv_articles_list (list of int): articles_ids of articles that has listed keywords
        '''
        cv_authors_list = []
        cv_articles_list = []
        if narrow==1:
            for i in range(len(self.articles)):
                if self.articles[i]['keywords'] == None or self.articles[i]['keywords'] == 'NaN':
                    pass
                else: 
                    for tag in tags:
                        if (tag.lower() in [k.lower() for k in self.articles[i]['keywords']]):
                            cv_articles_list.append(i)
                            for a in self.articles[i]['authorID']:
                                cv_authors_list.append(a)
        return(cv_authors_list, cv_articles_list)

    def co_graph(self, tags, narrow=1):
        ''' 
        Builds coathorship graph for the authors, who published articles for the given key words and their coauthors.
            Args:
                tags (list of str): tags that will be searched through articles keywords. the case doesn't matter.
            Returns:
                co_g = graph of coathorship
        '''
        cv_authors_list, cv_articles_list = self.subgraph(tags,narrow)
        edges = []
        for i in cv_authors_list:
            aut=self.get_aut_info(i)
            if aut!=None and aut['coauthors']!=None:
                for j in range(len(aut['coauthors'])):
                    try:
                        edges.append((aut['coauthors'][j],i))
                    except:
                        pass
        g = nx.Graph()
        for i,j in edges:
            g.add_edge(i,j) 
        self.co_graph = g
        return g
    def cite_graph(self,tags,narrow=1):
        ''' 
        Builds citations graph for the authors, who published articles for the given key words and the authors who were cited by them

        Args:
            tags (list of str): tags that will be searched through articles keywords. the case doesn't matter.

        Returns:
            cit_g (nx.DiGraph object): the graph of citations
        '''
        cv_authors_list, cv_articles_list = self.subgraph(tags,narrow)
        edges=[]
        for art_id in cv_articles_list:
            art=self.articles[int(art_id)]
            if art['workLinks']!= None and art['workLinks']!=[]:
                cites_id_list = art['workLinks']
                if cites_id_list!=[] and cites_id_list!= None:
                    aut_id_list = art['authorID']                    # MB here is reasonable to take only articles with <10 authors. Cuz biologists love to put all the relatives in the coauthors
                    cited_id_list = []
                    for c in cites_id_list:                         # for every article from the list
                        if self.get_art_info(i=c)!=None:
                            for aut in self.articles[c]['authorID']:         # we take its authors
                                cited_id_list.append(aut)               # put them to the list of cited by the original authors   
                    for aut_id in aut_id_list:                      # then for every author 
                        for in_id in cited_id_list:                 # we add adges to all the cited authors.
                            edges.append((aut_id,in_id))
        g = nx.DiGraph()
        for i,j in edges:
            g.add_edge(i,j)
        return g 
    
    def expert_search(self,tags,n=15, narrow=1):
        '''
        Returns a list of names of authors, who are experts in the field, determined by tags (list of strings).
            Warnings are printed if some articles that are cited were not found in the database. 
        Args:
            tags (list of str): tags that will be searched through articles keywords. the case doesn't matter.
            n (int): number of experts in the returned list
        Reterns 3 objects: [0] list of n names of experts
                           [1] graph of citations in the field
                           [2] sorted list of tuples (authors_id, pagerank) for all authors from the graph

        '''
        cite_g = self.cite_graph(tags=tags, narrow=narrow)
        pr = nx.pagerank(cite_g)
        highest_pr = [(k,v) for k, v in dict(pr).items()]
        highest_pr=sorted(highest_pr, key= lambda x: x[1], reverse = True)
        experts=[]
        for k,a in highest_pr[:n]:
            ex=self.get_aut_info(k)['name']
            experts.append(ex)
            print(ex)
        return experts, cite_g, highest_pr    

