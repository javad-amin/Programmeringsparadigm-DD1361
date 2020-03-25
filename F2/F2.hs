module F2 where
import Data.List
import Control.Monad

{- Authors:
Authors:
    Javad Amin
    Danilo Catalan Canales
    DD1361 - Progp HT17
    Labb: F2 -}



    ----------------------------------------------------------------------
            --              Molekylära sekvenser                --
    ----------------------------------------------------------------------
{- Uppgift 1 : Skapa en datatyp MolSeq för molekylära sekvenser som anger
sekvensnamn, sekvens (en sträng), och om det är DNA eller protein som
sekvensen beskriver. Du behöver inte begränsa vilka bokstäver som får
finnas i en DNA/protein-sträng. -}

-- DataTypen SekvensTyp: där sekvenstypen kan antingen vara DNA eller Protein
data SekvensTyp = DNA | Protein deriving (Eq, Show)

-- Definierar datatypen MolSeq som lagrar: SekvensNamnet som är av typ string,
-- självaProfile DNA/Protein Sekvensen, samt vilken typ av sekvens det är!
data MolSeq = MolSeq{
    sekvensnamn :: String,
    sekvens :: String,
    sekvenstyp :: SekvensTyp
} deriving (Show)

--Uppgift 2
{-Skriv en funktion string2seq med typsignaturen String -> String -> MolSeq.
  Dess första argument är ett namn och andra argument är en sekvens.
  Denna funktion ska automatiskt skilja på DNA och protein,
  genom att kontrollera om en sekvens bara innehåller A, C, G, samt T
  och då utgå ifrån att det är DNA. -}

--  isDNA är ett predikat som kollar om sekvensen inehåller endast DNA
--  nukleiderna "AGCT".
--  Om det är ett DNA så returneras True, om inte returneras False
--  (allstå är det ett Protein).

isDNA :: String -> Bool
isDNA [] = True
isDNA sekvens
  | (head sekvens) `elem` "AGCT" = isDNA (tail sekvens)
  | otherwise = False

-- Tar in två argument (sekvensnamn och sekvensen) där den returnerar MolSeq
-- där sekvensen bestämmer om det är ett DNA eller Protein
string2seq :: String -> String -> MolSeq
string2seq sekvensnamn sekvens
  | isDNA sekvens = MolSeq sekvensnamn sekvens DNA
  | otherwise = MolSeq sekvensnamn sekvens Protein

-- Uppgift 3
{-Skriv tre funktioner:
  seqName, seqSequence, seqLength som tar en MolSeq och returnerar namn,
  sekvens, respektive sekvenslängd. Du ska inte behöva duplicera din kod
  beroende på om det är DNA eller protein!-}

-- Tar in en MolSeq och returnerar namnet på MolSeq och ignorerar resten.
seqName :: MolSeq -> String
seqName (MolSeq namn _ _ ) = namn
-- Tar in en MolSeq och returnerar sekvensen på MolSeq och ignorerar resten.
seqSequence :: MolSeq -> String
seqSequence (MolSeq _ sekvens _ ) = sekvens
-- Tar in en MolSeq och returnerar längden på sekvensen på MolSeq och
-- ignorerar resten.
seqLength :: MolSeq -> Int
seqLength (MolSeq _ sekvens _) = length sekvens

seqType :: MolSeq -> SekvensTyp
seqType (MolSeq _ _ typ) = typ

-- Uppgift 4
{-
Implementera seqDistance :: MolSeq -> MolSeq -> Double som jämför två DNA-
sekvenser eller två proteinsekvenser och returnerar deras evolutionära avstånd.
Om man försöker jämföra DNA med protein ska det signaleras ett fel med hjälp av
funktionen error.
Du kan anta att de två sekvenserna har samma längd, och behöver inte hantera
fallet att de har olika längd.
 -}

{-
  En Funktion som tar in två stränar och jämför elementen i strängarna.
  Den räknar för varje gång sekvenserna skiljer sig åt.
Profile
-}
alpha :: String -> String -> Double
alpha sekvens1 sekvens2
  --om strängen inte har fler element så returnera 0
  | (sekvens1 == []) = 0.0
  -- om elementen inte är samma så räkna på det
  | (head sekvens1) /= (head sekvens2) = 1.0 + alpha (tail sekvens1) (tail sekvens2)
  -- om de är samma så tänk inte på det.
  | otherwise = alpha (tail sekvens1) (tail sekvens2)


