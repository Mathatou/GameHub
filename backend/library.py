from pathlib import Path
from typing import TypedDict
import json



BASE_DIR = Path(__file__).resolve().parent.parent
LIBRARY_FILE = BASE_DIR / "data" / "library.json"
CATEGORIES = ['family', 'friends', 'solo', 'party']
STATUS = ['to_play', 'played', 'loaned']
class GameEntry(TypedDict):
    status: str
    preferred_group_size: int | None
    my_rating: int | None
    category: str | None

class GameEntryUpdate(TypedDict, total=False):
    status: str
    preferred_group_size: int
    my_rating: int
    category: str

Library = dict[int, GameEntry]

class LibraryError(Exception):
    pass
# The entry is not found in lib
class IDNotFoundInLibraryError(LibraryError):
    pass
# The entry already exists in lib
class IDAlreadyExistsError(LibraryError):
    pass
# The entry is invalid
class InvalidEntryError(LibraryError):
    pass

# read the library from disk
def read_lib() -> Library:
    if LIBRARY_FILE.exists():
        data = json.loads(LIBRARY_FILE.read_text())
        return {int(key): value for key, value in data.items()}
    return {}

    
# write the library to disk
def write_lib(pDict: Library) -> None :
    if not LIBRARY_FILE.parent.exists():
        LIBRARY_FILE.parent.mkdir(parents=True)
    LIBRARY_FILE.write_text(json.dumps(pDict))

#add entry pEntry to library
def add_to_lib(pIDtoAdd : int) -> GameEntry:
    lib = read_lib()
    if pIDtoAdd in lib:
        raise IDAlreadyExistsError(f"Entry {pIDtoAdd} already exists in library")
    
    lib[pIDtoAdd] = {
        "status": "to_play",
        "preferred_group_size": None,
        "my_rating": None,
        "category": None
    }
    
    write_lib(lib)
    return lib[pIDtoAdd]

# remove entry at ID pID from library
def remove_from_lib(pID: int) -> int:
    lib = read_lib()
    if pID in lib.keys():
        del lib[pID]
        write_lib(lib)
        return len(lib)
    else:
        raise IDNotFoundInLibraryError(f"Entry {pID} does not exist in library")

# update entry at ID pID with pUpdatedEntry
def update_entry(pID: int, pPlayerRange : tuple[int, int], pUpdatedEntry: GameEntryUpdate) -> GameEntry:
    # the entry must be a dict because it could cause errors with set cast
    if isinstance(pUpdatedEntry, dict) is False:
        raise InvalidEntryError(f"Invalid entry {pUpdatedEntry}. Must be a dictionary.")
    lib = read_lib()
    # if the entry does not exist, raise an error
    if pID not in lib:
        raise IDNotFoundInLibraryError(f"Entry {pID} does not exist in library")
    # None values are not allowed by a design choice.
    for key, value in pUpdatedEntry.items():
            if value is None:
                raise InvalidEntryError(f"Invalid value for {key} in entry {pID}. Must not be None.")

    allowed_keys = {"status", "preferred_group_size", "my_rating", "category"}
    if not set(pUpdatedEntry).issubset(allowed_keys):
        raise InvalidEntryError(f"Invalid keys in entry {pID}. Must be one of 'status', 'preferred_group_size', 'my_rating', or 'category'.")
    # VALUE VALIDATION
    my_rating = pUpdatedEntry.get("my_rating")
    if my_rating is not None :
        if type(my_rating) is not int or not (1 <= my_rating <= 5):
            raise InvalidEntryError(f"Invalid rating {my_rating!r} for entry {pID}. Must be an integer between 1 and 5.")
        
    preferred_group_size = pUpdatedEntry.get("preferred_group_size")
    if preferred_group_size is not None :
        if type(preferred_group_size) is not int or not (pPlayerRange[0] <= preferred_group_size <= pPlayerRange[1]):
            raise InvalidEntryError(f"Invalid preferred group size {preferred_group_size} for entry {pID}. Must be an integer between {pPlayerRange[0]} and {pPlayerRange[1]} included.")
    status = pUpdatedEntry.get("status")
    if status is not None :
        if type(status) is not str or status not in STATUS:
            raise InvalidEntryError(f"Invalid status {status} for entry {pID}. Must be a string and one of {STATUS}.")
    category = pUpdatedEntry.get("category")
    if category is not None :
        if type(category) is not str or category not in CATEGORIES:
            raise InvalidEntryError(f"Invalid category {category} for entry {pID}. Must be a string and one of {CATEGORIES}.")

    lib[pID].update(pUpdatedEntry)
    write_lib(lib)
    return lib[pID]

