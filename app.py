# ########################################
# ########## SETUP

# APP.PY
# CS340 Project Group 21 - SQLurp the Pho
# Lorine Kaye Mijares and Annabel Vu

# Citation for the code below (all routes):
# Date: 6/5/2025
# All code for routes based on the the starter code in Module 8, Exploration "Implementing CUD operations in your app" 
# Source URl: https://canvas.oregonstate.edu/courses/1999601/pages/exploration-implementing-cud-operations-in-your-app?module_item_id=25352968

# Citation for use of AI Tools:
# Date: 6/5/2025
# Summary of prompts used on app.py
# AI used to troubleshoot errors in routes for Order Details causing blank dropdown menus on the add and update forms,
# duplication of IDs in the dropdown menus, and newly-added Order Details resetting the display table upon submitting the Add form
# AI Source URL: https://chatgpt.com

PORT = 10233
from flask import Flask, render_template, request, redirect
import database.db_connector as db  
from flask import request, redirect, url_for
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).with_name(".env"))

PORT = 10233
app = Flask(__name__)

# home page
@app.route("/", methods=["GET"])
def home():
    try:
        return render_template("home.j2")
    except Exception as e:
        print(f"Error rendering page: {e}")
        return "An error occurred while rendering the page.", 500


# READ customers
@app.route("/customers", methods=["GET"])
def customers():
    try:
        dbConnection = db.connectDB()
        query = "SELECT * FROM Customers;"
        customers = db.query(dbConnection, query)
        return render_template("customers.j2", customers=customers)
    except Exception as e:
        print(f"Error executing customers query: {e}")
        return "An error occurred while executing the database queries.", 500
    finally:
        if "dbConnection" in locals() and dbConnection:
            dbConnection.close()


# READ orders
@app.route("/orders", methods=["GET"])
def orders():
    try:
        dbConnection = db.connectDB()
        orders_query = "SELECT * FROM Orders;"
        customers_query = "SELECT customerID, firstName, lastName FROM Customers;"
        orders = db.query(dbConnection, orders_query)
        customers = db.query(dbConnection, customers_query)
        print("Orders:", orders)
        print("Customers:", customers)
        return render_template("orders.j2", orders=orders, customers=customers)
    except Exception as e:
        print(f"Error fetching orders: {e}")
        return "Failed to load orders", 500
    finally:
        if "dbConnection" in locals() and dbConnection:
            dbConnection.close()


# READ order details
@app.route('/order-details', methods=["GET"])
def order_details():
    conn = None
    try:
        conn = db.connectDB()

        # Show ALL order details, even if related rows are missing
        select_query = """
            SELECT 
                od.orderID,
                od.menuItemID,
                mi.itemName,
                od.quantityMenuItem,
                o.customerID,
                c.firstName,
                c.lastName
            FROM OrderDetails od
            LEFT JOIN MenuItems mi ON od.menuItemID = mi.menuItemID
            LEFT JOIN Orders o      ON od.orderID   = o.orderID
            LEFT JOIN Customers c   ON o.customerID = c.customerID
            ORDER BY od.orderID ASC, od.menuItemID ASC;
        """
        results = db.query(conn, select_query)
        print("DEBUG order_details count:", len(results))

        # Dropdowns
        orders = db.query(conn, "SELECT orderID FROM Orders ORDER BY orderID ASC;")
        menu_items = db.query(conn, "SELECT menuItemID, itemName FROM MenuItems ORDER BY menuItemID ASC;")

        return render_template(
            "order_details.j2",
            order_details=results,
            orders=orders,
            menu_items=menu_items
        )
    except Exception as e:
        print("Error fetching order details:", e)
        return "An error occurred while executing the database queries.", 500
    finally:
        try:
            if conn: conn.close()
        except:
            pass

