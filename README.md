# Job role generator
This Streamlit web application uses generative AI models, together with the LinkedIn API and the SERP API to make tailored job suggestions.

The end-to-end process for this application can be summarised as follows:
* User enters their LinkedIn profile
* A request is made to the LinkedIn API to retrieve their information
* The search results are summarised using a prompt template, generative model and LangChain
* Finally, the jobs are generated using the model, and displayed using Streamlit


## System design


## Models


## Requirements
```bash
python -m pip install -r requirements.txt
```


## Run App Locally

```bash
source build.sh
```


## Run App with Streamlit Cloud

[Launch App]()


## License

Distributed under the MIT License. See `LICENSE` for more information.
