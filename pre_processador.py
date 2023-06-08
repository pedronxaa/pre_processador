import re
from pathlib import Path

def pre_processar(CAMINHO_ARQUIVO_C, CAMINHO_BIBLI_PADRAO):
  with open(CAMINHO_ARQUIVO_C, "r") as arquivo:
      codigo_linha = arquivo.readlines()
  
  #expansao dos includes
  for x in range(len(codigo_linha)):
      if codigo_linha[x][0] == '#' and codigo_linha[x][1]=='i':
          include = ""
          for y in range(10, len(codigo_linha[x])-2):
              include += codigo_linha[x][y]
          if '"' in codigo_linha[x]:
            CAMINHO = Path.joinpath(Path(CAMINHO_ARQUIVO_C).parent, include)
            if CAMINHO.exists():
              pass
            else:
               CAMINHO = CAMINHO_BIBLI_PADRAO + include
          else:
              CAMINHO = CAMINHO_BIBLI_PADRAO + include
          with open(CAMINHO, "r") as arquivo_h:
              codigo_biblioteca = arquivo_h.read()
          with open("arquivo_final.c", "a") as arquivo:
              arquivo.write(codigo_biblioteca)
              arquivo.write("\n")
  
  # #retira identação
  for x in range(len(codigo_linha)):
    linha = ''
    cond = 0
    for y in range(len(codigo_linha[x])):
      if codigo_linha[x][y] != ' ' or cond == 1:
        linha += codigo_linha[x][y]
        cond = 1
    codigo_linha[x] = linha
  
  barra_n = 0
  
  #retira os \n
  for x in range(len(codigo_linha)-1):
    if codigo_linha[x]=='\n':
      barra_n += 1
  
  for x in range(barra_n):
    codigo_linha.remove('\n')
  
  # remove comentarios
  for x in range(len(codigo_linha)):
    linha = ''
    for y in range(len(codigo_linha[x])):
      if codigo_linha[x][y]== '/' and codigo_linha[x][y+1] == '/':
        break
      linha += codigo_linha[x][y]
    codigo_linha[x] = linha
  
  codigo = ''.join(codigo_linha)
  comments = r'/\*(.*?)\*/'
  codigo = re.sub(comments, '', codigo, flags=re.DOTALL)
  
  codigo = codigo.replace(" =", "=").replace("= ", "=").replace("+ ", '+').replace(" +", '+').replace(" -", '-').replace("- ", '-').replace("{ ", "{").replace(" {", "{").replace("} ", "}").replace(" }", "}").replace("( ", "(").replace(" (", "(").replace(") ", ")").replace(" )", ")").replace("; ", ";")

  codigo_linha = codigo.split('\n')
  
  for x in range(len(codigo_linha)):
    if not 'printf' in codigo_linha[x]:
      codigo_linha[x] = codigo_linha[x].replace(', ', ',')
  
  define_var = {}
  define_macro = {}
  
  # registra os defines 
  for x in range(len(codigo_linha)):
    # verifica se a linha está implementando um define
    if codigo_linha[x][0] == '#' and codigo_linha[x][1]=='d':
      define = ""
      define_valor = ''
      # verifica se o define é uma constante ou uma macro
      if not '(' in codigo_linha[x]:
        for y in range(8, len(codigo_linha[x])):
          if codigo_linha[x][y] != ' ':
            define += codigo_linha[x][y]
          elif codigo_linha[x][y] == ' ':
            for z in range(y+1, len(codigo_linha[x])):
              define_valor += codigo_linha[x][z]
            define_var[define] = define_valor
      elif '(' in codigo_linha[x]:
        lista = []
        index_ini_par=codigo_linha[x].find('(')
        index_fim_par=codigo_linha[x].find(')')
        index_ini_def_macro=index_fim_par+2
        for y in range(8, len(codigo_linha[x])):
          while codigo_linha[x][y] !='(':
            define += codigo_linha[x][y]
            break
          if codigo_linha[x][y] == '(':
            break
        define_macro[define] = []
        def_macro=''
        for y in range(index_ini_def_macro, len(codigo_linha[x])):
          def_macro+=codigo_linha[x][y]
        lista.append(def_macro)
        var = ''
        for y in range(index_ini_par+1, index_fim_par):
          while (ord(codigo_linha[x][y])>=65 and ord(codigo_linha[x][y])<=90) or (ord(codigo_linha[x][y])>=97 and ord(codigo_linha[x][y])<=122):
            var+=codigo_linha[x][y]
            break
          if not (ord(codigo_linha[x][y])>=65 and ord(codigo_linha[x][y])<=90) or (ord(codigo_linha[x][y])>=97 and ord(codigo_linha[x][y])<=122):
            lista.append((var,0))
            var=''
        for z in lista:
          if z[0]=='':
            lista.remove(z)
  
        define_macro[define] = lista
  
  # expande os defines       

  # expande os defines de constantes
  for x in range(len(codigo_linha)):
    # verifica se a linha é para definir um define, caso seja ele pula
    if not codigo_linha[x][0] == '#':
      # verifica linha por linha se possui uma constante definida a ser substituida
      for var in define_var:
        if var in codigo_linha[x] and not (ord(codigo_linha[x][codigo_linha[x].find(var)+len(var)]) >= 65 and ord(codigo_linha[x][codigo_linha[x].find(var)+len(var)]) <=90) and not (ord(codigo_linha[x][codigo_linha[x].find(var)+len(var)]) >= 97 and ord(codigo_linha[x][codigo_linha[x].find(var)+len(var)] <=122)):
          codigo_linha[x] = codigo_linha[x].replace(var, define_var[var])
  
  #expande os defines de macros
  for x in range(len(codigo_linha)):
    # verifica se a linha é para definir um define, caso seja ele pula
    if not codigo_linha[x][0] == '#':
      # percorre linha por linha para achar onde tem uma chamada de macro a ser substituida
      for macro in define_macro:
        if macro in codigo_linha[x]:
          for y in range(codigo_linha[x].find(macro),len(codigo_linha[x])):
            if codigo_linha[x][y] == ')':
              index_fim_chamada_macro = y
          num_var = 1
          lista_var = []
          valor_var = ''
          for y in range(codigo_linha[x].find(macro)+len(macro)+1,index_fim_chamada_macro):
            if codigo_linha[x][y].isnumeric():
              valor_var += codigo_linha[x][y]
            elif valor_var == '':
              pass
            else:
              lista_var.append(valor_var)
              valor_var = ''
          for y in range(codigo_linha[x].find(macro)+len(macro)+1,index_fim_chamada_macro-1):
            if num_var == len(define_macro[macro]):
              break
            else:
              if codigo_linha[x][y].isnumeric:
                define_macro[macro][num_var] = (define_macro[macro][num_var][0],lista_var[num_var-1])
                num_var+=1
          codigo_linha[x] = codigo_linha[x].replace(str(codigo_linha[x][codigo_linha[x].find(macro):index_fim_chamada_macro]),define_macro[macro][0])
          for z in range(len(define_macro[macro])-1):
            codigo_linha[x] = codigo_linha[x].replace(define_macro[macro][z+1][0],define_macro[macro][z+1][1])
  
  
  with open('arquivo_final.c', 'a') as arquivo:
    for x in range(len(codigo_linha)):
      if codigo_linha[x][0] == '#':
        pass
      else:
        arquivo.write(codigo_linha[x])
