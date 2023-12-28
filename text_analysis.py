
# Loading Module, Libraries, Functions and Files
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from bs4 import BeautifulSoup
import re
import requests

# Load URLs and headers from "Input.xlsx"
df = pd.read_excel("/home/raj/assignment/Input.xlsx")
url_ids = df["URL_ID"].tolist()  # Note the lowercase "url_id"
urls = df["URL"].tolist()

# Load stop words from multiple files
stop_words = set()  # Create an empty set first
for file in ["/home/raj/assignment/StopWords/StopWords_Auditor.txt",
             "/home/raj/assignment/StopWords/StopWords_Currencies.txt",
             '/home/raj/assignment/StopWords/StopWords_DatesandNumbers.txt',
             '/home/raj/assignment/StopWords/StopWords_Generic.txt',
             '/home/raj/assignment/StopWords/StopWords_GenericLong.txt',
             '/home/raj/assignment/StopWords/StopWords_Geographic.txt',
             '/home/raj/assignment/StopWords/StopWords_Names.txt']:
    with open(file, encoding="utf-8") as f:  # Specify encoding if needed
        stop_words.update(word.strip() for word in f.readlines())

# Load positive/negative words from MasterDictionary
with open("/home/raj/assignment/MasterDictionary/positive-words.txt") as f:
    positive_words = [word.strip() for word in f.readlines()]
with open("/home/raj/assignment/MasterDictionary/negative-words.txt") as f:
    negative_words = [word.strip() for word in f.readlines()]


# Defining extracting text function
def extract_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error if the request fails (e.g., 404)

        soup = BeautifulSoup(response.content, "html.parser")
        article = soup.find("article")

        if article:
            return article.get_text()  # Extract text if article is found
        else:
            print(f"Article not found at {url}")  # Notify about missing article
            return ""  # Return an empty string

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return ""


# Defining Counting number of syllables
def count_syllables(word):
  """
  Counts the number of syllables in a word, handling exceptions like "es" and "ed".

  Args:
    word: The word to count syllables for.

  Returns:
    The number of syllables in the word.
  """
  # Counting vowels, excluding silent "e" at the end
  vowel_count = sum(1 for char in word if char in "aeiouy" and char != word[-1])

  # Handle exceptions for words ending with "es" or "ed"
  if word.endswith("es"):
    # If the word has more than one syllable and ends with "es", we remove the "es"
    # unless it's a one-syllable word like "yes" or "make".
    if vowel_count > 1:
      vowel_count -= 1
  elif word.endswith("ed"):
    # If the word has more than one syllable and ends with "ed",we remove the "ed"
    # unless it's a one-syllable word like "bed" or "red".
    if vowel_count > 1 and not word.endswith("ied"):
      vowel_count -= 1

  return vowel_count


# Defining the methodologies for Text analysis
def analyze_text(text):
    # Tokenize the text into words
    words = word_tokenize(text.lower())

    # Remove stop words
    clean_words = [word for word in words if word not in stop_words]

    # Calculate sentiment scores
    positive_score = 0
    negative_score = 0
    for word in clean_words:
        if word in positive_words:
            positive_score += 1
        elif word in negative_words:
            negative_score -= 1  # Use -1 for negative words

    # Calculate polarity score
    polarity_score = (positive_score - negative_score) / (
        positive_score + negative_score + 0.000001
    )  # Avoid division by zero

    # Calculate subjectivity score
    subjectivity_score = (positive_score + negative_score) / (len(clean_words) + 0.000001)

    # Calculate readability scores
    sentences = re.split(r"[.!?]", text)  # Split text into sentences
    total_sentences = len(sentences)
    total_words = len(words)

    # Calculate complex word count (adjust based on your definition of "complex words")
    complex_word_count = sum(len(word) > 2 for word in words)  # Temporary definition

    # Calculate average sentence length
    total_sentence_length = sum(len(sentence) for sentence in sentences)
    

    avg_sentence_length = total_sentence_length / total_sentences



    # Calculate average number of words per sentence
    avg_word_per_sentence = total_words / total_sentences



    # Calculate percentage of complex words
    percentage_complex_words = (complex_word_count / total_words) * 100

    # Calculate Fog index
    fog_index = 0.4 * (avg_sentence_length + percentage_complex_words)

    # Calculate word count (excluding stop words and punctuation)
    word_count = len(clean_words)

    # Calculate syllable count per word 
    syllable_per_word = [count_syllables(word) for word in clean_words]

    # Calculate personal pronouns
    personal_pronouns = len(
        re.findall(r"\b(I|we|my|ours|us)\b", text, flags=re.IGNORECASE)
    )

    # Calculate average word length
    avg_word_length = sum(len(word) for word in clean_words) / word_count

    # Return scores and variables in a dictionary
    return {
        "POSITIVE_SCORE": positive_score,
        "NEGATIVE_SCORE": negative_score,
        "POLARITY_SCORE": polarity_score,
        "SUBJECTIVITY_SCORE": subjectivity_score,
        "AVG_SENTENCE_LENGTH": avg_sentence_length,
        "AVG_NUMBER_OF_WORDS_PER_SENTENCE": avg_word_per_sentence,

        
"PERCENTAGE_COMPLEX_WORDS": percentage_complex_words,
        "FOG_INDEX": fog_index,
        "WORD_COUNT": word_count,
        "SYLLABLE_PER_WORD": syllable_per_word,
        "PERSONAL_PRONOUNS": personal_pronouns,
        "AVG_WORD_LENGTH": avg_word_length,
        "COMPLEX_WORDS_COUNT" : complex_word_count
    }


# Calculating scores and storing them in a list
results = []
for url, url_id in zip(urls, url_ids):
    text = extract_text(url)
    if text:
        # Perform sentiment analysis, readability analysis, and other calculations
        scores = analyze_text(text)
        scores["URL_ID"] = url_id  # Add URL_ID to results
        scores["URL"] = url
        results.append(scores)

# Exporting the list data to dataframe and then Exporting it to an excel file
output_df = pd.DataFrame(results, columns=[
    "URL_ID", "URL", "POSITIVE_SCORE",
    "NEGATIVE_SCORE",
    "POLARITY_SCORE",
    "SUBJECTIVITY_SCORE",
    "AVG_SENTENCE_LENGTH",
    "PERCENTAGE_COMPLEX_WORDS",
    "FOG_INDEX",
    "AVG_NUMBER_OF_WORDS_PER_SENTENCE",
    "COMPLEX_WORDS_COUNT",  
    "WORD_COUNT",
    "SYLLABLE_PER_WORD",
    "PERSONAL_PRONOUNS",
    "AVG_WORD_LENGTH"
])
output_df.to_excel("/home/raj/assignment/Output Data Structure.xlsx", index=False)
print("done")



