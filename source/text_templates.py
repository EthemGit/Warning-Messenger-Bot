import json
import os

from enum_types import Button, ReplaceableAnswer, Answers, WarningSeverity, BotUsageHelp

file_path = "data/text_templates.json"

if not os.path.exists(file_path):
    raise FileNotFoundError("text templates file not found in given path")


def _read_file(path: str):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_button_name(button: Button) -> str:
    """
    Returns a string containing the button name of the desired button.

    Arguments:
        button: a Button to determine what button name you want to be returned

    Returns:
        A String containing the desired button name.
    """

    data = _read_file(file_path)

    for topic in data:
        if topic['topic'] == "buttons":
            return topic['names'][button.value]


def get_answers(answer: Answers) -> str:
    """
    Returns a string containing the desired answer text.

    Arguments:
        answer: an Answers to determine what answer text you want to be returned

    Returns:
        A String containing the desired answer text.
    """

    data = _read_file(file_path)

    for topic in data:
        if topic['topic'] == "answers":
            return topic['text'][answer.value]


def get_replaceable_answer(r_answer: ReplaceableAnswer) -> str:
    """
    Only applicable for text with replaceable elements. Returned string will
    contain the following form: %to_be_replaced.
    Takes a value of the Enum and returns a string with formatted info from a JSON file.

    Arguments:
        r_answer: a ReplaceableAnswer to determine what information you want to be returned

    Returns:
        A String containing the desired information.
    """
    result = ""

    data = _read_file(file_path)

    for topic in data:
        if topic['topic'] == "replaceable_answers":
            for answer in topic['all_answers']:
                if answer['topic'] == r_answer.value:
                    for information in answer['information']:
                        result += information['text'] + "\n"

    return result


def _get_complex_answer_dict(name: str) -> dict:
    """
    Returns a dictionary with the format for the given parameter

    Arguments:
        name: string with the name to search for in the json

    Returns:
        a dictionary with the format requested with name
    """
    data = _read_file(file_path)

    for topic in data:
        if topic['topic'] == "complex_answers":
            return topic["all_answers"][name]


# fill in the replaceable answer ---------------------------------------------------------------------------------------


def get_greeting_message(username: str) -> str:
    """
    This method will replace the placeholder (%name) with the given parameters from the greeting in the json

    Returns:
        Message that can be sent to the user with the parameter in the message
    """
    message = get_replaceable_answer(ReplaceableAnswer.GREETING)
    message = message.replace("%username", username)
    return message


def get_general_warning_message(event: str, headline: str, description: str, severity: str,
                                warning_type: str, start_date: str, date_expires: str, status: str, link: str) -> str:
    """
    This method will replace the placeholder (%name) with the given parameters from the message for general warnings in
    the json

    Returns:
        Message that can be sent to the user with the parameter in the message
    """

    placeholder = "-"

    message = get_replaceable_answer(ReplaceableAnswer.GENERAL_WARNING)
    if event is not None:
        message = message.replace("%event", event)
    else:
        message = message.replace("%event", placeholder)
    if headline is not None:
        message = message.replace("%headline", headline)
    else:
        message = message.replace("%headline", placeholder)
    if description is not None:
        message = message.replace("%description", description)
    else:
        message = message.replace("%description", placeholder)
    if severity is not None:
        message = message.replace("%severity", severity)
    else:
        message = message.replace("%severity", placeholder)
    if warning_type is not None:
        message = message.replace("%type", warning_type)
    else:
        message = message.replace("%type", placeholder)
    if start_date is not None:
        message = message.replace("%start_date", start_date)
    else:
        message = message.replace("%start_date", placeholder)
    if date_expires is not None:
        message = message.replace("%date_expires", date_expires)
    else:
        message = message.replace("%date_expires", placeholder)
    if status is not None:
        message = message.replace("%status", status)
    else:
        message = message.replace("%status", placeholder)
    if link is not None:
        message = message.replace("%link", link)
    else:
        message = message.replace("%link", placeholder)
    return message


