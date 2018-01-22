import string
import re
from collections import deque

_key=("auto","break","case","char","const","continue","default",  
"do","double","else","enum","extern","float","for",  
"goto","if","int","long","register","return","short",  
"signed","static","sizeof","struct","switch","typedef","union",  
"unsigned","void","volatile","while","define","strlen","using",
"namespace")

_bounds=',;(){}[]\'.'

_mathsign=("+","-","*","//","=","<",">",">=","<=","==","!=", 
"++","--","+=","-=","*=","//=","&",  
"&&","|","||","<<",">>","^","%","~"  
"^=","%=","!")


_code=''
_zhushi=[]
_line=0
_lexfile='编号\t行号\t字符\t类型\n'
_errorlog=''

#读文件
def codeFromFile():
   global _code
   file=open('1.cpp')
   _code=file.read()
   
   delComment()
   if not lexical():
      print(_errorlog)
   #else:
   print(_lexfile)
   file.close()

#词法分析
#暂时不处理以#开头的头文件包含
def lexical():
   global _code,_bounds,_line,_lexfile,_errorlog,_mathsign
   instring=False
   mathflag=False
   nextlineflag=False
   queue=deque()
   sign=0 #标识符1 常量2 运算符3 界符4 关键字5
   num=0
   word=''
   
   for i in _code:

      #C中的头文件
      if i=='#':
         nextlineflag=True
      
      if i=='\n':
         _line=_line+1
         if nextlineflag:
            nextlineflag=False
      if nextlineflag:
         continue
      
      #遇到界限符 作为分割标志
      #运算符先压栈 因为有+和++ +=等
      match=re.search('\s+',i)
      if match or i in _bounds or i in _mathsign:

         #字符串的开始或结束 (转义??)
         if i=='\'':
            instring=not instring

         if instring:
            queue.append(i)
            continue

         #运算符标记位的改变
         if i in _mathsign and not mathflag:
            mathflag=True
         if not i in _mathsign:
            if mathflag:
               mathflag=False
            
         #获取截取的单词
         while queue:
            ch=queue.popleft()
            word=word+ch
            #假如单词以数字开头 则不允许出现字母
            if word[0] in string.digits:
               if ch in string.ascii_letters:
                  _errorlog=_errorlog+'第 '+str(_line)+'行词法出错！\n'
                  return False

         if word:

            if word[0] in string.digits:
               sign=2
               num=num+1
               _lexfile=_lexfile+str(num)+'\t'+str(_line)+'\t'+word+'\t'+str(sign)+'\n'
            else:
               if word in _mathsign:
                  if i in _mathsign:
                     word=word+i
                     mathflag=False
                  if word in _mathsign:
                     sign=3
                     num=num+1
                     _lexfile=_lexfile+str(num)+'\t'+str(_line)+'\t'+word+'\t'+str(sign)+'\n'
                  else:
                     _errorlog=_errorlog+'第 '+str(_line)+'行词法出错！\n'
                     return False                 
                  
               elif word in _key:
                  sign=5
                  num=num+1
                  _lexfile=_lexfile+str(num)+'\t'+str(_line)+'\t'+word+'\t'+str(sign)+'\n'
               else:
                  sign=1
                  num=num+1
                  _lexfile=_lexfile+str(num)+'\t'+str(_line)+'\t'+word+'\t'+str(sign)+'\n'

            word=''
            
         if i in _bounds:
            sign=4
            num=num+1
            _lexfile=_lexfile+str(num)+'\t'+str(_line)+'\t'+i+'\t'+str(sign)+'\n'

         if mathflag:
            queue.append(i)

      #字母或数字 压入队列 之后判断是常量标识符还是关键字
      elif i in string.ascii_letters or i in string.digits:
         if mathflag:
            mathflag=False
            while queue:
               ch=queue.popleft()
               word=word+ch
               
            if word in _mathsign:
               sign=3
               num=num+1
               _lexfile=_lexfile+str(num)+'\t'+str(_line)+'\t'+word+'\t'+str(sign)+'\n'
            word=''
         queue.append(i)

#按行读取操作
#分行的/**/类型注释待解决
def delComment():
   #two type of comment in code // or /**/
   global _code
   state=0
   #0 normal
   #1 find / ready to be comment
   #2 in comment
   #3 ready to end in /**/
   #4 ready to end when meet \n
   
   startindex=0
   index=-1
   for i in _code:
      index=index+1
      if i=='/':
         if state==1:
            #// comment
            state=4
            #endindex=len(_code)
            break

         elif state==0:
            startindex=index
            state=1
            continue
         elif state==2:
            continue
         elif state==3:
            endindex=index+1
            replacecode=_code[startindex:endindex]
            _code=_code.replace(replacecode,' ')
            index=index-len(replacecode)+1
            state=0
            continue
         elif state==4:
            if i=='\n':
               endindex=index+1
               replacecode=_code[startindex:endindex]
               _code=_code.replace(replacecode,' ')
               index=index-len(replacecode)+1
               state=0
               continue

      elif i=='*':
         if state==1:
            #/* comment
            state=2
            continue
         elif state==0:
            #指针
            continue
         elif state==2:
            state=3
            continue

if __name__=='__main__':
   codeFromFile()
   
      
   
