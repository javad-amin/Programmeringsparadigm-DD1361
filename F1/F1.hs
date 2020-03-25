module F1 where

import Data.List
import System.IO
import Data.Char

{- Authors:
Authors:
    Mohammad Javad Ahmadi Amin
    Danilo Catalan Canales

    DD1361 - Progp HT17
    Labb: F1 -}

-- Uppgift 1: Fibonacci
fib :: Integer -> Integer
fib n
    | n == 0 = 0
    | n == 1 = 1
    | n > 1 = fib (n - 1) + fib (n - 2)

-- Uppgift 2: rovarspråk
rovarsprak :: String -> String
rovarsprak s
    | (s == "") = s
    | (head s `elem` ['a', 'e', 'o', 'i', 'y', 'u']) = [head s] ++ rovarsprak (tail s)
    | (head s `notElem` ['a', 'e', 'o', 'i', 'y', 'u']) = [head s] ++ "o" ++ [head s] ++ rovarsprak (tail s)

karpsravor :: String -> String
karpsravor s
    | (s == "") = s
    | (head s `elem` ['a', 'e', 'o', 'i', 'y', 'u']) = [head s] ++ karpsravor (tail s)
    | (head s `notElem` ['a', 'e', 'o', 'i', 'y', 'u']) = [head s] ++ karpsravor (tail (tail( tail s)))

-- Uppgift 3: Meddellängd
medellangd :: String -> Double
medellangd s =  fromIntegral (sum ordLengthLista) / fromIntegral (length ordLengthLista)
  where ordLengthLista = map length (words (taBortIckeAlpha s))

taBortIckeAlpha :: String -> String
taBortIckeAlpha s
    | (s == "") = s
    | (isAlpha (head s)) = [head s] ++ taBortIckeAlpha (tail s)
    | otherwise = [' '] ++taBortIckeAlpha (tail s)

--Uppgift 4: Skyffla
skyffla :: [a] -> [a]
skyffla [] = []
skyffla s = tempSkyffla s ++ skyffla (restSkyffla s)

tempSkyffla :: [a] -> [a]
tempSkyffla [] = []
tempSkyffla s
    | (length s > 1) = [head s] ++ tempSkyffla (tail (tail s))
    | otherwise = [head s]


restSkyffla :: [a] -> [a]
restSkyffla [] = []
restSkyffla s
    | (length s > 1) = [head (tail s)] ++ restSkyffla (tail (tail s))
    | otherwise = []

-- Uppgift 4: Alternativ lösning
-- bonus tar in ett index (som växlar mellan 1 och 2 där 1: går left och 2 går right)
-- left: lista som har vart annat element i listan och right: Elementen emellan
-- resultat: Slutkastet där man lägger ihop den med left hela tiden
-- lst: vår lista

bonus :: Int -> [a] -> [a] -> [a] -> [a] -> [a]

bonus index left right result  lst
  |(length lst) == 0 && (length right) == 0 = result ++ left
  |(length lst) == 0 = bonus 1 [] [] (result ++ left) right
  |odd index = bonus (index+1) (left ++ [head lst]) right result (tail lst)
  |even index = bonus (index-1) left (right ++ [head lst]) result (tail lst)

skyffla2 x = (bonus 1 [] [] []) x