# READ menu items
@app.route("/menu-items", methods=["GET"])
def menu_items():
    try:
        dbConnection = db.connectDB()
        query = "SELECT * FROM MenuItems;"
        items = db.query(dbConnection, query)
        return render_template("menu_items.j2", menu_items=items)
    except Exception as e:
        print(f"Error fetching menu items: {e}")
        return "Failed to load menu items", 500
    finally:
        if "dbConnection" in locals() and dbConnection:
            dbConnection.close()


# CREATE menu item
from decimal import Decimal, InvalidOperation
def _normalize_cost(raw: str | None) -> str | None:
    if not raw:
        return None
    v = raw.strip().replace('%', '').replace(' ', '')
    # accept 20, 20%, 0.2, 0.20, etc.
    if v in ('20', '020', '0.2', '0.20', '20.0'):
        return '20%'
    if v in ('50', '050', '0.5', '0.50', '50.0'):
        return '50%'
    return None

@app.route("/create-menu-item", methods=["POST"])
def create_menu_item():
    conn = None
    try:
        f = request.form
        print("DEBUG /create-menu-item raw form:", dict(f))  # <- watch your terminal

        name = (f.get("itemName") or "").strip()
        description = f.get("description") or None

        price_raw = f.get("price")
        try:
            price = float(Decimal(price_raw)) if price_raw not in (None, "") else None
        except (InvalidOperation, TypeError, ValueError):
            price = None

        cost = _normalize_cost(f.get("costOfFood"))

        # If anything is off, show exactly what parsed
        if not name or price is None or cost is None:
            print("DEBUG parsed ->", {"name": name, "price": price, "costOfFood": cost})
            raise ValueError("Invalid form data")

        conn = db.connectDB()

        # Call SP with OUT param (make sure you reloaded plsql.sql without the trailing SELECT)
        db.query(conn,
            "CALL sp_CreateMenuItem(%s, %s, %s, %s, @new_id)",
            [name, description, price, cost]
        )
        new_id = db.query(conn, "SELECT @new_id AS id")[0]["id"]
        print(f"Created menu item: {name} (ID: {new_id})")

        return redirect(url_for("menu_items"))
    except Exception as e:
        print("Error creating menu item:", e)
        return "Error creating menu item", 500
    finally:
        try:
            if conn: conn.close()
        except:
            pass



# UPDATE menu item
def _normalize_cost(raw: str | None) -> str | None:
    if not raw:
        return None
    v = raw.strip().replace('%', '').replace(' ', '')
    if v in ('20', '0.2', '0.20', '20.0'):
        return '20%'
    if v in ('50', '0.5', '0.50', '50.0'):
        return '50%'
    return None

@app.route("/update-menu-item", methods=["POST"])
def update_menu_item():
    conn = None
    try:
        f = request.form
        print("DEBUG /update-menu-item raw:", dict(f))

        # required IDs
        try:
            menu_id = int(str(f.get("menuItemID", "")).strip())
        except Exception:
            menu_id = 0

        # optional text fields (we'll backfill from DB if missing)
        name = (f.get("itemName") or "").strip()
        description = f.get("description") or None

        # price
        price_raw = f.get("price")
        try:
            price = float(Decimal(price_raw)) if price_raw not in (None, "") else None
        except (InvalidOperation, TypeError, ValueError):
            price = None

        # costOfFood enum
        cost = _normalize_cost(f.get("costOfFood"))

        if not menu_id:
            return ("Missing menuItemID", 400)

        conn = db.connectDB()

        # If form omitted name/description, pull current values from DB
        if not name or description is None:
            rows = db.query(conn, "SELECT itemName, description FROM MenuItems WHERE menuItemID = %s", [menu_id])
            if not rows:
                return ("Menu item not found", 404)
            current = rows[0]
            if not name:
                name = (current.get("itemName") or "").strip()
            if description is None:
                description = current.get("description")

        # Validate the numeric/enum fields now (we expect both present)
        if price is None:
            return ("Missing or invalid price", 400)
        if cost not in ("20%", "50%"):
            return ("Missing or invalid costOfFood (20% or 50%)", 400)

        # Call the stored procedure with ALL 5 args
        db.query(conn,
            "CALL sp_UpdateMenuItem(%s, %s, %s, %s, %s)",
            [menu_id, name, description, price, cost]
        )

        print(f"Updated menu item #{menu_id}: {name}")
        return redirect(url_for("menu_items"))

    except Exception as e:
        print("Error updating menu item:", e)
        return "Error updating menu item", 500
    finally:
        try:
            if conn: conn.close()
        except:
            pass


