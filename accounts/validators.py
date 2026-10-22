import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

LICENSE_LETTERS = "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"
LICENSE_PATTERN = re.compile(rf"^([{LICENSE_LETTERS}]{{2,3}})(\d{{6}})$")


def normalize_phone(value):
    digits = re.sub(r"\D", "", value or "")
    if len(digits) == 12 and digits.startswith("380"):
        return f"+{digits}"
    if len(digits) == 10 and digits.startswith("0"):
        return f"+38{digits}"
    raise ValidationError(_("Введіть український номер телефону, наприклад +380671234567."))


def normalize_rnokpp(value):
    digits = re.sub(r"\D", "", value or "")
    if not re.fullmatch(r"\d{10}", digits):
        raise ValidationError(_("РНОКПП має містити 10 цифр."))
    return digits


def normalize_driver_license(value):
    compact = re.sub(r"\s+", "", value or "").upper()
    match = LICENSE_PATTERN.fullmatch(compact)
    if not match:
        raise ValidationError(
            _(
                "Введіть серію та номер: ВХА 123456 для нового пластикового посвідчення "
                "або КІА 654321 для старого ламінованого."
            )
        )
    return f"{match.group(1)} {match.group(2)}"