def get_covid_info_message(location: str, infektionsgefahr_stufe: str, sieben_tage_inzidenz_bundesland: str,
                           sieben_tage_inzidenz_kreis: str, allgemeine_hinweise: str) -> str:
    """
    This method will replace the placeholder (%name) with the given parameters from the message for covid infos in
    the json

    Returns:
        Message that can be sent to the user with the parameter in the message
    """
    message = get_replaceable_answer(ReplaceableAnswer.COVID_INFO)
    message = message.replace("%location", location)
    message = message.replace("%infektionsgefahr_stufe", infektionsgefahr_stufe)
    message = message.replace("%sieben_tage_inzidenz_bundesland", sieben_tage_inzidenz_bundesland)
    message = message.replace("%sieben_tage_inzidenz_kreis", sieben_tage_inzidenz_kreis)
    message = message.replace("%allgemeine_hinweise", allgemeine_hinweise)
    return message


def get_covid_rules_message(location: str, vaccine_info: str, contact_terms: str, school_kita_rules: str,
                            hospital_rules: str, travelling_rules: str, fines: str) -> str:
    """
    This method will replace the placeholder (%name) with the given parameters from the message for covid rules in
    the json

    Returns:
        Message that can be sent to the user with the parameter in the message
    """
    replacer = get_answers(Answers.UNKNOWN)
    if location is None:
        location = replacer
    if vaccine_info is None:
        vaccine_info = replacer
    if contact_terms is None:
        contact_terms = replacer
    if school_kita_rules is None:
        school_kita_rules = replacer
    if hospital_rules is None:
        hospital_rules = replacer
    if travelling_rules is None:
        travelling_rules = replacer
    if fines is None:
        fines = replacer
    message = get_replaceable_answer(ReplaceableAnswer.COVID_RULES)
    message = message.replace("%location", location)
    message = message.replace("%vaccine_info", vaccine_info)
    message = message.replace("%contact_terms", contact_terms)
    message = message.replace("%school_kita_rules", school_kita_rules)
    message = message.replace("%hospital_rules", hospital_rules)
    message = message.replace("%travelling_rules", travelling_rules)
    message = message.replace("%fines", fines)
    return message


def get_add_subscription_message() -> str:
    """
    This method will return the message the bot will send when the user wants to add a subscription
    (pressed add subscription button)

    Returns:
        message from the json
    """
    message = get_replaceable_answer(ReplaceableAnswer.ADD_SUBSCRIPTION)
    message = message.replace("%location_button", get_button_name(Button.SEND_LOCATION))
    return message


def get_adding_subscription_level_message(location: str, warning: str) -> str:
    """
    This method will return the message the bot will send when the user is in the process of adding a subscription
    (needs to add the warning level)

    Arguments:
        location: a String with the location name
        warning: a String with the warning name

    Returns:
        message from the json with the parameters inserted
    """
    message = get_replaceable_answer(ReplaceableAnswer.ADDING_SUBSCRIPTION_LEVEL)
    message = message.replace("%location", location)
    message = message.replace("%warning", warning)
    return message


def get_adding_subscription_warning_message(location: str) -> str:
    """
    This method will return the message the bot will send when the user is in the process of adding a subscription
    (needs to add the warning)

    Arguments:
        location: a String with the location name

    Returns:
        message from the json with the parameters inserted
    """
    message = get_replaceable_answer(ReplaceableAnswer.ADDING_SUBSCRIPTION_WARNING)
    message = message.replace("%location", location)
    return message


def get_delete_subscription_message(location: str, warning: str) -> str:
    """
    This method will return the message the bot will send when the user deleted a Subscription

    Arguments:
        location: a String with the location name
        warning: a String with the warning name

    Returns:
        message from the json with the parameters inserted
    """
    message = get_replaceable_answer(ReplaceableAnswer.DELETE_SUBSCRIPTION)
    message = message.replace("%location", location)
    message = message.replace("%warning", warning)
    return message


def get_no_current_warnings_message(warning_category: str) -> str:
    """
    This method will replace the placeholder (%name) with the given parameters from the greeting in the json

    Returns:
        Message that can be sent to the user with the parameter in the message
    """
    message = get_replaceable_answer(ReplaceableAnswer.NO_CURRENT_WARNINGS)
    message = message.replace("%category", warning_category)
    return message


# complex answers ------------------------------------------------------------------------------------------------------


def get_show_subscriptions_for_one_location_messsage(location: str, warnings: list[str], levels: list[str]) -> str:
    """
    This method returns the string for showing one subscription (example: Darmstadt -> warnings + levels).
    The returned value can later be combined to one message in get_show_subscriptions_message

    ATTENTION:
    warnings and levels must be of same length -> warnings[0] has the level levels[0]

    Arguments:
        location: a string with the location name
        warnings: a list of strings with the warning names for that location
        levels: a list of string with the warning level names for the different warnings

    Returns:
        string with text for all subscriptions of one location
    """
    dic = _get_complex_answer_dict("show_subscriptions")
    message = dic["location"]
    message = message.replace("%location", location)
    for (warning, level) in zip(warnings, levels):
        single_warning = dic["warning"]
        single_warning = single_warning.replace("%warning", warning)
        single_warning = single_warning.replace("%level", level)
        message = message + "\n" + single_warning
    return message


