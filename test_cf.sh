#!/bin/bash
# Test suite for cf (Chatfile tool)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test directory
TEST_DIR=""
ORIGINAL_DIR="$(pwd)"
CF_PATH="$(realpath ./cf)"

# ============================================================================
# Test Framework
# ============================================================================

setup() {
    TEST_DIR=$(mktemp -d)
    cd "$TEST_DIR"
    # Create mock global dir to avoid touching real ~/.chatfiles
    export HOME="$TEST_DIR/home"
    mkdir -p "$HOME"
}

teardown() {
    cd "$ORIGINAL_DIR"
    # Remove append-only attributes before cleanup
    if [ -d "$TEST_DIR" ]; then
        find "$TEST_DIR" -type f -name "*.Chatfile" -exec sudo chattr -a {} \; 2>/dev/null || true
        find "$TEST_DIR" -type f -name "Chatfile" -exec sudo chattr -a {} \; 2>/dev/null || true
        rm -rf "$TEST_DIR"
    fi
}

pass() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    echo -e "${GREEN}✓${NC} $1"
}

fail() {
    TESTS_FAILED=$((TESTS_FAILED + 1))
    echo -e "${RED}✗${NC} $1"
    [ -n "$2" ] && echo "  Expected: $2"
    [ -n "$3" ] && echo "  Got: $3"
}

run_test() {
    TESTS_RUN=$((TESTS_RUN + 1))
    local name="$1"
    shift
    if "$@" 2>&1; then
        pass "$name"
    else
        fail "$name"
    fi
}

assert_eq() {
    local expected="$1"
    local actual="$2"
    local msg="$3"
    if [ "$expected" = "$actual" ]; then
        return 0
    else
        echo "  Expected: '$expected'" >&2
        echo "  Actual:   '$actual'" >&2
        return 1
    fi
}

assert_contains() {
    local haystack="$1"
    local needle="$2"
    if echo "$haystack" | grep -q "$needle"; then
        return 0
    else
        echo "  String does not contain: '$needle'" >&2
        echo "  In: '$haystack'" >&2
        return 1
    fi
}

assert_file_exists() {
    [ -f "$1" ] || { echo "  File not found: $1" >&2; return 1; }
}

assert_file_not_exists() {
    [ ! -f "$1" ] || { echo "  File should not exist: $1" >&2; return 1; }
}

assert_exit_code() {
    local expected="$1"
    local actual="$2"
    [ "$expected" -eq "$actual" ] || { echo "  Expected exit code $expected, got $actual" >&2; return 1; }
}

# ============================================================================
# Room Management Tests
# ============================================================================

test_create_room_default() {
    setup
    # Skip chattr (requires sudo)
    "$CF_PATH" create-room 2>/dev/null || true
    assert_file_exists "Chatfile"
    local content
    content=$(cat Chatfile)
    assert_contains "$content" "Chatroom"
    teardown
}

test_create_room_named() {
    setup
    "$CF_PATH" create-room myroom 2>/dev/null || true
    assert_file_exists "myroom.Chatfile"
    teardown
}

test_create_room_global() {
    setup
    "$CF_PATH" create-room testglobal -g 2>/dev/null || true
    assert_file_exists "$HOME/.chatfiles/testglobal.Chatfile"
    teardown
}

test_create_room_already_exists() {
    setup
    "$CF_PATH" create-room test 2>/dev/null || true
    local output
    output=$("$CF_PATH" create-room test 2>&1) && exit_code=0 || exit_code=$?
    assert_exit_code 1 "$exit_code"
    assert_contains "$output" "already exists"
    teardown
}

test_create_room_strips_extension() {
    setup
    "$CF_PATH" create-room "myroom.Chatfile" 2>/dev/null || true
    # Should create myroom.Chatfile, NOT myroom.Chatfile.Chatfile
    assert_file_exists "myroom.Chatfile"
    assert_file_not_exists "myroom.Chatfile.Chatfile"
    teardown
}

test_list_rooms_empty() {
    setup
    local output
    output=$("$CF_PATH" list-rooms 2>&1) || true
    # Should not error, just show nothing or empty lists
    teardown
}

