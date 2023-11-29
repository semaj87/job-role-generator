import os
import requests

from dotenv import find_dotenv, load_dotenv
from linkedin_api import Linkedin
from typing import Any


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
def find_job_related_keywords(linkedin_profile_dict: dict) -> list[str]:
    """
    This function is used to retrieve all the job related keywords from a user profile
    :param linkedin_profile_dict:
    :return: list of job related keywords
    """


# ------------------using serpapi to search for jobs using keywords------------------ #
def serp_search_for_jobs(query: str) -> dict:
    """
    This function is used to search for jobs using the serpapi
    :param query: query used to search
    :return: dict of search results
    """
