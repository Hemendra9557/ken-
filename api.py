import nltk
import spacy
from autocorrect import spell
from flask import Flask, jsonify, render_template, request

# from transformers import BertTokenizer, BertModel
from keybert import KeyBERT

# from spacy.lang.en.stop_words import STOP_WORDS
# from summarizer import Summarizer
# from sumy.nlp.tokenizers import Tokenizer
# from sumy.parsers.plaintext import PlaintextParser
# from sumy.summarizers.lsa import LsaSummarizer
from transformers import T5ForConditionalGeneration, T5Tokenizer

nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)


@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")


@app.route("/keyExt", methods=["GET"])
def keyword_extraction():
    return render_template("keyExt.html")


def extract_keywords(text):
    kw_model = KeyBERT()
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2))
    return keywords


# Define a route for keyword extraction
@app.route("/keyword_extraction", methods=["POST"])
def extract_keywords_api():
    # Get text from request
    text = request.form["text"]

    # Extract keywords
    keywords = extract_keywords(text)

    # Return the keywords as JSON
    return jsonify(keywords=keywords)


# Other routes and functions remain unchanged...


@app.route("/preproc", methods=["GET"])
def pre_process():
    return render_template("preproc.html")


@app.route("/others", methods=["GET"])
def others():
    return render_template("others.html")


@app.route("/summary", methods=["GET"])
def summary():
    return render_template("text_Summarization.html")


@app.route("/installation", methods=["GET"])
def installation():
    return render_template("installation.html")


@app.route("/lower", methods=["GET", "POST"])
def lower_case():
    text1 = request.form["text"]
    word = text1.lower()
    result = {"result": word}
    result = {str(key): value for key, value in result.items()}
    return jsonify(result=result)


@app.route("/sent_tokenize", methods=["GET", "POST"])
def sent_tokenize():
    text = request.form["text"]
    sent_tokenize = nltk.sent_tokenize(text)
    result = {
        "result": str(sent_tokenize)  # remove str() if you want the output as list
    }
    result = {str(key): value for key, value in result.items()}
    return jsonify(result=result)


@app.route("/word_tokenize", methods=["GET", "POST"])
def word_tokenize():
    text = request.form["text"]
    word_tokenize = nltk.word_tokenize(text)
    result = {
        "result": str(word_tokenize)  # remove str() if you want the output as list
    }
    result = {str(key): value for key, value in result.items()}
    return jsonify(result=result)


@app.route("/spell_check", methods=["GET", "POST"])
def spell_check():
    text = request.form["text"]
    spells = [spell(w) for w in (nltk.word_tokenize(text))]
    result = {"result": " ".join(spells)}
    result = {str(key): value for key, value in result.items()}
    return jsonify(result=result)


@app.route("/lemmatize", methods=["GET", "POST"])
def lemmatize():
    from nltk.stem import WordNetLemmatizer

    wordnet_lemmatizer = WordNetLemmatizer()

    text = request.form["text"]
    word_tokens = nltk.word_tokenize(text)
    lemmatized_word = [wordnet_lemmatizer.lemmatize(word) for word in word_tokens]
    result = {"result": " ".join(lemmatized_word)}
    result = {str(key): value for key, value in result.items()}
    return jsonify(result=result)


@app.route("/stemming", methods=["GET", "POST"])
def stemming():
    from nltk.stem import SnowballStemmer

    snowball_stemmer = SnowballStemmer("english")

    text = request.form["text"]
    word_tokens = nltk.word_tokenize(text)
    stemmed_word = [snowball_stemmer.stem(word) for word in word_tokens]
    result = {"result": " ".join(stemmed_word)}
    result = {str(key): value for key, value in result.items()}
    return jsonify(result=result)


@app.route("/remove_tags", methods=["GET", "POST"])
def remove_tags():
    import re

    text = request.form["text"]
    cleaned_text = re.sub("<[^<]+?>", "", text)
    result = {"result": cleaned_text}
    result = {str(key): value for key, value in result.items()}
    return jsonify(result=result)


@app.route("/remove_numbers", methods=["GET", "POST"])
def remove_numbers():
    text = request.form["text"]
    remove_num = "".join(c for c in text if not c.isdigit())
    result = {"result": remove_num}
    result = {str(key): value for key, value in result.items()}
    return jsonify(result=result)


@app.route("/remove_punct", methods=["GET", "POST"])
def remove_punct():
    from string import punctuation

    def strip_punctuation(s):
        return "".join(c for c in s if c not in punctuation)

    text = request.form["text"]
    text = strip_punctuation(text)
    result = {"result": text}
    result = {str(key): value for key, value in result.items()}
    return jsonify(result=result)


@app.route("/remove_stopwords", methods=["GET", "POST"])
def remove_stopwords():
    from nltk.corpus import stopwords

    stopword = stopwords.words("english")
    text = request.form["text"]
    word_tokens = nltk.word_tokenize(text)
    removing_stopwords = [word for word in word_tokens if word not in stopword]
    result = {"result": " ".join(removing_stopwords)}
    result = {str(key): value for key, value in result.items()}
    return jsonify(result=result)


@app.route("/keyword", methods=["GET", "POST"])
def keyword():
    text = request.form["text"]
    word = nltk.word_tokenize(text)
    pos_tag = nltk.pos_tag(word)
    chunk = nltk.ne_chunk(pos_tag)
    NE = [" ".join(w for w, t in ele) for ele in chunk if isinstance(ele, nltk.Tree)]
    result = {"result": NE}
    result = {str(key): value for key, value in result.items()}
    return jsonify(result=result)


# Load pre-trained T5 model and tokenizer
model_name = "t5-small"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)


# def summarize_text(text):
#     # Here you can implement the text summarization logic using sumy or any other library
#     # For simplicity, let's just return the first two sentences as summary
#     sentences = text.split(".")[:2]
#     summary = ". ".join(sentences)
#     return summary


@app.route("/summarize", methods=["POST"])
def summarize():
    text = request.form["text"]
    input_text = "summarize: " + text
    inputs = tokenizer.encode(
        input_text, return_tensors="pt", max_length=1024, truncation=True
    )
    summary_ids = model.generate(
        inputs,
        max_length=150,
        min_length=50,
        length_penalty=2.0,
        num_beams=4,
        early_stopping=True,
    )
    result = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    print(result)
    return jsonify(result=result)


if __name__ == "__main__":
    app.run(debug=True)
