import nltk
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import subprocess
import json

# Node.js script name
node_script = 'read_dataset_captions.js'

# Call Node.js script and get texts
result = subprocess.run(['node', node_script], capture_output=True, text=True)
texts = json.loads(result.stdout)

# Tokenize and create distance map
token_lists = tokenize_texts(texts)
distance_map = create_distance_map(token_lists)
nltk.download('punkt')

def tokenize_texts(texts):
    return [nltk.word_tokenize(text.lower()) for text in texts]

def create_distance_map(token_lists):
    vectorizer = CountVectorizer(tokenizer=lambda doc: doc, lowercase=False)
    vecs = vectorizer.fit_transform(token_lists)
    return cosine_similarity(vecs)

