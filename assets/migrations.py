import json
import uuid
from enum import StrEnum
from functools import reduce
from itertools import chain, combinations, pairwise
from operator import itemgetter
from pathlib import Path
from typing import TypedDict, cast


# Types
class PresenceState(StrEnum):
    OFFLINE = "offline"
    UNAVAILABLE = "unavailable"
    ONLINE = "online"


class CollatedPresenceUpdate(TypedDict):
    last_active_ago: int
    presence: PresenceState
    status_msg: str | None
    currently_active: bool | None


class UserPresenceUpdate(CollatedPresenceUpdate):
    user_id: str


class CollatedEDU(TypedDict):
    edu: CollatedPresenceUpdate
    origin_server_ts: int
    received_ts: int
    request: str


class EDUContent(TypedDict):
    push: list[UserPresenceUpdate]


class FullEDU(TypedDict):
    content: EDUContent
    edu_type: str


# Caddy compatibility
class CaddyRequest(TypedDict):
    client_ip: str
    host: str
    method: str
    proto: str
    remote_ip: str
    remote_port: str
    uri: str


class CaddyRequestBody(TypedDict):
    edus: list[dict[str, object]]
    pdus: list[dict[str, object]]
    origin: str
    origin_server_ts: int


class CaddyOutput(TypedDict):
    duration: float
    level: str
    logger: str
    msg: str
    req_body: str
    request: CaddyRequest
    resp_body: str
    size: int
    status: int
    ts: float


def nonempty_pairs(ordered_pairs: list[tuple[str, str]]) -> dict[str, str]:
    """Process dictionary items using the latest populated instance of a key."""
    out: dict[str, str] = {}
    for k, v in ordered_pairs:
        if k not in out or v:
            out[k] = v
    return out


class Transaction0(TypedDict):
    presence_edus: list[list[UserPresenceUpdate]]
    origin_server_ts: int
    received_ts: int
    request_uuid: str


def caddy_to_0(log_entries: list[CaddyOutput]) -> dict[str, list[Transaction0]]:
    """
    Process a Caddy log into Format 0 transactions.

    This:
    - Deduplicates transactions by the first instance of each ID
    - Filters transactions for those that contain presence
    - Unpacks `FullEDU`s into batches of `UserPresenceUpdate`s
    - Collates by origin
    """
    collated_origins: dict[str, list[Transaction0]] = {}
    seen_requests: set[str] = set()

    for entry in log_entries:
        request_uri = entry["request"]["uri"]
        if not request_uri.startswith("/_matrix/federation/v1/send"):
            continue

        txn_id = request_uri.removeprefix("/_matrix/federation/v1/send/")

        if txn_id in seen_requests:
            continue

        try:
            req_body = cast("CaddyRequestBody", json.loads(entry["req_body"]))
        except json.JSONDecodeError:
            continue

        if "edus" not in req_body:
            continue

        presence_edus = [
            cast("FullEDU", edu)["content"]["push"]  # pyright: ignore[reportInvalidCast]
            for edu in req_body["edus"]
            if edu["edu_type"] == "m.presence"
        ]

        if not presence_edus:
            continue

        received_ts = int(entry["ts"] * 1000)
        collated_origins.setdefault(req_body["origin"], []).append(
            {
                "presence_edus": presence_edus,
                "request_uuid": txn_id,
                "origin_server_ts": req_body["origin_server_ts"],
                "received_ts": received_ts,
            }
        )
        seen_requests.add(f"{req_body['origin']}:{txn_id}")

    return collated_origins


def load_caddy(path: Path) -> list[CaddyOutput]:
    """Load a Caddy transaction log."""
    return [
        json.loads(line, object_pairs_hook=nonempty_pairs)
        for line in path.read_text(encoding="utf-8").splitlines()
    ]


class Transaction1(TypedDict):
    edu: CollatedPresenceUpdate
    origin_server_ts: int
    received_ts: int
    request_uuid: str


