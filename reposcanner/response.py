import abc
import six
from enum import Enum


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
            By default this is None.
        """
        self._status = status
        self._message = message
        self._attachments = attachments

    def hasMessage(self):
        return self._message is not None

    def getMessage(self):
        return self._message

    def hasAttachments(self):
        return self._attachments is not None

    def getAttachments(self):
        return self._attachments

    def wasSuccessful(self):
        if self._status == ResponseStatus.SUCCESS:
            return True
        else:
            return False