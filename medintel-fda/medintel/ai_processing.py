import time
import chromadb
from chromadb.utils import embedding_functions
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from .utils import html_to_text

def analyze_medical_text(disease, results, st):
    chroma_client = chromadb.Client()
    collection = chroma_client.get_or_create_collection(
        name="medlineplus",
        embedding_function=embedding_functions.DefaultEmbeddingFunction()
    )

    existing_ids = collection.get()["ids"]
    if existing_ids:
        collection.delete(ids=existing_ids)

    for i, item in enumerate(results):
        collection.add(
            documents=[f"{item['title']} - {item['snippet']} ({item['url']})"],
            metadatas=[{
                "url": item["url"],
                "drugs": ", ".join(item["drugs"]) if item["drugs"] else ""
            }],
            ids=[f"doc_{i}"]
        )

    search_results = collection.query(query_texts=[disease], n_results=3)
    documents = search_results["documents"][0]
    context_text = "\n".join(documents)
    medical_text = html_to_text(context_text)

    llm = Ollama(model="mistral")

    single_word_prompt = PromptTemplate(
        input_variables=["context"],
        template="""From the text below, extract ONLY the name of the main medicine or drug mentioned.
Return just the medicine name, without extra words or diseases.

Text:
{context}"""
    )
    single_word_chain = LLMChain(llm=llm, prompt=single_word_prompt)

    summarizer_prompt = PromptTemplate(
        input_variables=["context"],
        template="Summarize the following medical text:\n\n{context}"
    )
    summarizer_chain = LLMChain(llm=llm, prompt=summarizer_prompt)

    chunks = [medical_text[i:i+1500] for i in range(0, len(medical_text), 1500)]
    all_summaries, all_one_words = [], []

    progress_text = "⏳ Analyzing text with AI..."
    progress_bar = st.progress(0, text=progress_text)

    for i, chunk in enumerate(chunks):
        summary = summarizer_chain.run(context=chunk)
        one_word = single_word_chain.run(context=chunk)
        all_summaries.append(summary.strip())
        all_one_words.append(one_word.strip())
        time.sleep(0.1)
        progress_bar.progress(int((i+1)/len(chunks)*100), text=progress_text)

    final_summary = "\n".join(all_summaries)
    final_one_word = ", ".join(set(all_one_words))

    drug_list = [d.strip() for d in final_one_word.split(",")]
    cleaned_list = [
        d for d in drug_list
        if d and d.lower() not in ["none", disease.lower()]
    ]
    return final_summary, cleaned_list
