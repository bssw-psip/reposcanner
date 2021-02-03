import abc
from enum import Enum
import collections


class ResponseStatus(Enum):
    """
    The status flag enum for ResponseModel objects. A response can either succeed or fail.
    """
    SUCCESS = 1
    FAILURE = 2


class ResponseFactory:
    """
    A factory for churning out response model objects. Classes should use this factory to construct responses.
    """
    def createSuccessResponse(self, message=None, attachments=None):
        return ResponseModel(status=ResponseStatus.SUCCESS,
                             message=message,
                             attachments=attachments)

    def createFailureResponse(self, message=None, attachments=None):
        return ResponseModel(status=ResponseStatus.FAILURE,
                             message=message,
                             attachments=attachments)


class ResponseModel:
    """
    The base class for all request models. Any outputs that Grover provides must be stored as a response model as
    opposed to providing entities directly. This allows the internal representation of our data to vary independently
    of how that data is presented to a client.
    """
    def __init__(self, status, message=None, attachments=None):
        """
        Parameters
        ----------
        status:
            A Status enum object that describes the outcome of a request.
        message:
            A string describing the outcome of the request.
            By default this is None.
        attachments:
            A field for storing output data that was the result of a request (if there is any to deliver).
            By default this is None. Callers are expected to pass either an iterable containing results or
            a single object.
        """
        self._status = status
        self._message = message
        self._attachments = []
        def isIterable(obj):
                try:
                        iter(obj)
                        return True
                except TypeError as e:
                        return False
        if attachments is not None:
                if isIterable(attachments) and not isinstance(attachments,str):
                        for attachment in attachments:
                                self._attachments.append(attachment)
                else:
                        self._attachments.append(attachment)

    def hasMessage(self):
        return self._message is not None

    def getMessage(self):
        return self._message

    def hasAttachments(self):
        return len(self._attachments) != 0

    def getAttachments(self):
        return self._attachments
        
    def addAttachment(self,attachment):
        self._attachments.append(attachment)
        
    def wasSuccessful(self):
        if self._status == ResponseStatus.SUCCESS:
            return True
        else:
            return False