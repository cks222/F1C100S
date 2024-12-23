from zhipuai import ZhipuAI
from typing import Callable
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
from azure.core.credentials import TokenCredential
from azure.core.pipeline.policies import BearerTokenCredentialPolicy
from azure.core.pipeline import PipelineRequest, PipelineContext
from azure.core.rest import HttpRequest
import logging
import fnmatch
import os
import re
import tiktoken


def _make_request() -> PipelineRequest[HttpRequest]:
    return PipelineRequest(HttpRequest("CredentialWrapper", "https://fakeurl"), PipelineContext(None))


def get_bearer_token_provider(credential: TokenCredential, *scopes: str) -> Callable[[], str]:

    policy = BearerTokenCredentialPolicy(credential, *scopes)

    def wrapper() -> str:
        request = _make_request()
        policy.on_request(request)
        return request.http_request.headers["Authorization"][len("Bearer ") :]

    return wrapper

def openai_client(targets):

    if targets == "aml":
        credential = DefaultAzureCredential(managed_identity_client_id="e6162a0d-e540-4454-995f-30bcb97f35b4")
    elif targets == "sing":
        credential = DefaultAzureCredential()

    token_provider = get_bearer_token_provider(
        credential,
        "https://cognitiveservices.azure.com/.default"
    )

    client = AzureOpenAI(
        api_version="2024-08-01-preview",
        azure_endpoint="https://cs-newsandfeeds-singularity-aoai.openai.azure.com/",
        azure_ad_token_provider=token_provider
    )

    return client

def get_ans2(prompt):
    # 需要修改为自己的智谱的api_key
    print(prompt)
    client = ZhipuAI(api_key="c072038a5d1b83c12934c9088f29b139.DRhAJELTdB98WVIq")
    response = client.chat.completions.create(
        model="glm-4",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        top_p=0.3,
        temperature=0.45,
        max_tokens=1024,
        stream=True,
        do_sample=True
    )

    ans = ""
    for trunk in response:
        ans += trunk.choices[0].delta.content
    ans = ans.replace("\n\n", "\n")
    return ans

def get_ans(prompt):
    # 需要修改为自己的智谱的api_key
    print(prompt)
    client = openai_client('sing')

    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    response = client.chat.completions.create(
        model="csnf-gpt-4o",
        messages=messages,
        top_p=0.3,
        temperature=0.45,
        max_tokens=1800,
    )

    ans = ""
    # for trunk in response:
    #     ans += trunk.choices[0].message.content
    # ans = ans.replace("\n\n", "\n")
    ans = response.choices[0].message.content
    return ans

if __name__ == "__main__":
    prompt = "What is a large model? Answer in English"
    aa = get_ans(prompt)
    print(aa)
