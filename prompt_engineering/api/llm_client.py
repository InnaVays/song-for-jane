import openai

def call_llm(prompt, model="gpt-4", temperature=0.9, max_tokens=100):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response['choices'][0]['message']['content'].strip()