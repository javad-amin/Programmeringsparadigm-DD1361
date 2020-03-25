# coding: utf-8
########################################################################
# Mall för labb S1, DD1361 Programmeringsparadigm.
# Författare: Javad Amin & Danilo Catalan
########################################################################

########################################################################
# Dessa funktioner är det som ska skrivas för att lösa de olika
# uppgifterna i labblydelsen.
########################################################################

def dna():          # uppgift 1
    # En dna-sekvens består av en eller flera av "ACGT" teckenuppsättning.
    return "^[ACGT]+$"

def sorted():       # uppgift 2
    # Först matchar vi 0 eller flera "9" sedan "8" osv.
    return "^9*8*7*6*5*4*3*2*1*0*$"

def hidden1(x):     # uppgift 3
    # Indata x är strängen som vi vill konstruera ett regex för att söka efter.
    # Vår regex innehåller indatan "x" och vad som helst "." kan komma före eller efter indatan.
    return "^.*" + x + ".*$"

def hidden2(x):     # uppgift 4
    # Indata x är strängen som vi vill konstruera ett regex för att söka efter.
    # Det ska finnas en sträng som innehåller vår indata om vi tar bort allt annat.
    # Vi matchar för alla tecken som är joinade med vår indata sekvens.
    return "^.*" + ".*".join(x) + ".*$"

def equation():     # uppgift 5
    # a. Minus och plus kan förekomma en (0 eller 1) gång i början av uttrycket.
    # b. Sedan kommer ett teckenuppsättning som består av ett eller flera siffror.
    # c. En aritmetisk operation följt av en uppsättning siffror kan förekomma.
    # d. a,b,c som föregår ett likhetstecken kan komma (0 eller 1) gång.
    return "^[-+]?[0-9]+([-+*/][0-9]+)*(=[+-]?[0-9]+([-+*/][0-9]+)*)?$"

def parentheses():  # uppgift 6
    # 1 eller flera uttryck som kan innehålla från 1 till 5 nästlade paranteser.
    return "^(\((\((\((\((\(\))*\))*\))*\))*\))+$"

def sorted3():      # uppgift 7
    # Vi matchar mot siffror från 0 till många.
    # Vi matchar mot någon av sorterade tal i mitten.
    return "^[0-9]*(01[2-9]|[0-1]2[3-9]|[0-2]3[4-9]|[0-3]4[5-9]|[0-4]5[6-9]|[0-5]6[7-9]|[0-6]7[8-9]|[0-7]89)[0-9]*$"

########################################################################
# Raderna nedan är lite testkod som du kan använda för att provköra
# dina regexar.  Koden definierar en main-metod som läser rader från
# standard input och kollar vilka av de olika regexarna som matchar
# indata-raden.  För de två hidden-uppgifterna används söksträngen
# x="test" (kan lätt ändras nedan).  Du behöver inte sätta dig in i hur
# koden nedan fungerar om du inte känner för det.
#
# För att provköra från terminal, kör:
# $ python s1.py
# Skriv in teststrängar:
# [skriv något roligt]
# ...
########################################################################
from sys import stdin
import re

def main():
    def hidden1_test(): return hidden1('test')
    def hidden2_test(): return hidden2('test')
    tasks = [dna, sorted, hidden1_test, hidden2_test, equation, parentheses, sorted3]
    print('Skriv in teststrängar:')
    while True:
        line = stdin.readline().rstrip('\r\n')
        if line == '': break
        for task in tasks:
            result = '' if re.search(task(), line) else 'INTE '
            print('%s(): "%s" matchar %suttrycket "%s"' % (task.__name__, line, result, task()))


if __name__ == '__main__': main()
