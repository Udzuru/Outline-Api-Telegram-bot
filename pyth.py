from g4f.client import Client
from g4f.Provider import RetryProvider, Phind, FreeChatgpt, Liaobots

import g4f.debug
g4f.debug.logging = True

client = Client(
    provider=RetryProvider([Phind, FreeChatgpt, Liaobots], shuffle=False)
)
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Say this is a test"}],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content or "", end="")
print(response.choices[0].message.content)
