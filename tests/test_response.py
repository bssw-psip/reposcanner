import pytest
import reposcanner.response as responseapi


def test_ResponseModel_CanConstructSuccessfulResponseByFactory():
    message = None
    attachments = None
    responseFactory = responseapi.ResponseFactory()
    successfulResponse = responseFactory.createSuccessResponse(
        message, attachments)
    assert (successfulResponse.wasSuccessful() is True)


def test_ResponseModel_CanConstructFailureResponseByFactory():
    message = None
    attachments = None
    responseFactory = responseapi.ResponseFactory()
    successfulResponse = responseFactory.createFailureResponse(
        message, attachments)
    assert (successfulResponse.wasSuccessful() is False)


def test_ResponseModel_HasNoMessageByDefault():
    status = None
    response = responseapi.ResponseModel(status)
    assert (response.hasMessage() is False)
    assert (response.getMessage() is None)


def test_ResponseModel_HasNoAttachmentsByDefault():
    status = None
    response = responseapi.ResponseModel(status)
    assert (response.hasAttachments() is False)
    assert (response.getAttachments() is None)


def test_ResponseModel_CanStoreAttachments():
    status = None
    attachments = ["dataA", "dataB"]
    response = responseapi.ResponseModel(status,
                                         message=None,
                                         attachments=attachments)
    assert (response.hasAttachments() is True)
    assert (len(response.getAttachments()) == 2)


def test_ResponseModel_CanStoreMessage():
    status = None
    message = "details listed here"
    response = responseapi.ResponseModel(status,
                                         message=message,
                                         attachments=None)
    assert (response.hasMessage() is True)
    assert (response.getMessage() == message)