-- seqDistance ska jämföra två DNA - sekvenser eller 2 proteinsekvenser
--och returnera deras evolutionära avstånd.
{-seqDistance :: MolSeq -> MolSeq -> Double
seqDistance mol1 mol2
  -- if the types do not match. Then it calls on error
  | (isDNA (seqSequence mol1)) /= isDNA (seqSequence mol2)  = error "Sequence types are not the same"
  --if the above isnt true then they must be the same, so we check if they are DNA or Protein
  --if DNA we proceed in doing the jukesCantor model calculation to calculate the evolutionary distance.
  | isDNA (seqSequence mol1) = jukesCantor ((alpha (seqSequence mol1) (seqSequence mol2))/ fromIntegral (seqLength mol1))
  --if Protein we calculate with the poissonModell calculation method
  | otherwise =  poissonModell ((alpha (seqSequence mol1) (seqSequence mol2))/ fromIntegral (seqLength mol1))-}


seqDistance :: MolSeq -> MolSeq -> Double
seqDistance mol1 mol2
  -- if the types do not match. Then it calls on error
  | seqType mol1 /= seqType mol2  = error "Sequence types are not the same"
  --if the above isnt true then they must be the same, so we check if they are DNA or Protein
  --if DNA we proceed in doing the jukesCantor model calculation to calculate the evolutionary distance.
  | seqType mol1 == DNA = jukesCantor ((alpha (seqSequence mol1) (seqSequence mol2))/ fromIntegral (seqLength mol1))
  --if Protein we calculate with the poissonModell calculation method
  | seqType mol1 == Protein =  poissonModell ((alpha (seqSequence mol1) (seqSequence mol2))/ fromIntegral (seqLength mol1))
--  this fulfills if the mol is a Protein
jukesCantor :: Double -> Double
jukesCantor a
  | a > 0.74 = 3.3
  | otherwise = -3/4 * log(1-4*a/3)

poissonModell :: Double -> Double
poissonModell a
  | a >= 0.94 = 3.7
  | otherwise = -(19/20) * log(1-(20*a/19))



----------------------------------------------------------------------
        --             Profiler och sekvenser               --
----------------------------------------------------------------------

-- Uppgift 1


{-Skapa en datatyp Profile för att lagra profiler. Datatypen ska lagra
  information om den profil som lagras med hjälp av matrisen M
  (enligt beskrivningen ovan), det är en profil för DNA eller protein,
  hur många sekvenser profilen är byggd ifrån, och ett namn på profilen.-}

-- skapar en typ, Profile, som lagrar namnet på Profilen samt MolSeq nummer
-- nummer av sekvenser samt en matris som tar in frekvensen av nukleiderna
data Profile =  Profile{
  theName :: String,
  typ     :: SekvensTyp,
  nrOfseq :: Int,
  matrixM :: [[(Char, Int)]]
} deriving Show



-- Uppgift 2

{-Skriv en funktion molseqs2profile :: String -> [MolSeq] -> Profile
  som returnerar en profil från de givna sekvenserna med den givna strängen
  som namn. Som hjälp för att skapa profil-matrisen har du koden i figur 2.
  Vid redovisning ska du kunna förklara exakt hur den fungerar,
  speciellt raderna (i)-(iv).
  Skriv gärna kommentarer direkt in i koden inför redovisningen,
  för så här kryptiskt ska det ju inte se ut!-}

-- HJÄLPSATS

nucleotides = "ACGT"
aminoacids = sort "ARNDCEQGHILKMFPSTWYVX"

makeProfileMatrix :: [MolSeq] -> [[(Char, Int)]]
makeProfileMatrix [] = error "Empty sequence list"
makeProfileMatrix sl = res -- Tar in en sequence List, returns the result of
  where                    -- the calculated work
    typ = seqType (head sl)
    defaults =
      if (typ == DNA) then
        zip nucleotides (replicate (length nucleotides) 0) {-Rad (i): skapar en
        lista med tuples för DNA med nucleotides [(A, 0),(C,0)].... -}
      else
        zip aminoacids (replicate (length aminoacids) 0)   {-Rad (ii): Det gör
        samma som rad i men för aminoacids -}
    strs = map seqSequence sl                              {-Rad (iii):
    tar seqSequence för varje molseq i listan sl, alltså tar varje sekvens ur
    de molseq vi har i listan sl och skapar en lista med tuples av sekvenserna -}
    tmp1 = map (map (\x -> ((head x), (length x))) . group . sort)
               (transpose strs)
{-Rad (iv): Funktionen tar första elementet ur den transponerade listan strs, vilket
är en lista med sekvenser. Tar listan, sorterar sedan grupperar upp sekvenserna
så att vi har alla "AGCT" i var sin grupperade lista som vi sedan tar tuple
("sekvensBokstav", längden på listan som innehåller alla dessa)-}
    equalFst a b = (fst a) == (fst b) -- predikat som jämför första på tuples
    res = map sort (map (\l -> unionBy equalFst l defaults) tmp1)
    -- vi tar unionBy alla tuples i tmp1 och jämför de med de vi skapar i default

