from flask import Flask, render_template, request, redirect, url_for, flash
import supabase
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Configure Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/support")
def support():
    return render_template("support.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "GET":
        return render_template("reset_password.html")
    
    email = request.form.get("email")
    if not email:
        flash("Please enter your email address.", "error")
        return redirect(url_for("reset_password"))
    
    try:
        supabase_client.auth.reset_password_for_email(
            email, redirect_to="https://familyalbum.hants-williams.com/reset-password-form"
        )
        flash("A password reset link has been sent to your email.", "success")
    except Exception as e:
        flash(f"Error sending reset email: {str(e)}", "error")
    
    return redirect(url_for("reset_password"))

@app.route("/reset-password-form", methods=["GET", "POST"])
def reset_password_form():
    if request.method == "GET":
        return render_template("reset_password_form.html")
    
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")
    
    if not new_password or not confirm_password:
        flash("Both password fields are required.", "error")
        return redirect(url_for("reset_password_form"))
    
    if new_password != confirm_password:
        flash("Passwords do not match.", "error")
        return redirect(url_for("reset_password_form"))
    
    try:
        supabase_client.auth.update_user({"password": new_password})
        flash("Your password has been updated successfully.", "success")
    except Exception as e:
        flash(f"Error updating password: {str(e)}", "error")
    
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
