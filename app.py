import os
import requests

from dotenv import find_dotenv, load_dotenv


# ---------loading credentials--------- #
load_dotenv(find_dotenv())
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")


# ------------------getting user information via the LinkedIn API------------------ #
def generate_authorisation_url():
    """
    Generate an authorization URL for a user to give permission to extract their LinkedIn Profile.

    The genereated URL will take the user to a LinkedIn page where the user will be asked to give explicit
    permission to share their profile with you (the application creator).

    Should the user agree, they will be redirected to `LINKEDIN_REDIRECT_URI`.
    In the redirect, two fields will appear in the URL parameter, namely `code` and `state`.

    * `state` is generated below using `secrets.token_hex(8).upper()`. This is as a form of identifier for this user.
    * `code` is the authorization_code, and can be used in `get_access_token()` to exchange for an `access_token`.
    :return None
    """
    LI_AUTH_URL = 'https://www.linkedin.com/oauth/v2/authorization'
    url = requests.Request('GET', LI_AUTH_URL,
                           params={
                               'response_type': 'code',
                               'client_id': LINKEDIN_CLIENT_ID,
                               'redirect_uri': LINKEDIN_REDIRECT_URI,
                               'state': secrets.token_hex(8).upper(),
                               'scope': '%20'.join(['r_liteprofile', 'r_emailaddress', 'w_member_social']),
                           }).prepare().url
    return url


def get_access_token(authorisation_code: str):
    """
    Given a authorization `code`, this function will return you `access_token` which can then be used to access a user's
     LinkedIn profile.
     :param authorisation_code: generated code from user permission
    """
    LI_ACCESS_TOKEN_EXCHANGE_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
    access_token = requests.post(LI_ACCESS_TOKEN_EXCHANGE_URL, params={
        'grant_type': 'authorization_code',
        'code': authorisation_code,
        'redirect_uri': LINKEDIN_REDIRECT_URI,
        'client_id': LINKEDIN_CLIENT_ID,
        'client_secret': LINKEDIN_CLIENT_SECRET,
    }).json()['access_token']

    return access_token


def get_user_profile(access_token: str) -> str:
    """
    This function is used to access a user's LinkedIn profile and retrieve the data
    :param access_token: token to access the user's profile
    :return JSON representation of the user's profile
    """
    LI_PROFILE_API_ENDPOINT = 'https://api.linkedin.com/v2/me'
    r = requests.get(LI_PROFILE_API_ENDPOINT, headers={
    'Authorization': 'Bearer ' + access_token})

    return r.json()


# ------------------find the most relevant keywords & data to improve the search------------------ #
def find_job_specific_data_from_profile(response_data: dict) -> list:
    """

    :param response_data:
    :return:
    """