def get_show_subscriptions_message(subscriptions: list[str], only_show: bool = False) -> str:
    """
    This method will build the show subscription message.

    Arguments:
        subscriptions: list of strings given from multiple calls of get_show_subscriptions_for_one_location_messsage
        only_show: a boolean when True then the user only want to see subscriptions and has not recently added one

    Returns:
        The subscriptions combined with the headline for showing subscriptions
    """
    dic = _get_complex_answer_dict("show_subscriptions")
    message = dic["headline"]
    if not only_show:
        message = dic["headline_after_insertion"] + "\n" + message
    for subscription in subscriptions:
        message = message + "\n" + subscription
    return message


def get_delete_subscriptions_for_one_location_messsage(location: str, warnings: list[str], levels: list[str],
                                                       corresponding_button_names: list[str]) -> str:
    """
    This method returns the string for deleting one subscription (example: Darmstadt -> warnings + levels).
    The returned value can later be combined to one message in get_delete_subscriptions_message

    ATTENTION:
    warnings, levels and corresponding_button_names must be of same length
    -> warnings[0] has the level levels[0] and will be deleted when pressing button corresponding_button_names[0]

    Arguments:
        location: a string with the location name
        warnings: a list of strings with the warning names for that location
        levels: a list of string with the warning level names for the different warnings
        corresponding_button_names: a list of string with the button name for deleting that subscription

    Returns:
        string with text for all subscriptions of one location and an information to the corresponding button name
    """
    dic = _get_complex_answer_dict("delete_subscription")
    message = dic["location"]
    message = message.replace("%location", location)
    for (warning, level, button) in zip(warnings, levels, corresponding_button_names):
        single_warning = dic["warning"]
        single_warning = single_warning.replace("%warning", warning)
        single_warning = single_warning.replace("%level", level)
        single_warning = single_warning.replace("%button_name", button)
        message = message + "\n" + single_warning
    return message


def get_delete_subscriptions_message(subscriptions: list[str]) -> str:
    """
    This method will build the delete-subscription message.

    Arguments:
        subscriptions: list of strings given from multiple calls of get_delete_subscriptions_for_one_location_messsage

    Returns:
        string with the subscriptions combined with the headline for deleting subscriptions
    """
    dic = _get_complex_answer_dict("delete_subscription")
    message = dic["headline"]
    for subscription in subscriptions:
        message = message + "\n" + subscription
    end_text = dic["end"]
    if end_text != "":
        message = message + "\n" + end_text
    return message


def get_select_location_for_one_location_messsage(district_name: str, place_name: str, postal_code: str,
                                                  corresponding_button_name: str) -> str:
    """
    This method will return the text for one location suggestion from place_converter.
    The returned value can later be combined to one message in get_select_location_message

    Arguments:
        district_name: string with the name of the suggested district
        place_name: string with the name of the suggested place (can be None)
        postal_code: string with the postal code of the suggested location
        corresponding_button_name: string with the name of the button that will represent this suggestion

    Returns:
        string with the text for one suggestion
    """
    dic = _get_complex_answer_dict("select_location")
    if place_name is None or place_name == district_name:
        message = dic["text_without_place"]
        message = message.replace("%district_name", district_name)
        message = message.replace("%button_name", corresponding_button_name)
        message = message.replace("%postal_code", postal_code)
        return message
    message = dic["text"]
    message = message.replace("%place_name", place_name)
    message = message.replace("%district_name", district_name)
    message = message.replace("%button_name", corresponding_button_name)
    message = message.replace("%postal_code", postal_code)
    return message


def get_select_location_message(locations: list[str]) -> str:
    """
    This method will combine multiple suggestions to one message.

    Arguments:
        locations: list of strings with the suggestions
            (suggestions come from the method get_select_location_for_one_location_messsage)

    Returns:
        string with the combined suggestions and a headline (and ending)
    """
    dic = _get_complex_answer_dict("select_location")
    message = dic["headline"]
    for location in locations:
        message = message + "\n" + location
    end_text = dic["end"]
    if end_text != "":
        message = message + "\n" + end_text
    return message


