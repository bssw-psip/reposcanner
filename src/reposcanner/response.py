# This future import allows us to reference a class in type annotations before it is declared.
from __future__ import annotations
import abc
from enum import Enum
import collections
from typing import Optional, List, Iterable, Union, Any
from reposcanner.data import ReposcannerDataEntity


AttachmentType = Union[ReposcannerDataEntity, str, Exception]


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

    def createSuccessResponse(
            self,
            message: Optional[str] = None,
            attachments: Union[None, AttachmentType, Iterable[AttachmentType]] = None,
    ) -> ResponseModel:
        return ResponseModel(status=ResponseStatus.SUCCESS,
                             message=message,
                             attachments=attachments)

    def createFailureResponse(
            self,
            message: Optional[str] = None,
            attachments: Union[None, AttachmentType, Iterable[AttachmentType]] = None,
    ) -> ResponseModel:
        return ResponseModel(status=ResponseStatus.FAILURE,
                             message=message,
                             attachments=attachments)


class ResponseModel:
    """
    The base class for all request models. Any outputs that Grover provides must be stored as a response model as
    opposed to providing entities directly. This allows the internal representation of our data to vary independently
    of how that data is presented to a client.
    """

    def __init__(
            self,
            status: ResponseStatus,
            message: Optional[str] = None,
            attachments: Union[None, AttachmentType, Iterable[AttachmentType]] = None,
    ) -> None:
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
        self._attachments: List[AttachmentType] = []

        def isIterable(obj: Any) -> bool:
            try:
                iter(obj)
                return True
            except TypeError as e:
                return False
        if attachments is not None:
            if isinstance(attachments, Iterable) and isIterable(attachments) and not isinstance(attachments, str):
                for attachment in attachments:
                    self._attachments.append(attachment)
            elif isinstance(attachments, (str, ReposcannerDataEntity, Exception)):
                self._attachments.append(attachments)
            else:
                raise TypeError("Invalid attachment type {attachmentType}".format(
                    attachmentType=str(type(attachments))))


    def hasMessage(self) -> bool:
        return self._message is not None

    def getMessage(self) -> Optional[str]:
        return self._message

    def hasAttachments(self) -> bool:
        return len(self._attachments) != 0

    def getAttachments(self) -> List[AttachmentType]:
        return self._attachments

    def addAttachment(self, attachment: AttachmentType) -> None:
        self._attachments.append(attachment)

    def wasSuccessful(self) -> bool:
        if self._status == ResponseStatus.SUCCESS:
            return True
        else:
            return False
