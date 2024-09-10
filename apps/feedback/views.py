from django.shortcuts import redirect
from django.contrib import messages
from django.views import View
from .models import Feedback

# Create your views here.


class FeedbackView(View):
    def post(self, request):
        try:
            # Get form data
            email = request.POST.get("email", "").strip()
            message = request.POST.get("message", "").strip()

            # Validate required fields
            if not message:
                messages.error(request, "Iltimos, xabar kiriting.")
                return redirect(request.META.get("HTTP_REFERER", "/"))

            # Create feedback object
            Feedback.objects.create(
                name=None,
                email=email if email else None,
                feedback_type="general",
                message=message,
                user=request.user if request.user.is_authenticated else None,
            )

            # Success message
            messages.success(
                request,
                "Fikr-mulohazangiz uchun rahmat! Biz sizning fikrlaringizni qadrlaymiz va ehtiyotkorlik bilan ko'rib chiqamiz.",
            )

            return redirect(request.META.get("HTTP_REFERER", "/"))

        except Exception:
            messages.error(
                request,
                "Kechirasiz, fikr-mulohazangizni yuborishda xatolik yuz berdi. Qaytadan urinib ko'ring.",
            )
            return redirect(request.META.get("HTTP_REFERER", "/"))