test_list_rooms_local() {
    setup
    "$CF_PATH" create-room foo 2>/dev/null || true
    "$CF_PATH" create-room bar 2>/dev/null || true
    local output
    output=$("$CF_PATH" list-rooms 2>&1)
    assert_contains "$output" "foo.Chatfile"
    assert_contains "$output" "bar.Chatfile"
    teardown
}

test_list_rooms_global() {
    setup
    "$CF_PATH" create-room globaltest -g 2>/dev/null || true
    local output
    output=$("$CF_PATH" list-rooms 2>&1)
    assert_contains "$output" "globaltest.Chatfile"
    assert_contains "$output" "Global rooms"
    teardown
}

test_delete_room() {
    setup
    "$CF_PATH" create-room todelete 2>/dev/null || true
    assert_file_exists "todelete.Chatfile"
    # Remove append-only attr if set (may fail without sudo, that's ok)
    sudo chattr -a "todelete.Chatfile" 2>/dev/null || true
    "$CF_PATH" delete-room todelete 2>/dev/null || true
    assert_file_not_exists "todelete.Chatfile"
    teardown
}

test_delete_room_not_found() {
    setup
    local output
    output=$("$CF_PATH" delete-room nonexistent 2>&1) && exit_code=0 || exit_code=$?
    assert_exit_code 1 "$exit_code"
    assert_contains "$output" "not found"
    teardown
}

# ============================================================================
# Session Management Tests
# ============================================================================

test_register_creates_session() {
    setup
    "$CF_PATH" create-room 2>/dev/null || true
    local username
    username=$("$CF_PATH" register Chatfile)
    assert_file_exists ".cf_session"
    # Username should match pattern: word-word-number
    [[ "$username" =~ ^[a-z]+-[a-z]+-[0-9]+$ ]] || { echo "Invalid username format: $username" >&2; return 1; }
    teardown
}

test_register_by_name() {
    setup
    "$CF_PATH" create-room myroom 2>/dev/null || true
    "$CF_PATH" register myroom >/dev/null
    assert_file_exists ".cf_session"
    local chatfile
    chatfile=$(head -1 .cf_session)
    assert_contains "$chatfile" "myroom.Chatfile"
    teardown
}

test_register_global_room() {
    setup
    "$CF_PATH" create-room globalroom -g 2>/dev/null || true
    "$CF_PATH" register globalroom >/dev/null
    local chatfile
    chatfile=$(head -1 .cf_session)
    assert_contains "$chatfile" ".chatfiles/globalroom.Chatfile"
    teardown
}

test_register_not_found() {
    setup
    local output
    output=$("$CF_PATH" register nosuchfile 2>&1) && exit_code=0 || exit_code=$?
    assert_exit_code 1 "$exit_code"
    assert_contains "$output" "not found"
    teardown
}

test_join() {
    setup
    "$CF_PATH" create-room 2>/dev/null || true
    "$CF_PATH" register Chatfile >/dev/null
    local output
    output=$("$CF_PATH" join)
    assert_contains "$output" "Joined as"
    # Check session file has JOINED set
    local joined
    joined=$(sed -n '3p' .cf_session)
    assert_eq "yes" "$joined"
    # Check chatfile has join message
    local chatfile_content
    chatfile_content=$(cat Chatfile)
    assert_contains "$chatfile_content" "joined"
    teardown
}

test_join_already_joined() {
    setup
    "$CF_PATH" create-room 2>/dev/null || true
    "$CF_PATH" register Chatfile >/dev/null
    "$CF_PATH" join >/dev/null
    local output
    output=$("$CF_PATH" join 2>&1) && exit_code=0 || exit_code=$?
    assert_exit_code 1 "$exit_code"
    assert_contains "$output" "Already joined"
    teardown
}

test_leave() {
    setup
    "$CF_PATH" create-room 2>/dev/null || true
    "$CF_PATH" register Chatfile >/dev/null
    "$CF_PATH" join >/dev/null
    local output
    output=$("$CF_PATH" leave)
    assert_contains "$output" "Left room"
    # Check session file has JOINED cleared
    local joined
    joined=$(sed -n '3p' .cf_session)
    assert_eq "" "$joined"
    teardown
}

