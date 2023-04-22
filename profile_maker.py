"""
# Extracts a profile for a specific person from the
# specified data store. Used as part of Lammpster.
#
# Copyright OmegaJunior Consultancy
# Since 2021-10-11
# Version 2.23.420.2300
#
"""

import datetime
from functools import partial
from string import Template
from typing import Any, Union
import db_handler_sheets


def get_current_year() -> int:
    """
    Retrieves the year number of today's date,
    whatever that is at the moment of execution.
    """
    return datetime.date.today().year


def create(
    config,
    store,
    case_row_index: int
) -> Union[dict[str, Any], None]:
    """
    Takes the cell values from a row, and turns them into a profile
    for injecting into a poster.

    Parameters
    ----------
    - config: ConfigParser, required
        Should have the configuration file preloaded.
    - store: that which holds the profile records, required
    - case_row_id: int, required
        Should be the number of that record in the store,
        that identifies of which to create a profile.
    """

    if not store or not case_row_index:
        return None
    get_stores_for_config = partial(
        db_handler_sheets.get_value_for_field_by_name,
        config
    )
    get_rows_for_store = partial(get_stores_for_config, store)
    get_cell_value = partial(get_rows_for_store, case_row_index)
    birth_year = get_cell_value("Birth Year")
    age = None
    if birth_year:
        age = get_current_year() - int(birth_year)
    return {
        "Age": age,
        "Birth Year": birth_year,
        "Case ID": get_cell_value("Case ID"),
        "Chosen Name": get_cell_value("Chosen Name"),
        "Disappearance Circumstances": get_cell_value(
            "Disappearance Circumstances"
        ),
        "Eyes": get_cell_value("Eyes"),
        "Hair": get_cell_value("Hair"),
        "Height": get_cell_value("Height"),
        "Identifying Features": get_cell_value("Identifying Features"),
        "Image 1 Path": get_cell_value("Image Path"),
        "Image 2 Path": get_cell_value("Image Path 2"),
        "Last Seen Date": get_cell_value("Last Seen Date"),
        "Last Seen Location": get_cell_value("Last Seen Location"),
        "Last Seen Wearing": get_cell_value("Last Seen Wearing"),
        "Other Notes": get_cell_value("Other Notes"),
        "Pronouns": get_cell_value("Pronouns"),
        "Race": get_cell_value("Race"),
        "Weight": get_cell_value("Weight"),
        "Who to Contact If Found": get_cell_value("Who to Contact If Found"),
    }


def apply_profile_to_template(profile, template_contents) -> str:
    """
    Substitutes known variables in the template contents
    with values from the profile. This will fail if expected
    variables do not exist in the template contents.

    Parameters
    ----------
    - profile: dict, required, with fields expected but not required:
      - Chosen Name,
      - Age,
      - Birth Year,
      - Race,
      - Height,
      - Weight,
      - Eyes,
      - Hair,
      - Pronouns,
      - Last Seen Date,
      - Last Seen Location,
      - Last Seen Wearing,
      - Identifying Features,
      - Disappearance Circumstances,
      - Who to Contact If Found,
      - Image 1 Path,
      - Image 2 Path,
      - Other Notes

    - template_contents: str, required, with these required variables:
      - name,
      - age,
      - race,
      - height,
      - weight,
      - eyes,
      - hair,
      - pronouns,
      - last_seen_on,
      - last_seen_where,
      - last_seen_wearing,
      - identifying_features,
      - disappearance_circumstances,
      - contact_if_found,
      - image_path_1,
      - image_path_2,
      - other_notes

    Returns
    -------
    str: The substitution result.
    """

    if not profile or not template_contents:
        return None

    try:
        result = Template(template_contents).substitute(
            name=profile.get("Chosen Name", ""),
            age=profile.get("Age", ""),
            race=profile.get("Race", ""),
            height=profile.get("Height", ""),
            weight=profile.get("Weight", ""),
            eyes=profile.get("Eyes", ""),
            hair=profile.get("Hair", ""),
            pronouns=profile.get("Pronouns", ""),
            last_seen_on=profile.get("Last Seen Date", ""),
            last_seen_where=profile.get("Last Seen Location", ""),
            last_seen_wearing=profile.get("Last Seen Wearing", ""),
            identifying_features=profile.get("Identifying Features", ""),
            disappearance_circumstances=profile.get(
                "Disappearance Circumstances",
                ""
            ),
            contact_if_found=profile.get("Who to Contact If Found", ""),
            image_path_1=profile.get(
                "Image 1 Path", "templates/transparent-1020x1024.png"
            ),
            image_path_2=profile.get(
                "Image 2 Path", "templates/transparent-1020x1024.png"
            ),
            other_notes=profile.get("Other Notes", ""),
        )
        return result
    except KeyError as err:
        msg = (
            "Error: failed to apply profile. "
            "Either the placeholder was not found, "
            f"or it was not given a substitute: {err}."
        )
        print(msg)
        raise
