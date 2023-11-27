import asyncio

class ObserverManager:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    async def notify(self, subject):
        await asyncio.gather(*(observer.update(subject) 
                               for observer in self._observers))