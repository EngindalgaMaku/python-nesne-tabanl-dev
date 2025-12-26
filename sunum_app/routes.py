from __future__ import annotations

import os

from flask import Flask
from flask import jsonify

from .controllers import (
    AdminEkipView,
    AdminOgretmenView,
    AdminOgrenciView,
    AdminPanelView,
    AdminSunumView,
    AyarlarView,
    DegerlendirmeYapView,
    IndexView,
    LoginView,
    LogoutView,
    SunumDetayView,
)


def register_routes(app: Flask) -> None:
    def favicon():
        return ("", 204)

    def build_info():
        return jsonify(
            {
                "render": {
                    "service_id": os.getenv("RENDER_SERVICE_ID"),
                    "service_name": os.getenv("RENDER_SERVICE_NAME"),
                    "git_commit": os.getenv("RENDER_GIT_COMMIT"),
                }
            }
        )

    app.add_url_rule("/", view_func=IndexView.as_view("index"))

    app.add_url_rule("/favicon.ico", view_func=favicon)

    app.add_url_rule("/__build", view_func=build_info)

    app.add_url_rule(
        "/login",
        view_func=LoginView.as_view("login"),
        methods=["GET", "POST"],
    )
    app.add_url_rule("/logout", view_func=LogoutView.as_view("logout"))

    app.add_url_rule("/admin", view_func=AdminPanelView.as_view("admin_panel"))

    app.add_url_rule(
        "/sunum/<int:sunum_id>",
        view_func=SunumDetayView.as_view("sunum_detay"),
    )

    app.add_url_rule(
        "/sunum/<int:sunum_id>/degerlendirme",
        view_func=DegerlendirmeYapView.as_view("degerlendirme_yap"),
        methods=["GET", "POST"],
    )

    app.add_url_rule(
        "/ayarlar",
        view_func=AyarlarView.as_view("ayarlar"),
        methods=["GET", "POST"],
    )

    app.add_url_rule(
        "/admin/ekip",
        view_func=AdminEkipView.as_view("admin_ekip"),
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/admin/ogrenci",
        view_func=AdminOgrenciView.as_view("admin_ogrenci"),
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/admin/ogretmen",
        view_func=AdminOgretmenView.as_view("admin_ogretmen"),
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/admin/sunum",
        view_func=AdminSunumView.as_view("admin_sunum"),
        methods=["GET", "POST"],
    )
