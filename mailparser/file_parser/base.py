from abc import ABCMeta, abstractmethod

class AbstractParser(metaclass=ABCMeta): 

    @abstractmethod
    def __call__(self): 
        return

    def __str__(self): 
        return self.__class__.__name__