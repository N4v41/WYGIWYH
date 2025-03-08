from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods

from apps.common.decorators.htmx import only_htmx
from apps.transactions.forms import TransactionCategoryForm
from apps.transactions.models import TransactionCategory
from apps.common.models import SharedObject
from apps.common.forms import SharedObjectForm


@login_required
@require_http_methods(["GET"])
def categories_index(request):
    return render(
        request,
        "categories/pages/index.html",
    )


@only_htmx
@login_required
@require_http_methods(["GET"])
def categories_list(request):
    return render(
        request,
        "categories/fragments/list.html",
    )


@only_htmx
@login_required
@require_http_methods(["GET"])
def categories_table_active(request):
    categories = TransactionCategory.objects.filter(active=True).order_by("id")
    return render(
        request,
        "categories/fragments/table.html",
        {"categories": categories, "active": True},
    )


@only_htmx
@login_required
@require_http_methods(["GET"])
def categories_table_archived(request):
    categories = TransactionCategory.objects.filter(active=False).order_by("id")
    return render(
        request,
        "categories/fragments/table.html",
        {"categories": categories, "active": False},
    )


@only_htmx
@login_required
@require_http_methods(["GET", "POST"])
def category_add(request, **kwargs):
    if request.method == "POST":
        form = TransactionCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Category added successfully"))

            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": "updated, hide_offcanvas",
                },
            )
    else:
        form = TransactionCategoryForm()

    return render(
        request,
        "categories/fragments/add.html",
        {"form": form},
    )


@only_htmx
@login_required
@require_http_methods(["GET", "POST"])
def category_edit(request, category_id):
    category = get_object_or_404(TransactionCategory, id=category_id)

    if category.owner and category.owner != request.user:
        messages.error(request, _("Only the owner can edit this"))

        return HttpResponse(
            status=204,
            headers={
                "HX-Trigger": "updated, hide_offcanvas",
            },
        )

    if request.method == "POST":
        form = TransactionCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, _("Category updated successfully"))

            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": "updated, hide_offcanvas",
                },
            )
    else:
        form = TransactionCategoryForm(instance=category)

    return render(
        request,
        "categories/fragments/edit.html",
        {"form": form, "category": category},
    )


@only_htmx
@login_required
@require_http_methods(["GET", "POST"])
def category_share(request, pk):
    obj = get_object_or_404(TransactionCategory, id=pk)

    if obj.owner and obj.owner != request.user:
        messages.error(request, _("Only the owner can edit this"))

        return HttpResponse(
            status=204,
            headers={
                "HX-Trigger": "updated, hide_offcanvas",
            },
        )

    if request.method == "POST":
        form = SharedObjectForm(request.POST, instance=obj, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Configuration saved successfully"))

            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": "updated, hide_offcanvas",
                },
            )
    else:
        form = SharedObjectForm(instance=obj, user=request.user)

    return render(
        request,
        "categories/fragments/share.html",
        {"form": form, "object": obj},
    )


@only_htmx
@login_required
@require_http_methods(["DELETE"])
def category_delete(request, category_id):
    category = get_object_or_404(TransactionCategory, id=category_id)

    if category.owner != request.user and request.user in category.shared_with.all():
        category.shared_with.remove(request.user)
        messages.success(request, _("Item no longer shared with you"))
    else:
        category.delete()
        messages.success(request, _("Category deleted successfully"))

    return HttpResponse(
        status=204,
        headers={
            "HX-Trigger": "updated, hide_offcanvas",
        },
    )


@only_htmx
@login_required
@require_http_methods(["GET"])
def category_take_ownership(request, category_id):
    category = get_object_or_404(TransactionCategory, id=category_id)

    if not category.owner:
        category.owner = request.user
        category.visibility = SharedObject.Visibility.private
        category.save()

        messages.success(request, _("Ownership taken successfully"))

    return HttpResponse(
        status=204,
        headers={
            "HX-Trigger": "updated, hide_offcanvas",
        },
    )
