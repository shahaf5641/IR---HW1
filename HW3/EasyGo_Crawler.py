import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from collections import defaultdict, Counter
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import math

# Define the base URL for the CDC search
BASE_URL = "https://search.cdc.gov/search/?query="

# Queries to search for
queries = [
    "How is jet lag treated?",
    "What are the symptoms of jaundice?",
    "What causes joint pain?"
]

# Fields to store results
data = {
    "Query": [],
    "Results": []
}

# Function to fetch search result URLs for a query with pagination support
def fetch_search_results(query, driver, max_results=20):
    urls_and_titles = []

    # Initial search
    search_url = f"{BASE_URL}{query.replace(' ', '+')}"
    driver.get(search_url)

    while len(urls_and_titles) < max_results:
        # Wait until the results div is present
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "results"))
            )
        except Exception as e:
            print(f"Error waiting for results to load: {e}")
            break

        soup = BeautifulSoup(driver.page_source, "html.parser")
        results_div = soup.find("div", class_="results webResults")
        if not results_div:
            print(f"No results found for query '{query}'.")
            break

        # Extract results from the current page
        result_items = results_div.find_all("div", class_="result")
        for item in result_items:
            link_tag = item.find("a", href=True)
            if link_tag:
                url = link_tag["href"]
                if not url.startswith("http"):
                    url = f"https://www.cdc.gov{url}"
                urls_and_titles.append((link_tag.text.strip(), url))
                print(f"Added ({len(urls_and_titles)}/{max_results}) URL: {url}")
                if len(urls_and_titles) >= max_results:
                    break

        print(f"Page returned {len(result_items)} results.")

        # Check for the next button
        next_button = driver.find_elements(By.LINK_TEXT, "Next")
        if next_button:
            next_button[0].click()
            time.sleep(2)  # Allow time for the next page to load
        else:
            print("No next button found. Ending pagination.")
            break

    return urls_and_titles[:max_results]

# Function to process search results for a query
def process_query_results(query, driver, max_results=20):
    search_results = fetch_search_results(query, driver, max_results=max_results)

    titles = [result[0] for result in search_results]
    urls = [result[1] for result in search_results]

    return titles, urls

# Function to store results in the data dictionary
def store_query_results(query, titles, urls):
    results = [{"Title": titles[idx], "URL": urls[idx]} for idx in range(len(titles))]
    data["Query"].append(query)
    data["Results"].append(results)

# Main function to process all queries
def process_queries():
    driver = webdriver.Chrome()

    for i, query in enumerate(queries):
        print(f"\nProcessing Query Number {i + 1}: '{query}'")

        titles, urls = process_query_results(query, driver, max_results=20)

        # Store the top results
        store_query_results(query, titles, urls)

    driver.quit()

# Run the process
process_queries()

# Save the results to an Excel file
output_file = "CDC_Data_Queries_Top20.xlsx"
all_data = []
for idx, query in enumerate(data["Query"]):
    for result_idx, result in enumerate(data["Results"][idx]):
        if result_idx == 0:
            all_data.append({"Query": query, "Title": result["Title"], "URL": result["URL"]})
        else:
            all_data.append({"Query": "--------------------------" if result_idx == len(data["Results"][idx]) else "", "Title": result["Title"], "URL": result["URL"]})

df = pd.DataFrame(all_data)

# Preprocess words: remove symbols, retain only letters, and exclude stop words
stop_words = set(stopwords.words("english"))
stemmer = PorterStemmer()

# TF-IDF calculation for the first query
query = queries[0]
query_terms = [re.sub(r"[^a-zA-Z]", "", word).lower() for word in query.split()]
query_terms = [stemmer.stem(word) for word in query_terms if word not in stop_words and len(word) > 1]

# Initialize TF and DF
tf = defaultdict(lambda: defaultdict(float))
df_counts = defaultdict(int)

# Filter results for the first query only
titles = data["Results"][0]

# Step 1: Calculate Term Frequencies (TF) and Document Frequencies (DF)
for idx, result in enumerate(titles):
    words = [re.sub(r"[^a-zA-Z]", "", word).lower() for word in result["Title"].split()]
    filtered_words = [stemmer.stem(word) for word in words if word not in stop_words and len(word) > 1]

    term_counts = Counter(filtered_words)
    for term in query_terms:
        tf[idx][term] = term_counts[term] / len(filtered_words) if len(filtered_words) > 0 else 0
        if term_counts[term] > 0:
            df_counts[term] += 1

# Step 2: Calculate Inverse Document Frequency (IDF)
total_docs = len(titles)
idf = {term: math.log(total_docs / (df_counts[term] if df_counts[term] > 0 else 1)) for term in query_terms}

# Step 3: Calculate TF-IDF for each term in each document
tf_idf = defaultdict(float)
for idx in tf.keys():
    for term in query_terms:
        tf_idf[idx] += tf[idx][term] * idf[term]

