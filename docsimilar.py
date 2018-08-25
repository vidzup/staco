# File Created by Vidhu Bhala R V
#
# This program is an application of text mining on test cases.
#

import itertools
import sys
sys.path.append("/home/vidzup/.local/lib/python2.7/site-packages/")
import nltk, string, numpy, re
from nltk.corpus import wordnet
import xlrd, xlwt
print "Reading file"
import pickle
import wordbuild
import sys, os
os.environ['PYTHONINSPECT'] = 'True'
argv=sys.argv[1:len(sys.argv)]

iREPOfile=argv[0]
iREPOfileTAB=argv[1]
iRELfile=argv[2]
iRELfileTAB=argv[3]
#iModule=argv[4]


### Previous accepted changes
# API-Acquisition

##OverrideSet = [[8,5], [480,481,482]]
OverrideSet=[]
OverridePairs = set()

# Here we build out pairs of test cases that are reviewed by SMEs and accepted as valid duplicates.  We should not keep on repeating these as errors

for i in OverrideSet:
    OverridePairs = OverridePairs.union(frozenset(x) for x in list(itertools.combinations(i,2)))

import warnings

# This section contains all pre-coded variables.
#iREPOfile= "Repository Data.xlsx"
#iREPOfileTAB = "Cards-Eclipse cards"
#iREPOfileTAB = "RB-FT"
#iREPOfileTAB = "RB-SAO"
#iREPOfileTAB = "WM-Citiplanner"
#iRELfile=""
#iRELfileTAB=""
#iRELfile= "April Data.xlsx"
#iRELfileTAB= "RB-SAO(Apr)"

##oppwords=[('same','next'),('without','with'),('after','before'),('yes','no'),('single','joint'),('local','foreign'),('same','different'),('individual','corporate'),('summary','detail')]

neggwords=['never','not','no']

if iRELfile=="":
    oResults="Final recommendations"+iREPOfileTAB+".xls"
else:
    oResults = "Final recommendations"+iREPOfileTAB+"_"+iRELfileTAB+".xls"
oTerms= "Terms"+iREPOfileTAB+".csv"
oSetTerms= "TermsSet6"+iREPOfileTAB+".xls"
oSMEFeedback = "SME_" + iREPOfileTAB+".xls"

# Open the results workbook for writing
book = xlwt.Workbook(encoding="utf-8")
book1 = xlwt.Workbook(encoding="utf-8")
bookSME = xlwt.Workbook(encoding = "utf-8")

sheet1 = book.add_sheet("Set1")
try:
    book.save(oResults) ## Early save to ensure that the file is not open
except Exception:
    print oResults, "Please close the output file and execute program again"
    sys.exit(0)

workbook = xlrd.open_workbook(iREPOfile,"rb")
sheet = workbook.sheet_by_name(iREPOfileTAB)

# Initialize all arrays
TC = []
logarray=[]
TCName=[]
TCid = []

# Values for July Repository files
colREPOTestCaseName = 2
colREPOTCid =1
colREPOTestCaseDesc=3

# Read all test cases - Names, IDs and Descriptions
for a in sheet.col(colREPOTestCaseName,1,sheet.nrows):

    TCName.append(a.value)

for a in sheet.col(colREPOTCid,1,sheet.nrows):
    TCid.append(a.value)

for a in sheet.col(colREPOTestCaseDesc,1,sheet.nrows):
    TC.append(a.value)
NumRepository = sheet.nrows - 1

print "Processing category :",iREPOfileTAB
print "# of Repository Test cases ", len(TC)
logarray.append(["Repository analyzed",iREPOfileTAB])
logarray.append(["Test Cases in the Repository",len(TC)])

if iRELfile == "":
    NumRelease = 0
