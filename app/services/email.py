from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings

# Configuración de la conexión al servidor de email
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)

async def enviar_email_verificacion(email: str, token: str):
    """
    HU-05 — Envía el email de confirmación al usuario recién registrado.
    El enlace contiene el token JWT de verificación.
    """
    enlace = f"http://localhost:8000/api/v1/auth/verificar-email?token={token}"

    mensaje = MessageSchema(
        subject="Verificá tu cuenta — Calistenia App",
        recipients=[email],
        body=f"""
        <h2>Bienvenido a Calistenia App</h2>
        <p>Hacé clic en el siguiente enlace para verificar tu cuenta:</p>
        <a href="{enlace}">Verificar mi cuenta</a>
        <p>Este enlace expira en 24 horas.</p>
        <br>
        <p>Si no creaste una cuenta, ignorá este email.</p>
        """,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(mensaje)

async def enviar_email_recuperacion(email: str, token: str):
    """
    HU-08 — Envía el email de recuperación de contraseña.
    El enlace contiene el token JWT de recuperación.
    """
    enlace = f"http://localhost:3000/recuperar-password?token={token}"

    mensaje = MessageSchema(
        subject="Recuperación de contraseña — Calistenia App",
        recipients=[email],
        body=f"""
        <h2>Recuperación de contraseña</h2>
        <p>Recibimos una solicitud para restablecer tu contraseña.</p>
        <p>Hacé clic en el siguiente enlace para crear una nueva:</p>
        <a href="{enlace}">Restablecer contraseña</a>
        <p>Este enlace expira en 1 hora.</p>
        <br>
        <p>Si no solicitaste esto, ignorá este email.</p>
        """,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(mensaje)

async def enviar_email_aprobacion(email: str, aprobado: bool, motivo: str = None):
    """
    HU-06 — Notifica al alumno el resultado de su solicitud de registro.
    """
    if aprobado:
        asunto = "¡Tu cuenta fue aprobada! — Calistenia App"
        cuerpo = """
        <h2>¡Bienvenido!</h2>
        <p>Tu cuenta fue aprobada por el profesor. Ya podés iniciar sesión.</p>
        """
    else:
        asunto = "Solicitud de cuenta rechazada — Calistenia App"
        cuerpo = f"""
        <h2>Solicitud rechazada</h2>
        <p>Tu solicitud de registro fue rechazada.</p>
        {"<p>Motivo: " + motivo + "</p>" if motivo else ""}
        <p>Contactá a tu profesor para más información.</p>
        """

    mensaje = MessageSchema(
        subject=asunto,
        recipients=[email],
        body=cuerpo,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(mensaje)