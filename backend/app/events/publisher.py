from asyncio import Queue
from collections import defaultdict
from typing import TypedDict
from uuid import UUID


class ResearchEvent(TypedDict):
    type: str
    data: dict


class EventPublisher:
    """
    In-memory event publisher for research progress updates.

    Each research task can have multiple subscribers.
    """

    def __init__(self) -> None:
        self._subscribers: dict[
            UUID,
            list[Queue[ResearchEvent | None]],
        ] = defaultdict(list)

    def subscribe(
        self,
        research_id: UUID,
        maxsize: int = 0,
    ) -> Queue[ResearchEvent | None]:
        """
        Register a new subscriber for a research task.
        """
        queue: Queue = Queue(maxsize=maxsize)
        self._subscribers[research_id].append(queue)
        return queue

    def unsubscribe(
        self,
        research_id: UUID,
        queue: Queue,
    ) -> None:
        """
        Remove a subscriber.
        """
        subscribers = self._subscribers.get(research_id)

        if subscribers is None:
            return

        if queue in subscribers:
            subscribers.remove(queue)

        if not subscribers:
            self._subscribers.pop(research_id, None)

    async def publish(
        self,
        research_id: UUID,
        event: ResearchEvent,
    ) -> None:
        """
        Publish an event to all subscribers.
        """
        for queue in list(self._subscribers.get(research_id, [])):
            await queue.put(event)

    async def shutdown(self, research_id: UUID) -> None:
        """
        Notify all subscribers that the stream has ended
        and remove them.
        """
        for queue in list(self._subscribers.pop(research_id, [])):
            await queue.put(None)
