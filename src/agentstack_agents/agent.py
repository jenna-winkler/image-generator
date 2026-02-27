import os
from typing import Annotated

import httpx
import openai
from a2a.types import Message
from a2a.utils.message import get_message_text

from agentstack_sdk.a2a.extensions.services.platform import (
    PlatformApiExtensionServer,
    PlatformApiExtensionSpec,  # required to initialize the platform client for file storage
)
from agentstack_sdk.a2a.types import AgentMessage
from agentstack_sdk.platform.file import File
from agentstack_sdk.server import Server
from agentstack_sdk.server.context import RunContext

server = Server()

# initialize OpenAI client with API key from environment
openai_client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def generate_image(prompt: str) -> bytes:
    # call DALL-E 3 to generate an image URL from the prompt
    response = await openai_client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        response_format="url",  # get a temporary URL back rather than base64
    )
    url = response.data[0].url

    # download the image bytes from the temporary URL
    async with httpx.AsyncClient() as client:
        image_response = await client.get(url)
        return image_response.content


@server.agent()
async def image_generator(
    input: Message,
    context: RunContext,
    _: Annotated[PlatformApiExtensionServer, PlatformApiExtensionSpec()],  # sets up platform client needed for File.create()
):
    """Agent that generates an image based on the user's prompt"""
    prompt = get_message_text(input)

    # let the user know generation is in progress
    yield AgentMessage(text=f"Generating an image for: *{prompt}*...")

    # generate image bytes via DALL-E 3
    image_bytes = await generate_image(prompt)

    # upload to Agent Stack file store so the UI can retrieve and render it
    uploaded = await File.create(
        filename="generated.png",
        content=image_bytes,
        content_type="image/png",
    )

    # render in chat using agentstack:// scheme — the UI rewrites this to the platform file endpoint
    yield AgentMessage(text=f"![{prompt}](agentstack://{uploaded.id})")


def run():
    try:
        server.run(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", 8000)))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run()