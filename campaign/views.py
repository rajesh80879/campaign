from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
import logging

# Loggers are added to check the failures
logger = logging.getLogger(__name__)


# I have added form fields here instead of this we can also get this data through database
FORM_STEPS = ["goal_selection", "deliverable", "audience", "campaign_design", "summary"]


def campaign_redirect(request):
    """Redirect to the first step of the campaign wizard."""
    return redirect("campaign_wizard", step=0)


def get_form_data(request):
    """Retrieve saved form data from session."""

    try:
        return request.session.get("campaign_data", {step: {} for step in FORM_STEPS})
    except Exception as e:
        logger.error(f"Error retrieving form data: {e}")
        return {step: {} for step in FORM_STEPS}


def save_form_data(request, step, data):
    """Save form step data to session."""
    try:
        form_data = get_form_data(request)
        form_data[step] = data
        request.session["campaign_data"] = form_data
        request.session.modified = True
        logger.info(f"Data saved for step: {step}")
    except Exception as e:
        logger.error(f"Error saving form data for {step}: {e}")


def reset_form(request):
    """Clear session data."""
    try:
        request.session["campaign_data"] = {step: {} for step in FORM_STEPS}
        request.session.modified = True
        logger.info("Form reset successfully.")
    except Exception as e:
        logger.error(f"Error resetting form: {e}")


def campaign_wizard(request, step=0):
    """Handle step-by-step form flow ensuring sequential completion."""
    try:
        if step >= len(FORM_STEPS):
            return redirect("campaign_dashboard")

        form_data = get_form_data(request)

        if step > 0 and not form_data[FORM_STEPS[step - 1]]:
            return redirect("campaign_wizard", step=step - 1)

        step_name = FORM_STEPS[step]
        saved_data = form_data.get(step_name, {})

        if request.method == "POST":
            save_form_data(request, step_name, request.POST.dict())

            if "continue" in request.POST:
                return redirect("campaign_wizard", step=step + 1)
            elif "do_later" in request.POST:
                return redirect("campaign_dashboard")
            elif "reset" in request.POST:
                reset_form(request)
                return redirect("campaign_wizard", step=step)

        return render(
            request,
            "campaign/step_form.html",
            {
                "step": step,
                "step_name": step_name,
                "saved_data": saved_data,
                "total_steps": len(FORM_STEPS),
                "step_range": range(
                    len(FORM_STEPS)
                ),  
            },
        )

    except Exception as e:
        logger.error(f"Error in campaign wizard step {step}: {e}")
        return HttpResponseBadRequest("An error occurred while processing the form.")


def campaign_dashboard(request):
    """Show saved campaign data."""
    try:
        return render(
            request,
            "campaign/dashboard.html",
            {"campaign_data": get_form_data(request)},
        )
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return HttpResponseBadRequest("Unable to load dashboard data.")