test_leave_not_joined() {
    setup
    "$CF_PATH" create-room 2>/dev/null || true
    "$CF_PATH" register Chatfile >/dev/null
    local output
    output=$("$CF_PATH" leave 2>&1) && exit_code=0 || exit_code=$?
    assert_exit_code 1 "$exit_code"
    assert_contains "$output" "Not in room"
    teardown
}

test_status() {
    setup
    "$CF_PATH" create-room 2>/dev/null || true
    local username
    username=$("$CF_PATH" register Chatfile)
    local output
    output=$("$CF_PATH" status)
    assert_contains "$output" "Session: $username"
    assert_contains "$output" "Chatfile:"
    assert_contains "$output" "Joined: no"
    teardown
}

test_status_joined() {
    setup
    "$CF_PATH" create-room 2>/dev/null || true
    "$CF_PATH" register Chatfile >/dev/null
    "$CF_PATH" join >/dev/null
    local output
    output=$("$CF_PATH" status)
    assert_contains "$output" "Joined: yes"
    teardown
}

test_status_no_session() {
    setup
    local output
    output=$("$CF_PATH" status 2>&1) && exit_code=0 || exit_code=$?
    assert_exit_code 1 "$exit_code"
    assert_contains "$output" "No active session"
    teardown
}

# ============================================================================
# Messaging Tests
# ============================================================================

test_send() {
    setup
    "$CF_PATH" create-room 2>/dev/null || true
    local username
    username=$("$CF_PATH" register Chatfile)
    "$CF_PATH" join >/dev/null
    "$CF_PATH" send "Hello, world!"
    local content
    content=$(cat Chatfile)
    assert_contains "$content" "$username: Hello, world!"
    teardown
}

test_send_not_joined() {
    setup
    "$CF_PATH" create-room 2>/dev/null || true
    "$CF_PATH" register Chatfile >/dev/null
    local output
    output=$("$CF_PATH" send "test" 2>&1) && exit_code=0 || exit_code=$?
    assert_exit_code 1 "$exit_code"
    assert_contains "$output" "Must join first"
    teardown
}

test_send_empty_message() {
    setup
    "$CF_PATH" create-room 2>/dev/null || true
    "$CF_PATH" register Chatfile >/dev/null
    "$CF_PATH" join >/dev/null
    local output
    output=$("$CF_PATH" send "" 2>&1) && exit_code=0 || exit_code=$?
    assert_exit_code 1 "$exit_code"
    assert_contains "$output" "Usage"
    teardown
}

test_read_default() {
    setup
    "$CF_PATH" create-room 2>/dev/null || true
    "$CF_PATH" register Chatfile >/dev/null
    "$CF_PATH" join >/dev/null
    "$CF_PATH" send "Message 1"
    "$CF_PATH" send "Message 2"
    local output
    output=$("$CF_PATH" read)
    assert_contains "$output" "Message 1"
    assert_contains "$output" "Message 2"
    teardown
}

test_read_limited() {
    setup
    "$CF_PATH" create-room 2>/dev/null || true
    "$CF_PATH" register Chatfile >/dev/null
    "$CF_PATH" join >/dev/null
    "$CF_PATH" send "Message 1"
    "$CF_PATH" send "Message 2"
    "$CF_PATH" send "Message 3"
    local output
    output=$("$CF_PATH" read 1)
    # Should only show last message
    local line_count
    line_count=$(echo "$output" | wc -l)
    assert_eq "1" "$line_count"
    teardown
}

# ============================================================================
# Command Alias Tests
# ============================================================================

test_command_aliases() {
    setup
    "$CF_PATH" create-room 2>/dev/null || true

    # Test 'cr' alias for create-room
    "$CF_PATH" cr aliasroom 2>/dev/null || true
    assert_file_exists "aliasroom.Chatfile"

    # Test 'ls' alias for list-rooms
    local output
    output=$("$CF_PATH" ls)
    assert_contains "$output" "aliasroom"

    # Test 'r' alias for register
    "$CF_PATH" r Chatfile >/dev/null
    assert_file_exists ".cf_session"

    # Test 'j' alias for join
    "$CF_PATH" j >/dev/null

    # Test 's' alias for send
    "$CF_PATH" s "test message" >/dev/null

    # Test 'st' alias for status
    output=$("$CF_PATH" st)
    assert_contains "$output" "Session:"

    # Test 'l' alias for leave
    "$CF_PATH" l >/dev/null

    teardown
}

