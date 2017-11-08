#!/usr/bin/python
# -*- coding: utf-8 -*-

''' @author: Robert ŠAMÁREK 
    Created on Thu Dec 22 21:00:00 2016

    syntaxe: seminarka.py <file|dir> [<output_file>] [-n|-d|-g]

    atribut soubor - zpracuje zadaný soubor
    atribut složka - zpracuje všechny soubory ve složce
    atribut další (neexistující) soubor - výstup jako CSV
    přepínače řazení (Date DEFAULT)
       -n   User-Name 
       -d   Called-Station-Id
       -g   Calling-Station-Id
'''


''' Požadovaný zápočtový projekt:

a) skript, který bude zpracovávat zdrojové soubory, 
   a to jak jeden nebo všechny ve složce.

výstupem bude:

1) csv soubor s hodnotami:

Mon Nov  9 05:51:41 2015 <- datum
User-Name = "chrobak.v" <- (řazení) uživatelské jméno
Called-Station-Id = "32-A4-3C-4D-7A-20:   oa-IT " -> jen SSID bez mac   <-(řazení)
Calling-Station-Id = "D0-59-E4-91-37-8D" -> mac <-(řazení)

2) vypis na obrazovku,

Oba výstupy si mohu seřadit podle jednotlivých parametrů (<-řazení) viz. výše.
'''


import os         # importuj potřebné knihovny 
import pandas as pd
import re
import os.path
import numpy as np
import sys

###########################################
#########         Funkce        ###########     
########################################### 
      
def refile(soubor):
    """
    Reads the file and filter out only specified lines. Returns list. 
    Adding missing values. 
    """
    u = 1                                                # nastavit čitače 
    d = 1
    g = 1    
    selection = []
    fi = open(soubor, "r")                               # otevře soubor v argumentu
    for line in fi:                                      # projít všechny řádky 
        if re.match("[^\t.+][^\n]", line):               # když DATE, 
            if u == 0:                                   # zkontrolovat, jestlii  
                selection.append("User-Name = ")         # je předchotí záznam 
            if d == 0:                                   # úplný. Pokud ne, 
                selection.append("Called-Station-Id = ") # doplnit prázdným(i) záznamem(y)...
            if g == 0:
                selection.append("Calling-Station-Id = ")
            selection.append(line.rstrip('\n'))               
            u = 0                                             
            d = 0
            g = 0    
        elif re.match("\\tUser-Name\s=\s.*", line):
            selection.append(line.lstrip('\t').rstrip('\n'))   
            u += 1
        elif re.match("\\tCalled-Station-Id\s=\s.*", line):
            if u == 0:
                selection.append("User-Name = ")
                u += 1
            selection.append(line.lstrip('\t').rstrip('\n'))
            d += 1
        elif re.match("\\tCalling-Station-Id\s=\s.*", line):
            if u == 0:
                selection.append("User-Name = ")
                u += 1
            if d == 0:
                selection.append("Called-Station-Id = ")
                d += 1
            selection.append(line.lstrip('\t').rstrip('\n'))
            g += 1       
    return selection 
        
def lidf(li): 
    """
    Transforms list to array, reshapes the array, and transform to 
    DataFrame. Labels columns. Sorts by date/time.
    """
    arr = np.array(li, dtype=object)        # list převést na np.array
    a4 = arr.reshape(-1,4)                  # přeformátovat na 4 sloupce 
    data_frame = pd.DataFrame(a4, columns=['Date', 'User', 'Called', 'Calling']) # a pojmenovat sloupce
    data_frame['DateTime'] = pd.to_datetime(data_frame['Date']) # pomocný sloupec
    data_frame.sort_values(by = 'DateTime', inplace = True) # seřadit dle data
    del data_frame['DateTime']
    return data_frame                       
                                             
def stdout(data_frame):
    """
    Printing out each line of DataFrame as a block of four lines.
    Each block is separated by an empty line.   
    """    
    for i in range(len(data_frame)):        # vypsat výsup v požadovaném formátu
        print(data_frame.Date[i])
        print(data_frame.User[i])
        print(data_frame.Called[i])
        print(data_frame.Calling[i])
        print("")

def sort(data_frame, method): 
    """
    Sorting DataFrame by switch.   
    """    
    dic = {
        "-n" : "User", 
        "-d" : "Called",
        "-g" : "Calling"
    }
    data_frame.sort_values(by = dic[method], inplace = True)
    return data_frame.reset_index()     # resetovat index - jinak by nefungovala funkce stdout()
      
def fileout(data_frame, soubor):
    """
    Saves DataFrame as CSV.    
    """    
    data_frame.to_csv(soubor, index = False)


###########################################
#########      Hlavní program   ########### 
###########################################


if len(sys.argv) == 1:                      # bez parametrů - vypiš hlášku 
    print("Type \'seminarka.py --help\' for help.")
    sys.exit()

fili = [] 
if os.path.isfile(sys.argv[1]):             # pokud je soubor 
    fili = refile(sys.argv[1])              # načti soubor do 1D pole fili 
elif os.path.isdir(sys.argv[1]):            # pokud je dir
    for eachFile in os.listdir(sys.argv[1]): # pstupně načti všechny 
        fili = fili + refile(sys.argv[1] + '/' + eachFile)  # soubory do fili
elif sys.argv[1] == "--help":
    print("seminarka.py <file|dir> [<output_file>] [-n|-d|-g] \n"
          "Sort by: -n   User-Name \n"
          "         -d   Called-Station-Id \n"
          "         -g   Calling-Station-Id")
    sys.exit()
else: 
    print("Type \'seminarka.py --help\' for help. ")
    sys.exit()

df = lidf(fili)             # převeď list na df 

if len(sys.argv) == 2:      # pokud nejsou další argumenty 
    stdout(df)              # vytiskni na obrazovku
    sys.exit()

if len(sys.argv) == 3:      # se 3 argumenty
    if ((sys.argv[2] == "-n") | (sys.argv[2] == "-d") | (sys.argv[2] == "-g")): 
        stdout(sort(df, sys.argv[2]))   # seřaď a vytikni
        sys.exit()
    else: 
        fileout(df, sys.argv[2]) # ulož bez třídění 
        sys.exit()
else:                       # se 4 argumenty - seřaď a ulož
    if ((sys.argv[3] == "-n") | (sys.argv[3] == "-d") | (sys.argv[3] == "-g")): 
        fileout(sort(df, sys.argv[3]), sys.argv[2])
    else: 
        print("Type \'seminarka.py --help\' for help. ")
    sys.exit()