-- Funktionen konverterar en lista av MolSeqs till en profile.
molseqs2profile :: String -> [MolSeq] -> Profile
molseqs2profile namn molseqLst = Profile namn typen antalSeq matrisen -- resultaten
    where
      typen = seqType (head molseqLst)        -- sequence typen
      antalSeq = length molseqLst             -- Längden på sequence listan
      matrisen = makeProfileMatrix molseqLst  -- Matrisen skapad av listan


profileName :: Profile -> String
profileName (Profile name _ _ _) = name

profilAnt :: Profile -> Int
profilAnt (Profile _ _ antal _ ) = antal

profilMat :: Profile -> [[(Char, Int)]]
profilMat (Profile _ _ _ matris) = matris

--tar frekvensen för den bokstaven i given position
profileFrequency :: Profile -> Int -> Char -> Double
profileFrequency profil position bokstav = tot
  where
    tot                    = fromIntegral rad/ fromIntegral column
    rad                    = miniMat ((profilMat profil) !! position) bokstav
    column                 = (profilAnt profil)

miniMat :: [(Char, Int)] -> Char -> Int
miniMat (x:xs) bokstav
  |fst x == bokstav = (snd x)
  |otherwise = miniMat xs bokstav

profileDistance :: Profile -> Profile -> Double
profileDistance pNr1 pNr2 = dist
  where
    --  tar skillnaden frekvensen för två profiler, på raden d och column m
    forEveryColumn m1 m2    = abs ((freq pNr1 m1) - (freq pNr2 m2))
    --  lägger ihop en lista som bearbetar varje column, sedan tar summan av
    --  listan
    forEveryRow d1 d2    = sum (zipWith forEveryColumn d1 d2 )
    -- tot sätter ihop en lista som bearbetar varje rad(bokstav), vi bearbetar
    -- varje column i matrisen för varje enskild bokstav med andra ord
    dist             = sum (zipWith forEveryRow (profilMat pNr1) (profilMat pNr2))
    -- freq tar frekvensen för den profil vi stoppar in
    freq p m        = fromIntegral (snd m) / fromIntegral (profilAnt p)

    ----------------------------------------------------------------------
            --    Generell Beräkning av AvståndsMatriser         --
    ----------------------------------------------------------------------
{-Implementera typklassen Evol och låt MolSeq och Profile bli instanser av Evol.
 Alla instanser av Evol ska implementera en funktion distance som mäter avstånd
 mellan två Evol, och en funktion name som ger namnet på en Evol.
 Finns det någon mer funktion som man bör implementera i Evol?-}


class Evol mol where
  namn :: mol  -> String
  distance :: mol -> mol -> Double
-- Bör man implementera mer? (y/n)? (maybe (just no?)
-- Gör en tabell med jämförelser mellan alla element i en lista så om det vore
-- profiler i en lista så jämför den profilerna i listan och sätter ihop de
-- i en lista med resultatet.
  distanceMatrix :: [mol] -> [(String, String, Double)]
  distanceMatrix [] = []
  distanceMatrix lstMol  =  doTo (head lstMol) lstMol ++ distanceMatrix (tail lstMol)
    where
      -- tupleCreator sätter ihop namnen samt distansen i en tuple
      tupleCreator p1 p2                = (namn p1, namn p2, distance p1 p2)
      -- vi anväder oss av map för att utföra "tupleCreator" för att uföra detta
      -- på det första sedan gör detta rekursivt för varje bokstav
      doTo first rest                 = map (\x -> tupleCreator first x) rest

-- definierar de tillåtna dataTyperna
instance Evol MolSeq where
  namn      = seqName
  distance  = seqDistance
instance Evol Profile where
  namn      = profileName
  distance  = profileDistance