# Step 4: Rank documents by TF-IDF score
ranked_docs = sorted(tf_idf.items(), key=lambda x: x[1], reverse=True)
ranked_docs_with_scores = [(titles[idx]["Title"], titles[idx]["URL"], score) for idx, score in ranked_docs]

# Step 5: Create an inverted index for the 15 most frequent words
word_counter = Counter()
for idx, row in df.iterrows():
    if row["Title"] != "--------------------------":
        words = [re.sub(r"[^a-zA-Z]", "", word).lower() for word in row["Title"].split()]
        filtered_words = [stemmer.stem(word) for word in words if word not in stop_words and len(word) > 1]
        word_counter.update(filtered_words)

# Select the 15 most common words
most_common_words = word_counter.most_common(15)
inverted_index = {word: [] for word, _ in most_common_words}
for idx, row in df.iterrows():
    if row["Title"] != "--------------------------":
        words = [re.sub(r"[^a-zA-Z]", "", word).lower() for word in row["Title"].split()]
        filtered_words = [stemmer.stem(word) for word in words if word not in stop_words and len(word) > 1]
        for word in filtered_words:
            if word in inverted_index:
                inverted_index[word].append(idx)

# Save the ranked documents and inverted index to Excel
with pd.ExcelWriter(output_file, mode="w") as writer:
    df.to_excel(writer, index=False, sheet_name="Results")
    ranked_df = pd.DataFrame(ranked_docs_with_scores, columns=["Title", "URL", "TF-IDF Score"])
    ranked_df.to_excel(writer, index=False, sheet_name="Ranked Results")
    pd.DataFrame({"Word": [word for word, _ in most_common_words],
                  "Indexes": [str(inverted_index[word]) for word, _ in most_common_words]}).to_excel(writer, index=False, sheet_name="Inverted Index")

# Function to collect feedback from users
def collect_feedback(results):
    user_feedback = {"User1": [], "User2": []}

    for idx, result in enumerate(results):
        print(f"\nResult {idx + 1}:")
        print(f"Title: {result['Title']}")
        print(f"URL: {result['URL']}")

        # Collect feedback from User 1
        feedback_user1 = input("User 1 - Is this result relevant? (Yes/No): ").strip().lower()
        user_feedback["User1"].append(feedback_user1 == "yes")

        # Collect feedback from User 2
        feedback_user2 = input("User 2 - Is this result relevant? (Yes/No): ").strip().lower()
        user_feedback["User2"].append(feedback_user2 == "yes")

    return user_feedback

# Function to calculate precision and recall
def calculate_precision_recall(feedback, total_relevant_in_dataset=20):
    precision = sum(feedback) / len(feedback)  # Relevant results / Total retrieved
    recall = sum(feedback) / total_relevant_in_dataset  # Relevant results / Total relevant in dataset
    return precision, recall

# Main function to process queries with user feedback
def process_queries_with_feedback():
    driver = webdriver.Chrome()

    # Process the first query only
    print(f"Processing Query: '{queries[0]}'")
    titles, urls = process_query_results(queries[0], driver, max_results=10)

    # Store the top 10 results
    store_query_results(queries[0], titles, urls)

    # Collect user feedback
    feedback = collect_feedback(data["Results"][0][:10])

    # Calculate precision and recall for each user
    precision_recall_data = []
    for user, user_feedback in feedback.items():
        precision, recall = calculate_precision_recall(user_feedback, total_relevant_in_dataset=15)
        print(f"\n{user} - Precision: {precision:.2f}, Recall: {recall:.2f}")
        precision_recall_data.append({"User": user, "Precision": precision, "Recall": recall})

    driver.quit()

    # Save results, user feedback, and precision/recall to Excel
    with pd.ExcelWriter(output_file, mode="w") as writer:
        # Save results
        df.to_excel(writer, index=False, sheet_name="Results")

        # Save ranked results
        ranked_df = pd.DataFrame(ranked_docs_with_scores, columns=["Title", "URL", "TF-IDF Score"])
        ranked_df.to_excel(writer, index=False, sheet_name="Ranked Results")

        # Save inverted index
        pd.DataFrame({"Word": [word for word, _ in most_common_words],
                      "Indexes": [str(inverted_index[word]) for word, _ in most_common_words]}).to_excel(writer, index=False, sheet_name="Inverted Index")

        # Save feedback and metrics
        feedback_df = pd.DataFrame.from_dict(feedback)
        feedback_df.to_excel(writer, index=False, sheet_name="User Feedback")

        # Save precision and recall
        precision_recall_df = pd.DataFrame(precision_recall_data)
        precision_recall_df.to_excel(writer, index=False, sheet_name="Precision Recall")

    print(f"User feedback, precision, and recall saved to '{output_file}'")

# Run the process with feedback
process_queries_with_feedback()
