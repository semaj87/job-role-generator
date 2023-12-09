import json
import os
from typing import Any

import requests
import streamlit as st
from dotenv import find_dotenv, load_dotenv
from huggingface_hub import login
from langchain.chains import LLMChain
from langchain.document_loaders import UnstructuredURLLoader
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from linkedin_api import Linkedin

from utils.custom import css_code
from utils.helper import get_keywords, cities, salaries, models, ui_spacer, ui_info, ui_progress_bar, progress_bar_map, \
    model_validator
from utils.messages import welcome_message, header_message, side_bar_temperature_message, side_bar_max_tokens_message

# ---------loading credentials--------- #
load_dotenv(find_dotenv())
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

# ---------huggingface login--------- #
login(token=HUGGINGFACE_API_TOKEN)

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
def find_the_best_job_search_url(response_data: dict, query: str, temperature: Any, model: Any) -> list:
    """
    This function is used to find the best job url using a prompt template and the gpt-3.5-turbo model
    :param response_data: dictionary of job search results
    :param query: query used to search for jobs
    :param temperature: randomness of model output
    :param model: generative model
    :return: list of the top job url
    """
    response_str = json.dumps(response_data)
    prompt_template: str = """
    You're a world class job recruiter, and are very good at finding the most relevant jobs for certain topics;
    {response_str}
    Above is a list of search results for the query {query}.
    Please choose the best jobs from the list, return ONLY an array of the top two urls, do not include anything else;
    """
    # logic for which model is passed in

    model_call: Any = model_validator(model=model, temperature=temperature)

    llm: Any = model_call

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
def summarise_the_job_content(data: list, query: str, temperature: Any, model: Any) -> list[str]:
    """
    This function is used to summarise the fetched job data using the gpt-3.5-turbo and prompt template
    :param data: job data to summarise
    :param query: query used for the job search
    :param temperature: randomness of model output
    :param model: generative model
    :return: list of summarised job specific text
    """
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=3000, chunk_overlap=200, length_function=len)
    text = text_splitter.split_documents(data)

    model_call: Any = model_validator(model=model, temperature=temperature)

    llm: Any = model_call

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
def generate_the_job_list(summaries: list, query: str, temperature: Any, model: Any) -> str:
    """
    This function is used to feed the summaries into an LLM, to generate job posts using a prompt template
    :param summaries: summarised job text
    :param query: query used for the job search
    :param temperature: randomness of model output
    :param model: generative model
    :return: generated job posts
    """
    summaries_str = str(summaries)

    model_call: Any = model_validator(model=model, temperature=temperature)

    llm: Any = model_call

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


# ------------------streamlit------------------ #
def _streamlit() -> None:
    """
    This function is used to build the streamlit web application
    :return: None
    """
    st.set_page_config(page_title="Job post generator", page_icon="img/webworks87-favicon-light.png", layout="wide")

    st.markdown(css_code, unsafe_allow_html=True)

    # ------------------sidebar------------------ #
    with st.sidebar:
        st.image("img/webworks87-light-logo.jpg")
        model: Any = st.selectbox(
            "Choose your model",
            (model for model in models)
        )
        ui_spacer(4)
        # st.write(side_bar_message)
        ui_spacer(1)
        temperature: Any = st.slider(
            "Temperature",
            0.00, 1.00, 0.50,
            help=side_bar_temperature_message
        )
        ui_spacer(2)
        max_tokens: Any = st.slider(
            "Max Tokens",
            5, 1000, 500,
            help=side_bar_max_tokens_message
        )
        ui_spacer(26)
        ui_info()

    # ------------------header & main paragraph------------------ #
    st.header(header_message)
    st.write(welcome_message)

    # ------------------form for handling all elements in a batch------------------ #
    with st.form("main_entry_form", clear_on_submit=False):
        linkedin_profile: Any = st.text_input("LinkedIn profile")

        location: Any = st.selectbox(
            "Location/City",
            (city for city in cities)
        )

        salary: Any = st.selectbox(
            "Salary",
            (salary for salary in salaries)
        )
        ui_spacer(1)
        radius: Any = st.slider("Radius(km)", 0, 100, 0)
        ui_spacer(1)
        main_submit: Any = st.form_submit_button("Submit")

    # ------------------passing main form & sidebar form variables to functions------------------ #
    if main_submit:

        linkedin_profile_result: dict[str, str] = get_linkedin_profile(
            client=linkedin_client, username=linkedin_profile)
        ui_progress_bar(user_feedback=progress_bar_map.get("get_linkedin_profile"))

        job_keywords_result: str = get_job_related_keywords(
            linkedin_profile_dict=linkedin_profile_result, keyword="most_recent_job_title")
        ui_progress_bar(user_feedback=progress_bar_map.get("get_job_related_keywords"))

        job_search_generator_result: str = job_search_sentence_generator(linkedin_profile_dict=linkedin_profile_result)
        ui_progress_bar(user_feedback=progress_bar_map.get("generate_job_search_query"))

        serp_search_job_result: dict = serp_search_for_jobs(query=job_search_generator_result)
        ui_progress_bar(user_feedback=progress_bar_map.get("search_for_job_roles"))

        find_best_job_result: list = find_the_best_job_search_url(
            response_data=serp_search_job_result, query=job_search_generator_result,
            temperature=temperature, model=model)
        ui_progress_bar(user_feedback=progress_bar_map.get("find_the_best_job_urls"))

        get_job_content_result: list = get_job_content_from_urls(urls=find_best_job_result)
        ui_progress_bar(user_feedback=progress_bar_map.get("get_content_from_urls"))

        summarise_job_content_result: list[str] = summarise_the_job_content(
            data=get_job_content_result, query=job_search_generator_result, temperature=temperature, model=model)
        ui_progress_bar(user_feedback=progress_bar_map.get("summarise_content"))

        generate_job_list_result: str = generate_the_job_list(
            summaries=summarise_job_content_result, query=job_search_generator_result,
            temperature=temperature, model=model)
        ui_progress_bar(user_feedback=progress_bar_map.get("generate_job_list"))

        # ------------------UI output------------------ #
        # with st.expander("LinkedIn profile"):
        #     st.info(linkedin_profile_result)
        # with st.expander("Job Keywords results"):
        #     st.info(job_keywords_result)
        # with st.expander("Job search generator"):
        #     st.info(job_search_generator_result)
        # with st.expander("Job search results"):
        #     st.info(serp_search_job_result)
        # with st.expander("Best jobs results"):
        #     st.info(find_best_job_result)
        # with st.expander("Job content results"):
        #     st.info(get_job_content_result)
        # with st.expander("Summarised job content results"):
        #     st.info(summarise_job_content_result)
        with st.expander("Generated job list results"):
            st.info(generate_job_list_result)


# ------------------main------------------ #
def main() -> None:
    """
    Main function
    :return: None
    """
    _streamlit()


if __name__ == "__main__":
    main()
