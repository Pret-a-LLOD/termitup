import argparse
import csv #libreria para exportar a excel o csv 
import requests #libreria para querys en api
import json #libreria para utulizar json en python
from random import randint #libreria para random
import re
import os
from os import remove
import collections
from os import listdir
from os.path import isfile, isdir

import time

def leerContextos(lang, termIn):
    
    configuration= {
    "es": "contexts/Spain-judgements-ES.ttl",
    "en": "contexts/UK-judgements-EN.ttl",
    "nl": "contexts/Austria-collectiveagreements-DE.ttl",
    "de": "contexts/contracts_de.ttl"
    }
    
    es = '%s'%configuration["es"]
    en = '%s'%configuration["en"]
    nl = '%s'%configuration["nl"]
    de = '%s'%configuration["de"]
    encoding = 'utf-8'
    if(lang=='es'):
        archivo = open(es, "r")
    elif(lang=='en'):
        archivo = open(en, "r")
    elif(lang=='de'):
        archivo = open(de, "r")
    elif(lang=='nl'):
        archivo = open(nl, "r")

    contenido = archivo.readlines()
    
    lista=[]
    lista1=[]
    matriz=[]
    contextlist=[]
    find=[]
    cont=0
    for i in contenido:
        encuentra=i.find('skos:Concept')
        if(encuentra!=-1):
            cont=cont+1
        
    for i in contenido:     
        encuentra1=i.find('skos:prefLabel')
        if(encuentra1!=-1):
            text = i.split('"')
            pref=text[1]    
            lista1.append(pref)
    cont1=0     
    for i in contenido:     
        encuentra=i.find('skos:Concept')
        encuentra2=i.find('lynxlang:hasExample')
        if(encuentra!=-1):
            matriz.insert(cont,[])
            cont1=cont1+1

        if(encuentra2!=-1):
            text1 = i.split('"',1)
            pref1=text1[1]
            lista.append(str(pref1)+'|'+str(cont1-1))   

    for i in range(cont):
        matriz[i].insert(0, lista1[i])
        slp=lista[i].split('|')
        matriz[i].insert(1, slp[0])

    limpiar=re.compile("<'\'.*?>")
    for i in matriz:

        r=''.join(i[0])
        r2=''.join(i[1])

        row1 = re.sub(r'<[^>]*?>','', r)
        row1 = row1.replace('@es;','')

        row2 = re.sub(r'<[^>]*?>','', r2)
        row2 = row2.replace('@es;','').replace('\\','').replace('"','')
        if(row1 in row2):
            
            contextlist.append([row1,row2[:-1]])
        
    for i in contextlist:
        if(termIn in i[0] and len(find)==0):
            start=i[1].index(termIn)
            tam=len(termIn)
            end=i[1].index(termIn)+tam
            find.append([termIn,i[1], start, end])
    return(find)

#funcion para obtener identificadores
def sctmid_creator():
    numb = randint(1000000, 9999999)
    SCTMID = "LT" + str(numb)
    return SCTMID
    
#funcion para obtener el baren token (access token)
def obtenerToken(): 
    response=requests.get('https://iate.europa.eu/uac-api/auth/token?username=VictorRodriguezDoncel&password=h4URE7N6fXa56wyK')
    reponse2=response.json()
    access=reponse2['tokens'][0]['access_token']
    return(access)

def haceJson(lista, idioma,targets):
    answer=[]
    auth_token=obtenerToken() 
    for i in lista:
        termino=i
        hed = {'Authorization': 'Bearer ' +auth_token}
        jsonList=[]
        data = {"query": termino,
        "source": idioma,
        "targets": targets,
        "search_in_fields": [
            0
        ],
        "search_in_term_types": [
                0,
                1,
                2,
                3,
                4
            ],
             
            "query_operator": 1
        }
        url= 'https://iate.europa.eu/em-api/entries/_search?expand=true&limit=5&offset=0'
        response = requests.get(url, json=data, headers=hed)
        reponse2=response.json()
        js=json.dumps(reponse2)
        answer.append(reponse2)
    jsondump=json.dumps(answer)
    return(jsondump)




def getIate(target, item,leng,termSearch):
    defi=''
    pref=''
    term_val=''
    syn=[]
    joinSyn=''
    if(target in leng):
        language=leng[target]
        for l in language:
            if('term_entries' in language.keys()):
                term_entries=language['term_entries']
                if(len(term_entries)>0):
                    pref=language['term_entries'][0]['term_value']
                    for t in range(len(term_entries)):
                        term_val=language['term_entries'][t]['term_value']
                        if(termSearch is not term_val):
                            syn.append(term_val)
                    syn=syn[0:len(term_entries)]
                    joinSyn='| '.join(syn)
            if('definition' in language.keys()):
                defi=language['definition']


    defi=re.sub(r'<[^>]*?>', '', defi)
    defi=defi.replace(',', '')
    return(defi, pref, joinSyn)




