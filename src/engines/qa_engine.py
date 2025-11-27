from storage import load_qa_data
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class QaEngine:
    """
    A simple TF-IDF-based question-answer search engine.

    Responsibilities:
        - Load the QA dataset
        - Build a TF-IDF matrix for the questions
        - Compute similarity between user input and known questions
        - Return:
            - all games
            - best match similarity score
            - full question list
            - full document list
            - index of best match
        
        Note: 
        The IntentHandler decides how to use these results. 
        QA engine only provides raw retrieval functionality.
    """
    def __init__(self):
        # Load data
        self.questions, self.answers, self.documents = load_qa_data()

        # Vectoriser: unigrams + bigrams, remove English stopwords
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1,2))

        # TF-IDF matrix of all questions in the dataset
        self.question_matrix = self.vectorizer.fit_transform(self.questions)

    def search(self, user_input: str):
        """
        Compute similarity between the user's input and all stored questions.
        """

        # Convert input to a TF-IDF vector
        query_vector = self.vectorizer.transform([user_input])

        # Compute cosine similarity against all questions
        similarity_scores = cosine_similarity(query_vector, self.question_matrix)[0]

        # Find the highest-scoring question index
        best_idx = int(np.argmax(similarity_scores))
        best_score = float(similarity_scores[best_idx])

        # Return raw structures; IntentHandler decides how to package them
        return self.answers, best_score, self.documents, best_idx