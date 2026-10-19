import argparse
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote_plus
import requests
from tqdm import tqdm
import extractions


DEFAULT_COUNTY_FILE = Path("county_list_by_state.json")
REQUEST_TIMEOUT = 15
DATA_EXTRACTORS = {
    "WTHGIS": lambda3.WTHGIS_extract,
}

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

@dataclass
class CountyInfo:
    """Represent one county's public-record search configuration."""

    name: str
    state: str
    data_type: str
    links: list[str] = field(default_factory=list)
    notes: str = ""

    @property
    def datacase(self):
        """Compatibility alias for extractors using the old attribute name."""
        return self.data_type

def load_county_list(filename=DEFAULT_COUNTY_FILE, state_filter=None, county_filter=None):
    """Load county configurations from a state-grouped JSON file."""
    filename = Path(filename)

    with filename.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("The county configuration's root must be a JSON object.")

    county_list = []

    for state_name, state_counties in data.items():
        if not isinstance(state_counties, dict):
            logger.warning(
                "Skipping invalid county collection for state %r",
                state_name,
            )
            continue

        if (
            state_filter
            and state_name.casefold() != state_filter.strip().casefold()
        ):
            continue

        for county_name, config in state_counties.items():
            if (
                county_filter
                and county_name.casefold() != county_filter.strip().casefold()
            ):
                continue

            if not isinstance(config, dict):
                logger.warning(
                    "Skipping invalid configuration for %s, %s",
                    county_name,
                    state_name,
                )
                continue

            # Support the current data_type field and the old datacase name.
            data_type = config.get("data_type", config.get("datacase", ""))
            links = config.get("links") or []
            if isinstance(links, str):
                links = [links]
            if not isinstance(links, list):
                logger.warning(
                    "Invalid links configuration for %s, %s",
                    county_name,
                    state_name,
                )
                continue
            county_list.append(
                CountyInfo(
                    name=county_name,
                    state=state_name,
                    data_type=str(data_type).upper(),
                    links=links,
                    notes=config.get("notes", "")
                )
            )

    return county_list

def build_search_url(county_info, first_name="", last_name=""):
    """Build a county search URL using its configured template."""
    if not county_info.links:
        return None

    template = county_info.links[0]

    return (
        template
        .replace("FIRSTNAME", quote_plus(first_name))
        .replace("LASTNAME", quote_plus(last_name))
    )


def search_county(session, county_info, first_name="", last_name=""):
    """Query one county and extract its results."""
    extractor = DATA_EXTRACTORS.get(county_info.data_type)

    if extractor is None:
        logger.warning(
            "Unsupported data type %r for %s, %s",
            county_info.data_type,
            county_info.name,
            county_info.state,
        )
        return None

    url = build_search_url(county_info, first_name, last_name)

    if url is None:
        logger.warning(
            "No search URL configured for %s, %s",
            county_info.name,
            county_info.state,
        )
        return None

    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning(
            "Request failed for %s, %s: %s",
            county_info.name,
            county_info.state,
            exc,
        )
        return None

    try:
        return extractor(response.text, county_info)
    except Exception as exc:
        logger.warning(
            "Extraction failed for %s, %s: %s",
            county_info.name,
            county_info.state,
            exc,
        )
        return None

def find(
    first_name="",
    last_name="",
    load_bar=True,
    county_file=DEFAULT_COUNTY_FILE,
    state_filter=None,
    county_filter=None,
):
    """Search configured counties and group results by state and county."""
    counties = load_county_list(
        filename=county_file,
        state_filter=state_filter,
        county_filter=county_filter,
    )

    results = {}

    iterator = (
        tqdm(counties, desc="Searching counties", unit="county")
        if load_bar
        else counties
    )

    with requests.Session() as session:
        session.headers.update(
            {"User-Agent": "CountyRecordResearch/1.0"}
        )

        for county_info in iterator:
            county_results = search_county(
                session=session,
                county_info=county_info,
                first_name=first_name,
                last_name=last_name,
            )

            if county_results is None:
                continue

            state_results = results.setdefault(county_info.state, {})
            state_results[county_info.name] = county_results

    return results

def parse_args(argv=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Search configured county public-record sources."
    )

    parser.add_argument(
        "-f",
        "--first",
        default="",
        help="First name to search",
    )
    parser.add_argument(
        "-l",
        "--last",
        default="",
        help="Last name to search",
    )
    parser.add_argument(
        "-b",
        "--both",
        nargs=2,
        metavar=("FIRST", "LAST"),
        help="Search using both first and last name",
    )
    parser.add_argument(
        "-n",
        "--no-progress",
        action="store_true",
        help="Disable the progress bar",
    )
    parser.add_argument(
        "--county-file",
        type=Path,
        default=DEFAULT_COUNTY_FILE,
        help="Path to the county configuration JSON",
    )
    parser.add_argument(
        "--state",
        help="Limit the search to one state",
    )
    parser.add_argument(
        "--county",
        help="Limit the search to one county",
    )

    args = parser.parse_args(argv)

    if args.both:
        args.first, args.last = args.both

    if not args.first and not args.last:
        parser.error("Provide at least one name using -f, -l, or -b.")

    return args

def main():
    """Run the search and print JSON results."""
    args = parse_args()

    try:
        results = find(
            first_name=args.first,
            last_name=args.last,
            load_bar=not args.no_progress,
            county_file=args.county_file,
            state_filter=args.state,
            county_filter=args.county,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        logger.error("Unable to load county configuration: %s", exc)
        return 1

    print(
        json.dumps(
            results,
            indent=2,
            ensure_ascii=False,
            default=str,
        )
    )

    return 0

if __name__ == "__main__":
        print(
        json.dumps(
            find(last_name="garrison"),
            indent=2,
            ensure_ascii=False,
            default=str,
        )
    )
