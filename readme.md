[中文說明](./readme.zh.md)

## Sport Center Booking Status App (Taipei)

This project is a Streamlit-based web application for checking and displaying the available booking slots at various Taipei sport centers. It fetches real-time data from the official booking system and presents it in a user-friendly table format.

### Features
- Select sport category (e.g., Badminton)
- Choose a date or date range
- Select a specific sport center location
- View all available booking slots in a table
- Data is fetched live from the official booking API

### Requirements
- Python 3.13+
- [Streamlit](https://streamlit.io/)
- [pandas](https://pandas.pydata.org/)
- [requests](https://docs.python-requests.org/)
- tqdm (optional, for progress bar)

Install dependencies:
```bash
# Create a virtual environment with uv package(recommended)
uv venv -p 3.13
# Install required packages
uv pip install -r requirements.txt
```

### How to Run
1. Open a terminal in the project directory.
2. Run the Streamlit app:
   ```bash
   uv run streamlit run src/sport_center_info.py
   ```
3. The app will open in your browser. Enter the category, select date(s), select time, and choose a location to view available slots.

### Unit Tests
Run the tests to ensure everything is working correctly:
```bash
uv run pytest --cov=. --cov-report=html:calc_cov .\tests\
```
That will generate a coverage report in the `calc_cov` directory.

### Project Structure
- `sport_center_info.py` - Main Streamlit app and booking logic
- `readme.md` - Project documentation

### Notes
- The app fetches data from the Taipei Sport Center booking system. Availability and data accuracy depend on the external API.
- For best results, use a stable internet connection.
