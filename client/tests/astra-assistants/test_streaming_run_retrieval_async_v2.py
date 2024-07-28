import json
import traceback

import pytest
import logging
import time

from openai.lib.streaming import AsyncAssistantEventHandler
from typing_extensions import override

logger = logging.getLogger(__name__)

async def run_with_assistant(assistant, client):
    logger.info(f"using assistant: {assistant}")
    logger.info("Uploading file:")
    # Upload the file
    file = await client.files.create(
        file=open(
            "./tests/fixtures/language_models_are_unsupervised_multitask_learners.pdf",
            "rb",
        ),
        purpose="assistants",
    )

    vector_store = await client.beta.vector_stores.create(
        name="papers",
        file_ids=[file.id]
    )

    # TODO support  vector store file creation
    #file = await client.beta.vector_stores.files.create_and_poll(
    #    vector_store_id=vector_store.id,
    #    file_id=file2.id
    #)

    # TODO support batch
    # Ready the files for upload to OpenAI
    #file_paths = ["edgar/goog-10k.pdf", "edgar/brka-10k.txt"]
    #file_streams = [open(path, "rb") for path in file_paths]

    # Use the upload and poll SDK helper to upload the files, add them to the vector store,
    # and poll the status of the file batch for completion.
    #file_batch = await client.beta.vector_stores.file_batches.upload_and_poll(
    #    vector_store_id=vector_store.id, files=file_streams
    #)

    # You can print the status and the file counts of the batch to see the result of this operation.
    #print(file_batch.status)
    #print(file_batch.file_counts)


    logger.info("adding vector_store id to assistant")
    # Update Assistant
    assistant = await client.beta.assistants.update(
        assistant.id,
        tools=[{"type": "file_search"}],
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )
    logger.info(f"updated assistant: {assistant}")
    user_message = "What are some cool math concepts behind this ML paper pdf? Explain in two sentences."
    logger.info("creating persistent thread and message")
    thread = await client.beta.threads.create()
    await client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    logger.info(f"> {user_message}")

    class EventHandler(AsyncAssistantEventHandler):
        def __init__(self):
            super().__init__()
            self.on_text_created_count = 0
            self.on_text_delta_count = 0

        @override
        async def on_exception(self, exception: Exception):
            logger.error(exception)
            trace = traceback.format_exc()
            logger.error(trace)
            raise exception

        @override
        def on_run_step_done(self, run_step) -> None:
            print("file_search")
            matches = []
            for tool_call in run_step.step_details.tool_calls:
                matches = tool_call.file_search
                print(json.dumps(tool_call.file_search))
            assert len(matches) > 0, "No matches found"

        @override
        def on_text_created(self, text) -> None:
            # Increment the counter each time the method is called
            self.on_text_created_count += 1
            print(f"\nassistant > {text}", end="", flush=True)

        @override
        def on_text_delta(self, delta, snapshot):
            # Increment the counter each time the method is called
            self.on_text_delta_count += 1
            print(delta.value, end="", flush=True)

    event_handler = EventHandler()

    logger.info(f"creating run")
    try:
        async with client.beta.threads.runs.create_and_stream(
                thread_id=thread.id,
                assistant_id=assistant.id,
                event_handler=event_handler,
        ) as stream:
            async for part in stream:
                print(part)

        assert event_handler.on_text_created_count > 0, "No text created"
        assert event_handler.on_text_delta_count > 0, "No text delta"
    except Exception as e:
        print(e)
        tcb = traceback.format_exc()
        print(tcb)
        raise e


instructions = "You are a personal math tutor. Answer thoroughly. The system will provide relevant context from files, use the context to respond."

@pytest.mark.asyncio
async def test_run_gpt_4o_mini(async_patched_openai_client):
    model = "gpt-4o-mini"
    name = f"{model} Math Tutor"

    gpt3_assistant = await async_patched_openai_client.beta.assistants.create(
        name=name,
        instructions=instructions,
        model=model,
    )
    await run_with_assistant(gpt3_assistant, async_patched_openai_client)