# DELETE menu item
@app.route("/delete-menu-item", methods=["POST"])
def delete_menu_item():
    print("Route /delete-menu-item was hit!")  # DEBUG LINE

    try:
        dbConnection = db.connectDB()
        cursor = dbConnection.cursor()

        item_id = request.form["menuItemID"]
        item_name = request.form["itemName"]

        query = "CALL sp_DeleteMenuItem(%s)";
        cursor.execute(query, (item_id,))
        dbConnection.commit()
        print(f"Deleted menu item: {item_name} (ID: {item_id})")

        return redirect("/menu-items")
    
    except Exception as e:
        print(f"Error deleting menu item: {e}")
        return "Failed to delete menu item", 500
    
    finally:
        if "dbConnection" in locals() and dbConnection:
            dbConnection.close()


# READ Sales Page
@app.route("/sales", methods=["GET"])
def sales():
    try:
        dbConnection = db.connectDB()
        sales_query = "SELECT * FROM Sales;"
        items_query = "SELECT * FROM MenuItems;"
        sales = db.query(dbConnection, sales_query)
        menu_items = db.query(dbConnection, items_query)
        return render_template("sales.j2", sales=sales, menu_items=menu_items)
    except Exception as e:
        print(f"Error fetching sales: {e}")
        return "Failed to load sales", 500
    finally:
        if "dbConnection" in locals() and dbConnection:
            dbConnection.close()


# ADD/CREATE order detail
# @app.route("/add-order-detail", methods=["POST"])
# def add_order_detail():
#     conn = None
#     try:
#         f = request.form
#         print("DEBUG /add-order-detail raw form:", dict(f))  # watch terminal

#         # Accept either 'quantityMenuItem' or a generic 'quantity'
#         qty_raw = f.get("quantityMenuItem") or f.get("quantity") or ""
#         try:
#             qty = int(qty_raw)
#         except Exception:
#             qty = None

#         # Parse IDs safely (avoid KeyError → 400)
#         try:
#             order_id = int(f.get("orderID", ""))
#             menu_id  = int(f.get("menuItemID", ""))
#         except Exception:
#             order_id = None
#             menu_id = None

#         # Validate inputs
#         if not order_id or not menu_id or not qty or qty < 1:
#             print("DEBUG parsed ->", {"orderID": order_id, "menuItemID": menu_id, "qty": qty})
#             return ("Missing or invalid form fields", 400)

#         conn = db.connectDB()

#         # Insert (update if the same (orderID, menuItemID) already exists)
#         db.query(conn, """
#             INSERT INTO OrderDetails (orderID, menuItemID, quantityMenuItem)
#             VALUES (%s, %s, %s) AS new
#             ON DUPLICATE KEY UPDATE quantityMenuItem = new.quantityMenuItem
#         """, [order_id, menu_id, qty])

#         return redirect(url_for("order_details"))
#     except Exception as e:
#         print("Error adding order detail:", e)
#         return "Error adding order detail", 500
#     finally:
#         try:
#             if conn: conn.close()
#         except:
#             pass

def _to_int(val):
    try:
        return int(str(val).strip())
    except Exception:
        return None

