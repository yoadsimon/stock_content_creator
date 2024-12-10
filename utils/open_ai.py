import os
from dotenv import load_dotenv
from openai import OpenAI
from inputs.video_map import VIDEO_DESCRIPTION_MAP

load_dotenv()


class OpenAIClient():
    def __init__(self):
        self.client = OpenAI(
            organization=os.getenv('OPEN_AI_ORGANIZATION_ID'),
            project=os.getenv('OPEN_AI_PROJECT_ID'),
            api_key=os.getenv('OPEN_AI_TOKEN')
        )

    def generate_text(self, prompt, model="gpt-4o-mini"):
        try:
            response = self.client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": prompt,
                }],
                model=model,
            )

            result = response.choices[0].message.content
        except Exception as e:
            print(f"Error: {e}")
            result = None

        return result


def check_if_article_relevant(text, link, company_name, stock_symbol, client) -> bool:
    prompt = (
        "You are a financial analyst specializing in evaluating news articles for their potential impact on a company's stock price.\n"
        "Analyze the following article and determine whether it is relevant to the future stock price movement of the specified company.\n"
        "Consider factors such as financial performance, market conditions, legal issues, management changes, or other significant events that could influence the stock price.\n"
        "Respond with 'True' if the article is relevant, or 'False' if it is not.\n"
        "Your response should be only 'True' or 'False'.\n"
        f"Company Name: {company_name}\n"
        f"Stock Symbol: {stock_symbol}\n"
        f"Article Link: {link}\n"
        f"Article Text: {text}"
    )
    response = client.generate_text(prompt)
    try:
        return response.strip().lower() == 'true'
    except Exception as e:
        print(f"Error: {e}")
        return False


def summarize_with_open_ai(text, link, company_name, stock_symbol):
    client = OpenAIClient()
    is_article_relevant = check_if_article_relevant(text, link, company_name, stock_symbol, client)
    if not is_article_relevant:
        return None
    prompt = (
        f"You are a financial analyst with expertise in assessing news impact on stock prices in the immediate term.\n"
        f"Please perform the following tasks:\n"
        f"1. **Summarize** the following news article related to {company_name} ({stock_symbol}) in 2-3 sentences.\n"
        f"2. **Evaluate** the likely impact of this news on the company's stock price for the next trading day. Indicate whether the impact is **positive**, **negative**, or **neutral**.\n"
        f"3. **Explain** your reasoning in 1-2 sentences.\n"
        f"Provide your response in a clear and organized manner, numbering each part accordingly.\n\n"
        f"Article Link: {link}\n\n"
        f"Article Text:\n{text}\n"
    )

    summary = client.generate_text(prompt)
    return summary


def generate_stock_opening_analysis(text, company_name, stock_symbol):
    client = OpenAIClient()

    prompt = (
        f"You are a seasoned financial analyst and market commentator.\n"
        f"Based on the latest news and developments related to {company_name} ({stock_symbol}), "
        f"provide a concise and insightful analysis of how the stock is likely to perform when the market opens today.\n"
        f"Your explanation should be professional, use clear language, and be suitable for an audio briefing to investors.\n\n"
        f"Latest News Summary:\n{text}\n\n"
        f"Your analysis should include:\n"
        f"1. A prediction on whether the stock will go **up** or **down** at market open, and why.\n"
        f"2. An estimated percentage of the expected price movement.\n"
        f"3. Key factors from the news that support your prediction.\n"
        f"Please present your analysis in a single, well-structured paragraph."
    )

    results = client.generate_text(prompt)
    return results


def add_SSML_tags(text, company_name, stock_symbol):
    # TODO - Implement SSML tagging better
    client = OpenAIClient()

    prompt = (
        f"You are a text-to-speech expert. Enhance the given text with SSML "
        f"tags, ensuring compliance with Amazon Polly's supported features. "
        f"Use pauses and adjust the speaking rate and volume as necessary for "
        f"an engaging audio presentation of a financial report on {company_name} "
        f"with stock symbol {stock_symbol}. SSML should include only supported tags.\n\n"
        f"Text:\n{text}\n"
        f"return ONLY the given text enhanced with SSML"

    )

    ssml_text = client.generate_text(prompt)
    ssml_text = ssml_text.replace('```', '').replace('xml', '').strip()
    return ssml_text


def match_text_to_videos(text) -> dict:
    video_description_map = VIDEO_DESCRIPTION_MAP  # This dictionary should be pre-defined
    client = OpenAIClient()

    prompt = f"""
    You are given a mapping of video descriptions and their corresponding video file names.
    Here is the video description map: {video_description_map}

    Your task is to analyze the following text and segment it into parts such that each part can be associated
    with a relevant video whose description closely matches the content or context of that text segment.

    Text:
    {text}

    Steps to follow:
    1. Break down the text into meaningful parts that can stand alone in terms of their themes or topics.
    2. For each part, identify and match it with a video whose description from the description map holds the most relevance.
    3. Return the results as a Python dictionary where each key is an EXACT segment of the original text, 
       and the corresponding value is the name of the video file that best matches it.
    """

    response = client.generate_text(prompt)
    start = response.find("{")
    end = response.find("}")
    response = response[start:end + 1]

    try:
        video_mapping = eval(response)
    except SyntaxError as e:
        raise ValueError(f"Error parsing response: {e}")
    for text, video_name in video_mapping.items():
        if video_name is None:
            import random
            random_number = random.randint(1, 2)
            if random_number == 1:
                video_mapping[text] = "Interactive_Trading_Screen.mp4"
            else:
                video_mapping[text] = "Stock_Ticker_Grid.mp4"

    return video_mapping


def match_text_to_video(text) -> str:
    video_description_map = VIDEO_DESCRIPTION_MAP
    client = OpenAIClient()

    prompt = f"""
    You are given a mapping of video descriptions and their corresponding video file names.
    Here is the video description map: {video_description_map}

    Your task is to analyze the following sentence and find the video whose description from the description map holds the most relevance.

    Sentence: "{text}"

    Return ONLY the name of the video file that best matches the sentence.
    """

    response = client.generate_text(prompt)
    if not response:
        import random
        random_number = random.randint(1, 2)
        if random_number == 1:
            response = "Interactive_Trading_Screen.mp4"
        else:
            response = "Stock_Ticker_Grid.mp4"
    return response

# if __name__ == "__main__":
#     text = "Meanwhile, despite competitive challenges and overall market declines, analysts highlight NVIDIA's strong position in the AI chip market, presenting a mixed sentiment for its future stock performance."
#     print(match_text_to_video(text))
