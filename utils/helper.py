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
def progress_bar(user_feedback: list[str], amount_of_time: int = 20) -> None:
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
        status.update(label=f"Download {user_feedback[0]} of 5 complete!", state="complete", expanded=False)


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
cities = ["Amsterdam", "Frankfurt", "Hong Kong", "London", "Oslo", "Paris", "Singapore", "Tokyo"]


# ------------------streamlit salaries list------------------ #
salaries = [
    "20k-40k", "40k-60k", "60k-80k", "80k-100k", "100k-120k",
    "120k-140k", "140k-160k", "160k-180k", "180k-200k", "200k-220k",
    "220k-240k"
]