# ADD / CREATE order detail
@app.route("/add-order-detail", methods=["POST"])
def add_order_detail():
    conn = None
    try:
        f = request.form
        print("DEBUG /add-order-detail raw form:", dict(f))

        order_id = _to_int(f.get("orderID"))
        menu_id  = _to_int(f.get("menuItemID"))
        qty      = _to_int(f.get("quantityMenuItem") or f.get("quantity"))

        # validate
        if not order_id or not menu_id or qty is None or qty < 1:
            print("DEBUG parsed ->", {"orderID": order_id, "menuItemID": menu_id, "qty": qty})
            return ("Missing or invalid form fields", 400)

        conn = db.connectDB()

        # 1) try UPDATE
        affected = db.query(conn, """
            UPDATE OrderDetails
            SET quantityMenuItem = %s
            WHERE orderID = %s AND menuItemID = %s
        """, [qty, order_id, menu_id])

        # 2) if nothing updated, INSERT the row
        if affected == 0:
            db.query(conn, """
                INSERT INTO OrderDetails (orderID, menuItemID, quantityMenuItem)
                VALUES (%s, %s, %s)
            """, [order_id, menu_id, qty])

        return redirect(url_for("order_details"))

    except Exception as e:
        print("Error adding order detail:", e)
        return "Error adding order detail", 500
    finally:
        try:
            if conn: conn.close()
        except:
            pass


# UPDATE order detail
@app.route("/update-order-detail", methods=["POST"])
def update_order_detail():
    conn = None
    try:
        f = request.form
        order_id = int(str(f.get("orderID", "")).strip() or 0)
        menu_id  = int(str(f.get("menuItemID", "")).strip() or 0)
        qty      = int(str(f.get("quantityMenuItem", "")).strip() or 0)

        if not order_id or not menu_id or qty < 1:
            return ("Missing or invalid form fields", 400)

        conn = db.connectDB()

        affected = db.query(conn, """
            UPDATE OrderDetails
            SET quantityMenuItem = %s
            WHERE orderID = %s AND menuItemID = %s
        """, [qty, order_id, menu_id])

        if affected == 0:
            db.query(conn, """
                INSERT INTO OrderDetails (orderID, menuItemID, quantityMenuItem)
                VALUES (%s, %s, %s)
            """, [order_id, menu_id, qty])

        return redirect(url_for("order_details"))
    except Exception as e:
        print("Error updating order detail:", e)
        return "Failed to update order detail", 500
    finally:
        try:
            if conn: conn.close()
        except:
            pass


# DELETE order detail
@app.route("/delete-order-detail", methods=["POST"])
def delete_order_detail():
    try:
        dbConnection = db.connectDB()
        cursor = dbConnection.cursor()

        order_id = request.form["orderID"]
        menu_item_id = request.form["menuItemID"]

        query = "CALL sp_DeleteOrderDetail(%s, %s);"
        cursor.execute(query, (order_id, menu_item_id))

        dbConnection.commit()
        print(f"Deleted Order Detail: OrderID={order_id}, MenuItemID={menu_item_id}")
        return redirect("/order-details")

    except Exception as e:
        print(f"Error deleting order detail: {e}")
        return "Failed to delete order detail", 500
    finally:
        if "dbConnection" in locals() and dbConnection:
            dbConnection.close()


# RESET db
@app.route("/reset-db", methods=["POST"])
def reset_db():
    try:
        dbConnection = db.connectDB()
        cursor = dbConnection.cursor()

        cursor.callproc("sp_reset_PHOdatabase")
        dbConnection.commit()
        print("Database reset successfully.")

        return redirect(request.referrer)
    
    except Exception as e:
        print(f"Error resetting database: {e}")
        return "Failed to reset database", 500
    
    finally:
        if "dbConnection" in locals() and dbConnection:
            dbConnection.close()

# LISTENER
if __name__ == "__main__":
    import os
    os.environ['FLASK_ENV'] = 'development'
    app.run(host="0.0.0.0", port=10233, debug=True)
