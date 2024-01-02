from django.utils import timezone


def get_ultimo_editor(self, obj):
    historial = obj.historical.all().order_by('-history_date')
    for record in historial:
        if record.history_user:
            return {
                'nombre_completo': record.history_user.nombre_completo,
                'perfil': record.history_user.perfil
            }
    return None


def get_fecha_ultima_modificacion(self, obj):
    try:
        ultimo_registro = obj.historical.latest('history_date')
        if ultimo_registro:
            fecha_local = timezone.localtime(ultimo_registro.history_date)
            return fecha_local.strftime('%d/%m/%Y - %H:%M')
        return None
    except obj.historical.model.DoesNotExist:
        return None


def calcular_tiempo_registro(self, etapa_obj, fecha_envio):
    if etapa_obj.fecha_inicio and fecha_envio:
        delta = fecha_envio - etapa_obj.fecha_inicio
        total_seconds = int(delta.total_seconds())
        dias = total_seconds // (24 * 3600)
        horas = (total_seconds % (24 * 3600)) // 3600
        minutos = (total_seconds % 3600) // 60
        return {'dias': dias, 'horas': horas, 'minutos': minutos}
    return {'dias': 0, 'horas': 0, 'minutos': 0}


def obtener_estado_accion_generico(
        self,
        condicion,
        usuario_grupo,
        conteo_condicion,
        nombre_singular,
        accion_usuario_grupo,
        accion_general,
        accion_finalizada_usuario_grupo,
        accion_finalizada_general,
        nombre_plural=None,
        condicion_anterior=None,
        id=None):

    return {
        "id": id,
        "nombre": nombre_plural if conteo_condicion > 1 else nombre_singular,
        "estado": 'finalizada' if condicion else 'revision' if condicion_anterior else 'pendiente',
        "accion": accion_finalizada_usuario_grupo if condicion else accion_usuario_grupo
    }
    user = self.context['request'].user
    grupos_usuario = [grupo.strip() for grupo in usuario_grupo.split(',')]

    # Verificar si el usuario pertenece a al menos uno de los grupos especificados
    es_grupo_usuario = any(user.groups.filter(name=grupo).exists() for grupo in grupos_usuario)

    if es_grupo_usuario:
        return {
            "id": id,
            "nombre": nombre_plural if conteo_condicion > 1 else nombre_singular,
            "estado": 'finalizada' if condicion else 'revision' if condicion_anterior else 'pendiente',
            "accion": accion_finalizada_usuario_grupo if condicion else accion_usuario_grupo
        }
    else:
        return {
            "id": id,
            "nombre": nombre_plural if conteo_condicion > 1 else nombre_singular,
            "estado": 'finalizada' if condicion else 'pendiente',
            "accion": accion_finalizada_general if condicion else accion_general
        }


def reordenar_detalle(self, detalle, user):
    # Identificar si el usuario actual está mencionado en cada elemento de detalle
    usuario_principal = []
    otros = []

    nombre_sector_usuario = user.sector.nombre if user.sector else None

    for d in detalle:
        if user.nombre_completo in d['nombre'] or (nombre_sector_usuario and nombre_sector_usuario in d['nombre']):
            usuario_principal.append(d)
        else:
            otros.append(d)

    return usuario_principal + otros
