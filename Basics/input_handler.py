from turtle import _Screen, Screen
from typing import Callable, Literal
from time import perf_counter, sleep
import threading

class KeyboardInputHandler:
    RELEASE_DELAY: float = 0.05
    AUTO_REPEAT_THRESHOLD: float = 0.25

    def __init__(self, screen: _Screen):
        self.screen: _Screen = screen
        self.key_status: dict[str, bool] = dict()
        self.key_press_events: dict[str, set[Callable[[], None]]] = dict() 
        self.key_release_events: dict[str, set[Callable[[], None]]] = dict()
        self.key_hold_events: dict[str, set[Callable[[], None]]] = dict() 
        self.listen = False
        self.frame_interval = 1 / 240
        
        self._pending_releases: dict[str, float] = dict()
        self._press_start_time: dict[str, float] = dict()
        self._lock = threading.Lock()

    def set_fps(self, fps: int):
        self.frame_interval = 1 / fps

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
            func()

    def _on_key_release(self, key: str):
        curr_time = perf_counter()
        with self._lock:
            # 이 키가 눌린 지 얼마나 지났는지 확인
            press_duration = curr_time - self._press_start_time.get(key, curr_time)
            
            if press_duration < self.AUTO_REPEAT_THRESHOLD:
                # 0.25초 안에 뗐다면 이건 가짜 연사가 아니라 유저의 '짧은 탭(Tap)'임.
                # 딜레이 없이 당장 이번 프레임 루프에서 떼도록 목표 시간을 0으로 설정
                self._pending_releases[key] = 0.0 
            else:
                # 0.25초 이상 꾹 누르고 있었다면 가짜 연사일 수 있으므로 디바운싱(안전장치) 가동
                self._pending_releases[key] = curr_time + self.RELEASE_DELAY

    def _actual_release(self, key: str):
        with self._lock:
            self.key_status[key] = False
        if not self.listen: return
        for func in self.key_release_events.get(key, set()):
            func()

    def bind(self, key: str, status: Literal["PRESS", "HOLD", "RELEASE"], func: Callable[[], None]):
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
    
    def unbind(self, key: str, status: Literal["PRESS", "HOLD", "RELEASE"], func: Callable[[], None]):
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
        self.screen.listen() # Tkinter 키보드 포커스 획득 (이게 없으면 이벤트가 영원히 안 먹힘)
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def _listen_loop(self):
        old_time = perf_counter()
        while True:
            curr_time = perf_counter()
            if curr_time >= old_time + self.frame_interval:
                
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
                        func()

                old_time += self.frame_interval
            else:
                sleep(0.001)

if __name__=="__main__":
    screen = Screen()
    input_handler = KeyboardInputHandler(screen)
    input_handler.bind("a", "PRESS", lambda: print("Pressing A"))
    input_handler.bind("a", "HOLD", lambda: print("Holding A"))
    input_handler.bind("a", "RELEASE", lambda: print("Releasing A"))
    input_handler.start_listen()
    screen.exitonclick()
