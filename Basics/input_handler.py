from turtle import _Screen, Screen
from typing import Callable, Literal, Union
from time import perf_counter
from dataclasses import dataclass

from Basics.design_pattern import *

@dataclass
class KeyboardInputEvent:
    event_time: float

@dataclass
class KeyPressEvent(KeyboardInputEvent):
    pass

@dataclass
class KeyReleaseEvent(KeyboardInputEvent):
    duration: float

@dataclass
class KeyHoldEvent(KeyboardInputEvent):
    duration: float

class KeyboardInputHandler(HasTimedLoop):
    RELEASE_DELAY: float = 0.015
    AUTO_REPEAT_THRESHOLD: float = 0.35

    def __init__(self, screen: _Screen):
        self.screen: _Screen = screen
        self.key_status: dict[str, bool] = dict()
        self.key_press_events: dict[str, set[Callable[[KeyPressEvent], None]]] = dict() 
        self.key_release_events: dict[str, set[Callable[[KeyReleaseEvent], None]]] = dict()
        self.key_hold_events: dict[str, set[Callable[[KeyHoldEvent], None]]] = dict() 
        self.listen = False
        self._frame_interval = 1 / 240
        
        self._pending_releases: dict[str, float] = dict()
        self._press_start_time: dict[str, float] = dict()
        self._lock = threading.Lock()

        self.base_time = 0.0

    @property
    def frame_interval(self):
        return self._frame_interval

    def set_fps(self, fps: int):
        self._frame_interval = 1 / fps

    def _on_key_press(self, key: str):
        with self._lock:
            if key in self._pending_releases:
                del self._pending_releases[key]
                
            if self.key_status.get(key, False):
                return
            
            self.key_status[key] = True
            self._press_start_time[key] = perf_counter() # 키 최초 입력 시간 스탬프
            
        if not self.listen: return
        for func in self.key_press_events.get(key, set()):
            func(KeyPressEvent(perf_counter() - self.base_time))

    def _on_key_release(self, key: str):
        curr_time = perf_counter()
        
        with self._lock:
            press_duration = curr_time - self._press_start_time.get(key, curr_time)

        if press_duration < self.AUTO_REPEAT_THRESHOLD:
            # 1. 큐 대기열에 혹시 남아있다면 즉시 청소
            with self._lock:
                if key in self._pending_releases:
                    del self._pending_releases[key]
            # 2. 데몬 스레드의 순회를 기다리지 않고 즉시(0ms) 릴리스 콜백 실행
            self._actual_release(key)
        else:
            # 긴 홀드일 때만 최소한의 디바운싱 딜레이(15ms) 적용
            with self._lock:
                self._pending_releases[key] = curr_time + self.RELEASE_DELAY

    def _actual_release(self, key: str):
        with self._lock:
            self.key_status[key] = False
        if not self.listen: return
        curr_time = perf_counter()
        for func in self.key_release_events.get(key, set()):
            func(KeyReleaseEvent(curr_time - self.base_time, curr_time - self._press_start_time[key]))

    def bind(self, key: str, status: Literal["PRESS", "HOLD", "RELEASE"], func: Union[Callable[[], None], Callable[[KeyboardInputEvent], None]]):
            if key not in self.key_status:
                self.key_status[key] = False
                self.screen.onkeypress(lambda: self._on_key_press(key), key)
                self.screen.onkey(lambda: self._on_key_release(key), key)
                
            match status:
                case "PRESS":
                    if key not in self.key_press_events:
                        self.key_press_events[key] = set()
                    self.key_press_events[key].add(func)
                case "HOLD":
                    if key not in self.key_hold_events:
                        self.key_hold_events[key] = set()
                    self.key_hold_events[key].add(func)
                case "RELEASE":
                    if key not in self.key_release_events:
                        self.key_release_events[key] = set()
                    self.key_release_events[key].add(func)
                case _:
                    raise ValueError(f"status는 PRESS, HOLD, RELEASE 중 하나여야 합니다 - 받은 값: {status}")
    
    def unbind(self, key: str, status: Literal["PRESS", "HOLD", "RELEASE"], func: Union[Callable[[], None], Callable[[KeyboardInputEvent], None]]):
        match status:
            case "PRESS":
                self.key_press_events[key].remove(func)
            case "HOLD":
                self.key_hold_events[key].remove(func)
            case "RELEASE":
                self.key_release_events[key].remove(func)
            case _:
                raise ValueError(f"status는 PRESS, HOLD, RELEASE 중 하나여야 합니다 - 받은 값: {status}")

    def start_listen(self):
        self.listen = True
        self.base_time = perf_counter()
        self.screen.listen() # Tkinter 키보드 포커스 획득 (이게 없으면 이벤트가 영원히 안 먹힘)
        self.begin_loop_thread()
        
    def _loop_action(self, curr_time, delta):
        # 떼는 키 대기열 처리
        keys_to_release = []
        with self._lock:
            for key, target_time in self._pending_releases.items():
                if curr_time >= target_time:
                    keys_to_release.append(key)
                    
            for key in keys_to_release:
                del self._pending_releases[key]
        
        # 키 떼기
        for key in keys_to_release:
            self._actual_release(key)
        
        with self._lock:
            active_holds = [
                key for key in self.key_hold_events 
                if self.key_status.get(key, False)
            ]
        
        for key in active_holds:
            for func in self.key_hold_events[key]:
                func(KeyHoldEvent(curr_time, curr_time - self._press_start_time[key]))


if __name__=="__main__":
    screen = Screen()
    input_handler = KeyboardInputHandler(screen)
    input_handler.bind("a", "PRESS", lambda ev: print(f"Pressed A at {ev.event_time}"))
    input_handler.bind("a", "HOLD", lambda ev: print(f"Holding A for {ev.duration}"))
    input_handler.bind("a", "RELEASE", lambda ev: print(f"Releasing A at {ev.event_time} after {ev.duration} of hold"))
    input_handler.start_listen()
    screen.exitonclick()
