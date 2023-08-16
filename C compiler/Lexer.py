# -*- coding: utf-8 -*-

from sly import Lexer
import os
import re
import sys



class CLexer(Lexer):
    
    
    tokens = {BREAK, CASE, CHAR, CONTINUE, DOUBLE, ELSE,
              FLOAT, FOR, IF, INT, LONG, RETURN, SWITCH, VOID, WHILE,
              INT_CONST, CHAR_CONST, DECIMAL_CONST, STR_CONST, IDENTIFIER, ERROR, 
              LE, GE, EQUAL, PLUSEQ, MINUSEQ, PLUSPLUS, MINUSMINUS, DIFFERENT, SUB}
    
    # Literals and Symbols
    literals = {'(',')','{','}','.','++','--','+','-','!','/','*','%','<','>',
                '<=','>=','==',';','=',',','#','+=','-=', ':'}
    SUB=r'-'
    LE = r'<='
    GE = r'>='
    EQUAL = r'=='
    DIFFERENT = r'!='
    PLUSEQ = r'\+='
    MINUSEQ = r'-='
    PLUSPLUS = r'\+\+'
    MINUSMINUS = r'--'

    # Keywords
    BREAK = r'\bbreak\b'
    CASE = r'\bcase\b'
    CHAR = r'\bchar\b'
    CONTINUE = r'\bcontinue\b'
    DOUBLE = r'\bdouble\b'
    ELSE = r'\belse\b'
    FLOAT= r'\bfloat\b'
    FOR = r'\bfor\b'
    IF= r'\bif\b'
    INT= r'\bint\b'
    LONG= r'\blong\b'
    RETURN= r'\breturn\b'
    SWITCH= r'\bswitch\b'
    VOID= r'\bvoid\b'
    WHILE= r'\bwhile\b'
    
    # Identifiers
    IDENTIFIER = r'[a-zA-Z_]+[a-zA-Z_0-9]*'
    
    # Type values
    DECIMAL_CONST = r'-?[0-9]+\.[0-9]+'
    INT_CONST = r'-?[0-9]+'
    CHAR_CONST = r'\'.{1}\''
    
    @_(r'//.*(\n|$)')
    def COMMENT(self, t):
        self.lineno += 1
        
    @_(r'/\*')
    def COMMENT_MULTILINE(self, t):
        self.begin(Comments)
        
    @_(r"\n")
    def NEW_LINE(self,t):
        self.lineno += 1
    
    @_(r'\'(\w|\d|\s)+\'')
    def ERROR(self, t):
        return t
    
    @_(r'\"')
    def STRINGS(self, t):
        self.begin(Strings)
    
    @_(r'\s')
    def BLANK(self, t):
        pass
    
    def salida(self, texto):
        list_strings = []
        lexer = CLexer()
        for token in lexer.tokenize(texto):
            result = f'#{token.lineno} {token.type} '
            if token.type == 'IDENTIFIER':
                if '[' in token.value:
                    result += f"{token.value[0:token.value.find('[')]}"
                else:
                    result += f"{token.value}"
            elif token.type in self.literals:
                result = f'#{token.lineno} \'{token.type}\''
            elif token.type == 'STR_CONST' or token.type == 'CHAR_CONST':
                result += token.value
            elif token.type == 'INT_CONST' or token.type == 'DECIMAL_CONST':
                result += str(token.value)
            elif token.type == 'STR_CONST':
                result += token.value
            elif token.type == 'ERROR':
                result = f'#{token.lineno} {token.type} "{token.value}"'
            else:
                result = f'#{token.lineno} {token.type}'

            list_strings.append(result)
        return list_strings
    

    
class Comments(Lexer):
    _contador = 1

    tokens = {}

    @_(r'.$')
    def EOF(self, t):
        self.lineno += 1
        t.lineno += 1
        self._caracteres = ''
        t.type = "ERROR"
        t.value = "EOF in comment"
        return t


    @_(r'\*\)$')
    def FINFILE2(self, t):
        self._contador -= 1
        if self._contador == 0:
            self._contador = 1
            self.begin(CLexer)
        else: 
            self._caracteres = ''
            t.type = "ERROR"
            t.value = "EOF in comment"
            return t



    @_(r'/\*')
    def BEGINING(self, t):
        self._contador += 1

    @_(r'\*/')
    def END(self, t):
        self._contador -= 1
        if self._contador == 0:
            self._contador = 1
            self.begin(CLexer)
    
    @_(r'\n')
    def NEW_LINE(self, t):
        self.lineno += 1

    @_(r'.')
    def CHARACTER(self, t):
        t.value = ''
        
        