def apply_1(
    transactions: dict[str, list[Transaction0]],
) -> dict[str, dict[str, list[Transaction1]]]:
    """
    Convert a record of Format 0 transactions to Format 1.

    This is the first Format where analysis is viable.

    This:
    - Converts the bundles of `UserPresenceUpdate` objects into a sequence of
      `CollatedPresenceUpdate`s annotated with request information, collated
      by origin and user
    - Converts all origin server names, user IDs, and request IDs into UUIDv4s
    - Always specifies all fields of `CollatedPresenceUpdate`, using `None`
      where one was missing
    - Sorts primarily by `origin_server_ts` and secondarily by `received_ts`
    """
    user_map: dict[str, str] = {}
    transaction_map: dict[str, str] = {}

    collated_users: dict[str, dict[str, list[Transaction1]]] = {}

    for origin_transactions in transactions.values():
        origin_id = str(uuid.uuid4())
        collated_users[origin_id] = {}
        for transaction in origin_transactions:
            for edu_container in transaction["presence_edus"]:
                for edu_inner in edu_container:
                    collated_users[origin_id].setdefault(
                        user_map.setdefault(
                            edu_inner["user_id"], str(uuid.uuid4())
                        ),
                        [],
                    ).append(
                        {
                            "edu": {
                                "currently_active": edu_inner.get(
                                    "currently_active"
                                ),
                                "status_msg": edu_inner.get("status_msg"),
                                "last_active_ago": edu_inner.get(
                                    "last_active_ago"
                                ),
                                "presence": edu_inner.get("presence"),
                            },
                            "origin_server_ts": transaction["origin_server_ts"],
                            "received_ts": transaction["received_ts"],
                            "request_uuid": transaction_map.setdefault(
                                transaction["request_uuid"], str(uuid.uuid4())
                            ),
                        }
                    )

    for origin_users in collated_users.values():
        for user_edus in origin_users.values():
            user_edus.sort(key=itemgetter("origin_server_ts", "received_ts"))

    return collated_users


class PresenceDeltaKey(StrEnum):
    LAA = "last_active_ago"
    PRESENCE = "presence"
    STATUS = "status_msg"
    ACTIVE = "currently_active"


PresenceDelta = (
    tuple[PresenceDeltaKey.LAA, int | None]
    | tuple[PresenceDeltaKey.PRESENCE, str | None]
    | tuple[PresenceDeltaKey.STATUS, str | None]
    | tuple[PresenceDeltaKey.ACTIVE, bool | None]
)


class Transaction2(TypedDict):
    edu: list[PresenceDelta]
    origin_server_ts: int
    received_ts: int
    request_uuid: str


"""
Format 1 transaction with an empty EDU.

WARNING: This violates Format 1 rules by having an empty EDU. Be careful.
"""
EMPTY_TRANSACTION_1: Transaction1 = {
    "edu": {},
    "origin_server_ts": 0,
    "received_ts": 0,
    "request_uuid": "",
}  # pyright: ignore[reportAssignmentType]


def apply_2(
    transactions: dict[str, dict[str, list[Transaction1]]],
) -> dict[str, dict[str, list[Transaction2]]]:
    """
    Convert a record of Format 1 transactions to Format 2.

    This is an optional step, useful for analysing how sequences of updates
    behave. It turns the `CollatedPresenceUpdate` into a sequence of
    `PresenceDelta`s, expressing updates from the previous state.
    """
    return {
        origin: {
            origin_user: [
                {
                    "edu": cast(
                        "list[PresenceDelta]",
                        list(
                            set(edu["edu"].items())
                            - set(last_edu["edu"].items())
                        ),
                    ),
                    "origin_server_ts": edu["origin_server_ts"],
                    "received_ts": edu["received_ts"],
                    "request_uuid": edu["request_uuid"],
                }
                for last_edu, edu in pairwise(
                    chain([EMPTY_TRANSACTION_1], user_edus)
                )
            ]
            for origin_user, user_edus in origin_users.items()
        }
        for origin, origin_users in transactions.items()
    }


# Analyses
def delta_combination_prevalence(
    transactions: dict[str, dict[str, list[Transaction2]]],
) -> list[tuple[tuple[PresenceDeltaKey, ...], int]]:
    """Get how often combinations of updates occur in Format 2 transactions."""
    return sorted(
        [
            (
                combination,
                reduce(
                    int.__add__,
                    (
                        1
                        for origin_users in transactions.values()
                        for user_updates in origin_users.values()
                        for update in user_updates
                        if set(map(itemgetter(0), update["edu"]))
                        == set(combination)
                    ),
                    0,
                ),
            )
            for combination in chain.from_iterable(
                combinations(PresenceDeltaKey.__members__.values(), i)
                for i in range(0, 5)
            )
        ],
        key=itemgetter(1),
    )


def containing_presence(
    transactions: dict[str, dict[str, list[Transaction2]]],
) -> int:
    """Get how many state or status updates occur in Format 2 transactions."""
    return reduce(
        int.__add__,
        (
            1
            for origin_users in transactions.values()
            for user_updates in origin_users.values()
            for update in user_updates
            if list(
                filter(
                    {
                        PresenceDeltaKey.PRESENCE,
                        PresenceDeltaKey.STATUS,
                    }.__contains__,
                    map(itemgetter(0), update["edu"]),
                )
            )
        ),
        0,
    )


def containing_status(
    transactions: dict[str, dict[str, list[Transaction2]]],
) -> int:
    """Get how many status updates occur in Format 2 transactions."""
    return reduce(
        int.__add__,
        (
            1
            for origin_users in transactions.values()
            for user_updates in origin_users.values()
            for update in user_updates
            if any(
                key == PresenceDeltaKey.STATUS and value is not None
                for key, value in update["edu"]
            )
        ),
        0,
    )
