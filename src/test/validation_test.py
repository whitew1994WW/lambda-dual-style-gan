import pytest
from src.validation import UserPayloadException, validate_user_payload, UserPayload


def test_should_throw_invalid_image():
    raw_payload = {
        "inputImage": None,
        "style": "cartoon",
        "intrinsicStyleWeight": 0.5,
        "extrinsicStyleWeight": 0.5,
        "styleVariant": 2,
    }

    with pytest.raises(UserPayloadException):
        validate_user_payload(raw_payload)


def test_should_throw_invalid_intrinsic_weight():
    raw_payload = {
        "inputImage": "image",
        "style": "cartoon",
        "intrinsicStyleWeight": None,
        "extrinsicStyleWeight": 0.5,
        "styleVariant": 2,
    }

    with pytest.raises(UserPayloadException):
        validate_user_payload(raw_payload)


def test_should_throw_invalid_intrinsic_above_one():
    raw_payload = {
        "inputImage": "image",
        "style": "cartoon",
        "intrinsicStyleWeight": 2,
        "extrinsicStyleWeight": 0.2,
        "styleVariant": 2,
    }

    with pytest.raises(UserPayloadException):
        validate_user_payload(raw_payload)


def test_should_throw_invalid_extrinsic_below_zero():
    raw_payload = {
        "inputImage": "image",
        "style": "cartoon",
        "intrinsicStyleWeight": -1,
        "extrinsicStyleWeight": 0.2,
        "styleVariant": 2,
    }

    with pytest.raises(UserPayloadException):
        validate_user_payload(raw_payload)


def test_should_throw_invalid_extrinsic_weight():
    raw_payload = {
        "inputImage": "image",
        "style": "cartoon",
        "intrinsicStyleWeight": 0.5,
        "extrinsicStyleWeight": None,
        "styleVariant": 2,
    }

    with pytest.raises(UserPayloadException):
        validate_user_payload(raw_payload)


def test_should_throw_invalid_extrinsic_above_one():
    raw_payload = {
        "inputImage": "image",
        "style": "cartoon",
        "intrinsicStyleWeight": 0.5,
        "extrinsicStyleWeight": 2,
        "styleVariant": 2,
    }

    with pytest.raises(UserPayloadException):
        validate_user_payload(raw_payload)


def test_should_throw_invalid_extrinsic_below_zero():
    raw_payload = {
        "inputImage": "image",
        "style": "cartoon",
        "intrinsicStyleWeight": 0.5,
        "extrinsicStyleWeight": -1,
        "styleVariant": 2,
    }

    with pytest.raises(UserPayloadException):
        validate_user_payload(raw_payload)


def test_should_throw_invalid_style():
    raw_payload = {
        "inputImage": "image",
        "style": None,
        "intrinsicStyleWeight": 0.5,
        "extrinsicStyleWeight": 0.5,
        "styleVariant": 2,
    }

    with pytest.raises(UserPayloadException):
        validate_user_payload(raw_payload)


def test_should_throw_unrecognised_style():
    raw_payload = {
        "inputImage": "image",
        "style": "foobar",
        "intrinsicStyleWeight": 0.5,
        "extrinsicStyleWeight": 0.5,
        "styleVariant": 2,
    }

    with pytest.raises(UserPayloadException):
        validate_user_payload(raw_payload)


def test_should_throw_invalid_style_variant():
    raw_payload = {
        "inputImage": "image",
        "style": "foobar",
        "intrinsicStyleWeight": 0.5,
        "extrinsicStyleWeight": 0.5,
        "styleVariant": "hehehehe",
    }

    with pytest.raises(UserPayloadException):
        validate_user_payload(raw_payload)


def test_should_return_user_payload():
    raw_payload = {
        "inputImage": "image",
        "style": "cartoon",
        "intrinsicStyleWeight": 0.5,
        "extrinsicStyleWeight": 0.5,
        "styleVariant": 50,
    }

    payload = validate_user_payload(raw_payload)
    assert isinstance(payload, UserPayload)
