from datetime import datetime
from typing import Any


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
