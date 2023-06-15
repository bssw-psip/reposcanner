import pytest
import reposcanner.response as responseapi


def test_ResponseModel_CanConstructSuccessfulResponseByFactory() -> None:
    message = None
    attachments = None
    responseFactory = responseapi.ResponseFactory()
    successfulResponse = responseFactory.createSuccessResponse(
        message, attachments)
    assert (successfulResponse.wasSuccessful() is True)


def test_ResponseModel_CanConstructFailureResponseByFactory() -> None:
    message = None
    attachments = None
    responseFactory = responseapi.ResponseFactory()
    successfulResponse = responseFactory.createFailureResponse(
        message, attachments)
    assert (successfulResponse.wasSuccessful() is False)


def test_ResponseModel_HasNoMessageByDefault() -> None:
    status = responseapi.ResponseStatus.SUCCESS
    response = responseapi.ResponseModel(status)
    assert (response.hasMessage() is False)
    assert (response.getMessage() is None)


def test_ResponseModel_HasNoAttachmentsByDefault() -> None:
    status = responseapi.ResponseStatus.SUCCESS
    response = responseapi.ResponseModel(status)
    assert (response.hasAttachments() is False)
    assert (len(response.getAttachments()) == 0)


def test_ResponseModel_CanStoreAttachments() -> None:
    status = responseapi.ResponseStatus.SUCCESS
    attachments = ["dataA", "dataB"]
    response = responseapi.ResponseModel(status,
                                         message=None,
                                         attachments=attachments)
    assert (response.hasAttachments() is True)
    assert (len(response.getAttachments()) == 2)


def test_ResponseModel_CanStoreMessage() -> None:
    status = responseapi.ResponseStatus.SUCCESS
    message = "details listed here"
    response = responseapi.ResponseModel(status,
                                         message=message,
                                         attachments=None)
    assert (response.hasMessage() is True)
    assert (response.getMessage() == message)