class Strings(Lexer):
    
    _caracteres = ''
    _null = False
    _nullEscapado = False
    _counter = 0
    
    tokens = {STR_CONST, ERROR}

    @_(r'\\\n')
    def SALTO_ESCAPADO(self,t):
        self.lineno += 1
        self._counter +=1
        t.type = "STR_CONST"
        self._caracteres += r'\n'
         
      
    @_(r'\\\t')
    def TABULADOR_ESCAPADO(self,t):
        t.type = "STR_CONST"
        self._caracteres += r'\t'
        
        
    @_(r'\\\x08')
    def ESPACIO_ESCAPADO(self,t):
        t.type = "STR_CONST"
        self._caracteres += r'\b'
        
        
    @_(r'\\\f')
    def FORMFEED_ESCAPADO(self,t):
        t.type = "STR_CONST"
        self._caracteres += r'\f'
           
        
    @_(r'\\\\')
    def DOBLE_BARRA(self, t):
        self._counter +=1
        t.type = "STR_CONST"
        self._caracteres += r"\\"

        
    @_(r'\\[tnbf"]')
    def ESPECIALES(self, t):
        t.type = "STR_CONST"
        self._caracteres += '\\' + t.value[1]
        self._counter += 1
     
    
    @_(r'[\x01-\x08]|\x0B|\x0D|\x0F|[\x10-\x19]|\x1A|\x1B|\x1C|\x1D|\x1E|\x1F')
    def CONTROL(self, t):
        t.type = "STR_CONST"
        self._caracteres += '\\' + oct(ord(t.value)).replace('o','')
    
    
    @_(r'\x0C')
    def NUEVA_PAGINA(self, t):
        t.type = "STR_CONST"
        self._caracteres += r'\f'
        
        
    @_(r'\\\x00')
    def NULO_ESCAPADO(self,t):
        self._nullEscapado = True  
         
        
    @_(r'\x00')
    def NULO(self,t):
        self._null = True


    @_(r'\\.')
    def POR_DEFECTO(self, t):
        t.type = "STR_CONST"
        self._caracteres += t.value[1]
        
        
    @_(r'\t')
    def TABULADOR(self, t):
        t.type = "STR_CONST"
        self._caracteres += r'\t'
    
   
    @_(r'[^\"]\n$')
    def SALTO_Y_EOF(self, t):
        return error_string_sin_terminar(self, t)
    
    
    @_(r'(.\\?$)|(.\\"$)')
    def EOF(self, t):
        if t.value == '"':
            
            # Comprobacion de caracteres nulos
            if self._null == True:
                return error_nulo(self, t)
            
            if self._nullEscapado == True:
                return error_nulo_escapado(self, t)
            
            # Correcto
            return string_correcto(self, t)
            
        # EOF    
        return error_eof(self, t)
    
    @_(r'.')
    def CARACTER(self, t):
        if t.value == '"':
                
            # Comprobacion de caracteres nulos
            if self._null == True:
                return error_nulo(self, t)
            
            if self._nullEscapado == True:
                return error_nulo_escapado(self, t)
            
            # Correcto
            return string_correcto(self, t)
        
        self._counter += 1
        self._caracteres += t.value
        
    
    @_(r'\n')
    def SALTO_LINEA(self,t):
        
        # Comprobacion de caracteres nulos
        if self._null == True:
            return error_nulo(self, t)
        
        if self._nullEscapado == True:
            return error_nulo_escapado(self, t)
        
        return error_string_sin_terminar(self, t)


def error_nulo(self, t):    
    if (t.value != '"'):
        self.lineno += 1
    self._counter = 0
    self._caracteres = ''
    self._null = False
    t.type = "ERROR"
    t.value = "String contains null character."
    self.begin(CLexer)
    return t


def error_nulo_escapado(self, t):   
    if (t.value != '"'):
        self.lineno += 1
    self._counter = 0
    self._caracteres = ''
    self._nullEscapado = False
    t.type = "ERROR"
    t.value = "String contains escaped null character."
    self.begin(CLexer)
    return t
    

def error_eof(self, t): 
    self._counter = 0
    self._caracteres = ''
    t.type = "ERROR"
    t.value = "EOF in string constant"
    self.begin(CLexer)
    return t


def error_string_sin_terminar(self, t): 
    self.lineno += 1
    t.lineno += 1
    self._counter = 0
    self._caracteres = ''
    t.type = "ERROR"
    t.value = "Unterminated string constant"
    self.begin(CLexer)
    return t

def string_correcto(self, t):
    t.value = f'"{self._caracteres}"'
    t.type = "STR_CONST"
    self._counter = 0
    self._caracteres = ''
    self.begin(CLexer)
    return t

