import mysql.connector
from datetime import datetime

class LittleLemonBookingSystem:
    def __init__(self, host, user, password, database):
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
        }
        self.conn = None
        self.cur = None

    def connect(self):
        try:
            self.conn = mysql.connector.connect(**self.config)
            self.cur = self.conn.cursor()
            print("Connected to database.")
            return True
        except mysql.connector.Error as e:
            print(f"Connection error: {e}")
            return False

    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        print("Database connection closed.")

    def add_booking(self, customer_id, table_id, booking_date, booking_time, number_of_guests):
        """AddBooking() procedure - add a new booking"""
        try:
            booking_datetime = datetime.strptime(f"{booking_date} {booking_time}", "%Y-%m-%d %H:%M:%S")
            sql = "INSERT INTO Bookings (customer_id, table_id, booking_datetime, number_of_guests, status) VALUES (%s, %s, %s, %s, %s)"
            values = (customer_id, table_id, booking_datetime, number_of_guests, 'Confirmed')
            self.cur.execute(sql, values)
            self.conn.commit()
            print(f"Booking added with ID: {self.cur.lastrowid}")
            return self.cur.lastrowid
        except Exception as e:
            print(f"Error in add_booking: {e}")
            self.conn.rollback()
            return None

    def update_booking(self, booking_id, **kwargs):
        """
        UpdateBooking() procedure - update booking details
        kwargs can be any of:
          table_id, booking_date, booking_time, number_of_guests, status
        """
        try:
            update_fields = []
            values = []

            if "table_id" in kwargs:
                update_fields.append("table_id = %s")
                values.append(kwargs["table_id"])

            if "booking_date" in kwargs and "booking_time" in kwargs:
                dt = datetime.strptime(f"{kwargs['booking_date']} {kwargs['booking_time']}", "%Y-%m-%d %H:%M:%S")
                update_fields.append("booking_datetime = %s")
                values.append(dt)
            elif "booking_date" in kwargs or "booking_time" in kwargs:
                print("Error: Please provide both booking_date and booking_time to update date/time.")
                return False

            if "number_of_guests" in kwargs:
                update_fields.append("number_of_guests = %s")
                values.append(kwargs["number_of_guests"])

            if "status" in kwargs:
                update_fields.append("status = %s")
                values.append(kwargs["status"])

            if not update_fields:
                print("No valid fields provided to update.")
                return False

            sql = f"UPDATE Bookings SET {', '.join(update_fields)} WHERE booking_id = %s"
            values.append(booking_id)

            self.cur.execute(sql, values)
            self.conn.commit()

            if self.cur.rowcount > 0:
                print(f"Booking {booking_id} updated successfully.")
                return True
            else:
                print(f"No booking found with ID {booking_id}.")
                return False

        except Exception as e:
            print(f"Error in update_booking: {e}")
            self.conn.rollback()
            return False

    def cancel_booking(self, booking_id):
        """CancelBooking() procedure - set booking status to Cancelled"""
        try:
            sql = "UPDATE Bookings SET status = 'Cancelled' WHERE booking_id = %s"
            self.cur.execute(sql, (booking_id,))
            self.conn.commit()
            if self.cur.rowcount > 0:
                print(f"Booking {booking_id} cancelled successfully.")
                return True
            else:
                print(f"No booking found with ID {booking_id} to cancel.")
                return False
        except Exception as e:
            print(f"Error in cancel_booking: {e}")
            self.conn.rollback()
            return False

    def get_max_quantity(self, table_id):
        """GetMaxQuantity() procedure - get max guests for a table"""
        try:
            sql = "SELECT capacity FROM Tables WHERE table_id = %s"
            self.cur.execute(sql, (table_id,))
            result = self.cur.fetchone()
            if result:
                print(f"Max capacity for table {table_id} is {result[0]}")
                return result[0]
            else:
                print(f"No table found with ID {table_id}.")
                return None
        except Exception as e:
            print(f"Error in get_max_quantity: {e}")
            return None

    def manage_booking(self, booking_id, action, **kwargs):
        """
        ManageBooking() procedure - react to changes in data or perform booking-related actions
        Example actions:
         - confirm: set status to Confirmed
         - decline: set status to Declined
         - reschedule: update booking_date and booking_time (pass as kwargs)
         - check_status: get current booking status
        """
        try:
            if action == "confirm":
                return self.update_booking(booking_id, status="Confirmed")
            elif action == "decline":
                return self.update_booking(booking_id, status="Declined")
            elif action == "reschedule":
                date = kwargs.get("booking_date")
                time = kwargs.get("booking_time")
                if date and time:
                    return self.update_booking(booking_id, booking_date=date, booking_time=time)
                else:
                    print("Reschedule requires booking_date and booking_time.")
                    return False
            elif action == "check_status":
                sql = "SELECT status FROM Bookings WHERE booking_id = %s"
                self.cur.execute(sql, (booking_id,))
                status = self.cur.fetchone()
                if status:
                    print(f"Booking {booking_id} status: {status[0]}")
                    return status[0]
                else:
                    print(f"No booking found with ID {booking_id}.")
                    return None
            else:
                print(f"Unknown action '{action}' in manage_booking.")
                return False

        except Exception as e:
            print(f"Error in manage_booking: {e}")
            self.conn.rollback()
            return False

# Example usage
if __name__ == "__main__":
    # MODIFY THESE with your actual MySQL credentials
    host = "localhost"
    user = "your_mysql_user"
    password = "your_mysql_password"
    database = "little_lemon"

    # Initialize system and connect
    ll = LittleLemonBookingSystem(host, user, password, database)
    if ll.connect():
        # Make sure your database has data in Customers and Tables for testing:
        # For quick testing you can do the following insertions in your MySQL shell:
        # INSERT INTO Customers(name,email,phone) VALUES ('Alice','alice@example.com','1234567890');
        # INSERT INTO Tables(capacity,location) VALUES (4,'Indoor');

        customer_id = 1    # Use existing customer_id from your Customers table
        table_id = 1       # Use existing table_id from your Tables table

        # Add a booking
        booking_id = ll.add_booking(customer_id, table_id, "2024-11-01", "19:00:00", 3)
        
        # Get max capacity
        ll.get_max_quantity(table_id)

        # Update booking number_of_guests and time
        if booking_id:
            ll.update_booking(booking_id, number_of_guests=4)
            ll.update_booking(booking_id, booking_date="2024-11-02", booking_time="20:00:00")

        # Manage booking status
        if booking_id:
            ll.manage_booking(booking_id, "confirm")
            ll.manage_booking(booking_id, "check_status")
            ll.manage_booking(booking_id, "reschedule", booking_date="2024-11-03", booking_time="18:00:00")
            ll.manage_booking(booking_id, "decline")

        # Cancel booking
        if booking_id:
            ll.cancel_booking(booking_id)

        ll.close()
