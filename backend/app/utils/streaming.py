from typing import AsyncGenerator


async def create_sse_response(data_generator: AsyncGenerator[str, None]) -> AsyncGenerator[str, None]:
    """Create Server-Sent Events response from data generator"""
    try:
        async for chunk in data_generator:
            if chunk.strip():
                yield f"data: {chunk}\n\n"
    except Exception as e:
        # Send error as SSE event
        yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
    finally:
        # Send completion signal
        yield "data: [DONE]\n\n"