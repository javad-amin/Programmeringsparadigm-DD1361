/* Authors:
Authors:
    Javad Amin
    Danilo Catalan Canales

    DD1361 - Progp HT17
    Labb: L1 */

/*
fib(N, F) :- F = N.
rovarsprak(Text, RovarText) :- RovarText = Text.
medellangd(Text, AvgLen) :- AvgLen = 1.0.
skyffla(Lista, Skyfflad) :- Skyfflad = Lista.
*/


/*
Vi använder oss av en rekursion som arbetar på den nya variabeln som man
skapar samtidigt som talet man skrev in minskar ner till basfallet (1,1,0).
Rekursionen sker i en linje fram och löses samma väg tillbaka.
*/
fib(0, 0).
fib(N, F) :- N > 0, fib(N, F, _).
fib(1, 1, 0).
fib(N, F1, F2) :-
    N > 1,
    N1 is N - 1,
    fib(N1, F2, F3),
    F1 is F2 + F3.

/*
Om ett tecken är en vokal så adderar vi det utan ändring.
Men om det är inte vokal så bygger vi konsonanten + o + konsonanten och sedan
kör rekursivt på resten av listan mi hermano.
*/
rovarsprak([],[]).
rovarsprak([Cabeza|Cola], [Cabeza|Restante]):- % Vokal
    isVowel(Cabeza), rovarsprak(Cola, Restante),!.
rovarsprak([Cabeza|Cola], [Cabeza, 111, Cabeza|Restante]):- % Ej Vokal
    rovarsprak(Cola, Restante),!.

/*
Ett predikat som kontrollerar om ett tecken är en vokal och returnerar sant i
så fall.
*/
isVowel(Letter) :-
    member(Letter, [97,101,105,111,117,121,65,69,73,79,85,89]).

/*
Vi använder oss av funktionen avgCalc för att beräkna medellängden.
*/
medellangd(Text,AvgLen):-!,
    taBortIckeAlpha(Text, AlphaText), % Bytter alla icke alfabet till mellanslag.
    words(AlphaText, OrdListan), % Splitrar varje ord i ett element i en lista.
    delete(OrdListan, [], CleanOrdLista), % Tar bort tomma listor.
    maplist(length, CleanOrdLista, OrdLengthLista), % Spara varje ords längd i en lista.
    sumlist(OrdLengthLista, SumListan),
    length(OrdLengthLista, LangdListan),
    AvgLen is SumListan / LangdListan.

/*
Vi tar bort alla icke alfabesiska tecken och byter dem mot mellanslag tecken.
*/
taBortIckeAlpha([],[]). % Basfall
taBortIckeAlpha([Head|Tail], [Head|Rest]):- % Ifall det finns i alfabetet.
    char_type(Head,alpha), taBortIckeAlpha(Tail,Rest),!.

taBortIckeAlpha([_|Tail],[32|Rest]):- % Annars
    taBortIckeAlpha(Tail,Rest),!.

/*
Skapar en lista med alla separerade ord.
*/
words(List, [Left|Rest]) :-
    Mellanslag is 32, % ASCII kod för mellanslag.
    append(Left, [Mellanslag|Right], List), !, % Vi splitrar listan när vi hittar en mellanslag.
    words(Right, Rest). % Kör rekursivt på resten av listan.
words(List, [List]). % När vi inte hittar en lista så sätter vi resten i en lista.


/*
medellangd("No, I am definitely not a pie!") ska returnera 3.14...

Test :medellang([078,111,044,032,073,032,097,109,032,100,101,102,105,
110,105,116,101,108,121,032,110,111,116,032,097,032,112,105,101,033], X).

medellangd("w0w such t3xt...") ska returnera 1.8
Test :
medellangd([119,048,119,032,115,117,099,104,032,116,051,120,116,046,046,046], X).
1.8
*/
/*BONUS MEDDELÄNGD Går igenom listan en gång
medellangd([],0).
medellangd(Text, AvgLen):- queue(Text, AvgLen, 0, 0, 0).

queue([Head|Rest], F , Bokstaver, Ord, O1):-
	char_type(Head, alpha),
	B1 is Bokstaver+1,
	O2 is Ord + O1,
	queue(Rest, F,B1, O2, 0).

queue([_|Rest], F ,Bokstaver, Ord, O1):-
	O2 is O1+1,
	O3 is O2/O2,
	queue(Rest, F,Bokstaver, Ord,O3).

queue([], F, Bokstaver, Ord, _):-
	O2 is Ord +1,
	F is Bokstaver/O2.
	*/
/*Kastar de till 2 lst där man arbetar på att lägga till de jämna i NL sedan TL. Rekursion sker sedan på TL. Car, Cadr och cddr 
tagna från scheme för att kunna bearbeta i listorna.*/
skyffla([],[]).
skyffla(Lista,NyLst):- skyffla(Lista, NyLst, [], []).

skyffla(Lista,NyLst,NL,TL):-
	length(Lista,I),
	I>0,
	car(Lista,X1),
	cadr(Lista,X2),
	cddr(Lista,Rest),
	append(NL,X1,L),
	append(TL,X2,Ls),
	skyffla(Rest, NyLst,L,Ls).

skyffla([], NyLst, NL, TL):-
	length(TL,I),
	I>0,
	skyffla(TL,NyLst,NL,[]).

skyffla(_,NyLst,NL,_):- append(NL,[],NyLst).


/* Varför det inte går att göra omvänt i detta fall så är det nog för car, cdr och cadr funktionerna som tar bort "The Accuracy"*/
car([X|_],[X]).
cadr([_,X|_],[X]).
cadr([_],[]).
cddr([_,_|Rest],Rest).
cddr([_],[]).
