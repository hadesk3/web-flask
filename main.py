from website import create_app
from flask_principal import Principal,Permission, RoleNeed,UserNeed,identity_changed,identity_loaded,Identity,AnonymousIdentity

app = create_app()
principal = Principal(app)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug = True)