#funcion que introduce todo en un csv 
def all(jsonlist, idioma, targets, context, contextFile,  wsid, schema, dataRetriever):
    data=json.loads(jsonlist)
    resultado=''
    results=[]
    termSearch=[]
    cont=0
    for i in data:
        results.insert(cont, [])
        termSearch.append(i['request']['query'])
        bloq=0
        if('items' in i.keys()):
            lang=[]
            definicion=[]
            definicion2=[]
            definicion_in=[]
            prefLabel=[]
            synonyms=[]
            pref=[]
            alt=[]
            defi=[]
            tar=[]
            lbloq=[]
            iateIde=[]
            iate=[]
            eurovoc=''
            euro=[]
            term=i['items']
            ide=sctmid_creator()
            for item in range(len(term)):#en cada de los siguientes ciclos se va interactuando en el json para obtener lo necesario
                ide_iate=i['items'][item]['id']
                leng=i['items'][item]['language']
                for target in targets:
                    get=getIate(target,item, leng, termSearch[cont])
                    if(target==idioma and get[0]!='' ):
                        definicion_in.append(get[0])

                    lbloq.append(bloq)
                    definicion.append(get[0])
                    definicion2.append(get[0]+':'+str(bloq))
                    prefLabel.append(get[1]+':'+str(bloq))
                    synonyms.append(get[2]+':'+str(bloq))
                    lang.append(target+':'+str(bloq)) 
                    iateIde.append(str(ide_iate)+':'+str(bloq))
                    
                bloq=bloq+1
            d=(definicion_in,[])
            if(wsid=='si'):
                maximo=wsidFunction(termSearch[cont],  context, contextFile,  d)
                if(maximo[2]!=200):
                    for j in range(len(lbloq)):
                        pref.append(prefLabel[j][:-2])
                        alt.append(synonyms[j][:-2])
                        defi.append(definicion2[j][:-2])
                        tar.append(lang[j][:-1])
                        iate.append(iateIde[j][:-2])
                else:
                    m=definicion.index(maximo[0])
                    b=lbloq[m]
                    for j in range(len(lbloq)):
                        if(str(b) in prefLabel[j][-1:]):
                            pref.append(prefLabel[j][:-2])
                            alt.append(synonyms[j][:-2])
                            defi.append(definicion2[j][:-2])
                            tar.append(lang[j][:-1])
                            iate.append(iateIde[j][:-2])
            else:
                for j in range(len(lbloq)):
                    pref.append(prefLabel[j][:-2])
                    alt.append(synonyms[j][:-2])
                    defi.append(definicion2[j][:-2])
                    tar.append(lang[j][:-1])
                    iate.append(iateIde[j][:-2])
            relations=['broader', 'narrower', 'related']
            euro=resultsEurovoc(termSearch[cont], idioma, relations, target,  context, contextFile, wsid)
            lexicala=resultsSyns(idioma,termSearch[cont],targets,context, contextFile,wsid)
            fin=fileJson(termSearch[cont], pref, alt, defi,idioma, tar, euro,iate, lexicala, schema, dataRetriever)
         
        cont=cont+1;
    return(fin)

