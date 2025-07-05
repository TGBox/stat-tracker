import pytest

from datetime import date, timedelta

from modules.holiday_and_appointment_tracker import (
    HolidayAndAppointmentTracker,
    Holiday,
    Appointment,
    HolidayAlreadyExistsError,
    AppointmentConflictError,
    HolidayNotFoundError,
    AppointmentNotFoundError,
)

def test_add_and_get_holiday():
    tracker = HolidayAndAppointmentTracker()
    holiday = Holiday(name="New Year", date=date(2024, 1, 1))
    tracker.add_holiday(holiday)
    holidays = tracker.get_holidays()
    assert len(holidays) == 1
    assert holidays[0].name == "New Year"
    assert holidays[0].date == date(2024, 1, 1)

def test_add_duplicate_holiday_raises():
    tracker = HolidayAndAppointmentTracker()
    holiday = Holiday(name="New Year", date=date(2024, 1, 1))
    tracker.add_holiday(holiday)
    with pytest.raises(HolidayAlreadyExistsError):
        tracker.add_holiday(holiday)

def test_remove_holiday():
    tracker = HolidayAndAppointmentTracker()
    holiday = Holiday(name="Christmas", date=date(2024, 12, 25))
    tracker.add_holiday(holiday)
    tracker.remove_holiday(holiday.date)
    assert tracker.get_holidays() == []

def test_remove_nonexistent_holiday_raises():
    tracker = HolidayAndAppointmentTracker()
    with pytest.raises(HolidayNotFoundError):
        tracker.remove_holiday(date(2024, 12, 25))

def test_add_and_get_appointment():
    tracker = HolidayAndAppointmentTracker()
    appt = Appointment(title="Doctor", date=date(2024, 6, 10), time="10:00")
    tracker.add_appointment(appt)
    appointments = tracker.get_appointments()
    assert len(appointments) == 1
    assert appointments[0].title == "Doctor"
    assert appointments[0].date == date(2024, 6, 10)
    assert appointments[0].time == "10:00"

def test_add_appointment_on_holiday_raises():
    tracker = HolidayAndAppointmentTracker()
    holiday = Holiday(name="Independence Day", date=date(2024, 7, 4))
    tracker.add_holiday(holiday)
    appt = Appointment(title="Meeting", date=date(2024, 7, 4), time="09:00")
    with pytest.raises(AppointmentConflictError):
        tracker.add_appointment(appt)

def test_remove_appointment():
    tracker = HolidayAndAppointmentTracker()
    appt = Appointment(title="Dentist", date=date(2024, 8, 15), time="14:00")
    tracker.add_appointment(appt)
    tracker.remove_appointment(appt.date, appt.time)
    assert tracker.get_appointments() == []

def test_remove_nonexistent_appointment_raises():
    tracker = HolidayAndAppointmentTracker()
    with pytest.raises(AppointmentNotFoundError):
        tracker.remove_appointment(date(2024, 8, 15), "14:00")

def test_appointments_do_not_conflict():
    tracker = HolidayAndAppointmentTracker()
    appt1 = Appointment(title="A", date=date(2024, 9, 1), time="09:00")
    appt2 = Appointment(title="B", date=date(2024, 9, 1), time="10:00")
    tracker.add_appointment(appt1)
    tracker.add_appointment(appt2)
    appointments = tracker.get_appointments()
    assert len(appointments) == 2

def test_get_holidays_and_appointments_empty():
    tracker = HolidayAndAppointmentTracker()
    assert tracker.get_holidays() == []
    assert tracker.get_appointments() == []

def test_add_multiple_holidays_and_appointments():
    tracker = HolidayAndAppointmentTracker()
    holidays = [
        Holiday(name="Holiday1", date=date(2024, 5, 1)),
        Holiday(name="Holiday2", date=date(2024, 5, 2)),
    ]
    appointments = [
        Appointment(title="Appt1", date=date(2024, 5, 3), time="11:00"),
        Appointment(title="Appt2", date=date(2024, 5, 4), time="12:00"),
    ]
    for h in holidays:
        tracker.add_holiday(h)
    for a in appointments:
        tracker.add_appointment(a)
    assert len(tracker.get_holidays()) == 2
    assert len(tracker.get_appointments()) == 2