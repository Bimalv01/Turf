# Go Truf - Premium Turf Management & Booking System

Go Truf is a modern Django-based web application designed to bridge the gap between turf owners and sports enthusiasts. It provides a seamless platform for owners to showcase their facilities and for players to discover and book turfs in real-time.

## 🚀 Key Features

### For Customers
- **Smart Search**: Find turfs by location and size (5s, 7s, 11s).
- **Photo Gallery**: Browse high-quality images of turfs via interactive carousels.
- **Instant Booking**: Check availability and book your favorite slot in seconds.
- **Booking Slips**: Automatic generation of professional booking invoices.

### For Turf Owners
- **Dashboard Analytics**: Track total revenue, bookings, and performance trends.
- **Management Tools**: Add, edit, and manage multiple turf listings.
- **Image Support**: Upload multiple photos for each turf for better visibility.
- **Sales Insights**: Real-time sales data and booking counts for each turf.

### For Administrators
- **Full Control**: Oversee all registered turfs and owners.
- **Management Table**: View total sales revenue per turf and manage the listing lifecycle.
- **Financial Overview**: High-level visualizations of system-wide revenue and trends.

## 🛠️ Tech Stack
- **Backend**: Python, Django
- **Frontend**: HTML5, Vanilla CSS, Bootstrap 5
- **Charts**: Chart.js
- **Database**: SQLite (default)
- **Image Processing**: Pillow (PIL)
- **PDF Generation**: xhtml2pdf

## ⚙️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone [repository-url]
   cd Turf
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux/macOS
   # venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install django Pillow xhtml2pdf
   ```

4. **Initialize the database**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (Admin)**:
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

7. **Access the application**:
   - Home Page: `http://127.0.0.1:8000/`
   - Owner Dashboard: `http://127.0.0.1:8000/turf_owner_dashboard/`
   - Admin Dashboard: `http://127.0.0.1:8000/admin-login/`

## 🎨 Rebranding Note
Earlier versions of this project were known as "Clarity Turf". The platform has been officially rebranded to **Go Truf** to better reflect its speed and mission.

---
Developed with ❤️ for the sports community.