def wsidFunction(termIn, context, contextFile,  definitions):
    defiMax=''
    idMax=''
    posMax=0
    code=0
    if(context):
        print('context')
        pesos=[]
        start=context.index(termIn)
        longTerm=len(termIn)
        end=context.index(termIn)+longTerm
        listdef=definitions[0]
        listIde=definitions[1]
        definitionsJoin=', '.join(listdef)
        response = requests.post(
                        'http://wsid-88-staging.cloud.itandtel.at/wsd/api/lm/disambiguate_demo/',
                        params={'context': context, 'start_ind': start, 'end_ind': end,  'senses': definitionsJoin}, 
                        headers ={'accept': 'application/json',
                                'X-CSRFToken': 'WCrrUzvdvbA4uahbunqIJGxTpyAwFuIGgIm9O91EfeiQwH3TnUUsnF2cdXkHXi94'
                                }
                        )
        code=response.status_code
        if(response.status_code==200):
            pesos=response.json()
        else:
            pesos=[]
        if(len(pesos)>0 and len(listdef)>0):
            max_item = max(pesos, key=int)
            posMax=pesos.index(max_item)
            defiMax=listdef[posMax]
            idMax=listIde[posMax]
        else:
            defiMax=''
            idMax=''
    
    elif(contextFile):
        print('contextFile')
        for i in contextFile:
            contextTerm=i[0]
            if(termIn in contextTerm):
                pesos=[]
                context=i[1]
                start=i[2]
                end=i[3]
                listdef=definitions[0]
                listIde=definitions[1]
                definitionsJoin=', '.join(listdef)
                print(definitionsJoin)
                response = requests.post(
                                'http://wsid-88-staging.cloud.itandtel.at/wsd/api/lm/disambiguate_demo/',
                                params={'context': context, 'start_ind': start, 'end_ind': end,  'senses': definitionsJoin}, 
                                headers ={'accept': 'application/json',
                                        'X-CSRFToken': 'WCrrUzvdvbA4uahbunqIJGxTpyAwFuIGgIm9O91EfeiQwH3TnUUsnF2cdXkHXi94'
                                        }
                                )
               
                code=response.status_code
                if(response.status_code==200):
                    pesos=response.json()
                else:
                    pesos=[]
                if(len(pesos)>0 and len(listdef)>0):
                    max_item = max(pesos, key=int)
                    posMax=pesos.index(max_item)
                    defiMax=listdef[posMax]
                    
                    if(len(listdef)>0):
                        defiMax=listdef[posMax]
                    else:
                        defiMax=''

                    if(len(listIde)>0):
                        idMax=listIde[posMax]
                    else:
                        idMax=''
                else:
                    defiMax=''
                    idMax=''
                break
            else:
                defiMax=''
                idMax=''

         
    return(defiMax, idMax,code)

