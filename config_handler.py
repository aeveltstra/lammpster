"""
# Reads a configuration file, returns parts of it.
#
# Copyright OmegaJunior Consultancy
# Since 2021-10-11
# Version 2.23.420.2300
#
"""

from configparser import ConfigParser, NoOptionError
from typing import Union, Optional


def read_config() -> ConfigParser:
    """
    Creates a ConfigParser instance and reads the configuration file
    named '.config' into it. See the README.md for its expected contents.

    Returns
    -------
    The loaded configuration.

    Exceptions
    ----------
    IOException in case no file was found by the name '.config'.
    """

    config = ConfigParser()
    config.read("./.config")
    return config


def maybe_get_config_entry(
    config: ConfigParser,
    section_name: str,
    entry_name: str,
    default: Optional[str] = None,
) -> Union[str, None]:
    """
    Hopes to retrieve a value from the configuration file, identified
    by the section name and entry name. If no such entry was found,
    the default value is returned.
    """

    result = None

    try:
        result = config.get(section_name, entry_name)

    except (KeyError, NoOptionError):
        if default:
            msg = (
                f"Info: found no entry {entry_name} in configuration "
                f"section {section_name}. Defaulting to {default}."
            )
            print(msg)
            result = default
        else:
            msg = (
                f"Warning: found no entry {entry_name} in configuration "
                f"section {section_name}. No default was provided."
            )
            print(msg)
            result = None

    return result


def maybe_get_config_section_items(
    config: ConfigParser, section_name: str, default: Optional[dict] = None
) -> Union[dict, None]:
    """
    Reads items from sections of the configuration file and returns them
    as a dict. Used for instance, to turn the listing of channels into
    an enumeration.

    Parameters
    ----------
    - config: ConfigParser, required
        The thing that can parse the configuration file.
    - section_name: str, required
        Identifies which section of the configuration file to read.
    - default: dict, optional
        Something to return in case the section name or entire
        configuration file cannot be found.

    Returns
    -------
    A dict containing the keys and values of a configuration section.

    """

    result = None

    try:
        result = config.items(section_name)
        return dict(result)

    except (KeyError, NoOptionError):
        if default:
            msg = (
                f"Info: found no configuration section {section_name}."
                f" Defaulting to {default}."
            )
            print(msg)
            result = default
        else:
            msg = (
                f"Warning: found no configuration section {section_name}."
                " No default was provided."
            )
            print(msg)
            result = None

    return result
