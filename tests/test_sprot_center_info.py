from unittest.mock import patch, MagicMock
from src.sport_center_info import SportCenterInfo, StreamlitUI
from datetime import datetime, timedelta


def test_fetch_for_date_all_locations_success():
    mock_response = MagicMock()
    mock_response.json.return_value = {"rows": [{"Status": "預約"}]}
    with patch("requests.post", return_value=mock_response) as mock_post:
        sci = SportCenterInfo()
        result = sci.fetch_for_date("2024-06-01")
        # Should have results for all locations
        assert isinstance(result, dict)
        for loc in SportCenterInfo.LOCATIONS.values():
            assert loc in result
            assert result[loc] == {"rows": [{"Status": "預約"}]}
        assert mock_post.call_count == len(SportCenterInfo.LOCATIONS)


def test_fetch_for_date_specific_location_success():
    mock_response = MagicMock()
    mock_response.json.return_value = {"rows": [{"Status": "預約"}]}
    with patch("requests.post", return_value=mock_response) as mock_post:
        sci = SportCenterInfo()
        result = sci.fetch_for_date("2024-06-01", location="文山")
        assert "WSSC" in result
        assert result["WSSC"] == {"rows": [{"Status": "預約"}]}
        assert mock_post.call_count == 1


def test_fetch_for_date_exception_handling():
    with patch("requests.post", side_effect=Exception("Network error")):
        sci = SportCenterInfo()
        result = sci.fetch_for_date("2024-06-01", location="文山")
        assert "WSSC" in result
        assert "error" in result["WSSC"]
        assert "Network error" in result["WSSC"]["error"]


def test_get_available_slots_filters_by_status_and_time():
    data = {
        "rows": [
            {
                "Status": "預約",
                "EndTime": {"Hours": 10},
                "StartTime": {"Hours": 8},
                "LIDName": "WSSC",
                "LSIDName": "Court 1",
                "TotalPrice": 100,
            },
            {
                "Status": "已預約",
                "EndTime": {"Hours": 11},
                "StartTime": {"Hours": 9},
                "LIDName": "WSSC",
                "LSIDName": "Court 2",
                "TotalPrice": 120,
            },
            {
                "Status": "預約",
                "EndTime": {"Hours": 20},
                "StartTime": {"Hours": 18},
                "LIDName": "WSSC",
                "LSIDName": "Court 3",
                "TotalPrice": 150,
            },
        ]
    }
    slots = SportCenterInfo.get_available_slots("2024-06-01", "Morning", data)
    assert len(slots) == 1
    assert slots[0]["Place"] == "Court 1"
    slots_evening = SportCenterInfo.get_available_slots("2024-06-01", "Evening", data)
    assert len(slots_evening) == 1
    assert slots_evening[0]["Place"] == "Court 3"


def test_get_available_slots_invalid_data():
    slots = SportCenterInfo.get_available_slots("2024-06-01", "Morning", {})
    assert slots == []
    slots = SportCenterInfo.get_available_slots(
        "2024-06-01", "Morning", {"rows": "notalist"}
    )
    assert slots == []


def test_get_available_slots_time_range_none():
    data = {
        "rows": [
            {
                "Status": "預約",
                "EndTime": {"Hours": 10},
                "StartTime": {"Hours": 8},
                "LIDName": "WSSC",
                "LSIDName": "Court 1",
                "TotalPrice": 100,
            }
        ]
    }
    slots = SportCenterInfo.get_available_slots("2024-06-01", "Nonexistent", data)
    # Should include slot since time_range is None (no filtering)
    assert len(slots) == 1
    assert slots[0]["Place"] == "Court 1"


def test_streamlitui_getstate_returns_expected(monkeypatch):
    mock_st = MagicMock()
    mock_st.text_input.return_value = "Badminton"
    mock_st.date_input.return_value = ["2024-06-01", "2024-06-02"]
    mock_st.selectbox.side_effect = [
        "Morning",  # time_selection
        "文山",  # location
    ]
    monkeypatch.setattr("src.sport_center_info.st", mock_st)
    ui = StreamlitUI()
    with patch("logging.warning"):
        state = ui.__getstate__()
    assert state[0] == "Badminton"
    assert state[1] == ["2024-06-01", "2024-06-02"]
    assert state[2] == "Morning"
    assert state[3] == "文山"


def test_streamlitui_get_date_range_single_date():
    ui = StreamlitUI()
    ui.date = datetime.strptime("2024-06-01", "%Y-%m-%d")
    with (
        patch("pandas.to_datetime", side_effect=lambda x: x),
        patch(
            "pandas.Timedelta",
            side_effect=lambda days=0: type("Delta", (), {"days": days})(),
        ),
    ):
        result = ui._get_date_range()
    assert result == ["2024-06-01"]


def test_streamlitui_get_date_range_range():
    ui = StreamlitUI()
    ui.date = (
        datetime.strptime("2024-06-01", "%Y-%m-%d"),
        datetime.strptime("2024-06-03", "%Y-%m-%d"),
    )
    # Patch pd.Timedelta and pd.to_datetime to behave as expected
    with (
        patch("pandas.Timedelta", side_effect=lambda days=0: timedelta(days=days)),
        patch("pandas.to_datetime", side_effect=lambda x: x),
    ):
        result = ui._get_date_range()
    assert result == ["2024-06-01", "2024-06-02", "2024-06-03"]