def fileJson(termSearch, prefLabel, altLabel,definition,idioma,lang, eurovoc,iate, lexicala, schema, dataRetriever):
    newFile=''
    raiz=os.getcwd()
    carpeta=os.listdir(raiz)
    if(idioma in carpeta):
        print('')
    else:
        os.mkdir(idioma)
    
    verify=verificar(idioma,termSearch, '')
    #print(verify)
    ide=verify[0]
    termSearch=verify[1]
    data={}
    if(termSearch!=termSearch):
        
        data={'@context':'','@id': ide, '@type':'skos:Concept', 'skos:inScheme': termSearch, "owl:sameAs":"https://iate.europa.eu/entry/result/"+iate[0],'skos:topConceptOf':ide, 'skos:prefLabel':'' }
        data['@context']={"@base":"http://lynx-project.eu/kos/"+schema , "dcterms": "http://purl.org/dc/terms/","rdfs":"http://www.w3.org/2000/01/rdf-schema#",  "rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "dc":"http://purl.org/dc/elements/1.1/","skos":"http://www.w3.org/2004/02/skos/core#","owl":"http://www.w3.org/2002/07/owl#","skos:broader":{ '@type':'@id'},"skos:inScheme":{ '@type':'@id'},'skos:related':{ '@type':'@id'},'skos:narrower':{ '@type':'@id'},'skos:hasTopConcept':{ '@type':'@id'},'skos:topConceptOf':{ '@type':'@id'}}
        data['skos:prefLabel']=[]
        data['skos:altLabel']=[]
        data['skos:definition']=[]
        
        
        for i in range(len(prefLabel)):
            if(lang[i][:-1]==idioma):
                if(prefLabel[i]!=''):
                    data['skos:prefLabel'].append({'@language':lang[i][:-1], '@value':termSearch.strip(' ')})
            else:
                if(prefLabel[i]!=''):
                    data['skos:prefLabel'].append({'@language':lang[i][:-1], '@value':prefLabel[i].strip(' ')})
        for i in range(len(altLabel)):
            if(altLabel[i]!=''):
                s_alt=altLabel[i].split('|')
                for j in s_alt:
                    if(j != prefLabel[i] and j!=''):
                        data['skos:altLabel'].append({'@language':lang[i][:-1], '@value':j.strip(' ')})
        
        data['skos:altLabel'].append({'@language':idioma, '@value':lexicala[0].strip(' ')})
        
        #print(lexicala[1])
        for i in lexicala[1]:
            s_lex=i.split(',')
            data['skos:altLabel'].append({'@language':s_lex[1], '@value':s_lex[0].strip(' ')})
        
        for i in range(len(definition)):
            if(definition[i]!=''):
                data['skos:definition'].append({'@language':lang[i][:-1], '@value':definition[i].strip(' ')})

      
        br=eurovoc[0][0][0]
        na=eurovoc[1][0][0]
        re=eurovoc[2][0][0]
        if(br!=''):
            data['skos:broader']=[]
        if(na!=''):
            data['skos:narrower']=[]
        if(re!=''):
            data['skos:related']=[]

        for i in eurovoc:
            relationsEurovoc(i[0], i[1], idioma,data, i[2], schema )
            
        newFile=idioma+'/'+termSearch+'_'+ide+'.json'
        with open(newFile, 'w') as file:
            json.dump(data, file, indent=4,ensure_ascii=False)
        if(dataRetriever=='si'):
            data=dataRetrieverFunction(newFile, idioma, schema)
    else:
        with open(idioma+'/'+termSearch+'_'+ide+'.json', 'r') as file:
            data = json.load(file)
    return(data)
        
        
def relationsEurovoc(relationList, uriList, idioma,data, relationEuro, schema):
    for i in range(len(relationList)):
        relation=relationList[i]
        uri=uriList[i]
        if(relation!=''):
            carpetas=os.listdir(idioma)
            if(relationEuro not in carpetas):
                os.makedirs(idioma+"/"+relationEuro)
            
            verify=verificar(idioma,  relation, relationEuro)
            ide=verify[0]
            termSearch=verify[1]
            if(ide!='' and termSearch!=''):
                if('skos:'+relationEuro in data.keys()):
                    data['skos:'+relationEuro].append(ide)
                    dataEurovoc=fileEurovoc(termSearch, ide, relation, uri, idioma, schema)

                    with open(idioma+'/'+relationEuro+'/'+termSearch+'_'+ide+'.json', 'w') as file:
                        json.dump(dataEurovoc, file, indent=4,ensure_ascii=False)
                   
        
def fileEurovoc(termSearch, ide, relation, iduri, idioma, schema):
    data={}
    data={'@context':'','@id': ide, '@type':'skos:Concept', 'skos:inScheme': termSearch, 'skos:topConceptOf':ide,"owl:sameAs":iduri, 'skos:prefLabel':'' }
    data['@context']={"@base":"http://lynx-project.eu/kos/"+schema ,"dcterms": "http://purl.org/dc/terms/","rdfs":"http://www.w3.org/2000/01/rdf-schema#",  "rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "dc":"http://purl.org/dc/elements/1.1/","skos":"http://www.w3.org/2004/02/skos/core#","owl":"http://www.w3.org/2002/07/owl#","skos:broader":{ '@type':'@id'},"skos:inScheme":{ '@type':'@id'},'skos:related':{ '@type':'@id'},'skos:narrower':{ '@type':'@id'},'skos:hasTopConcept':{ '@type':'@id'},'skos:topConceptOf':{ '@type':'@id'}}
    data['skos:prefLabel']=[]
    if(relation!=''):
        data['skos:prefLabel'].append({'@language':idioma, '@value':relation})
    return(data)

def verificar(idioma,  termSearch, relation):
    if(relation!=''):
        path=idioma+'/'+relation+'/'
    else:
        path=idioma+'/'
    lista_arq = [obj for obj in listdir(path) if isfile(path + obj)]
    ide=sctmid_creator()
    for i in lista_arq:
        slp=i.split('_')
        slp2=slp[1].split('.')
        idefile=slp2[0]
        termfile=slp[0]
        if(termSearch == termfile):
            termSearch=termSearch
            ide=idefile
        else:
            termSearch=termSearch
            if(ide in idefile):
                ide=sctmid_creator()
                verificar(idioma, termSearch, relation)
            else:
                ide=ide
    return(ide, termSearch)


def resultsEurovoc(termino, idioma, relations, target, context, contextFile, wsid):
    results=[]
    resultado=''
    relation=''
    uri=getUriTerm(termino, target, idioma)
    if(len(uri)>0):
        nameDef=getName(uri, idioma)
        nombres=nameDef[0]
        definiciones=nameDef[1]
        definicionesOnly=nameDef[2]
        d=(definicionesOnly, [])
        if(wsid=='si'):
            maximo=wsidFunction(termino, context, contextFile, d)
            if(maximo[2]!=200):
                uri=getUriTerm(termino, target, idioma) 
                for relation in relations: 
                    uriRelation=getRelation(uri, relation)
                    nameDef=getName(uriRelation, idioma)
                    nombres=nameDef[0]
                    definiciones=nameDef[1]
                    definicionesOnly=nameDef[2]
                    results.append([nombres, uriRelation, relation])

            else:
                m=definiciones.index(maximo[0])
                alta=nombres[m]
                uri=getUriTerm(alta, target, idioma) 
                for relation in relations: 
                    uriRelation=getRelation(uri, relation)
                    nameDef=getName(uriRelation, idioma)
                    nombres=nameDef[0]
                    definiciones=nameDef[1]
                    definicionesOnly=nameDef[2]
                    results.append([nombres, uriRelation, relation])
                    #print(nombres, uriRelation, relation)
        else:
            uri=getUriTerm(termino, target, idioma) 
            for relation in relations: 
                uriRelation=getRelation(uri, relation)
                nameDef=getName(uriRelation, idioma)
                nombres=nameDef[0]
                definiciones=nameDef[1]
                definicionesOnly=nameDef[2]
                results.append([nombres, uriRelation, relation])

          

    else:
        for relation in relations: 
            results.append([[''], [''], relation])
    #print(results)
    return(results)

      
    

#1. funcion que obtiene la uri de cada termino
def getUriTerm(termino,lenguaje, idioma):
    termino2='"'+termino+'"'
    lenguaje2='"'+lenguaje+'"'
    idioma2='"'+idioma+'"'
    resultado=[]
    resultadouri=''
    url = ("http://sparql.lynx-project.eu/")
    query = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT ?c ?label
    WHERE {
    GRAPH <http://sparql.lynx-project.eu/graph/eurovoc> {
    VALUES ?searchTerm { """+termino2+""" }
    VALUES ?searchLang { """+idioma2+""" }
    VALUES ?relation {skos:prefLabel skos:altLabel}
    ?c a skos:Concept .
    ?c ?relation ?label .
    filter ( contains(?label,?searchTerm) && lang(?label)=?searchLang )       
    }  
    }
    """
    #filter ( contains(?label,?searchTerm) && lang(?label)=?searchLang )
    #filter (regex(?label, "(^)"""+termino+"""($)"))
    r=requests.get(url, params={'format': 'json', 'query': query})
    results=json.loads(r.text)
    
    if (len(results["results"]["bindings"])==0):
        resultadouri=''
    else:
        for result in results["results"]["bindings"]:
            resultadouri=result["c"]["value"]
            resultadol=result["label"]["value"]
            resultado.append(resultadouri)
            
    return(resultado)

#2. funcion que recibe la uri del termino al que sele desea saber su BROADER, obtiene la uri del BROADER 
def getRelation(uri_termino, relacion):
    resultado=[]
    resultadoRel=''

    for i in uri_termino:
        url=("http://sparql.lynx-project.eu/")
        query="""
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT ?c ?label
        WHERE {
        GRAPH <http://sparql.lynx-project.eu/graph/eurovoc> {
        VALUES ?c {<"""+i+"""> }
        VALUES ?relation { skos:"""+relacion+""" } # skos:broader
        ?c a skos:Concept .
        ?c ?relation ?label .    
        }  
        }
        """
        r=requests.get(url, params={'format': 'json', 'query': query})
        results=json.loads(r.text)
        if (len(results["results"]["bindings"])==0):
                resultadoRel=''
        else:
            for result in results["results"]["bindings"]:
                resultadoRel=result["label"]["value"]
        resultado.append(resultadoRel)
    
    return(resultado)


#3. funcion que recibe la uri del broader y consulta cual es el termino correspondiente
def getName(uri,lenguaje):
    defs=[]
    defsOnly=[]
    names=[]
    nameUri=''
    valor=''
    for i in uri:
        lenguaje2='"'+lenguaje+'"'
        url=("http://sparql.lynx-project.eu/")
        query="""
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT ?c ?label
        WHERE {
        GRAPH <http://sparql.lynx-project.eu/graph/eurovoc> {
        VALUES ?c { <"""+i+"""> }
        VALUES ?searchLang { """+lenguaje2+""" undef } 
        VALUES ?relation { skos:prefLabel  } 
        ?c a skos:Concept . 
        ?c ?relation ?label . 
        filter ( lang(?label)=?searchLang )
        }
        }
        """
        r=requests.get(url, params={'format': 'json', 'query': query})
        results=json.loads(r.text)
        if (len(results["results"]["bindings"])==0):
                nameUri=''
        else:
            for result in results["results"]["bindings"]:
                nameUri=result["label"]["value"]
        valor=getDef( nameUri, i,lenguaje)
        v1=valor[1].replace(',','')
        defs.append(v1)
        names.append(valor[0])
        if(valor[1]!=''):
            defsOnly.append(v1)
        
    return(names, defs, defsOnly)

#3. funcion que recibe la uri del broader y consulta cual es el termino correspondiente
def getDef( nameUri,uriRelation,lenguaje):
    definicion=''
    resultado=[]
    #for i in range(len(uriRelation)):
    lenguaje2='"'+lenguaje+'"'
    url=("http://sparql.lynx-project.eu/")
    query="""
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT ?c ?label
        WHERE {
        GRAPH <http://sparql.lynx-project.eu/graph/eurovoc> {
        VALUES ?c { <"""+uriRelation+"""> }
        VALUES ?searchLang { """+lenguaje2+""" undef } 
        VALUES ?relation { skos:definition  } 
        ?c a skos:Concept . 
        ?c ?relation ?label . 
        filter ( lang(?label)=?searchLang )
        }
        }
        """
    r=requests.get(url, params={'format': 'json', 'query': query})
    results=json.loads(r.text)
    if (len(results["results"]["bindings"])==0):
                definicion=''
    else:
        for result in results["results"]["bindings"]:
            definicion=result["label"]["value"]
    #print(nameUri, definicion)
    return(nameUri, definicion)


def lexicalaSearch(languageIn, term):
    search = requests.get("https://dictapi.lexicala.com/search?source=global&language="+languageIn+"&text="+term+"", auth=('987123456', '987123456'))
    answerSearch=search.json()
    return(answerSearch)

def lexicalaSense(maximo):
    sense = requests.get("https://dictapi.lexicala.com/senses/"+maximo+"", auth=('987123456', '987123456'))
    answerSense=sense.json()
    return(answerSense)

def resultsSyns(idioma,termino,targets,context, contextFile,wsid): 
    tradMax=[]
    getsyn=''
    if(termino):
        answer=lexicalaSearch(idioma, termino)
        if('n_results' in answer):
            results=answer['n_results']
            if(results>0):
                definitions=definitionGet(answer)
                if(wsid=='si'):
                    maximo=wsidFunction(termino,context, contextFile, definitions)
                    if(maximo[2]!=200):
                        maximo=(termino, '')
                        tradMax=traductionGet(maximo, targets)
                        synsTrad=justSyn(tradMax)
                        getsyn=synonymsGet(maximo)
                    else:
                        if(maximo[1]!=''):
                            tradMax=traductionGet(maximo, targets)
                            print(tradMax)
                            synsTrad=justSyn(tradMax)
                            getsyn=synonymsGet(maximo)
                        else:
                            getsyn=''
                            tradMax=[]
                else:
                    maximo=(termino, '')
                    tradMax=traductionGet(maximo, targets)
                    synsTrad=justSyn(tradMax)
                    getsyn=synonymsGet(maximo)

                #print(termino, maximo[0], maximo[1], getsyn, tradMax, synsTrad)
    return(getsyn, tradMax)

def justSyn(tradMax):
    joinSyns=''
    if(len(tradMax)>0):
        slp=tradMax[0].split(',')
        listaSinonimos=[]
        answer=lexicalaSearch(slp[1], slp[0])
        results=answer['n_results']
        if(results>0):
            if('synonyms' in answer.keys() ):
                syn=answer['synonyms']
                if(len(syn)>0):
                    for j in range(len(syn)):
                        synonym=syn[j]
                        listaSinonimos.append(synonym)
        joinSyns=','.join(listaSinonimos)
    return(joinSyns)



def synonymsGet(maximo):
    listaSinonimos=[]
    answer=lexicalaSense(maximo[1])
    if('synonyms' in answer.keys() ):
        syn=answer['synonyms']
        if(len(syn)>0):
            for j in range(len(syn)):
                 synonym=syn[j]
                 listaSinonimos.append(synonym)
    joinSyns=','.join(listaSinonimos)
    return(joinSyns)
    

                
def definitionGet(answer):
    listaDefinition=[]
    listaId=[]
    sense0=answer['results'][0]
    if('senses' in sense0.keys()):
        sense1=sense0['senses']
        for i in range(len(sense1)):
            if('definition' in sense1[i].keys()):
                id_definitions=sense1[i]['id']
                definitions=sense1[i]['definition']
                listaDefinition.append(definitions.replace(',', ''))
                listaId.append(id_definitions)
    return(listaDefinition, listaId)




def traductionGet(maximo, targets):
    textList=[]
    jsonTrad=lexicalaSense(maximo[1])
    if('translations' in jsonTrad.keys()):
        translations=jsonTrad['translations']
        for j in targets:
            if(j in translations):
                idiomas=translations[j]
                if('text' in idiomas):
                    text=idiomas['text']
                    textList.append(text+','+ j)
                else:
                    for k in range(len(idiomas)):
                        text=idiomas[k]['text']
                        textList.append(text+','+ j)


    return(textList)

def get_conceptNet_synonyms(term, lang="es"):
    # Given a term, get the synonyms from ConcetpNet of the same language
    # Note that all words are in lower case on ConceptNet, unlike Wikidata
    # Start and end edges should be taken into account
    synonyms = list()
    query_url_pattern = "http://api.conceptnet.io/query?EDGEDIRECTION=/c/LANG/TERM&rel=/r/Synonym&limit=1000"
    
    edge_directions = {"start":"end", "end":"start"}
    for direction in edge_directions.keys():
        query_url = query_url_pattern.replace("EDGEDIRECTION", direction).replace("LANG", lang).replace("TERM", term)
        # print(query_url)
        obj = requests.get(query_url).json()
        for edge_index in range(len(obj['edges'])):
            syn_lang = obj['edges'][edge_index][edge_directions[direction]]["language"]
            if syn_lang == lang:
                synonyms.append(obj['edges'][edge_index][edge_directions[direction]]["label"])
    return list(set(synonyms))

def inducer(T, A, S):
    # Gets T, the list of preferred labels and A, the list of alternative labels
    # Using synonyms of T, S, it induces the semantic relationship that exists between T and A. 
    # S is a dictionary of word as term and dictionary {lang: synonyms} as values.
    semantic_relationship = None
    
    if len(A) and len(T):
        invalid = False


        if " ".join(A).lower() == " ".join(T).lower():
            # They are identical. No semantic relationship should be induced. 
            pass
        
        elif len(T) == len(A):
            case_check = list()
            for t in T:
                if t in A:
                    case_check.append(True)
                else:
                    # check if the language exists
                    if len(S[t]):
                        if True in [True for s_t in S[t] if s_t in A]:
                            case_check.append(True)
                        else:
                            case_check.append(False)
                    else:
                        invalid = True

            if case_check.count(True) < len(T):
                semantic_relationship = "related"
            if not invalid and False not in case_check: 
                semantic_relationship = "synonymy"

        elif len(T) < len(A):
            case_check = list()
            for t in T:
                if t in A:
                    case_check.append(True)
                else:
                    # check if the language exists
                    if len(S[t]):
                        if True in [True for s_t in S[t] if s_t in A]:
                            case_check.append(True)
                        else:
                            case_check.append(False)
                    else:
                        case_check.append(False)

            # print(case_check)
            if False not in case_check:
                semantic_relationship = "narrower"

        elif len(T) > len(A):
            case_check = True
            for a in A:
                # Find all the synonyms of the existing terms
                syns = list()
                for term_syn in S.values():
                    if len(term_syn):
                        syns = syns + term_syn
                    else:
                        pass

                syns = list(set(syns))
                if len(syns):
                    if not (a in T or True in [True for s_t in syns if a in s_t]):
                        case_check = False
                else:
                    invalid = True

            if not invalid and case_check:
                semantic_relationship = "broader"

        else:
            pass

    return semantic_relationship

def crearRelaciones(relacion, retrieved_wikidata,  A,idioma, schema):
    skos="skos:"+relacion
    if(skos in retrieved_wikidata.keys()):
        relat=retrieved_wikidata[skos]
        cambio=''.join(A)
        verify=verificar(idioma,  cambio, relacion)
        ideB=verify[0]
        termSearchB=verify[1]
        #print(ideB, termSearchB)
        if(termSearchB!=''):
            retrieved_wikidata[skos].append(ideB)
            dataEurovoc=fileEurovoc(termSearchB, ideB, A, '-', idioma, schema)
            carpetas=os.listdir(idioma)
            #print('NUEVO ',relacion,':', termSearchB, '-', ideB)
            if(relacion in carpetas):
                with open(idioma+'/'+relacion+'/'+termSearchB+'_'+ideB+'.json', 'w') as file:
                    json.dump(dataEurovoc, file, indent=4,ensure_ascii=False)
            else:
                os.makedirs(idioma+"/"+relacion)
                with open(idioma+'/'+relacion+'/'+termSearchB+'_'+ideB+'.json', 'w') as file:
                    json.dump(dataEurovoc, file, indent=4,ensure_ascii=False)

def dataRetrieverFunction(newFile, idioma, schema):
    print("============ Reading the configuration file")
    #with open("configuration.json", 'r') as f:
    #    configuration = json.load(f)
    configuration={
        "source_file_dir": "backup/July16/scterm_dict.csv",
        "gold_concepts_dir": "backup/July16/goldstandard.json",
        "retrieve_wikidata": "backup/July16/scterm_dict.csv",
        "retrieve_ConceptNet": "backup/July16/goldstandard.json",
       
    }

    
    wikidata_output_file_name =newFile

    #source_file = open(configuration["source_file_dir"], "r")
    #sterms = [t for t in source_file.read().split("\n")]
    source_file=configuration["source_file_dir"]
    terms = [t for t in source_file.split("\n")]
    

    # ================
    if configuration["retrieve_ConceptNet"]:
        print("====== Retrieving data from ConceptNet:")
        #print(configuration["retrieve_ConceptNet"])
        #print(wikidata_output_file_name)
        with open(wikidata_output_file_name, 'r') as f:
            retrieved_wikidata = json.load(f)
        all_inductions = list()
        induced_relationships = list()
        for pref in retrieved_wikidata["skos:prefLabel"]:
            altLabel_induction = dict()
            #T = retrieved_wikidata["skos:inScheme"].lower().split()
            T=pref["@value"].lower().split()
            lang = pref["@language"]
            S = dict()
            for t in T:
                if t not in S:
                    S[t] = get_conceptNet_synonyms(t, lang)
            if len(S):
                for altLabel in retrieved_wikidata["skos:altLabel"]:
                    A = altLabel["@value"].lower().split()
                    if len(A):
                            # Go for axiom induction
                        T_A_relationship = inducer(T, A, S)
                        altLabel_induction[" ".join(A)] = T_A_relationship
                        #print("A:", A, "SR:", T_A_relationship)
                        if(T_A_relationship=='related'):
                            crearRelaciones('related',retrieved_wikidata,A,idioma, schema)
                            retrieved_wikidata["skos:altLabel"].remove(altLabel)

                        elif(T_A_relationship=='narrower'):
                            crearRelaciones('narrower',retrieved_wikidata,A,idioma, schema)
                            retrieved_wikidata["skos:altLabel"].remove(altLabel)
                        elif(T_A_relationship=='broader'):
                            crearRelaciones('broader ',retrieved_wikidata,A,idioma, schema)
                            retrieved_wikidata["skos:altLabel"].remove(altLabel)

                        elif(T_A_relationship=='synonymy'):
                            print('')
                        
            else:
                # No synonyms found on ConceptNet"
                altLabel_induction = {}
                    
            induced_relationships.append({"T":" ".join(T), "lang": lang, "S": S, "A": altLabel_induction})
            # Not to get timeout from ConceptNet API
            time.sleep(2)
        all_inductions.append(induced_relationships)
        f.close()
        #remove(wikidata_output_file_name)
        if(len(retrieved_wikidata['skos:broader'])>0):
            retrieved_wikidata['skos:broader'].remove()

        with open(wikidata_output_file_name, 'w') as file:
            json.dump(retrieved_wikidata, file, indent=4,ensure_ascii=False)
        #print(retrieved_wikidata)
    return(retrieved_wikidata)
       

#---------------------------------MAIN---------------------------------------------------------------
'''
parser=argparse.ArgumentParser()
parser.add_argument("--sourceFile", help="Name of the source csv file (term list)") #nombre de archivo a leer
parser.add_argument("--sourceTerm", help="Source term to search")
parser.add_argument("--lang", help="Source language")
parser.add_argument("--targets", help="Source language out")
parser.add_argument("--context", help="Contexto")
parser.add_argument("--contextFile", help="Archivo de contextos")
parser.add_argument("--wsid", help="")
parser.add_argument("--schema", help="")
args=parser.parse_args()

termino=args.sourceTerm
listTerm=args.sourceFile
idioma=args.lang
targets=args.targets.split(' ')
context=args.context
contextFile=args.contextFile
wsid=args.wsid
schema=args.schema

if(termino):
    lista=[]
    lista.append(termino)
    if(context):
        context=context
    elif(contextFile):
        file=open(contextFile+'.csv', 'r')
        contextF=csv.reader(file)
        contextFile=[]
        for i in contextF:
            contextFile.append([i[0], i[1],i[2],i[3]])
    else:
        contextFile=leerContextos(idioma)
    jsonlist=haceJson(lista, idioma,targets)
    all( jsonlist, idioma, targets,context, contextFile,  wsid,schema)
    
else:
    if(context):
        context=context
    elif(contextFile):
        print('file')
        file=open(contextFile+'.csv', 'r')
        contextF=csv.reader(file)
        contextFile=[]
        for i in contextF:
            contextFile.append([i[0], i[1], i[2],i[3]])
    else:
        contextFile=leerContextos(idioma)
    
    lista=[]
    file=open(listTerm+'.csv', 'r')
    read=csv.reader(file)
    for i in read:
        lista.append(i[0])
    ini=0
    fin=200
    tam=len(lista)
    if(tam>200):
        while(fin<tam):
            lista1=[]
            lista1=lista[ini:fin]
            print(ini, fin)
            jsonlist=haceJson(lista1, idioma,targets)
            all( jsonlist, idioma, targets,context, contextFile,  wsid,schema)
            time.sleep(10)
            ini=ini+200
            fin=fin+200
    else:
        jsonlist=haceJson(lista, idioma,targets)
        all( jsonlist, idioma, targets,context, contextFile, wsid, schema)
            
#TERM
#python3 all.py --sourceTerm término --lang es --targets "es en de nl"
'''
