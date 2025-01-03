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
        # Render the password reset request form
        return render_template("reset_password.html")
    
    email = request.form.get("email")
    if not email:
        flash("Please enter your email address.", "error")
        return redirect(url_for("reset_password"))
    
    try:
        # Send the password reset email
        supabase_client.auth.reset_password_for_email(email)
        print("[DEBUG] Password reset email sent to:", email)
        return redirect(url_for("password_reset_email_sent"))
    except Exception as e:
        print("[ERROR] Failed to send password reset email:", str(e))
        flash("Failed to send password reset email. Please try again later.", "error")
        return redirect(url_for("reset_password"))

@app.route("/password-reset-email-sent", methods=["GET"])
def password_reset_email_sent():
    return render_template("password_reset_email_sent.html")


@app.route("/reset-password-form", methods=["GET", "POST"])
def reset_password_form():
    if request.method == "GET":
        # Render the password reset form without any token validation
        return render_template("reset_password_form.html", error_message=None, success_message=None)

    # Handle POST: Password reset form submission
    access_token = request.form.get("access_token")
    refresh_token = request.form.get("refresh_token")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if not access_token or not refresh_token:
        return render_template(
            "reset_password_form.html",
            error_message="Invalid or missing authentication tokens. Please request a new password reset.",
            success_message=None
        )

    if not new_password or not confirm_password:
        return render_template(
            "reset_password_form.html",
            error_message="Both password fields are required.",
            success_message=None
        )

    if new_password != confirm_password:
        return render_template(
            "reset_password_form.html",
            error_message="Passwords do not match.",
            success_message=None
        )
    
    # Authenticate the session using the provided tokens
    try:
        supabase_client.auth.set_session(access_token, refresh_token)
        print("[DEBUG] User session established with access token.")
    except Exception as e:
        print("[ERROR] Failed to establish session:", str(e))
        return render_template(
            "reset_password_form.html",
            error_message="Failed to authenticate with the provided tokens. Please request a new password reset.",
            success_message=None
        )

    # Update the user's password
    try:
        response = supabase_client.auth.update_user({"password": new_password})
        print("[DEBUG] Password update response:", response)

        if not hasattr(response, "user") or response.user is None:
            return render_template(
                "reset_password_form.html",
                error_message="Failed to update password. Please try again.",
                success_message=None
            )

        # Redirect to success page
        return redirect(url_for("password_reset_success"))
    
    except Exception as e:
        error_message = str(e)
        print("[ERROR] Exception during password update:", error_message)

        if "New password should be different from the old password" in error_message:
            error_message = "Your new password must be different from your old password."
        else:
            error_message = f"Error updating password: {error_message}"

        return render_template(
            "reset_password_form.html",
            error_message=error_message,
            success_message=None
        )

@app.route("/password-reset-success", methods=["GET"])
def password_reset_success():
    return render_template("password_reset_success.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
