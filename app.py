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


# ------------------testing------------------ #
# linkedin_profile: dict = get_linkedin_profile(linkedin_client, "jaymesaymer")
job_search_sentence: str = job_search_sentence_generator(test_data)
job_search_results: dict = serp_search_for_jobs(job_search_sentence)
best_job_search_url: list = find_the_best_job_search_url(job_search_results, job_search_sentence)
