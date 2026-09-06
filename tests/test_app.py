from app import create_app


def test_login_page_loads():
    app = create_app()
    app.config.update(TESTING=True)

    with app.test_client() as client:
        response = client.get("/login")

    assert response.status_code == 200
