"""
# Extracts a profile for a specific record from the
# specified data store. Used as part of Lammpster.
#
# Copyright OmegaJunior Consultancy, LLC.
# Since 2021-10-11
# Version 2.23.929.1504
#
"""

import datetime
import json
import os
import re
from functools import partial
from string import Template
from typing import Any, Union
import config_handler


def get_current_year() -> int:
    """
    Retrieves the year number of today's date, whatever that is at the
    moment of execution.
    """
    return datetime.date.today().year


def make_clean_file_name(haystack) -> str:
    """
    Removes all letters and symbols from the haystack,
    that could damage a file system. Keeps only alphabet
    letters and numerals a-z, A-Z, 0-9, and - and _.
    """

    if not haystack:
        return ""
    return re.sub("[^-_a-zA-Z0-9]*", "", haystack)


def try_cache_profile(config, profile) -> bool:
    """
    Attempts to persist the passed-in profile in a local cache folder.
    The config file will determine whether that needs to happen, and if
    so, where.
    """

    cache_folder = config_handler.maybe_get_config_entry(
        config,
        "profile",
        "cache",
        ""
    )
    if not cache_folder:
        return False
    if not os.path.exists(cache_folder):
        os.makedirs(cache_folder)
    clean_file_name = make_clean_file_name(profile.get('case_id'))
    with open(
            f"{cache_folder}/{clean_file_name}.json",
            'w',
            encoding="utf-8"
        ) as w:
        w.write(json.dumps(profile, sort_keys=True, indent=2))
    return True


def try_read_cached_profile(
    config,
    case_id
) -> Union[dict[str, Any], None]:
    """
    Attempts to read a profile that got cached previously.
    This is used to prevent reading from an online data store
    every time.
    """

    cache_folder = config_handler.maybe_get_config_entry(
        config,
        "profile",
        "cache",
        ""
    )
    if not cache_folder:
        return None
    clean_file_name = make_clean_file_name(case_id)
    try:
        with open(
            f"{cache_folder}/{clean_file_name}.json",
            'r',
            encoding="utf-8"
        ) as r:
            return json.loads(r.read())
    except IOError as ioE:
        print(ioE)
        return None


def create(
    config,
    store,
    db_handler,
    case_row_index: int
) -> Union[dict[str, Any], None]:
    """
    Takes the cell values from a row, and turns them into a profile
    for injecting into an output template. The input fields from the 
    store and the output fields for the profile are read from the 
    config. If possible, this method also attempts to cache the profile.

    Parameters
    ----------
    - config: ConfigParser, required
        Should have the configuration file preloaded.
    - store: that which holds the profile records, required
    - db_handler: the module that handles access to the data store,
      required.
    - case_row_index: int, required
        Should be the number of that record in the store,
        that identifies of which to create a profile.
        You can find this from db_handler_sheets.find_row_index().
        The header row is 1.

    Side Effects
    ------------
    An attempt will be made to cache a successfully read profile.
    See try_cache_profile().
    """

    if not store or not case_row_index:
        return None
    get_stores_for_config = partial(
        db_handler.get_value_for_field_by_name,
        config
    )
    get_rows_for_store = partial(get_stores_for_config, store)
    get_cell_value = partial(get_rows_for_store, case_row_index)
    profile_mapping = config_handler.maybe_get_config_section_items(
        config,
        "profile_map",
        {}
    )
    profile = {}
    for a, b in profile_mapping.items():
        profile[a] = get_cell_value(b)

    try_cache_profile(config, profile)
    return profile


def apply_profile_to_template(
    profile, 
    template_name, 
    template_contents
) -> str:
    """
    Substitutes known variables in the template contents
    with values from the profile. This will fail if expected
    variables do not exist in the template contents.

    Parameters
    ----------
    - profile: dict, required
        Should be the result of create()
    - template_name: str, required
        Should be the name of the file that contains the 
        contents speficified in the template_contents argument.
        Used in error logging.
    - template_contents: str, required
        Variables in the template should be defined in the config,
        in the section profile_map.

    Returns
    -------
    str: The substitution result.
    """

    if not profile or not template_contents:
        return None

    try:
        return Template(template_contents).substitute(profile)
    except KeyError as err:
        msg = (
            "Error: failed to apply the profile to the "
            f"template in file {template_name}. "
            "Either the placeholder was not found, "
            f"or it was not given a substitute: {err}."
        )
        print(msg)
        raise
