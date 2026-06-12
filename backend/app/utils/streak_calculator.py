from datetime import date, timedelta


def calculate_streak(checkin_dates: list[date]) -> int:
    if not checkin_dates:
        return 0

    unique_dates = sorted(set(checkin_dates))
    streak = 1
    expected = unique_dates[-1] - timedelta(days=1)

    for current_date in reversed(unique_dates[:-1]):
        if current_date == expected:
            streak += 1
            expected = current_date - timedelta(days=1)
        elif current_date < expected:
            break

    return streak


def calculate_longest_streak(checkin_dates: list[date]) -> int:
    if not checkin_dates:
        return 0

    unique_dates = sorted(set(checkin_dates))
    longest = 1
    current = 1

    for previous_date, current_date in zip(unique_dates, unique_dates[1:]):
        if current_date == previous_date + timedelta(days=1):
            current += 1
        else:
            longest = max(longest, current)
            current = 1

    return max(longest, current)