# ============================================================================
# Help Tests
# ============================================================================

test_help() {
    setup
    local output
    output=$("$CF_PATH" help)
    assert_contains "$output" "cf - Chatfile tool"
    assert_contains "$output" "create-room"
    assert_contains "$output" "register"
    assert_contains "$output" "send"
    teardown
}

test_help_flag() {
    setup
    local output
    output=$("$CF_PATH" --help)
    assert_contains "$output" "cf - Chatfile tool"
    teardown
}

# ============================================================================
# Edge Case Tests
# ============================================================================

test_username_uniqueness() {
    setup
    "$CF_PATH" create-room 2>/dev/null || true
    # Generate multiple usernames and check they're all different
    local usernames=()
    for i in {1..5}; do
        rm -f .cf_session
        username=$("$CF_PATH" register Chatfile)
        usernames+=("$username")
    done
    # Check all unique
    local unique_count
    unique_count=$(printf '%s\n' "${usernames[@]}" | sort -u | wc -l)
    assert_eq "5" "$unique_count"
    teardown
}

test_special_characters_in_message() {
    setup
    "$CF_PATH" create-room 2>/dev/null || true
    "$CF_PATH" register Chatfile >/dev/null
    "$CF_PATH" join >/dev/null
    "$CF_PATH" send "Hello! @#\$%^&*() test"
    local content
    content=$(cat Chatfile)
    assert_contains "$content" "Hello!"
    teardown
}

test_multiline_preserved() {
    setup
    "$CF_PATH" create-room 2>/dev/null || true
    "$CF_PATH" register Chatfile >/dev/null
    "$CF_PATH" join >/dev/null
    # Note: single message should stay on one line
    "$CF_PATH" send "Line one"
    "$CF_PATH" send "Line two"
    local line_count
    line_count=$(grep -c ":" Chatfile)
    # Should have system line + join + 2 messages = at least 4 lines with ':'
    [ "$line_count" -ge 2 ] || { echo "Expected at least 2 message lines, got $line_count" >&2; return 1; }
    teardown
}

# ============================================================================
# Run All Tests
# ============================================================================

echo "Running cf test suite..."
echo "========================"
echo ""

echo "Room Management Tests:"
run_test "create-room (default)" test_create_room_default
run_test "create-room (named)" test_create_room_named
run_test "create-room (global)" test_create_room_global
run_test "create-room (already exists)" test_create_room_already_exists
run_test "create-room (strips .Chatfile)" test_create_room_strips_extension
run_test "list-rooms (empty)" test_list_rooms_empty
run_test "list-rooms (local)" test_list_rooms_local
run_test "list-rooms (global)" test_list_rooms_global
run_test "delete-room" test_delete_room
run_test "delete-room (not found)" test_delete_room_not_found

echo ""
echo "Session Management Tests:"
run_test "register creates session" test_register_creates_session
run_test "register by name" test_register_by_name
run_test "register global room" test_register_global_room
run_test "register (not found)" test_register_not_found
run_test "join" test_join
run_test "join (already joined)" test_join_already_joined
run_test "leave" test_leave
run_test "leave (not joined)" test_leave_not_joined
run_test "status" test_status
run_test "status (joined)" test_status_joined
run_test "status (no session)" test_status_no_session

echo ""
echo "Messaging Tests:"
run_test "send" test_send
run_test "send (not joined)" test_send_not_joined
run_test "send (empty message)" test_send_empty_message
run_test "read (default)" test_read_default
run_test "read (limited)" test_read_limited

echo ""
echo "Command Alias Tests:"
run_test "command aliases" test_command_aliases

echo ""
echo "Help Tests:"
run_test "help" test_help
run_test "help flag" test_help_flag

echo ""
echo "Edge Case Tests:"
run_test "username uniqueness" test_username_uniqueness
run_test "special characters in message" test_special_characters_in_message
run_test "multiline preserved" test_multiline_preserved

echo ""
echo "========================"
echo -e "Tests run: $TESTS_RUN"
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"

if [ "$TESTS_FAILED" -gt 0 ]; then
    exit 1
fi
