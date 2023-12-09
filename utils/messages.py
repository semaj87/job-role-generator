header_message: str = "Job Post Generator"

welcome_message: str = """
Welcome! This Streamlit web application uses several generative AI models from 
[Hugging Face](https://huggingface.co/models) and [OpenAI](https://platform.openai.com/docs/models), together with the 
[LinkedIn API](https://developer.linkedin.com/product-catalog) and the [SERP API](https://serpapi.com/) to make 
tailored job suggestions. The end-to-end process for this application is made possible by the use of the parameters
stated below. First select your model and temperature value, before completing the main form below.

    1. LinkedIn profile
    2. Location
    3. Radius
    4. Salary
"""

side_bar_temperature_message: str = """
Set the temperature of the completion. Higher values make the output more random,lower values make it more focussed
"""

side_bar_max_tokens_message: str = """
Max response length. Together with your prompt, it shouldn't surpass the model's token limit (2048)
"""
