from abc import ABC, abstractmethod
from typing import Self, Optional

from time import perf_counter, sleep
import threading

class HasTimedLoop(ABC):
    @property
    @abstractmethod
    def frame_interval(self) -> float:
        pass

    @abstractmethod
    def _loop_action(self, curr_time: float, delta: float) -> None:
        pass

    def begin_loop_thread(self) -> threading.Thread:
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()
        return thread

    def _loop(self):
        old_time = perf_counter()
        accumulator = 0.0
        while True:
            curr_time = perf_counter()
            frame_time = curr_time - old_time
            old_time = curr_time

            if frame_time >= 0.1:
                frame_time = 0.1

            accumulator += frame_time

            while accumulator >= self.frame_interval:
                self._loop_action(curr_time, self.frame_interval)
                accumulator -= self.frame_interval

            time_left = self.frame_interval - accumulator
            if time_left > 0.002:
                sleep(0.001)
            else:
                sleep(0)

class Singleton(ABC):
    singleton: Optional[Self] = None

    @classmethod
    def instance(cls) -> Self:
        if cls.singleton is None:
            cls.singleton = cls()
        return cls.singleton