# get entry at ID pID
def get_entry(pID: int) -> GameEntry:
    lib = read_lib()
    if pID in lib.keys():
        return lib[pID]
    else:
        raise IDNotFoundInLibraryError(f"Entry {pID} does not exist in library")

def clean_library() -> None:
    if LIBRARY_FILE.exists():
        LIBRARY_FILE.unlink()


def main():
    clean_library()

    test_id = 40368
    unknown_id = 999999
    player_range = (2, 4)

    passed = 0
    failed = 0

    baseline = {
        "status": "to_play",
        "preferred_group_size": None,
        "my_rating": None,
        "category": None
    }

    def reset_entry():
        if test_id not in read_lib():
            add_to_lib(test_id)

        # Restore the complete baseline directly.
        lib = read_lib()
        lib[test_id] = baseline.copy()
        write_lib(lib)

    def run_test(name, test_function):
        nonlocal passed, failed

        try:
            reset_entry()
            test_function()
            print(f"[PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {name}: {type(e).__name__}: {e}")
            failed += 1

    def expect_exception(expected_exception, function):
        try:
            function()
        except expected_exception:
            return
        except Exception as e:
            raise AssertionError(
                f"Expected {expected_exception.__name__}, "
                f"got {type(e).__name__}: {e}"
            )

        raise AssertionError(
            f"Expected {expected_exception.__name__}, "
            "but no exception was raised"
        )

    def expect_invalid_unchanged(payload):
        original = get_entry(test_id).copy()

        expect_exception(
            InvalidEntryError,
            lambda: update_entry(test_id, player_range, payload)
        )

        current = get_entry(test_id)

        if current != original:
            raise AssertionError(
                f"Entry changed after invalid update!\n"
                f"Before: {original}\n"
                f"After: {current}"
            )

    # --------------------------------------------------
    # POSITIVE TESTS
    # --------------------------------------------------

    def test_default_status():
        result = add_to_lib(40369)

        if result["status"] != "to_play":
            raise AssertionError(
                f"Expected 'to_play', got {result['status']}"
            )

        if result["preferred_group_size"] is not None:
            raise AssertionError("Unexpected default group size")

        if result["my_rating"] is not None:
            raise AssertionError("Unexpected default rating")

        if result["category"] is not None:
            raise AssertionError("Unexpected default category")

        # Remove the additional test entry.
        remove_from_lib(40369)

    def test_valid_single_field():
        result = update_entry(
            test_id, player_range, {"status": "played"}
        )

        stored = get_entry(test_id)

        if result != stored:
            raise AssertionError("Returned entry differs from stored entry")

        if result["status"] != "played":
            raise AssertionError("Status was not updated")

        if set(result) != set(baseline):
            raise AssertionError("Returned entry is incomplete")

        for key in baseline:
            if key != "status" and result[key] != baseline[key]:
                raise AssertionError(f"Unexpected change to {key}")

    def test_partial_update_preserves_other_fields():
        initial = {
            "status": "played",
            "preferred_group_size": 3,
            "my_rating": 4,
            "category": "friends"
        }

        update_entry(test_id, player_range, initial)
        update_entry(test_id, player_range, {"my_rating": 5})

        expected = {
            "status": "played",
            "preferred_group_size": 3,
            "my_rating": 5,
            "category": "friends"
        }

        if get_entry(test_id) != expected:
            raise AssertionError(
                f"Expected {expected}, got {get_entry(test_id)}"
            )

    def test_empty_update():
        result = update_entry(test_id, player_range, {})

        if result != baseline:
            raise AssertionError("Empty update modified the entry")

        if get_entry(test_id) != baseline:
            raise AssertionError("Stored entry changed after empty update")

    def test_group_size_boundaries():
        for value in (2, 4):
            result = update_entry(
                test_id, player_range,
                {"preferred_group_size": value}
            )

            if result["preferred_group_size"] != value:
                raise AssertionError(f"Boundary {value} was not stored")

    # --------------------------------------------------
    # NEGATIVE TESTS
    # --------------------------------------------------

    def test_rating_too_high():
        expect_invalid_unchanged({"my_rating": 7})

    def test_invalid_rating_types():
        for value in ("5", True, 4.5):
            expect_invalid_unchanged({"my_rating": value})

    def test_group_size_outside_range():
        for value in (1, 5):
            expect_invalid_unchanged({"preferred_group_size": value})

    def test_bool_group_size():
        for value in (True, False):
            expect_invalid_unchanged({"preferred_group_size": value})

    def test_status_cannot_be_none():
        expect_invalid_unchanged({"status": None})

    def test_none_values():
        for field in (
            "preferred_group_size",
            "my_rating",
            "category"
        ):
            expect_invalid_unchanged({field: None})

    def test_unknown_field():
        expect_invalid_unchanged({"colour": "blue"})

    def test_invalid_status():
        for value in ("unknown", 123):
            expect_invalid_unchanged({"status": value})

    def test_invalid_category():
        for value in ("unknown", 123):
            expect_invalid_unchanged({"category": value})

    def test_non_dictionary_input():
        for value in ([], 123, "hello"):
            expect_invalid_unchanged(value)

    def test_valid_and_invalid_field():
        expect_invalid_unchanged({
            "status": "played",
            "my_rating": 7
        })

    def test_unknown_id():
        expect_exception(
            IDNotFoundInLibraryError,
            lambda: update_entry(
                unknown_id, player_range, {"status": "played"}
            )
        )

    # --------------------------------------------------
    # TEST REGISTRY
    # --------------------------------------------------

    tests = [
        # Positive tests
        ("Default status is to_play", test_default_status),
        ("Valid single-field update", test_valid_single_field),
        ("Partial update preserves other fields",
         test_partial_update_preserves_other_fields),
        ("Empty update", test_empty_update),
        ("Group size boundaries (2 and 4)",
         test_group_size_boundaries),

        # Negative tests
        ("Rating 7", test_rating_too_high),
        ("Invalid rating types", test_invalid_rating_types),
        ("Group size outside range (1 and 5)",
         test_group_size_outside_range),
        ("Boolean group size", test_bool_group_size),
        ("Status cannot be None", test_status_cannot_be_none),
        ("None values for optional fields", test_none_values),
        ("Unknown field 'colour'", test_unknown_field),
        ("Invalid status", test_invalid_status),
        ("Invalid category", test_invalid_category),
        ("Non-dictionary input", test_non_dictionary_input),
        ("Valid + invalid field (atomicity)",
         test_valid_and_invalid_field),
        ("Unknown ID", test_unknown_id),
    ]

    # --------------------------------------------------
    # RUN TESTS
    # --------------------------------------------------

    print("\n========== LIBRARY TESTS ==========\n")

    try:
        for name, test_function in tests:
            run_test(name, test_function)

        print("\n========== RESULTS ==========")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Total:  {passed + failed}")

    finally:
        clean_library()


if __name__ == "__main__":
    main()
