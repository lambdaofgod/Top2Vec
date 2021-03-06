from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from top2vec import Top2Vec

app = FastAPI(title="Top2Vec API",
              description="Speak REST to a Top2Vec trained model.",
              version="1.0.0", )

top2vec = Top2Vec.load("top2vec_model/top2vec_20newsgroups")


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=404,
        content={"message": str(exc)},
    )


class NumTopics(BaseModel):
    num_topics: int


class Topic(BaseModel):
    topic_num: int
    topic_words: List[str] = []
    word_scores: List[float] = []


class TopicResult(Topic):
    topic_score: float


class Document(BaseModel):
    content: str
    score: float
    doc_num: int


class KeywordSearch(BaseModel):
    keywords: List[str]
    keywords_neg: List[str]


class KeywordSearchDocument(KeywordSearch):
    num_docs: int


class KeywordSearchTopic(KeywordSearch):
    num_topics: int


class KeywordSearchWord(KeywordSearch):
    num_words: int


class WordResult(BaseModel):
    word: str
    score: float


@app.get("/topics/number", response_model=NumTopics, description="Returns number of topics in the model.",
         tags=["Topics"])
async def get_number_of_topics():
    return {"num_topics": top2vec.get_num_topics()}


@app.get("/topics/get-topics", response_model=List[Topic], description="Get number of topics.", tags=["Topics"])
async def get_topics(num_topics: int):
    topic_words, word_scores, topic_nums = top2vec.get_topics(num_topics)

    topics = []
    for words, scores, num in zip(topic_words, word_scores, topic_nums):
        topics.append(Topic(topic_num=num, topic_words=words, word_scores=scores))

    return topics


@app.post("/topics/search", response_model=List[TopicResult], description="Semantic search of topics using keywords.",
          tags=["Topics"])
async def search_topics_by_keywords(keyword_search: KeywordSearchTopic):
    topic_words, word_scores, topic_scores, topic_nums = top2vec.search_topics(keyword_search.keywords,
                                                                               keyword_search.num_topics,
                                                                               keyword_search.keywords_neg)

    topic_results = []
    for words, word_scores, topic_score, topic_num in zip(topic_words, word_scores, topic_scores, topic_nums):
        topic_results.append(TopicResult(topic_num=topic_num, topic_words=words,
                                         word_scores=word_scores, topic_score=topic_score))

    return topic_results


@app.get("/documents/search-by-topic", response_model=List[Document],
         description="Semantic search of documents using keywords.", tags=["Documents"])
async def search_documents_by_topic(topic_num: int, num_docs: int):
    docs, doc_scores, doc_nums = top2vec.search_documents_by_topic(topic_num, num_docs)

    documents = []
    for doc, score, num in zip(docs, doc_scores, doc_nums):
        documents.append(Document(content=doc, score=score, doc_num=num))

    return documents


@app.post("/documents/search-by-keyword", response_model=List[Document], description="Search documents by keywords.",
          tags=["Documents"])
async def search_documents_by_keywords(keyword_search: KeywordSearchDocument):
    docs, doc_scores, doc_nums = top2vec.search_documents_by_keyword(keyword_search.keywords, keyword_search.num_docs,
                                                                     keyword_search.keywords_neg)

    documents = []
    for doc, score, num in zip(docs, doc_scores, doc_nums):
        documents.append(Document(content=doc, score=score, doc_num=num))

    return documents


@app.post("/documents/search-by-document", response_model=List[Document], description="Find similar documents.",
          tags=["Documents"])
async def search_documents_by_document(doc_num: int, num_docs: int):
    docs, doc_scores, doc_nums = top2vec.search_documents_by_document(doc_num, num_docs)

    documents = []
    for doc, score, num in zip(docs, doc_scores, doc_nums):
        documents.append(Document(content=doc, score=score, doc_num=num))

    return documents


@app.post("/words/find-similar", response_model=List[WordResult], description="Search documents by keywords.",
          tags=["Words"])
async def find_similar_words(keyword_search: KeywordSearchWord):
    words, word_scores = top2vec.similar_words(keyword_search.keywords, keyword_search.num_words,
                                               keyword_search.keywords_neg)

    word_results = []
    for word, score in zip(words, word_scores):
        word_results.append(WordResult(word=word, score=score))

    return word_results