else:
    ## Read the release test cases
    
    workbook1 = xlrd.open_workbook(iRELfile,"rb")

    ##sheetRel = workbook1.sheet_by_index(0)
    sheetRel = workbook1.sheet_by_name(iRELfileTAB)
    colRELTestCaseName =1
    colRELTCid=0
    colRELTestCaseDesc=2
    colRELAutHours=3
    colRELcategory=4

    TCNameRel = []
    TCRel = []
    TCRelIds = []
    TCCat = []

    for a in sheetRel.col(colRELTestCaseName,1,sheetRel.nrows):
        TCNameRel.append(a.value)
        
    for a in sheetRel.col(colRELTestCaseDesc,1,sheetRel.nrows):
        TCRel.append(a.value)

    for a in sheetRel.col(colRELTCid,1,sheetRel.nrows):
        TCRelIds.append(a.value)

    logarray.append(["Release Data",iRELfile+"  "+ iRELfileTAB])
    logarray.append(["Test cases in Release",len(TCRel)])
    for a in sheetRel.col(colRELcategory,1,sheetRel.nrows):
        if a.value =='':
            TCCat.append('X')
        else:
            TCCat.append(a.value[0])
            
    NumRelease = sheetRel.nrows

    print "# of Release Test cases ", len(TCRel)


    TC.extend(TCRel)
    TCName.extend(TCNameRel)
    TCid.extend(TCRelIds)

import time
start_time = time.time()
print" Starting timer -----" 


##stemmer = nltk.stem.porter.PorterStemmer()
##
##def StemTokens(tokens):
##    return [stemmer.stem(token) for token in tokens]
##
##remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
##
##def StemNormalize(text):
##     return StemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))

lmtzr = nltk.WordNetLemmatizer().lemmatize


def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

##lemmer = nltk.stem.WordNetLemmatizer()

##def LemTokens(tokens):
##    return [lemmer.lemmatize(token) for token in tokens]

remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)


def normalize_text(text):
    word_pos = nltk.pos_tag(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))
    lemm_words = [lmtzr(sw[0], get_wordnet_pos(sw[1])) for sw in word_pos]

    return [x.lower() for x in lemm_words]

##
##def LemNormalize(text):
##    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))

print "Starting Tokenization, i.e  Lemmatization... and building the Term Frequency Matrix"

warnings.filterwarnings(module='sklearn*',action='ignore', category=DeprecationWarning)
def no_number_preprocessor(tokens):
    r = re.sub('(\d)+', '', tokens.lower())
    return r

from sklearn.feature_extraction.text import CountVectorizer
LemVectorizer = CountVectorizer(tokenizer=normalize_text, preprocessor = no_number_preprocessor, stop_words='english')

##LemVectorizer = CountVectorizer(tokenizer=LemNormalize)
print "Number of test case", len(TC)
LemVectorizer.fit_transform(TC)

print "After Lemmatization... Size of vocabulary : ",len(LemVectorizer.vocabulary_.keys())

tf_matrix = LemVectorizer.transform(TC).toarray()

#tf_matrixtmp = LemVectorizer.transform(TC)
#tf_matrix = numpy.asarray(tf_matrixtmp)

print "Normalizing the term frequency matrix and building distance matrix"
from sklearn.feature_extraction.text import TfidfTransformer
tfidfTran = TfidfTransformer(norm="l2")
tfidfTran.fit(tf_matrix)
#print tfidfTran.idf_

## Cosine similarity
import math
def idf(n,df):
    result = math.log((n+1.0)/(df+1.0)) + 1
    return result

tfidf_matrix = tfidfTran.transform(tf_matrix)

print "Creating Similarity matrix"
tmp_cos_similarity_matrix = tfidf_matrix * tfidf_matrix.T 
print "Created Similarity matrix"
cos_similarity_matrix = tmp_cos_similarity_matrix.toarray()

import difflib 

logarray.append(["Time taken for processing, i.e. creating similarity matrix(sec)",time.time() - start_time])

print(" Finished processing file inputs --- %s seconds ---" % (time.time() - start_time))

