from enum import StrEnum


class SourceType(StrEnum):
    yandex_direct = "yandex_direct"
    vk_ads = "vk_ads"
    yandex_business = "yandex_business"
    maps = "maps"
    two_gis = "2gis"
    seo = "seo"
    offline = "offline"
    referral = "referral"


class LeadStatus(StrEnum):
    new = "new"
    bot_qualified = "bot_qualified"
    in_progress = "in_progress"
    won = "won"
    lost = "lost"


class MatterType(StrEnum):
    arbitration = "arbitration"
    bankruptcy = "bankruptcy"
    family = "family"
    real_estate = "real_estate"
    debt_collection = "debt_collection"
    corporate = "corporate"
    unknown = "unknown"
