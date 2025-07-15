import requests
import time
from datetime import date
import logging
import streamlit as st
import pandas as pd
from tqdm import tqdm


class SportCenterInfo:
    BASE_URL = "https://booking-tpsc.sporetrofit.com/Location/findAllowBookingList?"
    LOCATIONS = {
        "ALL": "ALL",
        "文山": "WSSC",
        "信義": "XYSC",
        "中山": "ZSSC",
        "北投": "BTSC",
        "大安": "DASC",
        "大同": "DTSC",
        "內湖": "NHSC",
        "士林": "SLSC",
        "松山": "SSSC",
        "萬華": "WHSC",
    }
    DEFAULT_HEADERS = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "zh-TW,zh;q=0.9",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "priority": "u=1, i",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-requested-with": "XMLHttpRequest",
    }
    TIME_DICT = {
        "All Time": ["06", "22"],
        "Morning": ["06", "12"],
        "Afternoon": ["12", "18"],
        "Evening": ["18", "22"],
    }

    def __init__(self, category="Badminton", rows=200):
        self.category = category
        self.rows = rows

    def fetch_for_date(self, date, location="ALL"):
        """
        Fetch booking data for all locations for a given date.
        Args:
            date (str): The date string in YYYY-MM-DD format.
            location (str): The location key from LOCATIONS. Default is "ALL".
        Returns:
            dict: A dictionary with location keys and their corresponding booking data.
        """
        current_timestamp = int(time.time() * 1000)
        data = f"_search=false&nd={current_timestamp}&rows={self.rows}&page=1&sidx=&sord=asc"
        results = {}
        if location != "ALL":
            locations = [self.LOCATIONS.get(location, "ALL")]
        else:
            locations = self.LOCATIONS.values()

        for location in locations:
            url = f"{self.BASE_URL}LID={location}&categoryId={self.category}&useDate={date}"
            headers = self.DEFAULT_HEADERS.copy()
            headers["Referer"] = url
            try:
                response = requests.post(url, headers=headers, data=data)
                results[location] = response.json()
            except Exception as e:
                results[location] = {
                    "error": str(e),
                    "text": getattr(response, "text", ""),
                }
        return results

    @staticmethod
    def get_available_slots(date_str, time_period, data):
        """
        Return a list of available slots for a given location and date, filtered by time period.
        Args:
            date_str (str): The date string (YYYY-MM-DD).
            time_period (str): The time period key from TIME_DICT.
            data (dict): The booking data for a location and date.
        Returns:
            list[dict]: List of available slot dictionaries.
        """
        slots = []
        time_range = SportCenterInfo.TIME_DICT.get(time_period)
        if not (
            isinstance(data, dict) and "rows" in data and isinstance(data["rows"], list)
        ):
            return slots

        for row in data["rows"]:
            if row.get("Status") != "預約":
                continue
            end_hour = str(row.get("EndTime", {}).get("Hours", "")).zfill(2)
            if time_range:
                # Only include if end_hour is a valid hour and within the selected time range
                if not (
                    end_hour.isdigit() and time_range[0] < end_hour <= time_range[1]
                ):
                    continue
            start_hour = str(row.get("StartTime", {}).get("Hours", "")).zfill(2)
            slots.append(
                {
                    "Date": date_str,
                    "LIDName": row.get("LIDName"),
                    "Place": row.get("LSIDName"),
                    "Time": f"{start_hour}-{end_hour}",
                    "Price": row.get("TotalPrice"),
                }
            )
        return slots


class StreamlitUI:
    """Streamlit UI for displaying sport center booking status."""

    def __init__(self):
        st.title("Sport Center Booking Status")

    def __getstate__(self):
        """
        Get the state of the Streamlit UI for user input.Streamlit UI for user input.
        This method collects user inputs for category, date range, time selection, and location.

        Returns:
            tuple: A tuple containing category, date range, time selection, and location.
        """
        category = st.text_input("Enter category (e.g., Badminton):", "Badminton")
        date_range = st.date_input(
            "Select date(s):", [date.today()], format="YYYY-MM-DD"
        )
        time_selection = st.selectbox(
            "Select Time:", ["All Time", "Morning", "Afternoon", "Evening"]
        )
        location = st.selectbox("Select Location:", SportCenterInfo.LOCATIONS.keys())

        if len(date_range) == 2:
            s, e = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            date_range = [
                (s + pd.Timedelta(days=i)).strftime("%Y-%m-%d")
                for i in range((e - s).days + 1)
            ]
        else:
            date_range = [pd.to_datetime(date_range).strftime("%Y-%m-%d")]
        logging.warning(
            f"Using category: {category}, date range: {date_range}, Time: {time_selection}, location: {location}"
        )
        return category, date_range, time_selection, location


if __name__ == "__main__":
    if st is not None:
        category, date_range, time_selection, location = StreamlitUI().__getstate__()
        sci = SportCenterInfo(category=category)
        if st.button("Check Availability"):
            for select_day in tqdm(date_range):
                st.subheader(f"Date: {select_day}")
                results = sci.fetch_for_date(select_day, location)
                all_slots = []
                for _, data in results.items():
                    slots = sci.get_available_slots(select_day, time_selection, data)
                    all_slots.extend(slots)
                if all_slots:
                    df = pd.DataFrame(all_slots)
                    st.dataframe(df)
                else:
                    st.info("No available slots found for this date.")
    else:
        print("Please install streamlit to use the web UI: pip install streamlit")
