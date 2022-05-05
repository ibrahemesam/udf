def strdel(s,f,t=None):
    if t==None:t=f
    s=str(s);f=int(f);t=int(t)
    s=s[:f]+s[t+1:]
    return s

def strdelf(s,w):
    i=s.find(w)
    if i==-1:return s
    s=strdel(s,i,i+len(w)-1)
    return s

def strcon(s,w):
    if s.find(w)==-1:return 0
    num=0
    while True:
        s=strdelf(s,w)
        num=num+1
        if s.find(w)==-1:break

    return num

def isNull(v): #check if a var is None or equals ""
    if v==None:
        return True
    else:
        v=str(v)
        if v=="":
            return True
        else:return False

def strbt(string,start,end):
    string=str(string)
    start=str(start)
    end=str(end)
    #errors : if (string or start or end) is (None or "")
    if isNull(string)or isNull(start)or isNull(end): return -1
    #errors : if "start" not exist in "string"
    if not start in string:return -2
    #errors : if "end" not exist in "string"
    if not end in string:return -3
    array=[]

    #if between the same string
    if start==end:
        sepa=end
        #errors : if start is the same end (the same index)
        if not sepa in strdelf(string,sepa):return -4
        array=string.split(sepa)
        return array[1:len(array)-1]
        #not split : str="gh1h2h3hj" out="1,3" not"1,2,3"

    #errors : if start is est(a part of end or the opisite
    if (start in end)or(end in start):
        if len(start)>len(end):small=end
        elif len(start)<len(end):small=start
        if not small in strdelf(string,small):return -5

    while True:
        sfind=string.find(start)
        if sfind==-1:break
        result=string[sfind+len(start):]
        efind=result.find(end)
        if efind==-1:break
        result=result[:efind]
        array.append(result)
        string=string[string.find(result)+len(result)+len(end):]
    return array
