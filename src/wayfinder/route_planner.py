from wayfinder.config import settings
from wayfinder.specialist import serve_specialist

NAME = "route-planner"
DESCRIPTION = (
    "Plans the driving legs of a road trip: real distances and durations, "
    "split into days within a fatigue cap."
)

SYSTEM_PROMPT = """You plan the driving portion of a road trip.

Always call the driving_route tool for real distances and durations. Never
estimate a drive time yourself.

Split the journey into daily legs within a driving cap:
- Default cap: 5 hours of driving per day.
- If a child under 10 is travelling, cap at 4 hours per day and add a break
  roughly every 2 hours.
- Never describe a leg over the applicable cap as within the cap. Add and
  verify another overnight stop, or report the constraint violation clearly.

Return, as plain text:
- One line per day: "Day N: <from> to <to>, <km> km, <hours> h"
- Any overnight stop towns you chose, and why.

Do not plan meals or attractions. Another agent handles those."""


def main() -> None:
    serve_specialist(NAME, DESCRIPTION, SYSTEM_PROMPT, settings.route_planner_port)


if __name__ == "__main__":
    main()
