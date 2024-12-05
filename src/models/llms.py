from langchain_openai import ChatOpenAI



def load_llm(model_name):
    if model_name == "gpt-3.5-turbo":
        return ChatOpenAI(
            model=model_name,
            temperature=0.0,
            max_tokens=500,
        )
    elif model_name == "gpt-4":
        return ChatOpenAI(
            model=model_name,
            temperature=0.0,
            max_tokens=500,
        )
    elif model_name == "gemini-pro":
        # Import Gemini and Return Gemini mode
        pass
    else:
        raise ValueError(
            "Unknown model.\
                Please choose from ['gpt-3.5-turbo','gpt-4', ...]"
        )