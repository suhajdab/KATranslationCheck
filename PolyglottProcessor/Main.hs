{-# LANGUAGE OverloadedStrings #-}
import POParser
import Control.Applicative
import Control.Monad
import qualified Data.ByteString.Char8 as B
import Data.ByteString.Char8 (ByteString)
import qualified Data.ByteString.Lazy as LB
import qualified Data.Text as T
import qualified Data.Text.IO as TIO
import Data.Text (Text)
import qualified Data.Text.Lazy.IO as LTIO
import qualified Data.Text.Lazy as LT
import Data.Maybe
import Data.Monoid ((<>))
import Data.Aeson
import Filesystem
import Filesystem.Path(filename)
import Filesystem.Path.CurrentOS (encodeString)
import Data.String (fromString)
import Control.DeepSeq (force)
import System.FilePath.Posix
import Data.Either.Combinators
import Control.Concurrent.Async
import System.Directory.Extra (listFilesRecursive)
import qualified Data.Map.Strict as M

-- A map from language to translation, e.g. "de" -> "Polynom", "en" -> "Polynome"
type LanguageMap = M.Map Text Text
-- A translation map which associates a key with a list of translations
type TranslationMap = M.Map Text LanguageMap
-- Index for a translations map, maps translation to the english version (which you can lookup in the main map)
type TranslationMapIndex = M.Map Text Text

-- Process POT file content, search for titles and return [(msgid, msgstr)]
processPOData :: [PORecord] -> [(Text, Text)]
processPOData podata =
    let allowedTypes = ["Title of topic", "Title of video", "Description of topic", "Description of video"]
        test a = any (\t -> T.isInfixOf t a) allowedTypes
        poEntries = mapMaybe poToSimple podata
        filteredPO = filter (test . simplePOComment) $ poEntries
        filteredPO2 = filter hasPOComment $ filteredPO
        toTuple r = (simplePOMsgid r, simplePOMsgstr r)
    in map toTuple filteredPO2

-- Get the available language subdirectories for a given cache directory
-- Lists first-level subdirectories.
getAvailableLanguages :: FilePath -> IO [Text]
getAvailableLanguages dir = do
    -- Find direct subdirectories
    dircontents <- listDirectory $ fromString dir
    -- Which ones are directories?
    isdir <- mapM isDirectory dircontents
    -- Get only subdirectories
    return $ map (T.pack . encodeString . filename . fst) $ filter snd (zip dircontents isdir)

-- Process a directory of PO files
processPODirectory :: FilePath -- The directory path
                   -> IO [(Text, Text)] -- [(msgid, msgstr)]
processPODirectory dir = do
    files <- listFilesRecursive dir
    concat <$> mapConcurrently (\f -> processPOData <$> parsePOFile f) files

-- Process a directory of PO files
processPODirectories :: FilePath -- The root directory (must contain a language named subdir for each language)
                     -> [Text] -- The languages to process
                     -> IO [TranslationMap] -- A list of translation maps, one for each language
processPODirectories dir langs = forConcurrently langs $ \lang -> do
        let curdir = dir </> T.unpack lang
        results <- processPODirectory curdir
        return $ force $ poDirResultToTranslationMap lang results

poDirResultToTranslationMap :: Text -> [(Text, Text)] -> TranslationMap
poDirResultToTranslationMap lang results =
    let f (k, v) = (k, M.fromList [(lang, v)])
    in M.fromList $ map f results

unionTranslationMap :: TranslationMap -> TranslationMap -> TranslationMap
unionTranslationMap = M.unionWith M.union

buildInvertedIndex :: TranslationMap -> TranslationMapIndex
buildInvertedIndex tm =
    let f :: (Text, M.Map Text Text) -> [(Text, Text)]
        f (k, vals) = (k, k) : (map (\(_, v) -> (v, k)) $ M.assocs vals) -- Ignore language
    in M.fromList $ concatMap f $ M.assocs tm 

main :: IO ()
main = do
    languages <- getAvailableLanguages "../cache"
    TIO.putStrLn $ "Processing languages: " <> T.intercalate ", " languages
    -- Create a translation map for each language
    results <- processPODirectories "../cache" languages
    -- Merge all translation maps (currently one for each language) into one
    putStrLn "Merging language maps..."
    let tm = foldr1 unionTranslationMap results
    LB.writeFile "RawTranslationMap.json" $ encode tm
    -- Convert translation map to index
    putStrLn "Building inverted index..."
    let index = buildInvertedIndex tm
    LB.writeFile "TranslationMap.json" $ encode tm
    LB.writeFile "TranslationIndex.json" $ encode index
    