def fnWriteHeader(sht):   
    sht.write( 0, 0, "Confidence Level %")
    sht.write( 0, 1, "TC # 1")
    sht.write( 0, 2, "TC # 2")
    sht.write( 0, 3, "TCid # 1")
    sht.write( 0, 4, "TCid # 2")
    sht.write( 0, 5, "TC # 1 Name")
    sht.write( 0, 6, "TC # 2 Name")
    sht.write( 0, 7, "TC # 1 desc")
    sht.write( 0, 8, "TC # 2 desc")
    sht.write(0,9,"Direct String Match")
    sht.write(0,10,"TC Name similarity")
    sht.write(0,11,"Diff strings")

crRow = 1

Set1 = [] ## Same TC Name and Same desc
Set2 = [] ## Diff TC Desc - direct match
Set3 = [] ## Very similar TC design - 98%+ Match
Set4 = [] ## Similar TC design - 95%+ Match
Set5 = [] ## Sets of similary match
Set6 = [] ## Sets of direct match

FullAnalysis = []

## VB 29-6 COmmented to save time/space where running release comparison
for i in range(0, len(cos_similarity_matrix)):
    for j in range(0, i) :
        if cos_similarity_matrix[i,j] > .95: ##Chg this to align to base scores for now for better optimziation
            if i < NumRepository:
                iVal= "Repo-" + str(i+1)
            else:
                iVal= "Rels-" + str(i-NumRepository+1)        
            if j < NumRepository:
                jVal= "Repo-" + str(j+1)
            else:
                jVal= "Rels-" + str(j-NumRepository+1)
            FullAnalysis.append([cos_similarity_matrix[i,j], iVal,jVal, TCid[i], TCid[j], TCName[i], TCName[j], TC[i], TC[j]])
## -- Uncommented for BAU

print("Finished secondary processing --- %s seconds ---" % (time.time() - start_time))
print("Starting analysis for recommendations")

dct=wordbuild.load_antonyms()

def fnsplit(x):
        arrplus = []
        arrminus =[]
        modarr = re.split('\w+',x)
        wrdarr = re.split('\-|\+',x)[1:]
        j =0
        i=0

        for i in range(0,len(modarr)-1):
            if '+' in modarr[i]:
                arrplus.append(wrdarr[j])
                j=j+1
            elif '-' in modarr[i]:
                arrminus.append(wrdarr[j])
                j=j+1
        return arrplus, arrminus
    
def fnDiffTag(diffstr):
    d=diffstr.lower()
    d=d.replace('+++','')
    d= d.replace('---','')
    d = d.split('@@')

    for i in d:
        i=i.lstrip()
        m = re.match('\A.*?([\-]|[\+])',i)
        if m:
            x = m.group(0)[:-1]
            arr = i.split(' ')
            if arr[0]==[]:
                continue
            if arr[0][1].isdigit():
                continue
            arr.pop(-1)
            if arr!=[]:
                arrplus, arrminus = fnsplit(arr[0])
                for i in arrplus:
                    try:
                        if dct[i] in arrminus:
                            return "Opposing"
                    except KeyError:
                        continue
                for j in arrminus:
                    try:
                        if dct[j] in arrplus:
                            return "Opposing"
                    except KeyError:
                        continue
                for wrd in neggwords:
                    if wrd in arrplus and wrd not in arrminus:
                        return "Negated"
                    if wrd in arrminus and wrd not in arrplus:
                        return "Negated"
    return("Similar")

## VB 29-6 Comment to save space time
for x in FullAnalysis:
    flgval = re.sub("\s*", "", x[7]) == re.sub("\s*", "", x[8]) ## Same Test case description
    x.append(flgval)
    diffstr=""
    for df in difflib.unified_diff(x[7].split(),x[8].split(),n=1):
        diffstr=diffstr + df

    if flgval or diffstr=='': # Descriptions are matching
            TCNameMatch= difflib.SequenceMatcher(None, x[5], x[6]).ratio() 
            x.append(TCNameMatch)
            if TCNameMatch == 1:
                x.append("") # Dummy
                x.append("") # Another Dummy
                Set1.append(x)## TC Name & Desc matches
            else:
                x.append("") # Dummy
                x.append("") # Another Dummy
                Set2.append(x) ## TC Name mismatch & Desc same

    else: # Descriptions do not match
            TCNameMatch=0
            x.append("") ## Array Placeholder for TC Name Match
            if set([x[3],x[4]]) in OverridePairs:
                x.append("SME OK")
            else:
                x.append(fnDiffTag(diffstr))    
            x.append(diffstr)
            if x[0] >= .98:
                Set3.append(x) # Near similar matches
            elif x[0] >= .95:
                Set4.append(x)  # Similar matches          

