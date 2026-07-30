import pytest
from uuid import uuid4

from backend.app.events.publisher import EventPublisher


@pytest.mark.asyncio
async def test_subscribe():
    publisher = EventPublisher()

    research_id = uuid4()

    queue = publisher.subscribe(research_id)

    assert queue is not None
    assert research_id in publisher._subscribers
    assert len(publisher._subscribers[research_id]) == 1


@pytest.mark.asyncio
async def test_unsubscribe():
    publisher = EventPublisher()

    research_id = uuid4()

    queue = publisher.subscribe(research_id)

    publisher.unsubscribe(
        research_id,
        queue,
    )

    assert research_id not in publisher._subscribers


@pytest.mark.asyncio
async def test_publish_single_subscriber():
    publisher = EventPublisher()

    research_id = uuid4()

    queue = publisher.subscribe(research_id)

    event = {
        "event": "progress",
        "data": {
            "progress": 50,
        },
    }

    await publisher.publish(
        research_id,
        event,
    )

    received = await queue.get()

    assert received == event


@pytest.mark.asyncio
async def test_publish_multiple_subscribers():
    publisher = EventPublisher()

    research_id = uuid4()

    queue1 = publisher.subscribe(research_id)
    queue2 = publisher.subscribe(research_id)

    event = {
        "event": "completed",
        "data": {
            "progress": 100,
        },
    }

    await publisher.publish(
        research_id,
        event,
    )

    assert await queue1.get() == event
    assert await queue2.get() == event


@pytest.mark.asyncio
async def test_publish_no_subscribers():
    publisher = EventPublisher()

    await publisher.publish(
        uuid4(),
        {
            "event": "progress",
            "data": {},
        },
    )


@pytest.mark.asyncio
async def test_shutdown():
    publisher = EventPublisher()

    research_id = uuid4()

    queue1 = publisher.subscribe(research_id)
    queue2 = publisher.subscribe(research_id)

    await publisher.shutdown(research_id)

    assert await queue1.get() is None
    assert await queue2.get() is None

    assert research_id not in publisher._subscribers