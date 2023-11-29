import os
import requests
import json

from utils.helper import get_keywords, test_data
from dotenv import find_dotenv, load_dotenv
from linkedin_api import Linkedin
from typing import Any
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import UnstructuredURLLoader
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter


# ---------loading credentials--------- #
load_dotenv(find_dotenv())
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")


# ---------linkedin client--------- #
linkedin_client: Any = Linkedin(LINKEDIN_USERNAME, LINKEDIN_PASSWORD)


# ------------------getting user information via the LinkedIn API------------------ #
def get_linkedin_profile(client: Any, username: str) -> dict[str, str]:
    """
    This function is used to get the profile of the specified user
    :param client: LinkedIn client
    :param username: LinkedIn username
    :return: user profile dict
    """
    profile: dict = client.get_profile(username)
    print(profile)

    return profile


# ------------------find the most relevant keywords & data to improve the search------------------ #
def get_job_related_keywords(linkedin_profile_dict: dict, keyword: str) -> str:
    """
    This function is used to retrieve all the job related keywords from a user profile
    :param linkedin_profile_dict: returned LinkedIn profile data
    :param keyword: identified LinkedIn keyword
    :return: list of job related keywords
    """
    linkedin_profile_keywords: tuple = ("most_recent_degree", "current_location", "most_recent_job_title",
                                        "years_in_most_recent_job", "most_recent_industry")

    if keyword in linkedin_profile_keywords:
        return get_keywords(keyword, linkedin_profile_dict)


def job_search_sentence_generator(linkedin_profile_dict: dict) -> str:
    """
    This function is used to generate a sentence that will be used as a job search query
    :param linkedin_profile_dict: returned LinkedIn profile data
    :return: job search sentence
    """
    job_search_sentence: str = (f"{get_job_related_keywords(linkedin_profile_dict, 'most_recent_job_title')} "
                                f"jobs in {get_job_related_keywords(linkedin_profile_dict, 'current_location')}")

    return job_search_sentence


# ------------------using serpapi to search for jobs using keywords------------------ #
def serp_search_for_jobs(query: str) -> dict:
    """
    This function is used to search for jobs using the serpapi
    :param query: query used to search
    :return: dict of search results
    """
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": query
    })
    headers = {
        "X-API-KEY": SERPAPI_API_KEY,
        "Content-Type": "application/json"
    }
    response: Any = requests.request("POST", url, headers=headers, data=payload)
    response_data: dict = response.json()

    return response_data


# ------------------prompt template and the gpt-3.5-turbo model------------------ #
def find_the_best_job_search_url(response_data: dict, query: str) -> list:
    """
    This function is used to find the best job url using a prompt template and the gpt-3.5-turbo model
    :param response_data: dictionary of job search results
    :param query: query used to search for jobs
    :return: list of the top job url
    """
    response_str = json.dumps(response_data)
    prompt_template: str = """
    You're a world class job recruiter, and are very good at finding the most relevant jobs for certain topics;
    {response_str}
    Above is a list of search results for the query {query}.
    Please choose the best jobs from the list, return ONLY an array of the top two urls, do not include anything else;
    """
    llm: Any = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1)

    prompt: PromptTemplate = PromptTemplate(template=prompt_template, input_variables=["response_str", "query"])

    job_finder: Any = LLMChain(llm=llm, prompt=prompt, verbose=True)

    generated_urls = job_finder.predict(response_str=response_str, query=query)

    url_list = json.loads(generated_urls)
    print(url_list)

    return url_list


# ------------------data extraction from the job urls------------------ #
def get_job_content_from_urls(urls: list) -> list:
    """
    This is a function is used to fetch the data from the passed in url list
    :param urls: job urls
    :return: list of extracted data
    """
    loader = UnstructuredURLLoader(urls=urls)
    data = loader.load()

    return data


# ------------------prompt template and the gpt-3.5-turbo model------------------ #
def summarise_the_job_content(data: list, query: str) -> list[str]:
    """
    This function is used to summarise the fetched job data using the gpt-3.5-turbo and prompt template
    :param data: job data to summarise
    :param query: query used for the job search
    :return: list of summarised job specific text
    """
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=3000, chunk_overlap=200, length_function=len)
    text = text_splitter.split_documents(data)

    llm: Any = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
    prompt_template: str = """
    {text}
    You're a world class job recruiter, and you'll summarise the text above in order to create a job posting {query}
    Please follow all of the following rules when summarising:
    1/ Make sure the content is engaging information with good data
    2/ The content should address the {query} topic very well
    3/ The content needs to written in a way that is easy to read and understand
    4/ The content needs to give the reader some actions for applying to the jobs
    5/ Only include content with a salary
    
    SUMMARY:
    """

    prompt: PromptTemplate = PromptTemplate(template=prompt_template, input_variables=["text", "query"])

    llm_summariser: Any = LLMChain(llm=llm, prompt=prompt, verbose=True)

    summaries: list = []

    for chunk in enumerate(text):
        print(chunk)
        summary = llm_summariser.predict(text=chunk, query=query)
        summaries.append(summary)

    print(summaries)
    return summaries


# ------------------prompt template and the gpt-3.5-turbo model------------------ #
def generate_the_job_posts(summaries: list, query: str) -> str:
    """
    This function is used to feed the summaries into an LLM, to generate job posts using a prompt template
    :param summaries: summarised job text
    :param query: query used for the job search
    :return: generated job posts
    """
    summaries_str = str(summaries)

    llm = Any = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
    prompt_template = """
    {summaries_str}
    You are a world class recruiter with a lot of experience and the text above is some content about {query}. 
    Please write a job post about {query} using the text above, whilst following all the rules below:
    1/ The job posts needs to be engaging and informative with good data
    2/ Make sure the job posts are easily readable, and not too long
    3/ The job posts should address the {query} topic very well
    4/ The job posts need to be written in a way that is easy to read and understand
    6/ The job posts need to give the reader some actions for applying to the jobs
    7/ The job posts need to clearly display the salary
    
    JOB POST:
    """

    prompt: PromptTemplate = PromptTemplate(template=prompt_template, input_variables=["summaries_str", "query"])

    job_post_chain: Any = LLMChain(llm=llm, prompt=prompt, verbose=True)

    job_post: Any = job_post_chain.predict(summaries_str=summaries_str, query=query)

    return job_post


# ------------------testing------------------ #
# linkedin_profile: dict = get_linkedin_profile(linkedin_client, "jaymesaymer")
job_search_sentence: str = job_search_sentence_generator(test_data)
job_search_results: dict = serp_search_for_jobs(job_search_sentence)
best_job_search_url: list = find_the_best_job_search_url(job_search_results, job_search_sentence)
content: list = get_job_content_from_urls(best_job_search_url)
job_summary: list = summarise_the_job_content(content, job_search_sentence)
generated_job_post: str = generate_the_job_posts(job_summary, job_search_sentence)