##--VB

print("Time elapsed to create recommendations --- %s seconds ---" % (time.time() - start_time))

logarray.append(["Time elapsed to segregate recommendations in various Sets (sec)",time.time() - start_time])

def fnWriteSet(SetNum, ShtObj):
    fnWriteHeader(ShtObj)
    r = 1
    ShtObj.col(7).width = 256 * 50
    ShtObj.col(8).width = 256 * 50
    
    try:
        for x in SetNum:
            for c in range(0,13):
                ShtObj.write(r,c,x[c])
            r = r + 1
    except Exception: ## In the rare case, It will generate more than 65 K rows and Excel cannot handle.
        return

fnWriteSet(Set1,sheet1) # We already created sheet1 to check if the file was accessible
fnWriteSet(Set2, book.add_sheet("Set2"))

## VB 28-6 Temp remove to save space and time
fnWriteSet(Set3, book.add_sheet("Set3"))
fnWriteSet(Set4, book.add_sheet("Set4"))

## --VB
print(" Time elapsed to write recommendations to file --- %s seconds ---" % (time.time() - start_time))

##match = numpy.where(cos_similarity_matrix >= 0.99999)
##arrMatch = []
##ar = []
##arrMatchExact = []
##arEx=[]


##for i in range(0,len(match[0])):
##    if match[0][i]!= match[0][i-1]:
##        arrMatch.append(set(ar))
##        try:
##            arrMatchExact.append(set(arEx))
##        except Exception: 
##            continue
##        ar=[]
##        arEx=[]
##    ar.append(match[0][i])
##    ar.append(match[1][i])
##    if TC[match[0][i]]==TC[match[1][i]]:
##        arEx.append(match[0][i])
##        arEx.append(match[1][i])

arrX=[]

for c,t in enumerate(cos_similarity_matrix):
    i = numpy.where(cos_similarity_matrix[c]>0.99999)
## VB add for EMEA Deepak Temp to reduce threshold
##    i=numpy.where(cos_similarity_matrix[c]>0.95)
    if len(i[0])>1:
        arrX.append(sorted(set(i[0])))

newarr=[]

for i in arrX:
    if i not in newarr:
        newarr.append(i)       
    
##for i in stSame:
##    if i not in newarrEx and len(i) > 1:
##        newarrEx.append(i)

logarray.append(["Time taken incl recommendation (sec)",time.time() - start_time])

logarray.append(["Set1 : Pairs of Cases with same Names and Descriptions",len(Set1)])
logarray.append(["Set2 : Pairs of Cases with same Descriptions",len(Set2)])
logarray.append(["Set3 : Pairs of Cases with 98% similar descriptions",len(Set3)])
logarray.append(["Set4 : Pairs of Cases with 95% similar descriptions",len(Set4)])

import operator
def fnWriteSetDetl(sht,arrMatch):
    Gp = 0
    prvGp = -1
    prvi=""
    r=1
    c=0
    TCarr=[]
    for x in arrMatch:
        Gp = Gp + 1
        for y in x:
            TCarr.append([Gp, TCid[y],TC[y]])
        
    TCarr.sort(key=operator.itemgetter(0,2))

    for i in TCarr:
        sht.write(r,0,str(i[0]))
        sht.write(r,1,str(i[1]))
        sht.write(r,4,i[2])
        if prvGp == i[0]:
            ##sht.write(r,2,xlwt.Formula('$E$%d=$E$%d' % (r+1,r)))

            diffstr=""
            for df in difflib.unified_diff(i[2].split(),prvi.split(),n=1):
                diffstr = diffstr + df
            if diffstr == "":
                diffstr = "No change"
                if set ([prvTCid,i[1]]) in OverridePairs:
                    sht.write(r,2,"SME OK")
                else:
                    sht.write(r,2,"Same")
            else:
                if set([prvTCid,i[1]]) in OverridePairs:
                    sht.write(r,2,"SME OK")
                else:
                    sht.write(r,2,fnDiffTag(diffstr))
            sht.write(r,3,diffstr)
        r=r+1
        prvGp = i[0]
        prvTCid = i[1]
        prvi=i[2]
    return r-1

