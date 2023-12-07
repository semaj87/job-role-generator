from datetime import datetime
from typing import Any
import streamlit as st
import time


# ------------------LinkedIn keyword dict------------------ #
def get_keywords(keyword: str, data: dict) -> str:
    """
    This helper function is used to retrieve keyword information from a user profile
    :param keyword: (experience, education, location, title, industry)
    :param data: returned user profile from LinkedIn API
    :return: keyword information
    """
    keywords_map: dict = {
        "most_recent_degree": data.get('education')[0]['fieldOfStudy'],
        "current_location": data.get("experience")[0]["locationName"],
        "most_recent_job_title": data.get("experience")[0]["title"],
        "years_in_most_recent_job": datetime.now().year - data.get("experience")[0]["timePeriod"]["startDate"]["year"],
        "most_recent_industry": data.get("experience")[0]["company"]["industries"]
    }
    return keywords_map[keyword]


# ------------------progress bar------------------ #
def ui_progress_bar(user_feedback: list[str], amount_of_time: int = 20) -> None:
    """
    This function is used to create a progress bar to improve the UX
    :param user_feedback: messages to output with the progress bar
    :param amount_of_time: time taken to sleep
    :return: None
    """
    with st.status("AI models hard at work", expanded=True) as status:
        st.write(user_feedback[1])
        time.sleep(amount_of_time)
        st.write(user_feedback[2])
        time.sleep(1)
        status.update(label=f"Download {user_feedback[0]} of 8 complete!", state="complete", expanded=False)


# ------------------UI author information------------------ #
def ui_info() -> None:
    ui_spacer(1)
    st.write("Made by [James Aymer](https://www.linkedin.com/in/jamesaymer/)", unsafe_allow_html=True)
    st.markdown('Source code can be found [here](https://github.com/semaj87/job-role-generator)')


def ui_text_update_markdown(text: str, alignment: str) -> str:
    text_update: list[str] = '<div style="text-align: alignment;">text</div>'.split("text<")
    tmp_string = text_update[0] + text + text_update[-1]
    alignment_update: list[str] = tmp_string.split("alignment")
    updated_markdown: str = alignment_update[0] + alignment + alignment_update[-1]

    return updated_markdown


def ui_text_align(markdown_text: str) -> None:
    st.markdown(markdown_text, unsafe_allow_html=True)


# ------------------UI spacer------------------ #
def ui_spacer(n=2, line=False, next_n=0):
    for _ in range(n):
        st.write('')
    if line:
        st.tabs([' '])
    for _ in range(next_n):
        st.write('')


# ------------------test LinkedIn user profile data------------------ #
test_data: Any = {
    'experience': [{'locationName': 'London, United Kingdom',
                    'entityUrn': 'urn:li:fs_position:(ABCDEFGHIJK,1120846238)',
                    'geoLocationName': 'London, United Kingdom',
                    'geoUrn': 'urn:li:fs_geo:123456',
                    'companyName': 'Webworks87',
                    'timePeriod': {'startDate': {'month': 9, 'year': 2017}},
                    'company': {'employeeCountRange': {'start': 10001},
                                'industries': ['Software']},
                    'title': 'AI Software Engineer',
                    'region': 'urn:li:fs_region:(gb,6789)',
                    'companyUrn': 'urn:li:fs_miniCompany:9823'
                    }],
    'education': [{'entityUrn': 'urn:li:fs_education:(AC12345)',
                   'timePeriod': {'endDate': {'year': 2016}, 'startDate': {'year': 2013}},
                   'degreeName': 'Bachelor of Science (BSc)',
                   'schoolName': 'University of Reading',
                   'fieldOfStudy': 'Computer Science',
                   'schoolUrn': 'urn:li:fs_miniSchool:123456'
                   }]
}

# ------------------streamlit cities set------------------ #
cities = ["Amsterdam", "Copenhagen", "Frankfurt", "Hong Kong", "London", "Oslo", "Paris", "Singapore", "Tokyo"]

# ------------------streamlit salaries list------------------ #
salaries = [
    "20k-40k", "40k-60k", "60k-80k", "80k-100k", "100k-120k",
    "120k-140k", "140k-160k", "160k-180k", "180k-200k", "200k-220k",
    "220k-240k"
]

# ------------------streamlit models list------------------ #
models = [
    "gpt-3.5-turbo", "flan-t5-base", "fastchat-t5-3b-v1.0",
    "BELLE-7B-2M", "m2m100_418M", "mbart-large-50"
]

# ------------------progress bar map------------------ #
progress_bar_map: dict = {
    "get_linkedin_profile": [1, "Retrieving linkedin profile...", "Profile found."],
    "get_job_related_keywords": [2, "Extracting job related keywords...", "Keywords extracted."],
    "generate_job_search_query": [3, "Generating job query...", "Query generated."],
    "search_for_job_roles": [4, "Searching for job roles...", "Job roles found."],
    "find_the_best_job_urls": [5, "Searching for top job URLs...", "URLs found."],
    "get_content_from_urls": [6, "Extracting job content from the URLs...", "Content extracted."],
    "summarise_content": [7, "Summarising job content...", "J content summarised."],
    "generate_job_list": [8, "Generating job list...", "Job list generated."]
}
