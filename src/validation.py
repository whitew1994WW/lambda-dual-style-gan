from typing import Dict, Any

DEFAULT_INTRINSIC_STYLE_WEIGHT = 0.6
DEFAULT_EXTRINSIC_STYLE_WEIGHT = 0.4
DEFAULT_STYLE_VARIANT = 1

valid_styles = {
    "cartoon",
    "caricature",
    "arcane",
    "comic",
    "pixar",
    "slamdunk",
}


class UserPayload:
    def __init__(
        self,
        input_image: str,
        intrinsic_style_weight: int,
        extrinsic_style_weight: int,
        style: str,
        style_variant: str,
    ) -> None:
        self.input_image = input_image
        self.intrinsic_style_weight = intrinsic_style_weight
        self.extrinsic_style_weight = extrinsic_style_weight
        self.style = style
        self.style_variant = style_variant


class UserPayloadException(Exception):
    pass


def is_numeric(num: Any) -> bool:
    """Is num numeric

    :param num: Value to test
    :return: bool
    """
    return isinstance(num, float) or isinstance(num, int)


def validate_user_payload(payload: Dict[str, Any]) -> UserPayload:
    """Create UserPayload or throw

    {
        "inputImage": <string>,
        "style": <string>,
        "intrinsicStyleWeight": <number>,
        "extrinsicStyleWeight": <number>,
        "styleVariant": <number> | <None>,
    }

    :param payload: Raw json dictionary
    :return: UserPayload
    """
    payload_errors = []
    input_image = payload.get("inputImage", None)
    if not isinstance(input_image, str):
        payload_errors.append(
            "Invalid input 'inputImage' must be defined and of type string"
        )

    intrinsic_style_weight = payload.get(
        "intrinsicStyleWeight", DEFAULT_INTRINSIC_STYLE_WEIGHT
    )
    intrinsic_is_numeric = is_numeric(intrinsic_style_weight)

    if not intrinsic_is_numeric:
        payload_errors.append(
            "Invalid input 'intrinsicStyleWeight' must be defined and of type float or int"
        )
    elif intrinsic_style_weight <= 0 or intrinsic_style_weight >= 1:
        payload_errors.append(
            "Invalid input 'intrinsicStyleWeight' must be between 0 and 1"
        )

    extrinsic_style_weight = payload.get(
        "extrinsicStyleWeight", DEFAULT_EXTRINSIC_STYLE_WEIGHT
    )
    extrinsic_is_numeric = is_numeric(extrinsic_style_weight)
    if not extrinsic_is_numeric:
        payload_errors.append(
            "Invalid input 'extrinsic_style_weight' must be defined and of type float or int"
        )
    elif extrinsic_style_weight <= 0 or extrinsic_style_weight >= 1:
        payload_errors.append(
            "Invalid input 'extrinsicStyleWeight' must be between 0 and 1"
        )

    style = payload.get("style", None)
    if not isinstance(style, str):
        payload_errors.append(
            "Invalid input 'style' must be defined and of type string"
        )

    if style not in valid_styles:
        payload_errors.append(
            """Incorrect style. It must be one of ["cartoon", "caricature", "arcane", "comic", "pixar", "slamdunk"]"""
        )

    style_variant = payload.get("styleVariant", DEFAULT_STYLE_VARIANT)
    if not isinstance(style_variant, int):
        payload_errors.append("Invalid input 'styleVariant' must be of type int")

    if len(payload_errors) > 0:
        raise UserPayloadException("\n".join(payload_errors))

    return UserPayload(
        input_image=input_image,
        intrinsic_style_weight=intrinsic_style_weight,
        extrinsic_style_weight=extrinsic_style_weight,
        style=style,
        style_variant=style_variant,
    )