def fnNodiff(str1, str2):
    diffstr=""
    for df in difflib.unified_diff(str1.split(),str2.split(),n=1):
        diffstr=diffstr+df
    if diffstr=="":
        return True
    else:
        return False

def fnWriteSetHeader(sht):   
    sht.write( 0, 0, "Group")
    sht.write( 0, 1, "TC id")
    sht.write( 0, 4, "TC Description")
    sht.write( 0, 2, "Match with previous item in Group?")
    sht.write( 0, 3, "Diff String with previous item")
    sht.col(3).width = 70*256
    return sht

TCSet5 = fnWriteSetDetl(fnWriteSetHeader(book.add_sheet("Set5")),newarr)

logarray.append(["Set5 : Number of sets of matches found",len(newarr)])
logarray.append(["Set5 : Number of Test cases that can be reduced",TCSet5-len(newarr)])

##
##print  "Release TC #, Release TC id, Repository TC#, Repository TC id, Similarity%"
##
##for i in range(NumRepository-1,len(cos_similarity_matrix)):
##	for j in range(0,NumRepository-1):
##		if cos_similarity_matrix[i,j] > .90:
##			print i-NumRepository, 0, i-NumRepository, ",", TCid[i],",",j,",",TCid[j],",", cos_similarity_matrix[i,j]
##			

##https://sites.temple.edu/tudsc/2017/03/30/measuring-similarity-between-texts-in-python/

## When comparing Release to Repository, find Potential A, B, C cases

if len(iRELfile) >0: # Only if release cases are included.
    sheet4 = book.add_sheet("Categorization")

    row = 0
    col = 0

    sheet4.write(row,col,"Release TC#")
    sheet4.write(row,col+1,"Release TC QC id#")
    sheet4.write(row,col+2,"SME Recommendation")
    sheet4.write(row,col+3,"List of Potential A matches")
    sheet4.write(row,col+4,"List of Potential B matches")
    sheet4.write(row,col+5,"Any cases >70% similarity")
    sheet4.write(row,col+6,"Tool Recommendation")
    sheet4.write(row,col+8,"Recommendation Match")

    row = row+1
                    
    arrA=[]
    arrB=[]
    arrC=[]

    AConfidence = .99999
    BConfidence = .8
    CConfidence = .7

    for i in range (NumRepository,NumRelease + NumRepository - 1):
            vA = numpy.ix_(cos_similarity_matrix[i][:NumRepository-1] >= AConfidence)[0]
            arrA.append(vA)
            vB = numpy.where(numpy.logical_and(cos_similarity_matrix[i][:NumRepository-1]>=BConfidence, cos_similarity_matrix[i][:NumRepository-1]<1))[0]
            arrB.append(vB)
            vC = (cos_similarity_matrix[i][:NumRepository-1] < CConfidence).all()
            arrC.append(vC)
            sheet4.write(row,col,i - NumRepository + 1)
            sheet4.write(row,col+1,TCid[i])
            ## sheet4.write(row,col+2,str([int(TCid[x]) for x in vA if re.sub("\s*", "", TC[i]) == re.sub("\s*", "", TC[x])]))
            sheet4.write(row,col+3,str([int(TCid[x]) for x in vA if fnNodiff(TC[i],TC[x])]))
            sheet4.write(row,col+4,str([int(TCid[y]) for y in vB if not fnNodiff(TC[i],TC[y])]))
           ## re.sub("\s*", "", TC[i]) != re.sub("\s*", "", TC[y])]))
            sheet4.write(row,col+5,str(vC))
            sheet4.write(row,col+6,xlwt.Formula('IF($D$%d="[]",IF($E$%d="[]","C","B"),"A")' % (row+1,row+1)))
            sheet4.write(row,col+2,TCCat[i - NumRepository])
            sheet4.write(row,col+7,xlwt.Formula("$C$%d=$G$%d" % (row+1,row+1)))
            
            row = row+1

        

