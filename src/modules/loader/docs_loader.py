from abc import ABC, abstractmethod

from src.modules.loader.docs import Docs


class DocsLoader(ABC):
    """
    로더의 공통 인터페이스를 정의한 추상 베이스 클래스입니다.
    """

    @abstractmethod
    def load(self, source: str) -> "Docs":
        """
        주어진 source(예: URL, Path)로부터 문서를 로드하여 Document 객체로 반환합니다.
        """
        pass
