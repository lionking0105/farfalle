import asyncio
import json
import logging
from typing import Any, AsyncGenerator, AsyncIterator, Generator, List

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from llama_index.llms.openai import OpenAI
from prompts import CHAT_PROMPT, RELATED_QUESTION_PROMPT, HISTORY_QUERY_REPHRASE
from search import search_tavily
from sse_starlette.sse import EventSourceResponse
from llama_index.llms.groq import Groq
from llama_index.core.program import FunctionCallingProgram
import instructor


load_dotenv()


from schemas import (
    ChatRequest,
    ChatResponseEvent,
    Message,
    RelatedQueries,
    RelatedQueriesStream,
    SearchResult,
    SearchResultStream,
    StreamEndStream,
    StreamEvent,
    TextChunkStream,
)

GPT4_MODEL = "gpt-4-turbo"
GPT3_MODEL = "gpt-3.5-turbo"
LLAMA_8B_MODEL = "llama3-8b-8192"
LLAMA_70B_MODEL = "llama3-70b-8192"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(await request.body())
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logging.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@app.post("/chat")
async def chat(
    chat_request: ChatRequest, request: Request
) -> Generator[ChatResponseEvent, None, None]:
    async def generator():
        async for obj in stream_qa_objects(chat_request):
            yield json.dumps(jsonable_encoder(obj))
            await asyncio.sleep(0)

    return EventSourceResponse(generator(), media_type="text/event-stream")


def rephrase_query_with_history(
    question: str, history: List[Message], llm: OpenAI
) -> str:
    if history:
        history_str = "\n".join([f"{msg.role}: {msg.content}" for msg in history])
        return llm.complete(
            HISTORY_QUERY_REPHRASE.format(chat_history=history_str, question=question)
        ).text
    return question


async def stream_qa_objects(request: ChatRequest) -> AsyncIterator[ChatResponseEvent]:
    # TODO: idea, get chunks from search results (like make a request) and just put them through a re-ranker
    # Might be slow though

    # llm = OpenAI(model=GPT4_MODEL)
    llm = Groq(model=LLAMA_70B_MODEL)
    query = rephrase_query_with_history(request.query, request.history, llm)

    search_results = await search_tavily(query)

    related_queries_task = asyncio.create_task(
        generate_related_queries(query, search_results)
    )

    yield ChatResponseEvent(
        event=StreamEvent.SEARCH_RESULTS,
        data=SearchResultStream(
            results=search_results,
        ),
    )

    context_str = "\n\n".join(
        [f"Citation {i+1}. {str(result)}" for i, result in enumerate(search_results)]
    )

    fmt_qa_prompt = CHAT_PROMPT.format(
        my_context=context_str,
        my_query=query,
    )

    for completion in llm.stream_complete(fmt_qa_prompt):
        yield ChatResponseEvent(
            event=StreamEvent.TEXT_CHUNK,
            data=TextChunkStream(text=completion.delta or ""),
        )

    related_queries = await related_queries_task
    yield ChatResponseEvent(
        event=StreamEvent.RELATED_QUERIES,
        data=RelatedQueriesStream(related_queries=related_queries),
    )

    yield ChatResponseEvent(
        event=StreamEvent.STREAM_END,
        data=StreamEndStream(),
    )


async def generate_related_queries(
    query: str, search_results: list[SearchResult]
) -> list[str]:
    from openai import OpenAI

    context = "\n\n".join([f"{str(result)}" for result in search_results])
    client = instructor.from_openai(OpenAI())

    related = client.chat.completions.create(
        model=GPT3_MODEL,
        response_model=RelatedQueries,
        messages=[
            {
                "role": "user",
                "content": RELATED_QUESTION_PROMPT.format(query=query, context=context),
            },
        ],
    )

    return related.related_queries