################# Post printing - not part of the processing #############
####

## Write the terms to an excel - this is for future use.

## VB 28-6: Comment all section below to save time/space
## Start
print " Writing terms ..."
import csv

TermRef = tfidf_matrix.transpose()
PosVector=[]
WhereVector=(TermRef!=0).sum(1)

Set6=[]
with open(oTerms, 'w') as csvfile:
    writer = csv.writer(csvfile)
    for c,i in enumerate(LemVectorizer.get_feature_names()):
        s1= wordnet.synsets(i)
        if s1 !=[]:
            v1= s1[0].pos()
        else:
            v1="?"
            Set6.append([c,i,numpy.nonzero(TermRef[c])[1]])
        PosVector.append(v1)
        try:
            s1= [str(i),v1]
            s1.extend(tf_matrix[c])
        except Exception:
            continue
        writer.writerow(s1)

## --VB

def fnWriteSet6Detl(arrMatch,sht):
    r=1
    for c,x in enumerate(arrMatch):
        for i,BadTC in enumerate(x[2]): # The list of test case References
            if r < 65535:
                sht.write(r,0,x[0])
                sht.write(r,1,x[1])
                sht.write(r,2,str(BadTC))
                sht.write(r,3,str(TCid[BadTC]))
                sht.write(r,4,TC[BadTC])            
            r=r+1
    return r-1
    
def fnWriteSet(arrMatch,sht):   
    sht.write( 0, 0, "Term Num")
    sht.write( 0, 1, "Term")
    sht.write( 0, 2, "TC Ref")
    sht.write( 0, 3, "TC id")
    sht.write( 0, 4, "TC Desc")
    return fnWriteSet6Detl(arrMatch,sht)

##VB28-6 Commented to save space/time
BadTermsTCs = fnWriteSet(Set6, book1.add_sheet("Set6"))
book1.save(oSetTerms)
## --VB

logarray.append(["Vocabulary size (# of Terms)",len(LemVectorizer.vocabulary_.keys())])
logarray.append(["Bad Terms - with no meanings",len(Set6)])

## VB 28-6 Comment to save space/time
##logarray.append(["Test Cases with bad terms - Total impacts per term & test case",BadTermsTCs])

## This is where we print the log details to the file.

sheet2 = book.add_sheet("Summary Information")
for c,logrow in enumerate(logarray):
	sheet2.write(c,0,logrow[0])
	sheet2.write(c,1,str(logrow[1]))

strInstr = [
"The recommended order in which the above recommendation should be reviewed.  The number of errors you find will reduce as you go down the list",
"Number 1 : Review sheet Set5 - which has grouped test cases that are similar",
"   Use the third and fourth columns in the sheet to enable you to quickly spot the differences in the description",
"Number 2 : Review sheet Set1 - you can quickly eliminate duplicates or make changes to the test case name/description",
"Number 3 : Ignore Set2 - it is already covered in Set5",
"Number 4 : Review sheet Set 3 - these are near similar pairs of cases.  Use the difference strings to quickly spot differences",
"Number 5 : Review sheet Set 4 - these are also similar pairs, but are more likely changes to test data only.  Use the difference strings to quickly spot differences",
" ---- The above are the main recommendations --- ",
"In addition, there is a separate sheet that lists various key words and test cases against them.  Please help to spot and correct spelling mistakes or report that the word is valid.",
"It is normal to see some words that are reported after removal of punctuation and lower case letters.  Just tag these as 'No error in test case' "
]

for num, logrow in enumerate(strInstr):
    sheet2.write(c+num + 2,0,strInstr[num])