def get_changed_auto_covid_updates_message(interval: str) -> str:
    """
    This method will return the message that is sent to the user when auto covid updates are changed.

    Arguments:
        interval: string with the new interval

    Returns:
        string with the message informing the user what the new interval of auto covid updates is
    """
    message = get_replaceable_answer(ReplaceableAnswer.CHANGED_AUTO_COVID_UPDATES)
    message = message.replace("%interval", interval)
    return message


def get_quickly_add_to_subscriptions_message(location_name: str, warning_name: str) -> str:
    """
    This method will return the message that is sent to the user when they get asked if they want to add a warning to
    subscriptions

    Arguments:
        location_name: string with the location name
        warning_name: string with the warning name

    Returns:
        string with the message asking the user if they want to add the warning to their subscriptions
    """
    message = get_replaceable_answer(ReplaceableAnswer.QUICKLY_ADD_TO_SUBSCRIPTIONS)
    message = message.replace("%warning", warning_name)
    message = message.replace("%location", location_name)
    return message


def get_show_favorites_message(favorites: list[str]) -> str:
    """
    This method will build the message containing the favorites that the user has set

    Arguments:
        favorites: list of strings representing the favorites the user has set

    Returns:
        string with the message showing the user all favorites
    """
    dic = _get_complex_answer_dict("favorites")
    message = dic["headline"]
    for favorite in favorites:
        message = message + "\n" + dic["favorite"].replace("%f", favorite)
    return message


def get_set_default_level_message(level: WarningSeverity) -> str:
    """
    This method will build the message to inform the user what default level they have now

    Arguments:
        level: WarningSeverity representing the new default level

    Returns:
        string with the message showing the default level the user has now
    """
    dic = _get_complex_answer_dict("set_default_level")
    if level == WarningSeverity.MANUAL:
        message = dic["manual"]
    else:
        message = dic["other"]
        message = message.replace("%level", get_button_name(Button[level.name]))
    return message


def get_faq_message(questions: list[str], answers: list[str]) -> str:
    """
    This method will create the faq answer with the given questions and answers
    IMPORTANT: question[0] gets answered by answer[0] and so on

    Args:
        questions: list with the questions as string
        answers: list with the answers as strings

    Returns:
        string with the faq
    """
    dic = _get_complex_answer_dict("faq")

    message = dic["headline"]
    for (question, answer) in zip(questions, answers):
        one_faq = dic["question_format"]
        one_faq = one_faq.replace("%question", question)
        one_faq = one_faq.replace("%answer", answer)
        message = message + "\n" + one_faq
    message = message + "\n" + dic["end"]
    return message


def get_faq_message_from_templates() -> str:
    """
    This method will create the faq answer with the questions and answers from the text_templates.json

    Returns:
        string with the faq
    """
    dic = _get_complex_answer_dict("faq")
    questions = dic["faq_questions"].keys()
    answers = dic["faq_questions"].values()

    message = dic["headline"]
    for (question, answer) in zip(questions, answers):
        one_faq = dic["question_format"]
        one_faq = one_faq.replace("%question", question)
        one_faq = one_faq.replace("%answer", answer)
        message = message + "\n" + one_faq
    message = message + "\n" + dic["end"]
    return message


def get_help_message(help_for: BotUsageHelp) -> str:
    """
    This method will create the requested help answer

    Args:
        help_for: BotUsageHelp enum which tells this method what help to return

    Returns:
        string with the requested help message
    """
    dic = _get_complex_answer_dict("bot_usage")

    if help_for == BotUsageHelp.EVERYTHING:
        message = dic["headline"]
        list_help = list(BotUsageHelp)
        list_help.remove(BotUsageHelp.EVERYTHING)
        for help_in in list_help:
            one_help = "\n\n" + dic[help_in.value + "_navigation"]
            one_help = one_help + "\n" + dic[help_in.value]
            message = message + one_help
    else:
        message = dic[help_for.value]
    message = message + "\n" + dic["general"]
    return message


def get_display_name_for_location(district_name: str, place_name: str, postal_code: str) -> str:
    """
    This method is for getting the display name of a location

    Args:
        district_name: district name
        place_name: place name
        postal_code: postal code

    Returns:
        the name that should be displayed for the user
    """
    if place_name == district_name:
        return district_name + " (" + postal_code + ")"
    return place_name + " in " + district_name + " (" + postal_code + ")"
