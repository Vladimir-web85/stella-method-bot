from datetime import datetime

MASTER_NUMBERS = {11, 22, 33}

MEANINGS = {
    1: "Тема инициативы и самостоятельности. Вопрос: где тебе хочется проявить больше инициативы?",
    2: "Тема сотрудничества и чувствительности. Вопрос: как учитывать других и при этом сохранять свои границы?",
    3: "Тема творчества и выражения. Вопрос: каким способом тебе легче всего делиться своими идеями?",
    4: "Тема структуры и устойчивости. Вопрос: какая небольшая привычка даст тебе больше опоры?",
    5: "Тема перемен и исследования. Вопрос: как сочетать свободу с ответственностью?",
    6: "Тема заботы и ответственности. Вопрос: как заботиться о других, не забывая о собственных потребностях?",
    7: "Тема исследования и внутреннего поиска. Вопрос: что тебе хочется понять глубже?",
    8: "Тема организации и реализации. Вопрос: какая цель сейчас заслуживает твоего внимания?",
    9: "Тема сострадания и завершения. Вопрос: что ты хотел(а) бы завершить или отпустить?",
    11: "В некоторых нумерологических традициях 11 считают мастер-числом, связанным с интуицией и вдохновением. Вопрос: как отличать интуитивное ощущение от проверяемых фактов?",
    22: "В некоторых нумерологических традициях 22 считают мастер-числом, связанным с воплощением замыслов. Вопрос: какой большой план можно разбить на реальные шаги?",
    33: "В некоторых нумерологических традициях 33 связывают со служением и заботой. Вопрос: как помогать другим, сохраняя собственные силы?",
}

def life_path_number(date_text: str) -> int:
    """Calculate a common numerology life-path number from DD.MM.YYYY.

    This project uses a documented digit-sum convention and preserves 11, 22, 33.
    Numerology schools vary; this is a convention, not an empirically validated measure.
    """
    try:
        birth_date = datetime.strptime(date_text, "%d.%m.%Y")
    except ValueError as exc:
        raise ValueError("Expected date in DD.MM.YYYY format") from exc

    if birth_date.date() > datetime.now().date():
        raise ValueError("Birth date cannot be in the future")

    total = sum(int(char) for char in birth_date.strftime("%d%m%Y"))
    while total > 9 and total not in MASTER_NUMBERS:
        total = sum(int(char) for char in str(total))
    if total not in set(range(1, 10)) | MASTER_NUMBERS:
        raise ValueError("Unexpected calculated number")
    return total

def interpretation(number: int) -> str:
    try:
        return MEANINGS[number]
    except KeyError as exc:
        raise ValueError("Unsupported numerology number") from exc