sheet2.col(0).width = 70*256

book.save(oResults)

print "Recommendations are printed and ready for your view.."
logarray.append(["Total end to end time taken was (sec)",time.time() - start_time])

#sys.exit(0)

##for i in range (NumRepository,NumRelease + NumRepository - 1):
##	vB = numpy.where(numpy.logical_and(cos_similarity_matrix[i][:NumRepository-1]<=.20, cos_similarity_matrix[i][:NumRepository-1]<1))[0]
##	arrB.append(vB)
##	print TCid[i], " : ", len(vB)

##
##for i in range(0,len(arrRel)):
##	print i,
##	try:
##		x = TCid.index(arrRep[i])
##		print arrRel[i], arrRep[i], TCid.index(arrRel[i]), TCid.index(arrRep[i]),cos_similarity_matrix[TCid.index(arrRel[i]),x]
##	except ValueError:
##		print "Not found " , arrRep[i]	
##
##qryString = "To check GL entries when Fund transfer results in a time-out."
##TC.append(qryString)
##qryString = "To check Fund transfer on domestic currency to Voyager card."
##TC.append(qryString)
##LemVectorizer.fit_transform(TC)
##tf_matrix = LemVectorizer.transform(TC).toarray()
##tfidfTran = TfidfTransformer(norm="l2")
##tfidfTran.fit(tf_matrix)
##tfidf_matrix = tfidfTran.transform(tf_matrix)
##cos_similarity_matrix = (tfidf_matrix * tfidf_matrix.T).toarray()
#
print "Drawing the terms"

from graphviz import Digraph
G= Digraph(name = 'Only Nouns',engine='neato')
G1=Digraph(name ='Nouns and UnKnowns',engine='neato')
G2=Digraph(name='Inverted keywords',engine='neato')
mxSum=0
SumWhere=WhereVector.sum(axis=1)
for c,i in enumerate(LemVectorizer.get_feature_names()):
    if PosVector[c] =='n' or PosVector[c]=='?':
        if mxSum < SumWhere[c].sum():
            mxSum=SumWhere[c].sum()
## Remove max 10 occuring values

trray = sorted([(x,i) for (i,x) in enumerate(SumWhere)],reverse=True)[:10]
mxSum=trray[-1][0][0][0]
print mxSum

sh =  bookSME.add_sheet("SME Feedback")
sh.write(0,0,"Term")
sh.write(0,1,"Decision (Ignore/Type/Domain)")
sh.write(0,2,"Changed Word")
sh.write(0,3,"Category")
        
rw = 1

for  c,i in enumerate(LemVectorizer.get_feature_names()):
    arrSum=SumWhere[c].sum()
    fsize=str(arrSum)
    isizenum=int((float(mxSum-arrSum)/mxSum)*100.0)
    if isizenum<1:
        isize=str(1)
    else:
        isize=str(isizenum)
    if PosVector[c]=='n':
        G.node(i,color='black',shape='record',fontsize = fsize)
        G1.node(i,color='black',shape='record',fontsize = fsize)
        G2.node(i,color='black',fontsize= isize)
    if PosVector[c]=='?':
        G1.node(i,color='red',shape='record',fontsize = fsize)
        G2.node(i,color='red',fontsize = isize)
        sh.write(rw,0,i)
        rw = rw  +1

## VB 28-6 Comment to save space/time
bookSME.save(oSMEFeedback)
G.render()
G1.render()
G2.render()
## --VB

def fnQueryResults(QV,maxnum=10):
    arr=LemVectorizer.transform([QV])
    QTerms = numpy.nonzero(arr)[1]
    Subset= tfidf_matrix[:,QTerms]
    SumMatches = numpy.sum(Subset,axis=1).tolist()
    ranks = sorted( [(x,i) for (i,x) in enumerate(SumMatches)], reverse=True )
    cnt = 0
    for x, i in ranks:
        if x==[0] or cnt == maxnum:
            break
                                                                                
        print x, TCid[i], TC[i]
        cnt = cnt + 1
        raw_input("")
                                                                                                      


